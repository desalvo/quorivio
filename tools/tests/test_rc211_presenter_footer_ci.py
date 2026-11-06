"""RC211: historic RC91/RC195 contract must preserve RC206 presenter numbering.

Fast fail-closed checks, without Node/Chromium: distinguish the page used to
render participant content from the presenter's current display number.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
UI = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
MASTER = (ROOT / 'apps/web/src/slide-master.ts').read_text(encoding='utf8')
RC91 = (ROOT / 'tools/tests/test_rc91_scheme_stage.py').read_text(encoding='utf8')
RC195 = (ROOT / 'tools/tests/test_rc195_master_typography_ci.py').read_text(encoding='utf8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
CURRENT = 'viewPageNumber=slidePageNumber(activities,activity.id)'
OBSOLETE = 'viewPageNumber=slidePageNumber(activities,viewActivity.id)'

def require_presenter_numbering(source: str) -> None:
    anchor = source.index("const renderSlide=(viewer:'presenter'|'participant',mobile=false)=>")
    section = source[anchor:source.index('return <section className="rehearsal-slide"', anchor)]
    if "const viewActivity=viewer==='presenter'?activity:audienceActivity;" not in section:
        raise AssertionError('independent presenter/audience rendering lost')
    if CURRENT not in section:
        raise AssertionError('audience footer no longer follows presenter page ordinal')
    if OBSOLETE in section:
        raise AssertionError('audience page independently numbered')

class RC211PresenterFooterCI(unittest.TestCase):
    def test_independent_content_and_shared_presenter_page_number(self):
        require_presenter_numbering(UI)
        self.assertIn('const index=activities.findIndex(a=>a.id===id);', MASTER)
        self.assertIn("activities.slice(0,index+1).filter(a=>a.page_design?.presenterHidden!==true).length", MASTER)
        self.assertIn('pageNumber={viewPageNumber}', UI)

    def test_reconciled_historical_contracts_and_preflights(self):
        for name, code in (('RC91', RC91), ('RC195', RC195)):
            with self.subTest(name=name):
                self.assertIn(CURRENT, code)
                self.assertIn(OBSOLETE, code)  # only as forbidden/regression mutation
                self.assertNotIn('self.assertIn(\'' + OBSOLETE + '\',UI)', code)
        self.assertIn('tools.tests.test_rc91_scheme_stage', WORKFLOW)
        self.assertIn('tools.tests.test_rc195_master_typography_ci', WORKFLOW)
        self.assertIn('tools.tests.test_rc211_presenter_footer_ci', WORKFLOW)

    def test_negative_mutations_fail_closed(self):
        for broken in (
            UI.replace(CURRENT, OBSOLETE, 1),
            UI.replace(CURRENT, 'viewPageNumber=page+1', 1),
            UI.replace('const viewActivity=viewer===\'presenter\'?activity:audienceActivity;',
                       'const viewActivity=activity;', 1),
        ):
            self.assertNotEqual(broken, UI)
            with self.assertRaises(AssertionError):
                require_presenter_numbering(broken)

if __name__ == '__main__':
    unittest.main()
