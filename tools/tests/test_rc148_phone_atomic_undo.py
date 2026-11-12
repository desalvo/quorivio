"""RC148: source-contract compatibility with independent phone canvas and undo."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from tools.tests.test_rc_cycle117_autofit_atomic_undo import preserves_atomic_undo

ROOT = Path(__file__).resolve().parents[2]
EDITOR = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
HISTORY = (ROOT / 'apps/web/src/widget-history.ts').read_text(encoding='utf8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')


class RC148PhoneAtomicUndo(unittest.TestCase):
    def test_desktop_fits_inside_existing_atomic_history_step(self):
        self.assertTrue(preserves_atomic_undo(HISTORY, EDITOR))
        self.assertIn('!same(state.present, base)', HISTORY)
        self.assertIn('return {...state, present: fitted}', HISTORY)
        self.assertNotIn('if(onAutoFit)onAutoFit(widgets,changes);else onChange(changes)', EDITOR)
        self.assertIn('proportionalWidgetScale({', EDITOR)

    def test_phone_branch_must_not_use_desktop_fit(self):
        self.assertTrue(preserves_atomic_undo(HISTORY, EDITOR))
        self.assertFalse(preserves_atomic_undo(HISTORY, EDITOR.replace(
            "canvasDevice==='phone'?undefined:reconcilePageAutoFit",
            "canvasDevice==='phone'?reconcilePageAutoFit:undefined")))

    def test_stale_effect_and_extra_undo_action_are_rejected(self):
        self.assertFalse(preserves_atomic_undo(HISTORY.replace('!same(state.present, base)', 'false'), EDITOR))
        self.assertFalse(preserves_atomic_undo(HISTORY.replace('return {...state, present: fitted}', 'return editWidgets(state,fitted)'), EDITOR))

    def test_mobile_background_upload_regression_preserves_existing_security(self):
        from tools.tests.test_rc_cycle114_editor_preflight import background_contract
        self.assertTrue(background_contract(EDITOR))
        self.assertIn("onBackgroundUpload={file=>uploadBackground(file,false,canvasDevice==='phone')}", EDITOR)
        self.assertIn("if(forMobile){setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));}", EDITOR)
        self.assertFalse(background_contract(EDITOR.replace("if(applied){", "if(true){", 1)))

    def test_preflight_and_historical_inventory_remain_enforced(self):
        self.assertIn('tools.tests.test_rc_cycle117_autofit_atomic_undo', WORKFLOW)
        self.assertIn('tools.tests.test_rc148_phone_atomic_undo', WORKFLOW)
        self.assertIn('tools/verify_rc_cycle147_inventory.py --historical', WORKFLOW)
        self.assertIn('tools/verify_rc_cycle148_inventory.py', WORKFLOW)
        self.assertLess(WORKFLOW.index('test_rc148_phone_atomic_undo'), WORKFLOW.index('npm ci --ignore-scripts'))


if __name__ == '__main__':
    unittest.main()
