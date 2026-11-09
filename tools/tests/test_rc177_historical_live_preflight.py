"""RC177: historical live contracts must track the current three-mode UI fixture.

The safety assertions are retained: presenter-only widgets stay hidden, the
phone stage excludes them before allocating height, and accessible reading has
an independent widget order.  Legacy two-way selectors and 1174px fixture
heights are no longer valid once RC176 was introduced.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
POLICY=(ROOT/'apps/web/src/live-slide-policy.ts').read_text(encoding='utf-8')
BROWSER=(ROOT/'tools/ci_browser_participant.py').read_text(encoding='utf-8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
LEGACY=('test_rc144_mobile_rating.py', 'test_rc167_live_preview_fidelity.py',
        'test_rc168_phone_preview_parity.py', 'test_rc169_rating_typography_parity.py')
THREE_MODE='audiencePortrait?audiencePhoneLayout.widgets:participantReadingMode?audienceReadingWidgets:audienceVisibleWidgets'

class RC177HistoricalLivePreflight(unittest.TestCase):
    def test_real_three_mode_runtime_and_filtered_phone_layout(self):
        self.assertIn(THREE_MODE, UI)
        self.assertIn('const audienceReadingWidgets=participantReadingWidgets(audienceAuthoredWidgets)', UI)
        self.assertIn('const visible = participantVisibleWidgets(widgets);', POLICY)
        self.assertIn('mobilePageWidgets(visible, mobile)', POLICY)
        self.assertIn('mobileStageHeight(visible, mobile)', POLICY)
        self.assertIn("['results-button', 'participant-count']", POLICY)

    def test_historical_preflights_match_the_current_semantics(self):
        for name in LEGACY[:3]:
            with self.subTest(module=name):
                test=(ROOT/'tools/tests'/name).read_text(encoding='utf-8')
                self.assertIn(THREE_MODE, test)
                # Never accept a regression that silently drops reading mode.
                self.assertNotIn("self.assertIn('audiencePortrait?audiencePhoneLayout.widgets:audienceVisibleWidgets'", test)
        for name in LEGACY[2:]:
            test=(ROOT/'tools/tests'/name).read_text(encoding='utf-8')
            self.assertIn("geometry['height']-geometry['expectedHeight']",test.replace("\\'", "'"))
            self.assertNotIn("geometry['height']-998",test.replace("\\'", "'"))

    def test_browser_fixture_and_negative_mutation_prove_private_height(self):
        self.assertIn("geometry['height']-geometry['expectedHeight']", BROWSER)
        self.assertIn("'results-button','participant-count'", BROWSER)
        old=BROWSER.replace("geometry['height']-geometry['expectedHeight']", "geometry['height']-1174")
        self.assertNotEqual(old,BROWSER)
        self.assertNotIn("geometry['height']-geometry['expectedHeight']",old)

    def test_early_ci_checks_legacy_and_current_contracts(self):
        self.assertIn('tools.tests.test_rc177_historical_live_preflight',CI)
        for cycle in (144,167,168,169,176):
            token=f'tools.tests.test_rc{cycle}_'
            self.assertIn(token, CI)
        self.assertLess(CI.index('tools.tests.test_rc177_historical_live_preflight'), CI.index('npm ci --ignore-scripts'))

if __name__=='__main__':unittest.main()
