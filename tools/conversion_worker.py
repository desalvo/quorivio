#!/usr/bin/env python3
"""Private conversion worker. Only opaque job IDs, no filesystem paths over HTTP."""
import hmac
import json
import os
import pathlib
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from import_presentation import convert
from pptx_portable import pptx_to_portable, portable_to_pptx, inspect_pptx_fidelity

ROOT = pathlib.Path(os.environ.get('QUORIVIO_CONVERSION_DIR', '/conversions')).resolve()
TOKEN = os.environ.get('QUORIVIO_WORKER_TOKEN', '')
JOB = re.compile(r'^[0-9a-f]{32}$')
_ACTIVE_JOBS = set()
_ACTIVE_LOCK = threading.Lock()


def execute_job(job):
    if not JOB.fullmatch(job):
        raise ValueError('invalid job id')
    workspace = ROOT / job
    if workspace.is_symlink() or not workspace.is_dir():
        raise ValueError('unknown job')
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


def execute_portable_job(job, mode):
    """Run bounded portable conversion in the isolated worker; opaque job IDs only."""
    if not JOB.fullmatch(job):
        raise ValueError('invalid job id')
    workspace = ROOT / job
    if workspace.is_symlink() or not workspace.is_dir():
        raise ValueError('unknown job')
    reservation = workspace / '.conversion-lock'
    with _ACTIVE_LOCK:
        if job in _ACTIVE_JOBS:
            raise ValueError('job already running')
        _ACTIVE_JOBS.add(job)
    acquired = False
    try:
        reservation.mkdir(mode=0o700)
        acquired = True
        if mode == 'import':
            source = workspace / 'source.pptx'
            destination = workspace / 'portable.json'
            if not source.is_file() or source.is_symlink() or destination.exists():
                raise ValueError('invalid import source')
            result = pptx_to_portable(source, media_dir=workspace / "import-media")
            encoded = json.dumps(result, ensure_ascii=False).encode('utf-8')
            if len(encoded) > 2 * 1024 * 1024:
                raise ValueError('portable definition too large')
            destination.write_bytes(encoded)
            return {'pages': len(result['activities']), 'fidelity': inspect_pptx_fidelity(source)}
        if mode == 'export':
            source = workspace / 'portable.json'
            destination = workspace / 'presentation.pptx'
            if not source.is_file() or source.is_symlink() or destination.exists() or source.stat().st_size > 2 * 1024 * 1024:
                raise ValueError('invalid export source')
            portable_to_pptx(json.loads(source.read_text(encoding='utf-8')), destination, media_dir=workspace / 'export-media')
            if destination.stat().st_size > 50 * 1024 * 1024:
                destination.unlink()
                raise ValueError('export too large')
            return {'bytes': destination.stat().st_size}
        raise ValueError('invalid portable mode')
    finally:
        if acquired:
            reservation.rmdir()
        with _ACTIVE_LOCK:
            _ACTIVE_JOBS.discard(job)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != '/health':
            return self.reply(404, {'error': 'not_found'})
        ready = bool(TOKEN) and ROOT.is_dir()
        return self.reply(200 if ready else 503, {'ready': ready})

    def do_POST(self):
        if self.path not in ('/convert', '/portable-import', '/portable-export'):
            return self.reply(404, {'error': 'not_found'})
        credential = self.headers.get('Authorization', '').removeprefix('Bearer ')
        if not TOKEN or not hmac.compare_digest(credential, TOKEN):
            return self.reply(403, {'error': 'forbidden'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 1 <= size <= 256:
                return self.reply(413 if size > 256 else 400, {'error': 'invalid_request'})
            request = json.loads(self.rfile.read(size))
            if not isinstance(request, dict) or not isinstance(request.get('job'), str):
                return self.reply(400, {'error': 'invalid_request'})
            return self.reply(200, execute_job(request['job']) if self.path == '/convert' else execute_portable_job(request['job'], 'import' if self.path == '/portable-import' else 'export'))
        except (ValueError, OSError, RuntimeError, TimeoutError, json.JSONDecodeError) as exc:
            self.log_error('conversion rejected: %s', type(exc).__name__)
            return self.reply(422, {'error': 'conversion_failed'})

    def reply(self, status, payload):
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


if __name__ == '__main__':
    if len(TOKEN) < 32:
        raise SystemExit('QUORIVIO_WORKER_TOKEN must contain at least 32 characters')
    ROOT.mkdir(parents=True, exist_ok=True)
    ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '8099'))), Handler).serve_forever()
