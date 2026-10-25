"""Release-candidate conversion boundary: adversarial PDF/PPTX, publication, worker.

These tests exercise the actual converter/worker APIs, not merely source strings.
"""
import http.client
import io
import json
import os
import pathlib
import stat
import struct
import sys
import tempfile
import threading
import unittest
import zlib
from http.server import ThreadingHTTPServer
from unittest.mock import patch
from zipfile import ZipFile, ZIP_DEFLATED, ZipInfo

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import import_presentation as converter
import conversion_worker as worker


def png(width=2, height=2):
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    def chunk(name, body):
        return struct.pack('>I', len(body)) + name + body + struct.pack('>I', zlib.crc32(name + body))
    pixels = (b'\x00' + b'\x00\x00\x00' * width) * height if width * height < 200 else b'\x00'
    return converter.PNG_SIGNATURE + chunk(b'IHDR', ihdr) + chunk(b'IDAT', zlib.compress(pixels)) + chunk(b'IEND', b'')


class ConversionBoundary30(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)

    def source(self, name='sample.pdf', payload=b'%PDF-1.7\n%fixture\n'):
        path = self.root / name
        path.write_bytes(payload)
        return path

    def pptx(self, members=None):
        path = self.root / 'sample.pptx'
        with ZipFile(path, 'w', ZIP_DEFLATED) as archive:
            for name, content in (members or {'[Content_Types].xml': b'<Types/>', 'ppt/presentation.xml': b'<p:presentation/>'}).items():
                archive.writestr(name, content)
        return path

    def render_mock(self, pages, generated=None, extra=None):
        """Mock subprocesses while executing actual converter file/manifest publication."""
        generated = generated or {i: png() for i in range(1, pages + 1)}
        def command(args, timeout=90):
            if args[0] == 'pdfinfo':
                return f'Pages: {pages}\n'.encode()
            if args[0] == 'pdftoppm':
                target = pathlib.Path(args[-1])
                for number, content in generated.items():
                    (target.parent / f'page-{number}.png').write_bytes(content)
                for name, content in (extra or {}).items():
                    (target.parent / name).write_bytes(content)
                return b''
            raise AssertionError(args)
        return patch.object(converter, 'run', side_effect=command)

    def test_01_pdf_header_is_required(self):
        with self.assertRaisesRegex(ValueError, 'PDF signature'):
            converter.inspect_source(self.source(payload=b'not pdf at all'))

    def test_02_extension_is_required(self):
        with self.assertRaisesRegex(ValueError, 'Only PDF'):
            converter.inspect_source(self.source('bad.txt'))

    def test_03_source_symlink_is_forbidden(self):
        original = self.source()
        alias = self.root / 'alias.pdf'
        alias.symlink_to(original)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            converter.inspect_source(alias)

    def test_04_source_directory_is_forbidden(self):
        path = self.root / 'folder.pdf'
        path.mkdir()
        with self.assertRaisesRegex(ValueError, 'regular file'):
            converter.inspect_source(path)

    def test_05_zero_length_source_is_forbidden(self):
        with self.assertRaisesRegex(ValueError, 'size'):
            converter.inspect_source(self.source(payload=b''))

    def test_06_oversized_source_is_forbidden(self):
        path = self.source()
        with path.open('r+b') as stream:
            stream.truncate(converter.MAX_BYTES + 1)
        with self.assertRaisesRegex(ValueError, 'size'):
            converter.inspect_source(path)

    def test_07_valid_ooxml_inspection(self):
        self.assertEqual(converter.inspect_source(self.pptx()), '.pptx')

    def test_08_ooxml_traversal_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Unsafe'):
            converter.inspect_source(self.pptx({'[Content_Types].xml': b'a', 'ppt/presentation.xml': b'b', '../bad': b'x'}))

    def test_09_ooxml_external_relationship_rejected(self):
        with self.assertRaisesRegex(ValueError, 'External'):
            converter.inspect_source(self.pptx({'[Content_Types].xml': b'a', 'ppt/presentation.xml': b'b', 'ppt/_rels/presentation.xml.rels': b'<Relationship TargetMode="External"/>'}))

    def test_10_ooxml_macro_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Macro'):
            converter.inspect_source(self.pptx({'[Content_Types].xml': b'a', 'ppt/presentation.xml': b'b', 'ppt/vbaProject.bin': b'evil'}))

    def test_11_ooxml_bomb_rejected(self):
        with self.assertRaisesRegex(ValueError, 'compression ratio'):
            converter.inspect_source(self.pptx({'[Content_Types].xml': b'a', 'ppt/presentation.xml': b'b', 'ppt/bomb.xml': b'Z' * (2 * 1024 * 1024)}))

    def test_12_ooxml_missing_required_part_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Not an OOXML'):
            converter.inspect_source(self.pptx({'[Content_Types].xml': b'a'}))

    def test_13_ooxml_duplicate_part_rejected(self):
        path = self.root / 'dup.pptx'
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore', UserWarning)
            with ZipFile(path, 'w') as archive:
                archive.writestr('[Content_Types].xml', b'a')
                archive.writestr('ppt/presentation.xml', b'b')
                archive.writestr('ppt/presentation.xml', b'c')
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            converter.inspect_source(path)

    def test_14_page_count_zero_rejected(self):
        with patch.object(converter, 'run', return_value=b'Pages: 0\n'):
            with self.assertRaisesRegex(ValueError, 'range'):
                converter._page_count(self.root / 'test.pdf')

    def test_15_page_count_above_limit_rejected(self):
        with patch.object(converter, 'run', return_value=b'Pages: 201\n'):
            with self.assertRaisesRegex(ValueError, 'range'):
                converter._page_count(self.root / 'test.pdf')

    def test_16_ambiguous_page_count_rejected(self):
        with patch.object(converter, 'run', return_value=b'Pages: 1\nPages: 2\n'):
            with self.assertRaisesRegex(ValueError, 'ambiguous'):
                converter._page_count(self.root / 'test.pdf')

    def test_17_converter_timeout_is_safe(self):
        import subprocess
        with patch.object(converter.subprocess, 'run', side_effect=subprocess.TimeoutExpired(['pdfinfo'], 20)):
            with self.assertRaisesRegex(RuntimeError, 'timed out'):
                converter.run(['pdfinfo', 'x'])

    def test_18_converter_error_does_not_leak_stderr(self):
        import subprocess
        completed = subprocess.CompletedProcess(['pdfinfo'], 1, b'', b'/private/secret')
        with patch.object(converter.subprocess, 'run', return_value=completed):
            with self.assertRaisesRegex(RuntimeError, 'subprocess failed') as captured:
                converter.run(['pdfinfo', 'x'])
        self.assertNotIn('secret', str(captured.exception))

    def test_19_output_symlink_rejected(self):
        target = self.root / 'target'
        target.mkdir()
        output = self.root / 'pages'
        output.symlink_to(target, target_is_directory=True)
        with self.assertRaises(FileExistsError):
            converter._safe_destination(output)

    def test_20_symlink_parent_rejected(self):
        actual = self.root / 'actual'
        actual.mkdir()
        link = self.root / 'link'
        link.symlink_to(actual, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Symlinked'):
            converter._safe_destination(link / 'pages')

    def test_21_png_signature_rejected(self):
        image = self.root / 'fake.png'
        image.write_bytes(b'X' * 64)
        with self.assertRaisesRegex(ValueError, 'PNG header'):
            converter._verify_png(image)

    def test_22_png_crc_rejected(self):
        image = self.root / 'badcrc.png'
        raw = bytearray(png())
        raw[29] ^= 0xFF
        image.write_bytes(raw)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            converter._verify_png(image)

    def test_23_png_dimensions_rejected(self):
        image = self.root / 'wide.png'
        image.write_bytes(png(9000, 2))
        with self.assertRaisesRegex(ValueError, 'dimensions'):
            converter._verify_png(image)

    def test_24_png_pixel_area_rejected(self):
        image = self.root / 'huge.png'
        image.write_bytes(png(8192, 8192))
        with self.assertRaisesRegex(ValueError, 'dimensions'):
            converter._verify_png(image)

    def test_25_png_symlink_rejected(self):
        image = self.root / 'safe.png'
        image.write_bytes(png())
        alias = self.root / 'alias.png'
        alias.symlink_to(image)
        with self.assertRaisesRegex(ValueError, 'PNG'):
            converter._verify_png(alias)

    def test_26_out_of_order_render_is_sorted_numerically(self):
        source = self.source()
        with self.render_mock(12):
            manifest = converter.convert(source, self.root / 'rendered')
        self.assertEqual(manifest['page_count'], 12)
        self.assertEqual(manifest['pages'][9]['image'], 'page-0010.png')
        self.assertEqual(manifest['pages'][11]['position'], 12)
        self.assertEqual(sorted(p.name for p in (self.root / 'rendered').glob('*.png'))[0], 'page-0001.png')

    def test_27_render_extra_file_rejected_without_publication(self):
        source = self.source()
        with self.render_mock(1, extra={'bad.txt': b'x'}):
            with self.assertRaisesRegex(RuntimeError, 'Unexpected render'):
                converter.convert(source, self.root / 'rendered')
        self.assertFalse((self.root / 'rendered').exists())

    def test_28_render_missing_page_rejected_without_publication(self):
        source = self.source()
        with self.render_mock(2, generated={1: png()}):
            with self.assertRaisesRegex(RuntimeError, 'number of rendered'):
                converter.convert(source, self.root / 'rendered')
        self.assertFalse((self.root / 'rendered').exists())

    def test_29_render_oversized_page_rejected(self):
        source = self.source()
        with patch.object(converter, 'MAX_PAGE_BYTES', 40), self.render_mock(1):
            with self.assertRaisesRegex(ValueError, 'oversized'):
                converter.convert(source, self.root / 'rendered')
        self.assertFalse((self.root / 'rendered').exists())

    def test_30_render_total_quota_rejected(self):
        source = self.source()
        with patch.object(converter, 'MAX_RENDER_BYTES', 100), self.render_mock(2):
            with self.assertRaisesRegex(ValueError, 'storage limit'):
                converter.convert(source, self.root / 'rendered')
        self.assertFalse((self.root / 'rendered').exists())

    def test_31_source_mutation_during_render_rejected(self):
        source = self.source()
        def command(args, timeout=90):
            if args[0] == 'pdfinfo':
                return b'Pages: 1\n'
            if args[0] == 'pdftoppm':
                source.write_bytes(b'%PDF-1.7\n%changed\n')
                pathlib.Path(args[-1] + '-1.png').write_bytes(png())
                return b''
            raise AssertionError(args)
        with patch.object(converter, 'run', side_effect=command):
            with self.assertRaisesRegex(ValueError, 'changed'):
                converter.convert(source, self.root / 'rendered')
        self.assertFalse((self.root / 'rendered').exists())

    def test_32_manifest_and_files_private_and_consistent(self):
        source = self.source()
        with self.render_mock(1):
            manifest = converter.convert(source, self.root / 'rendered')
        destination = self.root / 'rendered'
        actual = json.loads((destination / 'manifest.json').read_text())
        self.assertEqual(manifest, actual)
        self.assertEqual(actual['source_sha256'], converter._sha256_file(source))
        self.assertEqual(stat.S_IMODE((destination / 'page-0001.png').stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE((destination / 'manifest.json').stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o700)

    def test_33_existing_output_never_overwritten(self):
        source = self.source()
        output = self.root / 'rendered'
        output.mkdir()
        (output / 'keep.txt').write_text('important')
        with self.assertRaises(FileExistsError):
            converter.convert(source, output)
        self.assertEqual((output / 'keep.txt').read_text(), 'important')

    def test_34_real_pdf_twelve_pages_and_manifest_hashes(self):
        from reportlab.pdfgen.canvas import Canvas
        import hashlib
        source = self.root / 'twelve.pdf'
        canvas = Canvas(str(source))
        for index in range(12):
            canvas.drawString(100, 600, f'Quorivio page {index + 1}')
            canvas.showPage()
        canvas.save()
        result = converter.convert(source, self.root / 'rendered')
        self.assertEqual(result['page_count'], 12)
        self.assertEqual(result['pages'][9]['image'], 'page-0010.png')
        for page in result['pages']:
            data = (self.root / 'rendered' / page['image']).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), page['sha256'])
            self.assertEqual(len(data), page['bytes'])

    def test_35_real_pptx_flattening_when_libreoffice_available(self):
        import shutil
        self.assertIsNotNone(shutil.which('libreoffice'), 'LibreOffice is mandatory for real PPTX acceptance')
        from pptx import Presentation
        from pptx.util import Inches
        source = self.root / 'deck.pptx'
        deck = Presentation()
        slide = deck.slides.add_slide(deck.slide_layouts[6])
        slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1)).text = 'Quorivio conversion'
        deck.save(source)
        result = converter.convert(source, self.root / 'rendered')
        self.assertEqual(result['page_count'], 1)
        self.assertEqual(result['source_type'], 'pptx')
        self.assertTrue((self.root / 'rendered' / 'page-0001.png').is_file())


