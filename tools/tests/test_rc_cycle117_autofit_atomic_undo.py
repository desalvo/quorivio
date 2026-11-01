"""RC117 non-invasive source contracts for auto-fit/undo atomicity and browser acceptance."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
HISTORY=(ROOT/'apps/web/src/widget-history.ts').read_text(encoding='utf8')
EDITOR=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
BROWSER=(ROOT/'tools/ci_browser_editor.py').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def preserves_atomic_undo(history, editor):
    return all(s in history for s in (
      'export function reconcileWidgetAutoFit<T>',
      'state.gestureBase !== null',
      '!same(state.present, base)',
      'past:',  # still a bounded explicit edit/undo history
      'return {...state, present: fitted}',
    )) and all(s in editor for s in (
      'onAutoFit?:(base:any[],fitted:any[])=>void',
      'if(onAutoFit)onAutoFit(widgets,changes);else onChange(changes)',
      'onAutoFit={reconcilePageAutoFit}',
      'setWidgetHistory(h=>reconcileWidgetAutoFit(h,base,fitted))',
    ))


class RC117AtomicUndo(unittest.TestCase):
    def test_derived_fit_is_not_separate_history_step(self):
        self.assertTrue(preserves_atomic_undo(HISTORY,EDITOR))

    def test_rejects_legacy_fit_replay_and_stale_state(self):
        self.assertFalse(preserves_atomic_undo(HISTORY,EDITOR.replace('if(onAutoFit)onAutoFit(widgets,changes);else onChange(changes)','onChange(changes)')))
        self.assertFalse(preserves_atomic_undo(HISTORY.replace('!same(state.present, base)','false'),EDITOR))
        self.assertFalse(preserves_atomic_undo(HISTORY.replace('return {...state, present: fitted}','return editWidgets(state,fitted)'),EDITOR))

    def test_chromium_still_requires_single_undo_and_exact_result(self):
        self.assertIn("await click_canvas_tool(page,'Duplica selezione')",BROWSER)
        self.assertIn("to_have_count(5)",BROWSER)
        self.assertIn("await page.keyboard.press('Control+z')",BROWSER)
        self.assertIn("to_have_count(3)",BROWSER)
        self.assertIn('One undo must revert the user',BROWSER)
        self.assertIn("locator('button:visible').first.focus()",BROWSER)
        self.assertIn('await select_exact_widget_pair(page)',BROWSER)

    def test_mandatory_preflight_and_histories(self):
        self.assertIn('test_rc_cycle117_autofit_atomic_undo',WORKFLOW)
        self.assertLess(WORKFLOW.index('test_rc_cycle117_autofit_atomic_undo'),WORKFLOW.index('npm install --ignore-scripts'))
        self.assertIn('python3 tools/ci_browser_editor.py',WORKFLOW)
        self.assertIn('python3 tools/verify_rc_cycle117_inventory.py',WORKFLOW)

if __name__=='__main__':unittest.main()
