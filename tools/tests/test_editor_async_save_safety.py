"""Regression safeguards for async editor persistence and keyboard saving."""
import unittest
from pathlib import Path

SOURCE = (Path(__file__).resolve().parents[2] / 'apps/web/src/main.tsx').read_text()

class AsyncEditorSaveSafety(unittest.TestCase):
    def test_concurrent_saves_are_blocked(self):
        self.assertIn('if(!designActivity||pendingPageSave.current)return', SOURCE)
        self.assertIn('pendingPageSave.current=true', SOURCE)
        self.assertIn('finally{pendingPageSave.current=false;setPageSavePending(false)}', SOURCE)

    def test_navigation_waits_for_inflight_save(self):
        self.assertIn('if(pendingPageSave.current){setNotice(', SOURCE)
        self.assertIn('Attendi la conclusione del salvataggio', SOURCE)

    def test_save_captures_exact_submitted_draft(self):
        self.assertIn('const savedSignature=pageDraftSignature()', SOURCE)
        self.assertIn('savedPageDraft.current=savedSignature', SOURCE)
        self.assertIn('latestPageDraft.current===savedSignature', SOURCE)
        self.assertNotIn('savedPageDraft.current=pageDraftSignature();setNotice', SOURCE)

    def test_keyboard_save_and_disabled_control(self):
        self.assertIn("event.key.toLowerCase()==='s'", SOURCE)
        self.assertIn('event.preventDefault()', SOURCE)
        self.assertIn('disabled={!pageHasUnsavedChanges||pageSavePending}>Salva layout', SOURCE)

if __name__ == '__main__': unittest.main()
