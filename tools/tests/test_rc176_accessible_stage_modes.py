"""RC176 early CI contract for real public mode transitions and reading DOM order."""
from __future__ import annotations

import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
POLICY=(ROOT/'apps/web/src/live-slide-policy.ts').read_text(encoding='utf-8')
BROWSER=(ROOT/'tools/ci_browser_participant.py').read_text(encoding='utf-8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')


def browser_mode_guards(source:str)->bool:
    try:ast.parse(source)
    except SyntaxError:return False
    phone="await p2.get_by_role('button',name='Layout smartphone').click()"
    phone_stage="await expect(p2.locator('.audience-widget-layout.stage-phone')).to_have_count(1)"
    reading="await p2.get_by_role('button',name='Lettura accessibile').click()"
    reading_stage="await expect(p2.locator('.audience-widget-layout.stage-reading')).to_have_count(1)"
    # RC238: phone stage also exists before the explicit switch as the mobile default.
    # Restrict this historical RC176 ordering assertion to its own explicit click.
    return (all(x in source for x in (phone,phone_stage,reading,reading_stage,
         'normalized_slide_geometry(p1)','normalized_slide_geometry(p2)',
         "reading['kinds'][-1]=='footer'", "reading['fieldHeight']>=44"))
         and source.index(phone)<source.index(phone_stage, source.index(phone))<source.index(reading)<source.index(reading_stage))


class RC176AccessibleModes(unittest.TestCase):
    def test_real_chromium_fixture_tests_three_distinct_modes(self):
        self.assertTrue(browser_mode_guards(BROWSER))

    def test_negative_mutation_reading_confused_with_phone_fails(self):
        mutated=BROWSER.replace("await expect(p2.locator('.audience-widget-layout.stage-reading')).to_have_count(1)",
                                "await expect(p2.locator('.audience-widget-layout.stage-phone')).to_have_count(1)",1)
        self.assertNotEqual(mutated,BROWSER)
        self.assertFalse(browser_mode_guards(mutated))

    def test_negative_mutation_mode_switch_missing_fails(self):
        mutated=BROWSER.replace("await p2.get_by_role('button',name='Layout smartphone').click()", "# no phone switch",1)
        self.assertFalse(browser_mode_guards(mutated))

    def test_source_dom_order_not_css_only(self):
        self.assertIn('export function participantReadingWidgets',POLICY)
        self.assertIn("a.widget.kind === 'footer'",POLICY)
        self.assertIn(".filter(({widget}) => !LABELLESS_GRAPHICS.has(widget.kind))",POLICY)
        self.assertIn('const audienceReadingWidgets=participantReadingWidgets(audienceAuthoredWidgets)',UI)
        self.assertIn('participantReadingMode?audienceReadingWidgets:audienceVisibleWidgets',UI)

    def test_ci_includes_current_accessibility_and_authored_postgres_acceptance(self):
        self.assertIn('python3 tools/rc176_browser_reading_order.py',WORKFLOW)
        self.assertIn('python3 tools/ci_browser_participant.py',WORKFLOW)
        self.assertIn('tools.tests.test_rc176_accessible_stage_modes',WORKFLOW)
        self.assertLess(WORKFLOW.index('tools.tests.test_rc176_accessible_stage_modes'),
                        WORKFLOW.index('npm install --ignore-scripts'))


if __name__=='__main__': unittest.main()
