#!/usr/bin/env python3
"""Offline, bounded PDF/PPTX -> slide PNG converter; publish only complete page sets.

No database mutations, network downloads, or user-controlled subprocess flags.
The API independently checks the manifest, hashes, and source identity.
"""
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import stat
import struct
import subprocess
import tempfile
import zlib

try:
    from pptx_portable import validate_pptx_archive
except ModuleNotFoundError:
    from tools.pptx_portable import validate_pptx_archive

MAX_BYTES = 100 * 1024 * 1024
MAX_PAGES = 200
MAX_PAGE_BYTES = 24 * 1024 * 1024
MAX_RENDER_BYTES = 256 * 1024 * 1024
MAX_RENDER_DIMENSION = 8192
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'


def _regular_private_source(path):
    if path.is_symlink() or not path.is_file():
        raise ValueError('Source must be a regular file, not a symlink')
    mode = path.stat().st_mode
    if not stat.S_ISREG(mode):
        raise ValueError('Source must be a regular file')
    size = path.stat().st_size
    if not 8 <= size <= MAX_BYTES:
        raise ValueError('Invalid source file size')


def _sha256_file(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_source(source):
    path = pathlib.Path(source)
    _regular_private_source(path)
    ext = path.suffix.lower()
    if ext not in ('.pdf', '.pptx'):
        raise ValueError('Only PDF and PPTX are supported')
    with path.open('rb') as stream:
        signature = stream.read(8)
    if ext == '.pdf':
        if not signature.startswith(b'%PDF-'):
            raise ValueError('Invalid PDF signature')
    else:
        # One consistent native OOXML policy for flattened and editable imports:
        # quotas, duplicate members, traversal, symlinks, macros, external rels.
        validate_pptx_archive(path)
    return ext


def run(args, timeout=90):
    try:
        process = subprocess.run(args, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('Conversion subprocess timed out') from exc
    if process.returncode:
        # Do not reflect arbitrary untrusted document names or converter diagnostics.
        raise RuntimeError('Conversion subprocess failed')
    return process.stdout


def _page_count(pdf):
    try:
        info = run(['pdfinfo', str(pdf)], timeout=20).decode('utf-8', errors='replace')
    except UnicodeError as exc:
        raise ValueError('Invalid PDF metadata') from exc
    matches = re.findall(r'^Pages:\s*(\d+)\s*$', info, flags=re.MULTILINE)
    if len(matches) != 1:
        raise ValueError('Page count unavailable or ambiguous')
    # Poppler reports active content and encryption in normal pdfinfo output.
    # The converter is deliberately a static slide renderer, not a PDF viewer.
    if re.search(r'^Encrypted:\s*yes\b', info, re.I | re.M):
        raise ValueError('Encrypted PDF cannot be imported')
    if re.search(r'^JavaScript:\s*yes\b', info, re.I | re.M):
        raise ValueError('Active PDF JavaScript is not supported')
    pages = int(matches[0])
    if not 1 <= pages <= MAX_PAGES:
        raise ValueError('Page count out of supported range')
    return pages


def _verify_png(path):
    size = path.stat().st_size
    if not 33 <= size <= MAX_PAGE_BYTES or path.is_symlink() or not path.is_file():
        raise ValueError('Invalid or oversized rendered PNG')
    with path.open('rb') as stream:
        header = stream.read(33)
    if not header.startswith(PNG_SIGNATURE) or header[12:16] != b'IHDR' or header[8:12] != b'\x00\x00\x00\x0d':
        raise ValueError('Invalid rendered PNG header')
    width, height = struct.unpack('>II', header[16:24])
    if not (0 < width <= MAX_RENDER_DIMENSION and 0 < height <= MAX_RENDER_DIMENSION and
            width * height <= 16 * 1024 * 1024):
        raise ValueError('Rendered PNG dimensions exceed limits')
    if zlib.crc32(header[12:29]) & 0xffffffff != struct.unpack('>I', header[29:33])[0]:
        raise ValueError('Invalid rendered PNG IHDR checksum')
    if (header[24] not in (1, 2, 4, 8, 16) or header[25] not in (0, 2, 3, 4, 6) or
            header[26] != 0 or header[27] != 0 or header[28] not in (0, 1)):
        raise ValueError('Unsupported rendered PNG format')
    # Check every PNG chunk, including CRC and IEND termination. Pillow may
    # decode pixels successfully even if an untrusted ancillary chunk is corrupt
    # or if bytes have been appended after the final image chunk.
    data = path.read_bytes()
    offset = len(PNG_SIGNATURE)
    chunk_index = 0
    idat_seen = False
    idat_finished = False
    iend_seen = False
    while offset < len(data):
        if len(data) - offset < 12:
            raise ValueError('Truncated rendered PNG chunk')
        length = struct.unpack_from('>I', data, offset)[0]
        end = offset + 12 + length
        if length > MAX_PAGE_BYTES or end > len(data):
            raise ValueError('Truncated or oversized rendered PNG chunk')
        kind = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + length]
        expected = struct.unpack_from('>I', data, offset + 8 + length)[0]
        if zlib.crc32(kind + body) & 0xffffffff != expected:
            raise ValueError('Invalid rendered PNG chunk checksum')
        if not all((65 <= char <= 90 or 97 <= char <= 122) for char in kind):
            raise ValueError('Invalid rendered PNG chunk type')
        if chunk_index == 0 and (kind != b'IHDR' or length != 13):
            raise ValueError('Rendered PNG missing IHDR')
        if chunk_index and kind == b'IHDR':
            raise ValueError('Duplicate rendered PNG IHDR')
        if kind == b'IDAT':
            if idat_finished:
                raise ValueError('Noncontiguous rendered PNG image data')
            idat_seen = True
        elif idat_seen:
            idat_finished = True
        if kind == b'IEND':
            if length or not idat_seen or end != len(data):
                raise ValueError('Invalid rendered PNG terminator')
            iend_seen = True
        elif kind[0] & 32 == 0 and kind not in (b'IHDR', b'PLTE', b'IDAT'):
            raise ValueError('Unsupported rendered PNG critical chunk')
        chunk_index += 1
        offset = end
        if iend_seen:
            break
    if not iend_seen:
        raise ValueError('Rendered PNG missing terminator')

    # Header-only checks accept forged IDAT/IEND streams. Decode the full
    # untrusted raster before any page becomes visible to the API.
    try:
        from PIL import Image, UnidentifiedImageError
        with Image.open(path) as picture:
            if picture.format != 'PNG' or picture.size != (width, height):
                raise ValueError('Rendered PNG format mismatch')
            picture.verify()
        with Image.open(path) as picture:
            picture.load()
            if picture.size != (width, height):
                raise ValueError('Rendered PNG dimensions changed')
    except (OSError, SyntaxError, UnidentifiedImageError, Image.DecompressionBombError) as exc:
        raise ValueError('Rendered PNG failed full decoding') from exc
    return size


def _safe_destination(output):
    if output.exists() or output.is_symlink():
        raise FileExistsError('Output directory already exists')
    # The worker supplies a private job workspace. Refuse symlink ancestors,
    # including a symlink that could be introduced in an output parent.
    for parent in (output.parent, *output.parents):
        if parent.is_symlink():
            raise ValueError('Symlinked output parent is forbidden')
    output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)


