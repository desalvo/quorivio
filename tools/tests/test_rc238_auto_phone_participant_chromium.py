"""RC238: real joined-phone Chromium CI must honor auto phone mode, then compare 16:9.

Full CI 42269302109 reached PostgreSQL-backed participant Chromium but the old
fixture assumed a 16:9 default on both devices. Since RC227 phone is selected
by default for touch/narrow viewports, the fixture must explicitly switch to
16:9 for faithful cross-device geometry, including after a full mobile reload.
"""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BROWSER = ROOT / 'tools/ci_browser_participant.py'
APP = ROOT / 'apps/web/src/main.tsx'
WORKFLOW = ROOT / '.github/workflows/ci.yml'

PHONE_PRESSED = "await expect(page.get_by_role('button',name='Layout smartphone')).to_have_attribute('aria-pressed','true')"
PHONE_STAGE = "await expect(page.locator('.audience-widget-layout.stage-phone')).to_have_count(1)"
FAITHFUL_CLICK = "await page.get_by_role('button',name='Diapositiva 16:9').click()"
FAITHFUL_STAGE = "await expect(page.locator('.audience-widget-layout.stage-fidelity')).to_have_count(1)"
RELOAD_PHONE = "await expect(p2.get_by_role('button',name='Layout smartphone')).to_have_attribute('aria-pressed','true')"
RELOAD_CLICK = "await p2.get_by_role('button',name='Diapositiva 16:9').click()"


def validate_contract(source: str, app: str, workflow: str) -> None:
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.AsyncFunctionDef)}
    if not {'enter', 'run'}.issubset(functions):
        raise AssertionError('missing real Chromium join and participant flow')
    entry = ast.get_source_segment(source, functions['enter']) or ''
    run = ast.get_source_segment(source, functions['run']) or ''
    for required in (
        'async def enter(page,secret,name,default_phone=False)',
        'if default_phone:', PHONE_PRESSED, PHONE_STAGE, FAITHFUL_CLICK,
        FAITHFUL_STAGE,
        "await expect(page.locator('[data-widget-kind=\"question\"]')).to_have_count(1)",
    ):
        if required not in entry:
            raise AssertionError('joined phone Chromium regression: missing ' + required)
    if not (entry.index('if default_phone:') < entry.index(PHONE_PRESSED) <
            entry.index(PHONE_STAGE) < entry.index(FAITHFUL_CLICK) <
            entry.index(FAITHFUL_STAGE)):
        raise AssertionError('phone default must be verified before switching to faithful 16:9')
    expected = (
        "await enter(p1,secret,'Browser Alice')",
        "await enter(p2,code,'Browser Bob',default_phone=True)",
        "await p2.reload(wait_until='domcontentloaded')",
        RELOAD_PHONE,
        "await expect(p2.locator('.audience-widget-layout.stage-phone')).to_have_count(1)",
        RELOAD_CLICK,
        "await expect(p2.locator('.audience-widget-layout.stage-fidelity')).to_have_count(1)",
        'normalized_slide_geometry(p2)',
        "await p2.get_by_role('button',name='Layout smartphone').click()",
        "await p2.get_by_role('button',name='Lettura accessibile').click()",
    )
    for value in expected:
        if value not in run:
            raise AssertionError('real participant workflow no longer exercises ' + value)
    if not (run.index("await p2.reload(wait_until='domcontentloaded')") <
            run.index(RELOAD_PHONE) <
            run.index(RELOAD_CLICK) <
            run.index('normalized_slide_geometry(p2)') <
            run.index("await p2.get_by_role('button',name='Layout smartphone').click()")):
        raise AssertionError('mobile reload default and explicit geometry mode order drifted')
    for value in (
        'defaultParticipantPhoneMode(window.innerWidth,window.matchMedia',
        'if(participantModeExplicit)return;',
        "aria-pressed={!!audiencePortrait}",
        "aria-pressed={!participantReadingMode&&!audiencePortrait}",
        'setParticipantModeExplicit(true);setParticipantReadingMode(false);setParticipantPhoneMode(false)',
    ):
        if value not in app:
            raise AssertionError('product phone-mode contract drifted: ' + value)
    early = 'python3 -m unittest tools.tests.test_rc238_auto_phone_participant_chromium -q'
    browser = 'python3 tools/ci_browser_participant.py'
    if early not in workflow or browser not in workflow:
        raise AssertionError('mandatory early preflight or real PostgreSQL Chromium acceptance removed')
    if not workflow.index(early) < workflow.index('npm ci --ignore-scripts') < workflow.index(browser):
        raise AssertionError('RC238 regression or end-to-end acceptance is in the wrong CI phase')


class RC238AutoPhoneParticipantChromium(unittest.TestCase):
    def test_current_prod_and_browser_contract(self):
        validate_contract(BROWSER.read_text(), APP.read_text(), WORKFLOW.read_text())

    def test_negative_mobile_default_cannot_be_replaced_by_desktop_expectation(self):
        source = BROWSER.read_text()
        self.assertIn(PHONE_PRESSED, source)
        with self.assertRaisesRegex(AssertionError, 'phone Chromium regression'):
            validate_contract(source.replace(PHONE_PRESSED,
                "await expect(page.get_by_role('button',name='Diapositiva 16:9')).to_have_attribute('aria-pressed','true')", 1), APP.read_text(), WORKFLOW.read_text())

    def test_negative_explicit_mode_switch_cannot_be_removed(self):
        source = BROWSER.read_text()
        self.assertIn(FAITHFUL_CLICK, source)
        with self.assertRaisesRegex(AssertionError, 'phone Chromium regression'):
            validate_contract(source.replace(FAITHFUL_CLICK, 'await page.wait_for_timeout(1)', 1), APP.read_text(), WORKFLOW.read_text())

    def test_negative_reload_requires_reselecting_faithful_slide(self):
        source = BROWSER.read_text()
        self.assertIn(RELOAD_CLICK, source)
        with self.assertRaisesRegex(AssertionError, 'mobile reload default'):
            validate_contract(source.replace(RELOAD_CLICK, 'await p2.wait_for_timeout(1)', 1), APP.read_text(), WORKFLOW.read_text())

    def test_negative_mobile_context_cannot_be_mislabeled_desktop(self):
        source = BROWSER.read_text()
        self.assertIn("await enter(p2,code,'Browser Bob',default_phone=True)", source)
        with self.assertRaisesRegex(AssertionError, 'real participant workflow'):
            validate_contract(source.replace("await enter(p2,code,'Browser Bob',default_phone=True)",
                                     "await enter(p2,code,'Browser Bob')", 1), APP.read_text(), WORKFLOW.read_text())

    def test_negative_device_default_and_ci_cannot_be_removed(self):
        for value in ('if(participantModeExplicit)return;',
                      'defaultParticipantPhoneMode(window.innerWidth,window.matchMedia'):
            with self.subTest(value=value), self.assertRaisesRegex(AssertionError, 'product phone-mode contract'):
                validate_contract(BROWSER.read_text(), APP.read_text().replace(value, 'missing_value', 1), WORKFLOW.read_text())
        with self.assertRaisesRegex(AssertionError, 'mandatory early preflight'):
            validate_contract(BROWSER.read_text(), APP.read_text(),
                              WORKFLOW.read_text().replace('python3 tools/ci_browser_participant.py', '# removed', 1))


if __name__ == '__main__':
    unittest.main()
