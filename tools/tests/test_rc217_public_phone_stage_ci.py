"""RC217: fail closed on phantom public-phone stage geometry and RC207 regressions."""
from pathlib import Path
import ast
import unittest

ROOT=Path(__file__).resolve().parents[2]
BROWSER=(ROOT/'tools/ci_browser_participant.py').read_text(encoding='utf8')
POLICY=(ROOT/'apps/web/src/live-slide-policy.ts').read_text(encoding='utf8')
LAYOUT=(ROOT/'apps/web/src/mobile-page-layout.ts').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def check_public_phone_contract(browser:str, policy:str, layout:str, workflow:str):
    ast.parse(browser)
    tokens=(
        "const publicWidgets=[...stage.querySelectorAll(':scope>.page-widget')]",
        'const expectedHeight=16+ordered.reduce((sum,r)=>sum+r.height,0)+Math.max(0,ordered.length-1)*8+16;',
        "abs(geometry['height']-geometry['expectedHeight'])<2",
        "geometry['questionHeight']>=150+44*geometry['choiceCount']-1",
        "geometry['choiceCount']==2",
        "all(height>=43.5 for height in geometry['choiceHeights'])",
        "all(size>=17.5 for size in geometry['choiceFontSizes'])",
        "abs(geometry['topGap']-16)<2",
        "all(abs(gap-8)<2 for gap in geometry['gaps'])",
        "geometry['kinds'].count('footer')==1",
        "{'results-button','participant-count'}.intersection(geometry['kinds'])",
        "10<=geometry['footerOffset']<=20",
    )
    for token in tokens:
        if token not in browser:
            raise AssertionError('phone geometry invariant missing: '+token)
    if "geometry['height']-998" in browser or "geometry['height']-1028" in browser:
        raise AssertionError('stale hard-coded phone stage height')
    if ('const visible = participantVisibleWidgets(widgets);' not in policy or
        'mobilePageWidgets(visible, mobile)' not in policy or
        'mobileStageHeight(visible, mobile)' not in policy):
        raise AssertionError('presenter private-widget filter before public layout missing')
    if 'Math.max(44,Math.ceil(Math.max(1,label.length)/32)*26+12)' not in layout:
        raise AssertionError('RC207 answer rows are no longer readable')
    required=(
        'tools.tests.test_rc217_public_phone_stage_ci',
        'node --experimental-strip-types --test apps/web/test/rc217-public-phone-stage.test.ts',
        'python3 tools/ci_browser_participant.py',
    )
    if any(x not in workflow for x in required) or workflow.index(required[0])>workflow.index('npm install --ignore-scripts'):
        raise AssertionError('CI must check public-phone geometry early and in real Chromium')


class RC217PublicPhoneStageCI(unittest.TestCase):
    def test_current_browser_and_source_invariants(self):
        check_public_phone_contract(BROWSER,POLICY,LAYOUT,WORKFLOW)

    def test_negative_hardcoded_height_and_missing_phantom_check(self):
        for broken in (
            BROWSER.replace("abs(geometry['height']-geometry['expectedHeight'])<2", "abs(geometry['height']-1028)<2"),
            BROWSER.replace("geometry['questionHeight']>=150+44*geometry['choiceCount']-1", "True"),
            BROWSER.replace("all(height>=43.5 for height in geometry['choiceHeights'])", "True"),
            BROWSER.replace("all(size>=17.5 for size in geometry['choiceFontSizes'])", "True"),
            BROWSER.replace("all(abs(gap-8)<2 for gap in geometry['gaps'])", "True"),
        ):
            with self.assertRaisesRegex(AssertionError,'geometry|hard-coded'):
                check_public_phone_contract(broken,POLICY,LAYOUT,WORKFLOW)

    def test_negative_unfiltered_private_layout(self):
        broken=POLICY.replace('mobileStageHeight(visible, mobile)','mobileStageHeight(widgets, mobile)')
        with self.assertRaisesRegex(AssertionError,'filter'):
            check_public_phone_contract(BROWSER,broken,LAYOUT,WORKFLOW)

    def test_negative_removed_touch_height_and_missing_ci(self):
        with self.assertRaisesRegex(AssertionError,'readable'):
            check_public_phone_contract(BROWSER,POLICY,LAYOUT.replace('Math.max(44,Math.ceil(Math.max(1,label.length)/32)*26+12)','16'),WORKFLOW)
        with self.assertRaisesRegex(AssertionError,'CI'):
            check_public_phone_contract(BROWSER,POLICY,LAYOUT,WORKFLOW.replace('tools.tests.test_rc217_public_phone_stage_ci','removed'))

if __name__=='__main__':unittest.main()
