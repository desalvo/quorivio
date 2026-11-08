"""RC257: catch stale source-literal font assertions before historical UI gates.

The broken RC193 check was another raw-source assertion accidentally omitted from
RC256's early inventory. A broad scan prevents a future delayed failure of the
same class while retaining the independent runtime Node assertions in the CI.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC257Preflight(unittest.TestCase):
    def test_historical_python_gates_cannot_require_unsafe_font_fallbacks(self):
        violations=[]
        for source in sorted((ROOT/'tools/tests').glob('test_*.py')):
            for number,line in enumerate(source.read_text(encoding='utf8').splitlines(),1):
                # An assertion that *requires* a raw style fallback is unsafe;
                # reject the entire family of font input/answer/title variants.
                if ('assertIn(' in line and 'assertNotIn(' not in line
                    and 'fontFamily||' in line):
                    violations.append(f'{source.name}:{number}')
        self.assertFalse(violations,'Unsafe legacy font literal assertions: '+', '.join(violations))

    def test_rc193_guards_independent_option_and_submit_fallbacks(self):
        options=(ROOT/'apps/web/src/widget-answer-style.ts').read_text(encoding='utf8')
        self.assertIn('const family=safeWidgetFontFamily(style?.answerFontFamily,safeWidgetFontFamily(style?.fontFamily));',options)
        self.assertIn('fontFamily:safeWidgetFontFamily(style?.submitFontFamily,safeWidgetFontFamily(style?.fontFamily))',options)
        self.assertNotIn("style?.fontFamily||'Arial'",options)

    def test_ci_executes_rc193_before_rc242_and_rc193_legacy_step(self):
        first=CI.index('RC257 all historical Arial text fallback guards before npm')
        self.assertLess(first,CI.index('RC242 Arial and app-wide zoom contract before npm'))
        self.assertLess(first,CI.index('RC193 editor focus ownership and font controls before npm'))
        section=CI[first:CI.index('RC242 Arial and app-wide zoom contract before npm')]
        for fragment in ('tools.tests.test_rc257_full_arial_preflight',
                         'tools.tests.test_rc193_focus_and_font',
                         'apps/web/test/rc254-all-widget-schema-fonts.test.ts'):
            self.assertIn(fragment,section)

if __name__=='__main__': unittest.main()