def convert(source, dest):
    ext = inspect_source(source)
    source = pathlib.Path(source)
    source_hash = _sha256_file(source)
    output = pathlib.Path(dest)
    _safe_destination(output)
    with tempfile.TemporaryDirectory(prefix='quorivio-import-') as scratch:
        tmp = pathlib.Path(scratch)
        pdf = source
        if ext == '.pptx':
            if not shutil.which('libreoffice'):
                raise RuntimeError('LibreOffice required for PPTX import')
            profile = (tmp / 'lo-profile').as_uri()
            run(['libreoffice', '-env:UserInstallation=' + profile, '--headless',
                 '--convert-to', 'pdf', '--outdir', str(tmp), str(source.resolve())], 120)
            pdf = tmp / (source.stem + '.pdf')
            if not pdf.is_file() or pdf.is_symlink():
                raise RuntimeError('PPTX conversion produced no PDF')
        if not shutil.which('pdfinfo') or not shutil.which('pdftoppm'):
            raise RuntimeError('Poppler pdfinfo and pdftoppm required')
        pages = _page_count(pdf)
        images = tmp / 'pages'
        images.mkdir(mode=0o700)
        run(['pdftoppm', '-f', '1', '-l', str(pages), '-scale-to', '1600',
             '-png', '-r', '96', str(pdf), str(images / 'page')], 180)
        rendered = list(images.iterdir())
        # Poppler may pad the numeric suffix depending on page count; do not
        # accidentally sort page-10 before page-2 or accept stray output files.
        by_number = {}
        for image in rendered:
            match = re.fullmatch(r'page-(\d+)\.png', image.name)
            if not match:
                raise RuntimeError('Unexpected render output file')
            number = int(match.group(1))
            if number in by_number or number < 1 or number > pages:
                raise RuntimeError('Duplicate or out-of-range rendered page')
            by_number[number] = image
        if len(by_number) != pages:
            raise RuntimeError('Unexpected number of rendered pages')
        manifest = {'format': 'quorivio-presentation-pages', 'version': 1,
                    'source_type': ext[1:], 'source_sha256': source_hash,
                    'page_count': pages, 'pages': [],
                    'notes': 'Flattened slide images; animations and embedded video are not preserved.'}
        total = 0
        for index in range(1, pages + 1):
            image = by_number[index]
            size = _verify_png(image)
            total += size
            if total > MAX_RENDER_BYTES:
                raise ValueError('Rendered pages exceed total storage limit')
            name = f'page-{index:04d}.png'
            target = images / name
            if image != target:
                image.rename(target)
            target.chmod(0o600)
            manifest['pages'].append({'position': index, 'image': name,
                                      'sha256': _sha256_file(target), 'bytes': size})
        # Catch input modification during long-running external conversion.
        if _sha256_file(source) != source_hash or not source.is_file() or source.is_symlink():
            raise ValueError('Source changed during conversion')
        (images/'manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        (images / 'manifest.json').chmod(0o600)
        # Never expose a partially rendered presentation to the API reader.
        images.rename(output)
        return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert PDF/PPTX into Quorivio slide images (offline staging)')
    parser.add_argument('source')
    parser.add_argument('output_dir')
    args = parser.parse_args()
    print(json.dumps(convert(args.source, args.output_dir), indent=2))
