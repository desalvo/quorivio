"""Prevent editor/dashboard from mounting two interacting modal focus traps.

A second rehearsal component made both body-level portals inert and aria-hidden
in GitHub Actions run 40689633215, which appeared as a Playwright strict-mode
violation after the earlier fix for inaccessible nested dialogs.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CI=(ROOT/'tools/ci_browser_editor.py').read_text(encoding='utf8')

class RehearsalUniqueMount(unittest.TestCase):
    def test_only_two_declaration_sites_have_disjoint_guards(self):
        self.assertEqual(UI.count('<SessionRehearsal '), 2)
        self.assertIn('{rehearsalOpen&&!designActivity&&<RehearsalErrorBoundary ', UI,
                      'Dashboard preview must not mount while the editor exists')
        self.assertIn('{rehearsalOpen&&<RehearsalErrorBoundary ', UI,
                      'Editor preview should mount inside the conditionally rendered editor')
        self.assertIn('{designActivity&&<section className="panel powerpoint-editor editor-ux-v2"', UI)
    def test_chromium_rejects_multiple_dialogs_before_accessibility_assertions(self):
        count = "await expect(backdrop).to_have_count(1)"
        visible = 'await expect(backdrop).to_be_visible()'
        self.assertIn(count, CI)
        self.assertLess(CI.index(count), CI.index(visible))
        self.assertIn('node.parentElement===document.body', CI)
        self.assertIn('!node.closest("[inert],[aria-hidden=true]")', CI)
    def test_offline_browser_uses_production_bundle_and_real_editor_dashboard(self):
        script=(ROOT/'tools/ci_rehearsal_singleton_offline_chromium.py').read_text(encoding='utf8')
        workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        self.assertIn('ci_rehearsal_singleton_offline_chromium.py', workflow)
        for contract in ("index-*.js", "index-*.css", "Anteprime della sessione",
                         ".editor-preview-open.preview-both", "to_have_count(1)",
                         "get_by_role('dialog',name='Anteprima interattiva della sessione')",
                         "await page.keyboard.press('Escape')"):
            self.assertIn(contract,script)
        css=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
        self.assertIn('header.rehearsal-toolbar{height:auto',css)

    def test_editor_preview_uses_unsaved_canvas_not_dashboard_snapshot(self):
        self.assertIn('widgets:pageWidgets,backgroundColor:questionBackgroundColor', UI)
        self.assertIn('initialPageId={designActivity}', UI)
    def test_dashboard_preview_keeps_original_session_snapshot(self):
        self.assertIn('initialMode={rehearsalMode} snapshot={snap}', UI)

if __name__=='__main__':
    unittest.main()
