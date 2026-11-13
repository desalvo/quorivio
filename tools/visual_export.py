"""Capture the actual React presentation as 16:9 PNG slides, then package as PPTX.

This deliberately produces image-backed *visual* exports: the existing editable
OOXML exporter cannot reproduce the real browser's fonts, widget layout, results,
SVG and backgrounds. No external URL is read by Chromium and no user session
cookie/credential is sent to the converter. Only a per-job secret grants the
private capture page access to the owner's sanitized definition.
"""
from __future__ import annotations
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from urllib.parse import urlparse

from pptx import Presentation
from pptx.util import Inches
import qrcode

VIEWERS = frozenset(('presenter', 'participant'))
JOB_RE = re.compile(r'[0-9a-f]{32}\Z')
ASSET_RE = re.compile(r'[0-9a-fA-F-]{36}\Z')
MAX_EXPORT_SIZE = 50 * 1024 * 1024


def presenter_steps(definition):
    """Match the React rehearsal: each presenter step may map another audience page."""
    activities = definition.get('activities')
    if not isinstance(activities, list) or not 1 <= len(activities) <= 200:
        raise ValueError('Invalid presentation page count')
    visible = [a for a in activities if isinstance(a, dict) and (a.get('page_design') or {}).get('presenterHidden') is not True]
    if not visible:
        raise ValueError('No visible presenter pages')
    ids = {a.get('portable_id') for a in activities}
    if len(ids) != len(activities) or None in ids:
        raise ValueError('Missing or duplicate page IDs')
    for item in visible:
        audience = (item.get('page_design') or {}).get('audiencePageId')
        if audience and audience not in ids:
            raise ValueError('Missing mapped participant page')
    return visible


def _safe_capture_url(url):
    if not isinstance(url, str) or len(url) > 180:
        raise ValueError('Capture origin not configured')
    parsed = urlparse(url)
    if parsed.scheme != 'http' or not parsed.hostname or not parsed.port or parsed.username or parsed.password or parsed.path not in ('', '/') or parsed.query or parsed.fragment:
        raise ValueError('Capture origin must be an internal HTTP host:port')
    if not re.fullmatch(r'[A-Za-z0-9.-]+', parsed.hostname):
        raise ValueError('Invalid capture origin hostname')
    return f'{parsed.scheme}://{parsed.netloc}'


def _image_response(route, asset_path: Path):
    if asset_path.is_symlink() or not asset_path.is_file() or asset_path.stat().st_size > 10 * 1024 * 1024:
        route.abort();return
    data = asset_path.read_bytes()
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        content_type = 'image/png'
    elif data.startswith(b'\xff\xd8\xff'):
        content_type = 'image/jpeg'
    elif data.startswith((b'GIF87a', b'GIF89a')):
        content_type = 'image/gif'
    elif data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        content_type = 'image/webp'
    elif data.startswith(b'%PDF-'):
        content_type = 'application/pdf'
    elif data[:4] == b'\x1aE\xdf\xa3':
        content_type = 'video/webm'
    elif data[4:8] == b'ftyp':
        content_type = 'video/mp4'
    else:
        route.abort();return
    route.fulfill(status=200, body=data, headers={'Content-Type': content_type, 'Cache-Control': 'no-store'})


def _qr_png(target):
    if not isinstance(target, str) or not target.startswith(('https://', 'http://')) or len(target) > 2048:
        return None
    stream = io.BytesIO()
    image = qrcode.make(target, box_size=6, border=2)
    image.save(stream, format='PNG')
    return stream.getvalue()


