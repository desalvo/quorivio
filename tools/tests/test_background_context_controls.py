"""Static regression guard for independent, removable page/result backgrounds."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = (ROOT / 'apps/web/src/main.tsx').read_text()

class BackgroundContextControls(unittest.TestCase):
    def test_context_choices_are_separate(self):
        self.assertIn('Seleziona sfondo pagina dalla libreria', SOURCE)
        self.assertIn('Seleziona sfondo risultati dalla libreria', SOURCE)
        self.assertIn('uploadBackground(e.target.files?.[0],false)', SOURCE)
        self.assertIn('uploadBackground(e.target.files?.[0],true)', SOURCE)
    def test_removal_clears_url_and_asset(self):
        self.assertIn("setQuestionBackgroundAsset('');setQuestionBackground('')", SOURCE)
        self.assertIn("setResultBackgroundAsset('');setResultBackground('')", SOURCE)
        self.assertIn('backgroundUrl:questionBackground||undefined', SOURCE)
        self.assertIn('backgroundUrl:resultBackground||undefined', SOURCE)
    def test_context_uploads_are_authenticated_existing_handler(self):
        self.assertIn('function uploadBackground', SOURCE)
        self.assertIn("credentials:'include'", SOURCE)

if __name__ == '__main__':
    unittest.main()
