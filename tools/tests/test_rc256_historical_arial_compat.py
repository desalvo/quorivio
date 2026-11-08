"""RC256: obsolete source-literal Arial assertions must not outlive the safe renderer.

The RC254 renderer intentionally uses a validated font allowlist instead of
`style?.fontFamily||'Arial'`, which accepts a literal `undefined` CSS family.
This guard prevents historical Python assertions from blocking safe changes
and validates the runtime Node contract in the surrounding CI step.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

HISTORICAL=(
    'tools/tests/test_rc145_mobile_background_font.py',
    'tools/tests/test_rc161_master_background_graphics.py',
    'tools/tests/test_rc194_question_typography.py',
    'tools/tests/test_rc195_master_typography_ci.py',
    'tools/tests/test_rc242_arial_master_zoom.py',
)


class RC256HistoricalArialCompat(unittest.TestCase):
    def test_historical_checks_follow_current_safe_fallback(self):
        for name in HISTORICAL:
            text=(ROOT/name).read_text(encoding='utf8')
            with self.subTest(name=name):
                self.assertIn('safeWidgetFontFamily(',text)
                self.assertNotIn('self.assertIn("fontFamily:style?.fontFamily||',text)
                self.assertNotIn('self.assertIn("answerFontFamily:style?.answerFontFamily||',text)
                self.assertNotIn("self.assertIn('fontFamily:footer.style?.footerNumberFontFamily||",text)

    def test_font_default_contract_rejects_literal_undefined(self):
        defaults=(ROOT/'apps/web/src/widget-typography-defaults.ts').read_text(encoding='utf8')
        appearance=(ROOT/'apps/web/src/widget-appearance.ts').read_text(encoding='utf8')
        footer=(ROOT/'apps/web/src/slide-master.ts').read_text(encoding='utf8')
        self.assertIn("export const WIDGET_FONT_FAMILIES=['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace']",defaults)
        self.assertIn("fontFamily:safeWidgetFontFamily(style?.fontFamily)",defaults)
        self.assertIn("answerFontFamily:safeWidgetFontFamily(style?.answerFontFamily,safeWidgetFontFamily(style?.fontFamily))",defaults)
        self.assertIn("fontFamily:safeWidgetFontFamily(style?.fontFamily)",appearance)
        self.assertIn("fontFamily:safeWidgetFontFamily(footer.style?.footerNumberFontFamily,safeWidgetFontFamily(footer.style?.fontFamily))",footer)
        self.assertNotIn("fontFamily:style?.fontFamily||'Arial'",defaults)
        self.assertNotIn("fontFamily:style?.fontFamily||'Arial'",appearance)

    def test_mutations_no_longer_mask_loss_of_safe_fallback(self):
        source=(ROOT/'apps/web/src/widget-appearance.ts').read_text(encoding='utf8')
        target='fontFamily:safeWidgetFontFamily(style?.fontFamily)'
        self.assertIn(target,source)
        for replacement in ("fontFamily:'Arial'", "fontFamily:style?.fontFamily||'Arial'"):
            self.assertNotIn(target,source.replace(target,replacement))
        historical=(ROOT/'tools/tests/test_rc195_master_typography_ci.py').read_text(encoding='utf8')
        self.assertIn('self.assertNotIn(original,damaged)',historical)

    def test_ci_exercises_old_and_new_behavior_before_rc242(self):
        ci=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        early=ci.index('RC256 reconciled historical Arial widget and master tests before npm')
        late=ci.index('RC242 Arial and app-wide zoom contract before npm')
        self.assertLess(early,late)
        preflight=ci[early:late]
        for module in ('test_rc256_historical_arial_compat','test_rc242_arial_master_zoom',
                       'test_rc194_question_typography','test_rc195_master_typography_ci',
                       'test_rc161_master_background_graphics','test_rc145_mobile_background_font'):
            self.assertIn('tools.tests.'+module,preflight)
        self.assertIn('node --experimental-strip-types --test apps/web/test/rc254-all-widget-schema-fonts.test.ts',preflight)


if __name__=='__main__':
    unittest.main()
