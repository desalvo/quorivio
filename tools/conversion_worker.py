#!/usr/bin/env python3
"""Private conversion worker. Only opaque job IDs, no filesystem paths over HTTP."""
import hmac
import hashlib
import stat
import json
import os
import pathlib
import re
import shutil
import tempfile
import uuid
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from import_presentation import convert
from pptx_portable import pptx_to_portable, portable_to_pptx, inspect_pptx_fidelity

ROOT = pathlib.Path(os.path.abspath(os.environ.get('QUORIVIO_CONVERSION_DIR', '/conversions')))  # Do not resolve away a symlink before checking it
TOKEN = os.environ.get('QUORIVIO_WORKER_TOKEN', '')
JOB = re.compile(r'^[0-9a-f]{32}$')
_ACTIVE_JOBS = set()
_ACTIVE_LOCK = threading.Lock()


def _workspace(job):
    if not JOB.fullmatch(job):
        raise ValueError('invalid job id')
    if any(parent.is_symlink() for parent in (ROOT, *ROOT.parents)) or not ROOT.is_dir():
        raise ValueError('unsafe conversion root')
    workspace = ROOT / job
    if workspace.is_symlink() or not workspace.is_dir():
        raise ValueError('unknown job')
    return workspace


def _publish_file_exclusive(source, destination):
    """Link within the same workspace, failing if destination appears concurrently."""
    os.link(source, destination, follow_symlinks=False)
    source.unlink()