def render_deck(workspace: Path, *, view: str, origin: str):
    if view not in VIEWERS:
        raise ValueError('Unsupported export viewer')
    if not JOB_RE.fullmatch(workspace.name):
        raise ValueError('Invalid export job')
    origin = _safe_capture_url(origin)
    token_path = workspace / 'capture-token'
    portable_path = workspace / 'portable.json'
    if token_path.is_symlink() or portable_path.is_symlink():
        raise ValueError('Unsafe export job')
    token = token_path.read_text(encoding='ascii')
    if not re.fullmatch(r'[0-9a-f]{64}', token):
        raise ValueError('Invalid export capability')
    definition = json.loads(portable_path.read_text(encoding='utf-8'))
    if definition.get('format') != 'quorivio-session' or definition.get('version') != 1:
        raise ValueError('Invalid portable definition')
    steps = presenter_steps(definition)
    session_id = definition.get('capture_session_id')
    if not isinstance(session_id, str) or not ASSET_RE.fullmatch(session_id):
        raise ValueError('Invalid export session ID')
    png_qr = _qr_png((definition.get('session') or {}).get('participant_join_url'))
    media_base = workspace / 'export-media'
    captures = workspace / 'visual-pages'
    captures.mkdir(mode=0o700)

    # A dependency is intentionally imported only for visual export, not for
    # legacy OOXML import/export. No local or remote secrets are passed to JS.
    from playwright.sync_api import sync_playwright
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            executable_path=os.environ.get('QUORIVIO_CAPTURE_BROWSER', '/usr/bin/chromium'),
            headless=True, args=['--disable-dev-shm-usage', '--disable-extensions', '--no-first-run'])
        try:
            context = browser.new_context(viewport={'width': 1280, 'height': 720},
                device_scale_factor=1, reduced_motion='reduce', java_script_enabled=True)
            def route_request(route):
                request = route.request
                parsed = urlparse(request.url)
                # No network outside the internal application origin: a slide
                # with an external URL must never cause a privileged SSRF.
                if f'{parsed.scheme}://{parsed.netloc}' != origin:
                    route.abort();return
                route_path = parsed.path
                if route_path == f'/api/export-render/{workspace.name}':
                    headers = dict(request.headers)
                    headers['x-quorivio-capture-token'] = token
                    route.continue_(headers=headers)
                    return
                if route_path == f'/api/export-render/{workspace.name}/qr.png' and png_qr:
                    route.fulfill(status=200, body=png_qr, headers={'Content-Type':'image/png', 'Cache-Control':'no-store'})
                    return
                profile_prefix = f'/api/export-render/{workspace.name}/profile/'
                if route_path.startswith(profile_prefix):
                    image_id = route_path[len(profile_prefix):]
                    if not ASSET_RE.fullmatch(image_id):
                        route.abort();return
                    _image_response(route,media_base / ('profile-'+image_id))
                    return
                asset_prefix = f'/api/sessions/{session_id}/assets/'
                if route_path.startswith(asset_prefix):
                    asset_id = route_path[len(asset_prefix):]
                    if not ASSET_RE.fullmatch(asset_id):
                        route.abort();return
                    _image_response(route, media_base / asset_id)
                    return
                # Never proxy authenticated/private API endpoints other than
                # the one-time capture definition, and never open public links.
                if route_path.startswith('/api/'):
                    route.abort();return
                route.continue_()
            context.route('**/*', route_request)
            page = context.new_page()
            page.goto(f'{origin}/export-render/{workspace.name}?view={view}',
                      wait_until='domcontentloaded',timeout=45000)
            page.wait_for_selector('#quorivio-export-slide[data-export-page="0"]', timeout=45000)
            images = []
            for i in range(len(steps)):
                if i:
                    page.evaluate('(index) => window.__quorivioExportSetPage(index)', i)
                    page.wait_for_selector(f'#quorivio-export-slide[data-export-page="{i}"]', timeout=20000)
                page.evaluate('() => document.fonts.ready')
                page.wait_for_function("""() => [...document.querySelectorAll('#quorivio-export-slide img')].every(img => !img.getAttribute('src') || (img.complete && img.naturalWidth > 0))""", timeout=20000)
                target = captures / f'page-{i+1:04d}.png'
                page.locator('#quorivio-export-slide').screenshot(path=str(target), animations='disabled', timeout=30000)
                images.append(target)
                if sum(p.stat().st_size for p in images) > MAX_EXPORT_SIZE:
                    raise ValueError('Captured presentation exceeds size limit')
            context.close()
        finally:
            browser.close()
    return images


def image_deck_to_pptx(image_files, destination):
    """One PNG/slide fills the entire canvas; no secondary OOXML reconstruction."""
    image_files = list(image_files)
    if not 1 <= len(image_files) <= 200:
        raise ValueError('Invalid visual deck length')
    pptx = Presentation()
    pptx.slide_width = Inches(13.333333)
    pptx.slide_height = Inches(7.5)
    for png in image_files:
        if not png.is_file() or png.is_symlink() or png.stat().st_size > MAX_EXPORT_SIZE:
            raise ValueError('Missing visual slide')
        slide = pptx.slides.add_slide(pptx.slide_layouts[6])
        slide.shapes.add_picture(str(png), 0, 0, pptx.slide_width, pptx.slide_height)
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError('Visual export destination exists')
    with tempfile.NamedTemporaryFile(dir=destination.parent,prefix='.visual-deck-',delete=False) as tmp:
        staged = Path(tmp.name)
    try:
        pptx.save(str(staged))
        if not 8 <= staged.stat().st_size <= MAX_EXPORT_SIZE:
            raise ValueError('Visual export exceeds size limit')
        os.link(staged,destination,follow_symlinks=False)
        destination.chmod(0o600)
    finally:
        staged.unlink(missing_ok=True)


def render_visual_export(workspace,mode):
    if mode not in ('visual-export','visual-export-pdf'):
        raise ValueError('Unknown visual export mode')
    viewer_path=workspace/'export-view'
    if viewer_path.is_symlink():
        raise ValueError('Invalid export mode file')
    view=viewer_path.read_text(encoding='ascii')
    pages=render_deck(workspace,view=view,origin=os.environ.get('QUORIVIO_CAPTURE_BASE_URL',''))
    pptx=workspace/'presentation.pptx'
    image_deck_to_pptx(pages,pptx)
    if mode=='visual-export-pdf':
        profile=workspace/'.lo-visual-export-profile'
        result=subprocess.run(['libreoffice','-env:UserInstallation=file://'+str(profile),
            '--headless','--convert-to','pdf:impress_pdf_Export',
            '--outdir',str(workspace),str(pptx)],stdin=subprocess.DEVNULL,
            capture_output=True,timeout=120,check=False)
        output=workspace/'presentation.pdf'
        if result.returncode or output.is_symlink() or not output.is_file() or not 8 <= output.stat().st_size <= MAX_EXPORT_SIZE or output.open('rb').read(5)!=b'%PDF-':
            raise ValueError('Invalid visual PDF')
        output.chmod(0o600)
    return {'pages': len(pages), 'bytes':(workspace/('presentation.pdf' if mode=='visual-export-pdf' else 'presentation.pptx')).stat().st_size}
