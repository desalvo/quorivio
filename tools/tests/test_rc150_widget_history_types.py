"""RC150: keep editor-history widget fields aligned with the saved PageDesign type.

This preflight does not replace the `npm run build` TypeScript type checker.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / 'apps/web/src/main.tsx'
DOMAIN = ROOT / 'apps/api/src/domain.ts'
WORKFLOW = ROOT / '.github/workflows/ci.yml'


def widget_history_contract(main: str, domain: str) -> bool:
    match = re.search(r"type EditorWidgetPermissionFields\s*=\s*Pick<NonNullable<PageDesign\['widgets'\]>\[number\],\s*(.*?)>;",main,re.S)
    if not match:
        return False
    selected = set(re.findall(r"'([A-Za-z][A-Za-z0-9]+)'", match.group(1)))
    if not {'position','resultTopCount','autoFit','resultsOnly'}.issubset(selected):
        return False
    if not re.search(r'newWidgetHistory<.*?&\s*EditorWidgetPermissionFields>\(', main, re.S):
        return False
    if not re.search(r"position\?:\{x:number;y:number;width:number",domain):
        return False
    if 'resultTopCount?:number' not in domain:
        return False
    return True


class RC150WidgetHistoryTypes(unittest.TestCase):
    def test_widget_history_covers_persisted_geometry_and_result_count(self):
        self.assertTrue(widget_history_contract(MAIN.read_text(encoding='utf8'),DOMAIN.read_text(encoding='utf8')))

    def test_removing_position_from_history_contract_fails(self):
        source=MAIN.read_text(encoding='utf8')
        self.assertFalse(widget_history_contract(source.replace(" | 'position' | 'resultTopCount'>;", " | 'resultTopCount'>;",1),DOMAIN.read_text(encoding='utf8')))

    def test_removing_result_top_count_from_history_contract_fails(self):
        source=MAIN.read_text(encoding='utf8')
        self.assertFalse(widget_history_contract(source.replace(" | 'position' | 'resultTopCount'>;", " | 'position'>;",1),DOMAIN.read_text(encoding='utf8')))

    def test_preflight_runs_before_frontend_build(self):
        workflow=WORKFLOW.read_text(encoding='utf8')
        self.assertIn('tools.tests.test_rc150_widget_history_types',workflow)
        self.assertIn('tools/verify_rc_cycle149_inventory.py --historical',workflow)
        self.assertIn('tools/verify_rc_cycle150_inventory.py',workflow)
        self.assertLess(workflow.index('test_rc150_widget_history_types'),workflow.index('npm install --ignore-scripts'))


if __name__=='__main__':
    unittest.main()
