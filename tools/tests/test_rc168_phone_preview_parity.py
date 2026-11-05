"""RC168: participant phone geometry must exclude presenter tools before stacking."""
from __future__ import annotations
from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[2]
POLICY = (ROOT / 'apps/web/src/live-slide-policy.ts').read_text(encoding='utf8')
UI = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
BROWSER = (ROOT / 'tools/ci_browser_participant.py').read_text(encoding='utf8')
CHROMIUM = (ROOT / 'tools/ci_rc168_phone_footer_chromium.py').read_text(encoding='utf8')
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')


class RC168PhoneParity(unittest.TestCase):
    def test_shared_helper_filters_before_automatic_layout_and_height(self):
        self.assertIn('const visible = participantVisibleWidgets(widgets);', POLICY)
        self.assertIn('mobilePageWidgets(visible, mobile)', POLICY)
        self.assertIn('mobileStageHeight(visible, mobile)', POLICY)
        self.assertLess(POLICY.index('const visible = participantVisibleWidgets(widgets);'),
                        POLICY.index('return {widgets: mobilePageWidgets(visible, mobile)'))
        self.assertIn("['results-button', 'participant-count']", POLICY)

    def test_negative_old_filter_after_layout_is_detected(self):
        broken = POLICY.replace('mobilePageWidgets(visible, mobile)',
                                'participantVisibleWidgets(mobilePageWidgets(widgets, mobile))', 1)
        self.assertNotIn('return {widgets: mobilePageWidgets(visible, mobile)', broken)
        broken = POLICY.replace('mobileStageHeight(visible, mobile)', 'mobileStageHeight(widgets)', 1)
        self.assertNotIn('height: mobileStageHeight(visible)', broken)

    def test_real_participant_uses_one_layout_for_height_and_contents(self):
        self.assertIn('const audiencePhoneLayout=participantPhoneLayout(audienceAuthoredWidgets', UI)
        self.assertIn('height:audiencePhoneLayout.height', UI)
        self.assertIn('audiencePortrait?audiencePhoneLayout.widgets:participantReadingMode?audienceReadingWidgets:audienceVisibleWidgets', UI)
        self.assertIn('const audienceReadingWidgets=participantReadingWidgets(audienceAuthoredWidgets)', UI)
        self.assertNotIn('height:mobileStageHeight(resolveSlideMasterWidgets(', UI)
        self.assertNotIn('participantVisibleWidgets(audiencePortrait?mobilePageWidgets(', UI)

    def test_rehearsal_participant_shares_layout_but_presenter_keeps_own(self):
        self.assertIn('mobile?participantPhoneLayout(viewWidgets,viewActivity?.page_design?.mobile).widgets', UI)
        self.assertIn('height={participantPhoneLayout(widgets,audienceActivity?.page_design?.mobile).height}', UI)
        self.assertIn("viewer==='presenter'?(mobile?mobilePageWidgets(viewWidgets", UI)

    def test_real_postgresql_fixture_checks_footer_and_drops_phantom_height(self):
        ast.parse(BROWSER)
        for marker in ('FOOTER_WIDGET', "'kind':'footer'", 'geometry[\'height\']-998',
                       "geometry['footerOffset']", "'.audience-widget-layout.stage-phone'",
                       'stage-reading', 'stage-fidelity', "'results-button','participant-count'"):
            self.assertIn(marker, BROWSER)
        # Browser errors can contain bearer join links; do not log their raw text.
        self.assertNotIn('assert not errors,errors', BROWSER)
        self.assertIn('details intentionally suppressed', BROWSER)

    def test_local_real_browser_css_does_not_skip_without_chromium(self):
        ast.parse(CHROMIUM)
        for marker in ('raise RuntimeError', 'page.evaluate(', "'footerAfterContent'",
                       "'bottomGap'", "'bodyOverflow'", "'ratio'", 'for viewport in (390,1440)'):
            self.assertIn(marker, CHROMIUM)

    def test_ci_runs_regressions_before_npm_and_chromium_with_other_stages(self):
        self.assertIn('tools.tests.test_rc168_phone_preview_parity', CI)
        self.assertLess(CI.index('tools.tests.test_rc168_phone_preview_parity'),
                        CI.index('npm install --ignore-scripts'))
        self.assertIn('python3 tools/ci_rc168_phone_footer_chromium.py', CI)
        self.assertIn('python3 tools/ci_browser_participant.py', CI)
        self.assertIn('python3 tools/verify_rc_cycle167_inventory.py --historical', CI)
        self.assertIn('python3 tools/verify_rc_cycle168_inventory.py', CI)


if __name__ == '__main__':
    unittest.main()