class WorkerAtomic30(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = pathlib.Path(self.temp.name)
        self.root_patch = patch.object(worker, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.job = 'a' * 32
        self.workspace = self.root / self.job
        self.workspace.mkdir()

    def test_34_symlinked_workspace_rejected(self):
        self.workspace.rmdir()
        self.workspace.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'unknown job'):
            worker.execute_portable_job(self.job, 'import')

    def test_35_symlinked_root_rejected(self):
        alias = self.root.parent / ('quorivio-root-' + self.job)
        alias.symlink_to(self.root, target_is_directory=True)
        self.addCleanup(alias.unlink)
        with patch.object(worker, 'ROOT', alias):
            with self.assertRaisesRegex(ValueError, 'unsafe'):
                worker.execute_job(self.job)

    def test_36_portable_import_existing_output_rejected(self):
        (self.workspace / 'source.pptx').write_bytes(b'PK fake')
        (self.workspace / 'portable.json').write_bytes(b'keep')
        with self.assertRaisesRegex(ValueError, 'existing output'):
            worker.execute_portable_job(self.job, 'import')
        self.assertEqual((self.workspace / 'portable.json').read_bytes(), b'keep')

    def test_37_portable_import_media_symlink_rejected(self):
        (self.workspace / 'source.pptx').write_bytes(b'PK fake')
        (self.workspace / 'import-media').symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'existing output'):
            worker.execute_portable_job(self.job, 'import')

    def test_38_import_failure_removes_media_and_temp(self):
        (self.workspace / 'source.pptx').write_bytes(b'PK fake')
        def bad_import(source, media_dir):
            (media_dir / 'asset').write_bytes(b'private')
            raise RuntimeError('injected failure')
        with patch.object(worker, 'pptx_to_portable', side_effect=bad_import):
            with self.assertRaisesRegex(RuntimeError, 'injected failure'):
                worker.execute_portable_job(self.job, 'import')
        self.assertFalse((self.workspace / 'import-media').exists())
        self.assertFalse((self.workspace / 'portable.json').exists())
        self.assertEqual(list(self.workspace.glob('.import-media-*')), [])
        self.assertFalse((self.workspace / '.conversion-lock').exists())

    def test_39_import_oversize_json_rejected_atomically(self):
        (self.workspace / 'source.pptx').write_bytes(b'PK fake')
        with patch.object(worker, 'pptx_to_portable', return_value={'activities': [{'x': 'x' * (3 * 1024 * 1024)}]}):
            with self.assertRaisesRegex(ValueError, 'too large'):
                worker.execute_portable_job(self.job, 'import')
        self.assertFalse((self.workspace / 'portable.json').exists())
        self.assertFalse((self.workspace / 'import-media').exists())

    def test_40_import_fidelity_failure_rejects_publication(self):
        (self.workspace / 'source.pptx').write_bytes(b'PK fake')
        with patch.object(worker, 'pptx_to_portable', return_value={'activities': []}), patch.object(worker, 'inspect_pptx_fidelity', side_effect=RuntimeError('fidelity failure')):
            with self.assertRaisesRegex(RuntimeError, 'fidelity failure'):
                worker.execute_portable_job(self.job, 'import')
        self.assertFalse((self.workspace / 'portable.json').exists())
        self.assertFalse((self.workspace / 'import-media').exists())

    def test_41_import_json_is_private(self):
        (self.workspace / 'source.pptx').write_bytes(b'PK fake')
        with patch.object(worker, 'pptx_to_portable', return_value={'activities': []}), patch.object(worker, 'inspect_pptx_fidelity', return_value={}):
            self.assertEqual(worker.execute_portable_job(self.job, 'import')['pages'], 0)
        self.assertEqual(stat.S_IMODE((self.workspace / 'portable.json').stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE((self.workspace / 'import-media').stat().st_mode), 0o700)

    def test_41b_import_publish_failure_cleans_published_media(self):
        (self.workspace / 'source.pptx').write_bytes(b'PK fake')
        def imported(source, media_dir):
            (media_dir / 'asset').write_bytes(b'private')
            return {'activities': []}
        with (patch.object(worker, 'pptx_to_portable', side_effect=imported),
              patch.object(worker, 'inspect_pptx_fidelity', return_value={}),
              patch.object(worker, '_publish_file_exclusive', side_effect=FileExistsError('raced'))):
            with self.assertRaisesRegex(FileExistsError, 'raced'):
                worker.execute_portable_job(self.job, 'import')
        self.assertFalse((self.workspace / 'import-media').exists())
        self.assertFalse((self.workspace / 'portable.json').exists())
        self.assertEqual(list(self.workspace.glob('.portable-*')), [])

    def test_42_export_existing_output_rejected(self):
        (self.workspace / 'portable.json').write_text('{}')
        (self.workspace / 'presentation.pptx').write_bytes(b'keep')
        with self.assertRaisesRegex(ValueError, 'existing output'):
            worker.execute_portable_job(self.job, 'export')
        self.assertEqual((self.workspace / 'presentation.pptx').read_bytes(), b'keep')

    def test_43_export_symlinked_media_rejected(self):
        (self.workspace / 'portable.json').write_text('{}')
        (self.workspace / 'export-media').symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'invalid export'):
            worker.execute_portable_job(self.job, 'export')

    def test_44_export_duplicate_json_key_rejected(self):
        (self.workspace / 'portable.json').write_text('{"a":1,"a":2}')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            worker.execute_portable_job(self.job, 'export')
        self.assertFalse((self.workspace / 'presentation.pptx').exists())

    def test_45_export_nonfinite_json_rejected(self):
        (self.workspace / 'portable.json').write_text('{"a":NaN}')
        with self.assertRaisesRegex(ValueError, 'non-finite'):
            worker.execute_portable_job(self.job, 'export')
        self.assertFalse((self.workspace / 'presentation.pptx').exists())

    def test_46_export_failure_removes_partial_file(self):
        (self.workspace / 'portable.json').write_text('{}')
        def bad_export(data, destination, media_dir):
            destination.write_bytes(b'partial')
            raise RuntimeError('injected export failure')
        with patch.object(worker, 'portable_to_pptx', side_effect=bad_export):
            with self.assertRaisesRegex(RuntimeError, 'injected export failure'):
                worker.execute_portable_job(self.job, 'export')
        self.assertFalse((self.workspace / 'presentation.pptx').exists())
        self.assertEqual(list(self.workspace.glob('.presentation-*')), [])
        self.assertFalse((self.workspace / '.conversion-lock').exists())

    def test_47_export_oversize_rejected_and_removed(self):
        (self.workspace / 'portable.json').write_text('{}')
        def oversized(data, destination, media_dir):
            with destination.open('wb') as stream:
                stream.truncate(50 * 1024 * 1024 + 1)
        with patch.object(worker, 'portable_to_pptx', side_effect=oversized):
            with self.assertRaisesRegex(ValueError, 'too large'):
                worker.execute_portable_job(self.job, 'export')
        self.assertFalse((self.workspace / 'presentation.pptx').exists())

    def test_48_export_private_atomic_file(self):
        (self.workspace / 'portable.json').write_text('{}')
        def export(data, destination, media_dir):
            self.assertFalse((self.workspace / 'presentation.pptx').exists())
            destination.write_bytes(b'PK presentation')
        with patch.object(worker, 'portable_to_pptx', side_effect=export):
            result = worker.execute_portable_job(self.job, 'export')
        self.assertEqual(result['bytes'], len(b'PK presentation'))
        self.assertEqual(stat.S_IMODE((self.workspace / 'presentation.pptx').stat().st_mode), 0o600)
        self.assertEqual(list(self.workspace.glob('.presentation-*')), [])

    def test_49_worker_rejects_invalid_mode(self):
        with self.assertRaisesRegex(ValueError, 'invalid portable mode'):
            worker.execute_portable_job(self.job, 'unknown')
        self.assertFalse((self.workspace / '.conversion-lock').exists())

    def test_50_worker_rejects_simultaneous_job(self):
        (self.workspace / 'portable.json').write_text('{}')
        def overlap(data, destination, media_dir):
            with self.assertRaisesRegex(ValueError, 'job already running'):
                worker.execute_portable_job(self.job, 'export')
            destination.write_bytes(b'PK presentation')
        with patch.object(worker, 'portable_to_pptx', side_effect=overlap):
            worker.execute_portable_job(self.job, 'export')
        self.assertFalse((self.workspace / '.conversion-lock').exists())


