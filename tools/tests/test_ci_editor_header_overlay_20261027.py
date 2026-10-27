"""CI contracts for real pointer-accessible editor context panels (40589103128)."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf-8')
HELPER=(ROOT/'tools/ci_editor_context_tools.py').read_text(encoding='utf-8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
BROWSER=(ROOT/'tools/ci_editor_context_header_overlay_chromium.py').read_text(encoding='utf-8')

class BrowserEditorContextHeaderRC(unittest.TestCase):
    def test_menu_anchors_to_viewport_below_header(self):
        fix=CSS.split('/* RC browser acceptance 40589103128:',1)[1]
        self.assertIn('.editor-ux-v2 .canvas-background-context{',fix)
        self.assertIn('position:fixed!important',fix)
        self.assertIn('top:max(76px',fix)
        self.assertIn('max-height:calc(100dvh - 94px)',fix)

    def test_selection_and_layer_panels_share_safe_anchor(self):
        fix=CSS.split('/* RC browser acceptance 40589103128:',1)[1]
        self.assertIn('.canvas-editor-group[data-tools-open=true]>.canvas-editor-tools{',fix)
        self.assertIn('top:max(204px',fix)
        self.assertIn('right:auto!important',fix)

    def test_browser_clicks_are_real_and_check_header_hit_target(self):
        self.assertIn('document.elementFromPoint',BROWSER)
        self.assertIn('get_by_role(',BROWSER)
        self.assertIn('await click_canvas_tool(page,',BROWSER)
        self.assertNotIn('force=True',BROWSER)
        self.assertIn('margin-top:-90px!important',BROWSER)
        self.assertIn('await verify(browser,1440,940,False)',BROWSER)
        self.assertIn('await verify(browser,390,844,True)',BROWSER)

    def test_shared_helper_reports_occluded_action_instead_of_forcing_click(self):
        self.assertIn('document.elementFromPoint',HELPER)
        self.assertIn('Canvas selection menu is covered',HELPER)
        self.assertNotIn('force=True',HELPER)

    def test_extended_workflow_runs_real_header_regression_before_full_editor(self):
        pos=WORKFLOW.index('python3 tools/ci_editor_context_header_overlay_chromium.py')
        self.assertLess(pos,WORKFLOW.index('python3 tools/ci_browser_editor.py'))
        self.assertIn('if: github.event_name == \'workflow_dispatch\' && inputs.browser_test',WORKFLOW)

if __name__=='__main__':unittest.main()
