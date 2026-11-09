"""RC196: regression against missing cross-page source import and editor widget type.

The historical Node-only checks did not compile the actual React frontend.
The corresponding strict TS compiler now runs immediately after npm setup.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
UI = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
DOMAIN = (ROOT / 'apps/api/src/domain.ts').read_text(encoding='utf8')
RESULTS = (ROOT / 'apps/web/src/widget-results.ts').read_text(encoding='utf8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
IMPORT = re.compile(r"import \{([^}]+)\} from './widget-results\.js';")
PERMISSIONS = re.compile(r'type EditorWidgetPermissionFields = (.*?);')


def frontend_contract(ui: str) -> bool:
    imports = IMPORT.findall(ui)
    permission = PERMISSIONS.search(ui)
    return bool(
        len(imports) == 1
        and 'linkedResultQuestion' in [name.strip() for name in imports[0].split(',')]
        and permission
        and "'showSourceQuestion'" in permission.group(1)
        and 'linkedResultQuestion(result,source)' in ui
        and '<LinkedResultSourceQuestion result={viewWidget} source={source}/>' in ui
        and 'const viewWidget={...widget,showCorrectAnswers:hasKey&&truthVisible}' in ui
        and 'showSourceQuestion:e.target.checked' in ui
    )


class RC196ResultsFrontendTyping(unittest.TestCase):
    def test_source_question_is_imported_and_editor_field_is_typed(self):
        self.assertTrue(frontend_contract(UI))
        self.assertIn('export function linkedResultQuestion(', RESULTS)
        self.assertIn('showSourceQuestion?:boolean', DOMAIN)
        self.assertIn('w.showSourceQuestion===undefined', DOMAIN)
        self.assertIn('showSourceQuestion?:boolean', RESULTS)

    def test_compile_frontend_early_after_install_not_just_api(self):
        self.assertIn('RC196 cross-page source question frontend typing contract before npm', WORKFLOW)
        self.assertIn('tools.tests.test_rc196_frontend_results_types', WORKFLOW)
        self.assertIn('RC196 strict frontend TypeScript typecheck before extended CI', WORKFLOW)
        self.assertIn('./node_modules/.bin/tsc --noEmit -p apps/web/tsconfig.json', WORKFLOW)
        self.assertLess(WORKFLOW.index('RC196 strict frontend TypeScript typecheck before extended CI'),
                        WORKFLOW.index('- name: Compile frontend and backend'))
        self.assertIn('python3 tools/verify_rc_cycle196_inventory.py', WORKFLOW)

    def test_mutations_reject_missing_import_or_untyped_option(self):
        self.assertFalse(frontend_contract(UI.replace('linkedStatisticSource,linkedResultQuestion,', 'linkedStatisticSource,', 1)))
        self.assertFalse(frontend_contract(UI.replace("'resultsOnly' | 'showSourceQuestion' |", "'resultsOnly' |", 1)))
        self.assertFalse(frontend_contract(UI.replace('linkedResultQuestion(result,source)', 'undefined', 1)))
        self.assertFalse(frontend_contract(UI.replace('showSourceQuestion:e.target.checked', 'showSourceQ:e.target.checked')))


if __name__ == '__main__':
    unittest.main()
