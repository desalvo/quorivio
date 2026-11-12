"""RC117 non-invasive source contracts for auto-fit/undo atomicity and browser acceptance."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
HISTORY=(ROOT/'apps/web/src/widget-history.ts').read_text(encoding='utf8')
EDITOR=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
BROWSER=(ROOT/'tools/ci_browser_editor.py').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def preserves_atomic_undo(history, editor):
    """RC326: auto-fit is a presentational transform, never a geometry history edit.

    Retain and verify the legacy stale-write protection, but do not require the
    now-removed auto-height DOM effect to mutate history when content changes.
    """
    return all(s in history for s in (
      'export function reconcileWidgetAutoFit<T>',
      'state.gestureBase !== null',
      '!same(state.present, base)',
      'past:',
      'return {...state, present: fitted}',
    )) and all(s in editor for s in (
      'onAutoFit?:(base:any[],fitted:any[])=>void',
      'setWidgetHistory(h=>reconcileWidgetAutoFit(h,base,fitted))',
      'autoFit is a content-fit preference, NEVER a widget geometry edit',
      'proportionalWidgetScale({',
      "allowScale={w.autoFit!==false&&!['qr','participant-count'].includes(w.kind)&&editing!==w.id}",
    )) and 'if(onAutoFit)onAutoFit(widgets,changes);else onChange(changes)' not in editor and 'autoFitExpandedPosition(' not in editor and bool(re.search(
      r'''onAutoFit\s*=\s*\{\s*canvasDevice\s*===\s*['"]phone['"]\s*\?\s*undefined\s*:\s*reconcilePageAutoFit\s*\}''',
      editor,
    ))

class RC117AtomicUndo(unittest.TestCase):
    def test_derived_fit_is_not_separate_history_step(self):
        self.assertTrue(preserves_atomic_undo(HISTORY,EDITOR))

    def test_rejects_legacy_fit_replay_and_stale_state(self):
        self.assertFalse(preserves_atomic_undo(HISTORY,EDITOR.replace('autoFit is a content-fit preference, NEVER a widget geometry edit','legacy auto-height mutates geometry')))
        self.assertFalse(preserves_atomic_undo(HISTORY.replace('!same(state.present, base)','false'),EDITOR))
        self.assertFalse(preserves_atomic_undo(HISTORY.replace('return {...state, present: fitted}','return editWidgets(state,fitted)'),EDITOR))

    def test_phone_does_not_inherit_desktop_autofit_and_history_remains_atomic(self):
        self.assertTrue(preserves_atomic_undo(HISTORY, EDITOR))
        self.assertFalse(preserves_atomic_undo(HISTORY, EDITOR.replace(
            "onAutoFit={canvasDevice==='phone'?undefined:reconcilePageAutoFit}",
            "onAutoFit={reconcilePageAutoFit}")))
        self.assertFalse(preserves_atomic_undo(HISTORY, EDITOR.replace(
            "onAutoFit={canvasDevice==='phone'?undefined:reconcilePageAutoFit}",
            "onAutoFit={canvasDevice==='phone'?reconcilePageAutoFit:undefined}")))
        # Weak source checks must not accept automatic fit as an additional
        # independent history edit, or the derived result as an outdated edit.
        self.assertFalse(preserves_atomic_undo(HISTORY.replace(
            'return {...state, present: fitted}', 'return editWidgets(state,fitted)'), EDITOR))

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
        self.assertLess(WORKFLOW.index('test_rc_cycle117_autofit_atomic_undo'),WORKFLOW.index('npm ci --ignore-scripts'))
        self.assertIn('python3 tools/ci_browser_editor.py',WORKFLOW)
        self.assertIn('python3 tools/verify_rc_cycle117_inventory.py',WORKFLOW)

if __name__=='__main__':unittest.main()
