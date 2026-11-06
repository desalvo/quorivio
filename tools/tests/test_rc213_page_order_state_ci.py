"""RC213: fail before npm if React hook dependency reads state in the TDZ.

RC212 full CI 42140973603 passed prior gates, then strict TS reported
TS2448/TS2454 because the thumbnail shortcut effect dependency array read
pageOrderPending before its useState declaration. Runtime logic is unchanged.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
UI = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
STATE = 'const [pageOrderPending,setPageOrderPending]=useState(false);'
BATCH = 'const [pageBatchBusy,setPageBatchBusy]=useState(false);'
EFFECT = '},[designActivity,snap,selectedPageIds,pageBatchBusy,pageOrderPending,pageHasUnsavedChanges]);'


def verify_order(source: str) -> None:
    if source.count(STATE) != 1:
        raise AssertionError('page order state must have exactly one initializer')
    app = source.index('function App(){')
    state = source.index(STATE)
    batch = source.index(BATCH)
    effect = source.index(EFFECT)
    if not app < batch < state < effect:
        raise AssertionError('pageOrderPending TDZ: state must precede dependent shortcut effect')
    if source.count(EFFECT) != 1:
        raise AssertionError('missing or duplicated thumbnail shortcut effect')
    if 'if(!action||pageBatchBusy||pageOrderPending||' not in source:
        raise AssertionError('page reordering guard removed from keyboard shortcuts')
    if 'aria-busy={pageOrderPending}' not in source:
        raise AssertionError('pending page order status is not rendered')


class RC213PageOrderStateCI(unittest.TestCase):
    def test_hook_initialized_before_effect_dependencies(self):
        verify_order(UI)

    def test_negative_mutations_reject_original_tdz_and_missing_guards(self):
        moved = UI.replace(STATE, '', 1).replace(EFFECT, EFFECT+'\n'+STATE, 1)
        duplicated = UI.replace(STATE, STATE+STATE, 1)
        no_guard = UI.replace('if(!action||pageBatchBusy||pageOrderPending||',
                              'if(!action||pageBatchBusy||', 1)
        for broken in (moved, duplicated, no_guard):
            self.assertNotEqual(broken, UI)
            with self.assertRaises(AssertionError):
                verify_order(broken)

    def test_early_ci_and_full_strict_typescript_gate_remain_enabled(self):
        self.assertIn('tools.tests.test_rc213_page_order_state_ci', WORKFLOW)
        self.assertIn('./node_modules/.bin/tsc --noEmit -p apps/web/tsconfig.json', WORKFLOW)
        self.assertIn('python3 tools/verify_rc_cycle212_inventory.py --historical', WORKFLOW)
        self.assertIn('python3 tools/verify_rc_cycle213_inventory.py', WORKFLOW)

if __name__ == '__main__':
    unittest.main()
