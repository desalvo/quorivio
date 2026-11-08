"""RC264: early CI must work without Pillow while production fails closed."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class EarlyCI(unittest.TestCase):
    def test_synthetic_converter_staging_tests_do_not_import_pillow(self):
        test=(ROOT/'tools/tests/test_rc261_conversion_mount_and_zlib.py').read_text(encoding='utf8')
        self.assertEqual(test.count("patch.object(converter,'_verify_png',side_effect=_verify_synthetic_png)"),2)
        self.assertIn('data != _valid_small_png()',test)
        self.assertIn('test_real_decoder_fails_closed_without_pillow',test)

    def test_production_keeps_double_pillow_validation_with_guarded_import(self):
        src=(ROOT/'tools/import_presentation.py').read_text(encoding='utf8')
        self.assertIn('except ImportError as exc:',src)
        self.assertIn("raise RuntimeError('Pillow required for full PNG verification')",src)
        self.assertIn('picture.verify()',src)
        self.assertIn('picture.load()',src)
        self.assertIn('UnidentifiedImageError, Image.DecompressionBombError',src)

    def test_ci_preflight_still_runs_existing_security_regressions(self):
        ci=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        self.assertIn('RC264 Pillow-independent simulated PDF early CI gate',ci)
        self.assertIn('tools.tests.test_rc264_pillow_independent_ci',ci)
        self.assertIn('tools.tests.test_rc261_conversion_mount_and_zlib',ci)
        self.assertIn('python3 tools/ci_converter_apt_security.py',ci)
        self.assertIn('severity: CRITICAL,HIGH',ci)

if __name__=='__main__':
    unittest.main()
