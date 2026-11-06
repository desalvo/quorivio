"""Regression contract for full-page editor unsaved-state guards."""
from pathlib import Path
import unittest

WEB = Path(__file__).resolve().parents[2] / "apps/web/src/main.tsx"

class EditorUnsavedGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = WEB.read_text()

    def test_draft_signature_includes_widgets_and_page_backgrounds(self):
        self.assertIn("function pageDraftSignature()", self.source)
        for part in ("widgets:pageWidgets", "questionHeader", "resultHeader", "questionBackgroundAsset", "resultBackgroundAsset"):
            self.assertIn(part, self.source)

    def test_navigation_and_close_are_guarded(self):
        # The RC206 thumbnail handler delegates to beginPageDesign(), where the
        # central unsaved-change check remains enforced for every page change.
        self.assertIn("if(designActivity&&designActivity!==a.id&&!skipNavigationConfirm&&!confirmPageNavigation())return", self.source)
        self.assertIn("setSelectedPageIds([a.id]);beginPageDesign(a)", self.source)
        self.assertNotIn("setSelectedPageIds([a.id]);beginPageDesign(a,true)", self.source)
        self.assertIn("if(confirmPageNavigation())setDesignActivity('')", self.source)
        self.assertIn("if(designActivity===a.id&&!confirmPageNavigation())return", self.source)

    def test_successful_save_and_unload_guard(self):
        self.assertIn("savedPageDraft.current=savedSignature", self.source)
        self.assertIn("addEventListener('beforeunload',onBeforeUnload)", self.source)
        self.assertIn("Modifiche non salvate", self.source)

if __name__ == "__main__": unittest.main()
