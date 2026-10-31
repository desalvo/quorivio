"""RC75: guard typed widget edits and optional footer context after RC74 TS CI failure."""
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RC75TypescriptRegression(unittest.TestCase):
    def test_editor_has_typed_reaction_icon_size_from_persisted_widget(self):
        ui = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
        domain = (ROOT / 'apps/api/src/domain.ts').read_text(encoding='utf8')
        contract = (ROOT / 'apps/web/src/widget-style-contract.ts').read_text(encoding='utf8')
        self.assertRegex(ui, r"type EditorWidgetPermissionFields\s*=\s*Pick<[^;]*'reactionIconSize'")
        self.assertIn('reactionIconSize?:number', domain)
        self.assertIn("StoredPageWidget['reactionIconSize'],number|undefined", contract)

    def test_optional_footer_number_is_narrowed_and_remains_bottom_right(self):
        source = (ROOT / 'apps/web/src/slide-master.ts').read_text(encoding='utf8')
        self.assertIn("typeof context.pageNumber==='number'", source)
        self.assertIn('Number.isInteger(context.pageNumber)', source)
        self.assertIn('String(context.pageNumber)', source)
        self.assertIn('position:{x:0,y:94,width:100,height:6,rotation:0}', source)

    def test_free_text_subquestions_are_typed_consistently(self):
        source = (ROOT / 'apps/web/src/widget-results.ts').read_text(encoding='utf8')
        self.assertIn('answerMode?:string;options?:', source)
        self.assertIn('questions?:{id:string;label:string;answerMode?:string;', source)
        self.assertIn('rehearsalFreeTextRows(source:StatisticalWidget,', source)

    @unittest.skipUnless(shutil.which('tsc'), 'TypeScript compiler is unavailable locally')
    def test_strict_typescript_compilation_of_affected_independent_modules(self):
        with tempfile.TemporaryDirectory() as td:
            result = subprocess.run([
                shutil.which('tsc'), '--noEmit', '--strict', '--target', 'ES2022',
                '--module', 'ESNext', '--moduleResolution', 'bundler',
                '--typeRoots', td, '--skipLibCheck',
                str(ROOT / 'apps/web/src/slide-master.ts'),
                str(ROOT / 'apps/web/src/widget-results.ts'),
            ], cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, (result.stdout + result.stderr)[:4000])


if __name__ == '__main__':
    unittest.main()
