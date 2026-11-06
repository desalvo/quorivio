"""RC233: keep editor results switches in the strongly typed widget draft.

The RC232 GitHub run reached the strict frontend compiler and failed on
seven TS2339 errors because the editor's Pick<> omitted three fields already
present in the canonical PageDesign widget model. This pre-npm check guards
the local type selection; the real tsc --noEmit remains mandatory later in CI.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / 'apps/web/src/main.tsx'
DOMAIN = ROOT / 'apps/api/src/domain.ts'
CI = ROOT / '.github/workflows/ci.yml'
PROPERTIES = ('showSourceTitle', 'showSourceAnswers', 'showCorrectAnswers')


def check_editor_type_contract(main: str, domain: str) -> None:
    declaration = re.search(
        r"type EditorWidgetPermissionFields\s*=\s*Pick<\s*NonNullable<PageDesign\['widgets'\]>\[number\],\s*([^;]+)>\s*;",
        main,
    )
    if declaration is None:
        raise AssertionError('Editor widget permission fields must use canonical PageDesign type')
    selected = set(re.findall(r"'([A-Za-z][A-Za-z0-9]*)'", declaration.group(1)))
    for prop in PROPERTIES:
        if prop not in selected:
            raise AssertionError(f'EditorWidgetPermissionFields omits {prop}')
        if re.search(rf'\b{prop}\?\s*:\s*boolean\b', domain) is None:
            raise AssertionError(f'Canonical PageDesign widget lacks typed {prop}')
    if 'EditorWidgetPermissionFields>([])' not in main:
        raise AssertionError('Editor history no longer uses strongly typed permission fields')


class RC233EditorResultsTypeContract(unittest.TestCase):
    def test_editor_type_picks_all_result_switches_from_api_domain(self):
        check_editor_type_contract(MAIN.read_text(encoding='utf8'), DOMAIN.read_text(encoding='utf8'))

    def test_switches_remain_user_operable_in_the_editor(self):
        main = MAIN.read_text(encoding='utf8')
        for label, prop in (
            ('Mostra titolo della widget collegata', 'showSourceTitle'),
            ('Mostra risposte della widget collegata', 'showSourceAnswers'),
            ('Evidenzia risposte vere nei risultati', 'showCorrectAnswers'),
        ):
            with self.subTest(prop=prop):
                self.assertIn(f'aria-label="{label}"', main)
                self.assertIn(f'{prop}:e.target.checked', main)
        self.assertIn("w.kind==='results-button'", main)
        self.assertIn('resultHasAnswerKey(', main)

    def test_missing_each_field_is_a_regression(self):
        main = MAIN.read_text(encoding='utf8')
        domain = DOMAIN.read_text(encoding='utf8')
        for prop in PROPERTIES:
            with self.subTest(prop=prop):
                mutated = main.replace(f"'showSourceQuestion' | '{prop}'", "'showSourceQuestion'", 1) if prop == 'showSourceTitle' else main.replace(f" | '{prop}'", '', 1)
                self.assertNotEqual(mutated, main)
                with self.assertRaisesRegex(AssertionError, prop):
                    check_editor_type_contract(mutated, domain)

    def test_full_typescript_compile_gate_is_still_mandatory(self):
        workflow = CI.read_text(encoding='utf8')
        self.assertIn('RC233 frontend linked-results TypeScript contract before npm', workflow)
        self.assertIn('python3 -m unittest tools.tests.test_rc233_editor_results_type_contract -q', workflow)
        self.assertIn('RC196 strict frontend TypeScript typecheck before extended CI', workflow)
        self.assertIn('./node_modules/.bin/tsc --noEmit -p apps/web/tsconfig.json', workflow)
        self.assertLess(workflow.index('RC233 frontend linked-results TypeScript contract before npm'), workflow.index('RC196 strict frontend TypeScript typecheck before extended CI'))


if __name__ == '__main__':
    unittest.main()