def _unique_json_pairs(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('duplicate JSON field')
        value[key] = item
    return value


def _reject_nonfinite(value):
    raise ValueError('non-finite JSON number')


def execute_job(job):
    workspace = _workspace(job)
    pages = workspace / 'pages'
    if pages.exists() or pages.is_symlink():
        raise ValueError('output already exists')
    sources = [p for p in (workspace / 'source.pdf', workspace / 'source.pptx') if p.is_file() and not p.is_symlink()]
    if len(sources) != 1:
        raise ValueError('expected exactly one source')
    source = sources[0]
    with _ACTIVE_LOCK:
        if job in _ACTIVE_JOBS:
            raise ValueError('job already running')
        _ACTIVE_JOBS.add(job)
    # Atomic mkdir also excludes other worker processes sharing this workspace.
    # A crash leaves the reservation in place: never steal an in-flight job.
    reservation = workspace / '.conversion-lock'
    acquired = False
    try:
        try:
            reservation.mkdir(mode=0o700)
            acquired = True
        except FileExistsError as exc:
            raise ValueError('job already running') from exc
        result = convert(source, pages)
        return {'page_count': result['page_count']}
    finally:
        if acquired:
            reservation.rmdir()
        with _ACTIVE_LOCK:
            _ACTIVE_JOBS.discard(job)


def _source_digest(path):
    if path.is_symlink() or not path.is_file() or not stat.S_ISREG(path.stat().st_mode):
        raise ValueError('Invalid source file')
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            digest.update(block)
    return digest.digest()


def execute_portable_job(job, mode):
    """Run bounded portable conversion in the isolated worker; opaque job IDs only."""
    workspace = _workspace(job)
    if mode not in ('import', 'export'):
        raise ValueError('invalid portable mode')
    reservation = workspace / '.conversion-lock'
    with _ACTIVE_LOCK:
        if job in _ACTIVE_JOBS:
            raise ValueError('job already running')
        _ACTIVE_JOBS.add(job)
    acquired = False
    staged_file = None
    staged_media = None
    published_media = False
    import_complete = False
    try:
        try:
            reservation.mkdir(mode=0o700)
            acquired = True
        except FileExistsError as exc:
            raise ValueError('job already running') from exc
        if mode == 'import':
            source = workspace / 'source.pptx'
            destination = workspace / 'portable.json'
            media = workspace / 'import-media'
            if (not source.is_file() or source.is_symlink() or
                    destination.exists() or destination.is_symlink() or
                    media.exists() or media.is_symlink()):
                raise ValueError('invalid import source or existing output')
            source_digest = _source_digest(source)
            staged_media = pathlib.Path(tempfile.mkdtemp(prefix='.import-media-', dir=workspace))
            result = pptx_to_portable(source, media_dir=staged_media)
            encoded = json.dumps(result, ensure_ascii=False, allow_nan=False).encode('utf-8')
            if len(encoded) > 2 * 1024 * 1024:
                raise ValueError('portable definition too large')
            staged_file = workspace / ('.portable-' + uuid.uuid4().hex + '.tmp')
            with staged_file.open('xb') as stream:
                os.chmod(staged_file, 0o600)
                stream.write(encoded)
            fidelity = inspect_pptx_fidelity(source)
            if _source_digest(source) != source_digest:
                raise ValueError('PowerPoint source changed during import')
            if media.exists() or media.is_symlink():
                raise ValueError('import media already exists')
            staged_media.rename(media)
            staged_media = None
            published_media = True
            _publish_file_exclusive(staged_file, destination)
            staged_file = None
            import_complete = True
            return {'pages': len(result['activities']), 'fidelity': fidelity}
        source = workspace / 'portable.json'
        destination = workspace / 'presentation.pptx'
        media = workspace / 'export-media'
        if (not source.is_file() or source.is_symlink() or
                destination.exists() or destination.is_symlink() or
                source.stat().st_size > 2 * 1024 * 1024 or media.is_symlink() or (media.exists() and not media.is_dir())):
            raise ValueError('invalid export source or existing output')
        source_digest = _source_digest(source)
        staged_file = workspace / ('.presentation-' + uuid.uuid4().hex + '.tmp')
        portable_to_pptx(json.loads(source.read_text(encoding='utf-8'),
                                    object_pairs_hook=_unique_json_pairs,
                                    parse_constant=_reject_nonfinite), staged_file, media_dir=media)
        if not staged_file.is_file() or staged_file.is_symlink() or staged_file.stat().st_size > 50 * 1024 * 1024:
            raise ValueError('export too large or missing')
        if _source_digest(source) != source_digest:
            raise ValueError('Portable definition changed during export')
        staged_file.chmod(0o600)
        size = staged_file.stat().st_size
        _publish_file_exclusive(staged_file, destination)
        staged_file = None
        return {'bytes': size}
    finally:
        if staged_file is not None:
            staged_file.unlink(missing_ok=True)
        if staged_media is not None:
            shutil.rmtree(staged_media)
        if published_media and not import_complete:
            shutil.rmtree(workspace / 'import-media')
        if acquired:
            reservation.rmdir()
        with _ACTIVE_LOCK:
            _ACTIVE_JOBS.discard(job)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/health':
            return self.reply(404, {'error': 'not_found'})
        ready = len(TOKEN) >= 32 and ROOT.is_dir() and not any(p.is_symlink() for p in (ROOT, *ROOT.parents))
        return self.reply(200 if ready else 503, {'ready': ready})

    def do_POST(self):
        if self.path not in ('/convert', '/portable-import', '/portable-export'):
            return self.reply(404, {'error': 'not_found'})
        auth_headers = self.headers.get_all('Authorization', [])
        auth = auth_headers[0] if len(auth_headers) == 1 else ''
        credential = auth[7:] if auth.startswith('Bearer ') else ''
        if len(TOKEN) < 32 or not hmac.compare_digest(credential, TOKEN):
            return self.reply(403, {'error': 'forbidden'})
        try:
            # Do not let a proxy and this worker disagree about request framing.
            if (self.headers.get('Transfer-Encoding') is not None or
                    len(self.headers.get_all('Content-Length', [])) != 1 or
                    self.headers.get('Content-Encoding') is not None):
                return self.reply(400, {'error': 'invalid_request'})
            raw_length = self.headers.get('Content-Length', '')
            if not raw_length.isascii() or not raw_length.isdecimal() or len(raw_length) > 3:
                return self.reply(400, {'error': 'invalid_request'})
            size = int(raw_length)
            if not 1 <= size <= 256:
                return self.reply(413 if size > 256 else 400, {'error': 'invalid_request'})
            if self.headers.get('Content-Type', '').split(';', 1)[0].strip().lower() != 'application/json':
                return self.reply(415, {'error': 'json_required'})
            request = json.loads(self.rfile.read(size), object_pairs_hook=_unique_json_pairs,
                                 parse_constant=_reject_nonfinite)
            if not isinstance(request, dict) or set(request) != {'job'} or not isinstance(request['job'], str):
                return self.reply(400, {'error': 'invalid_request'})
            return self.reply(200, execute_job(request['job']) if self.path == '/convert' else execute_portable_job(request['job'], 'import' if self.path == '/portable-import' else 'export'))
        except (ValueError, OSError, RuntimeError, TimeoutError, json.JSONDecodeError) as exc:
            self.log_error('conversion rejected: %s', type(exc).__name__)
            return self.reply(422, {'error': 'conversion_failed'})

    def reply(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == '__main__':
    if len(TOKEN) < 32:
        raise SystemExit('QUORIVIO_WORKER_TOKEN must contain at least 32 characters')
    if any(parent.is_symlink() for parent in (ROOT, *ROOT.parents)):
        raise SystemExit('Symlinked conversion root is forbidden')
    ROOT.mkdir(parents=True, exist_ok=True)
    ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '8099'))), Handler).serve_forever()
