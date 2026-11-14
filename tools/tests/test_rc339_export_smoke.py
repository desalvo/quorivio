"""Offline RC339 parser and transport-safety regressions (no secrets/network)."""
import importlib.util
import io
import pathlib
import unittest
from zipfile import ZipFile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ci_visual_export_smoke', ROOT / 'ci_visual_export_smoke.py')
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


class ExportSmokeChecks(unittest.TestCase):
    def test_staging_origin_is_https_or_loopback_only(self):
        self.assertEqual(smoke.validated_base('https://staging.example.invalid/'), 'https://staging.example.invalid')
        self.assertEqual(smoke.validated_base('http://127.0.0.1:8080/'), 'http://127.0.0.1:8080')
        for unsafe in ('http://staging.example.invalid', 'https://user:pass@staging.example.invalid',
                       'https://staging.example.invalid/path', 'https://staging.example.invalid/?token=abc',
                       'file:///tmp/something'):
            with self.subTest(unsafe=unsafe), self.assertRaises(smoke.SmokeFailure):
                smoke.validated_base(unsafe)

    def test_pdf_requires_real_signature_and_terminator(self):
        smoke.verify_pdf(b'%PDF-1.7\n%%EOF\n')
        for payload in (b'%PDF-1.7\n', b'<html>not a PDF</html>', b'PK\x03\x04%%EOF'):
            with self.assertRaises(smoke.SmokeFailure):
                smoke.verify_pdf(payload)

    def test_filename_requires_correct_view_and_utf8_attachment(self):
        smoke.check_filename("attachment; filename=\"ascii.pdf\"; filename*=UTF-8''S%C3%A9minaire%20-%20presentatore.pdf", 'presenter', 'pdf')
        for header in ('inline; filename*=UTF-8\'\'x%20-%20presentatore.pdf',
                       "attachment; filename*=UTF-8''x%20-%20partecipante.pdf",
                       "attachment; filename*=UTF-8''..%2Fx%20-%20presentatore.pdf"):
            with self.assertRaises(smoke.SmokeFailure):
                smoke.check_filename(header, 'presenter', 'pdf')

    def test_raster_pptx_has_picture_on_every_slide(self):
        def sample(with_picture=True):
            output = io.BytesIO()
            with ZipFile(output, 'w') as z:
                z.writestr('[Content_Types].xml', '<Types/>')
                z.writestr('ppt/presentation.xml', '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"/>')
                z.writestr('ppt/media/slide.png', b'PNG')
                pic = '<p:pic/>' if with_picture else '<p:sp/>'
                z.writestr('ppt/slides/slide1.xml', f'<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:spTree>{pic}</p:spTree></p:sld>')
            return output.getvalue()
        self.assertEqual(smoke.verify_visual_pptx(sample()), 1)
        with self.assertRaises(smoke.SmokeFailure):
            smoke.verify_visual_pptx(sample(False))
        with self.assertRaises(smoke.SmokeFailure):
            smoke.verify_visual_pptx(b'not a zip')


if __name__ == '__main__':
    unittest.main()
