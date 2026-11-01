"""RC98 source-level regression for the three frontend TS strict-build failures.

This dependency-free preflight supplements (but does not replace) `npm run build`,
which performs the actual strict TypeScript check after npm dependencies load.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
MAIN = ROOT / 'apps/web/src/main.tsx'
CI = ROOT / '.github/workflows/ci.yml'


class FrontendCompilerHotfix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MAIN.read_text(encoding='utf8')
        cls.workflow = CI.read_text(encoding='utf8')

    def test_pending_text_style_guards_both_nullable_properties(self):
        self.assertRegex(self.source, r'previous\?\.id===w\.id&&previous\?\.field===sel\.field\?previous\.style:\{\}')
        self.assertNotIn('previous?.id===w.id&&previous.field===sel.field', self.source)

    def test_presenter_navigation_recovers_using_the_component_state_setter(self):
        start = self.source.index('const changePage=async(direction:-1|1)=>')
        end = self.source.index('const latest=useRef(changePage)', start)
        section = self.source[start:end]
        self.assertIn('setData(await request<Snapshot>', section)
        self.assertNotIn('setRestSnapshot', section)
        self.assertIn('}finally{pending.current=false;setBusy(false)}', section)

    def test_master_editor_consumes_widget_arrays_not_state_updater_functions(self):
        start = self.source.index('<div className="slide-scheme-layout">')
        end = self.source.index('onInspectWidget={setSchemaInspected}', start)
        section = self.source[start:end]
        self.assertIn('onChange={next=>setSchemaWidgets(masterWidgetTemplate(next))}', section)
        self.assertNotIn("typeof next==='function'", section)
        self.assertRegex(self.source, r'onChange:\(items:any\[\]\)=>void')

    def test_actual_typescript_build_remains_blocking_after_npm(self):
        self.assertIn('- name: Compile frontend and backend', self.workflow)
        self.assertRegex(self.workflow, r'- name: Compile frontend and backend\s+run: npm run build')
        self.assertIn('"build": "tsc --noEmit && vite build"',
                      (ROOT / 'apps/web/package.json').read_text(encoding='utf8'))


if __name__ == '__main__':
    unittest.main()
