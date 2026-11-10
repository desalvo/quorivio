"""RC301: runtime and privacy scope of native-engine accessible pie acceptance."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'tools/ci_rc301_pie_cross_engine.py'
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC301NativePie(unittest.TestCase):
    def test_script_compiles_and_imports_actual_pie_geometry(self):
        source=SCRIPT.read_text(encoding='utf8')
        compile(source,str(SCRIPT),'exec')
        for mark in (
            "import {resultPieLayout} from './apps/web/src/result-pie-layout.ts'",
            'production_geometry()', 'get_by_role',
            'webkit','firefox','chromium', 'tinySharePresent',
            'longNameHasMultipleLines', "all('%' not in value for value in titles)",
        ):
            with self.subTest(mark=mark):
                self.assertIn(mark,source)
        for forbidden in ('page.route(', 'route.fulfill(', 'page.set_content(MOCK_', 'sampleStatisticRows('):
            self.assertNotIn(forbidden,source)

    def test_long_mobile_names_wrap_instead_of_being_ellipsized(self):
        mark='.linked-results .linked-results-pie-mobile-name{'
        self.assertIn(mark,CSS)
        block=CSS.split(mark)[-1].split('}',1)[0]
        self.assertIn('white-space:normal',block)
        self.assertIn('overflow-wrap:anywhere',block)
        self.assertNotIn('white-space:nowrap',block)
        self.assertNotIn('text-overflow:ellipsis',block)
        self.assertIn('min-width:0',block)

    def test_both_natively_rendered_engines_are_mandatory_in_full_ci(self):
        self.assertIn('name: RC301 native Firefox and WebKit readable pie legends',WORKFLOW)
        self.assertIn('python3 tools/ci_rc301_pie_cross_engine.py --engines firefox webkit',WORKFLOW)
        self.assertIn('python3 tools/ci_rc301_pie_cross_engine.py --engines chromium',WORKFLOW)
        self.assertIn('python3 -m unittest tools.tests.test_rc301_native_pie -q',WORKFLOW)
        self.assertLess(WORKFLOW.index('name: RC301 native Firefox and WebKit readable pie legends'),
                        WORKFLOW.index('name: Upload cross-browser failure evidence'))
        self.assertLess(WORKFLOW.index('name: RC301 Chromium readable pie legends'),
                        WORKFLOW.index('name: Capture real app screenshots for the manuals'))

if __name__=='__main__':
    unittest.main()
