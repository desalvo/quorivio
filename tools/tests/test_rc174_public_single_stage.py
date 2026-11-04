"""Fast RC174 contracts (optional full Chromium probe runs separately)."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def check_stage(ui: str, css: str) -> bool:
    begin=ui.find('{joinPath?<main id="main-content"')
    end=ui.find('publicPath?<PresenterLiveScreen',begin)
    if begin<0 or end<=begin:return False
    public=ui[begin:end]
    return all((
        "const participantSlideActive=!!(joinPath&&joined&&entry?.session?.status==='active'&&entry?.activity)" in ui,
        '{!participantSlideActive&&(entry?.theme?.logos||[]).map' in public,
        'participantSlideActive?"participant-session-heading-offscreen":undefined' in public,
        '{!audienceAuthoredWidgets.length&&(entry.activity.page_design?.media||[]).map' in public,
        'participant-slide-active .participant-session-heading-offscreen{' in css,
        'stage-fidelity>.page-widget :is(textarea,input,select){\n  font-size:1.015625cqw!important' in css,
        'padding:.9375cqw 1.09375cqw!important' in css,
        'stage-reading{\n  background:#fff!important;background-image:none!important' in css,
    ))


class RC174PublicStage(unittest.TestCase):
    def test_current_contract(self):self.assertTrue(check_stage(UI,CSS))
    def test_negative_duplicate_visual_hero(self):
        self.assertFalse(check_stage(UI.replace('{!participantSlideActive&&(entry?.theme?.logos||[]).map','{(entry?.theme?.logos||[]).map',1),CSS))
    def test_negative_legacy_media_duplicate(self):
        self.assertFalse(check_stage(UI.replace('{!audienceAuthoredWidgets.length&&(entry.activity.page_design?.media||[]).map','{(entry.activity.page_design?.media||[]).map',1),CSS))
    def test_negative_fixed_mobile_textarea(self):
        self.assertFalse(check_stage(UI,CSS.replace('padding:.9375cqw 1.09375cqw!important','padding:12px 14px!important',1)))
    def test_browser_probe_is_opt_in_after_playwright_install(self):
        self.assertIn('python3 tools/rc174_browser_geometry.py',CI)
        self.assertLess(CI.index("'playwright>=1.50,<2'"),CI.index('python3 tools/rc174_browser_geometry.py'))


if __name__=='__main__':unittest.main()