class WorkerHttpBoundary30(unittest.TestCase):
    def setUp(self):
        self.token = 'private-token-with-more-than-32-characters'
        self.token_patch = patch.object(worker, 'TOKEN', self.token)
        self.token_patch.start()
        self.addCleanup(self.token_patch.stop)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), worker.Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self._close)

    def _close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def post(self, data, content_type='application/json'):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=3)
        conn.request('POST', '/convert', data, {'Authorization': 'Bearer ' + self.token, 'Content-Type': content_type})
        reply = conn.getresponse()
        result = (reply.status, dict(reply.getheaders()), json.loads(reply.read()))
        conn.close()
        return result

    def test_51_reject_extra_job_field(self):
        self.assertEqual(self.post(b'{"job":"abc","extra":true}')[0], 400)

    def test_52_reject_duplicate_job_field(self):
        self.assertEqual(self.post(b'{"job":"abc","job":"def"}')[0], 422)

    def test_53_reject_non_json_media_type(self):
        self.assertEqual(self.post(b'{"job":"abc"}', 'text/plain')[0], 415)

    def test_54_reject_nan_body(self):
        self.assertEqual(self.post(b'{"job":NaN}')[0], 422)

    def test_55_response_is_private_and_nosniff(self):
        status, headers, body = self.post(b'{"job":"bad"}')
        self.assertEqual(status, 422)
        self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertEqual(headers['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(body, {'error': 'conversion_failed'})


if __name__ == '__main__':
    unittest.main()
