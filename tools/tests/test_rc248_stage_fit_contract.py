"""Fail-closed RC248 pre-npm checks for viewport vs remaining-stage height."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]


def valid_stage_fit(css: str)->bool:
    if '/* RC248: cap the desktop canvas' not in css:
        return False
    block=css[css.index('/* RC248: cap the desktop canvas'):]
    return all(x in block for x in (
        '@media(min-width:761px)',
        '.editor-ux-v2 .editor-stage{container-type:size}',
        'max-width:min(100%,calc(28px + (100cqh - 35px)*16/9))!important;',
    ))

class RC248StageFit(unittest.TestCase):
    def test_dynamic_stage_container_not_viewport_height(self):
        css=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
        self.assertTrue(valid_stage_fit(css))
        self.assertFalse(valid_stage_fit(css.split('/* RC248: cap the desktop canvas')[0]))
        self.assertFalse(valid_stage_fit(css.replace('100cqh - 35px', '100dvh - 35px')))
        self.assertFalse(valid_stage_fit(css.replace('28px + (100cqh', '0px + (100cqh')))
        self.assertFalse(valid_stage_fit(css.replace('container-type:size', 'container-type:inline-size')))
    def test_real_chromium_and_historic_mock_kept_in_ci(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
        self.assertIn('python3 -m unittest tools.tests.test_rc248_stage_fit_contract -q',workflow)
        self.assertIn('python3 tools/ci_rc248_stage_fit_chromium.py',workflow)
        self.assertIn('python3 tools/ci_editor_mock_layout_chromium.py',workflow)
        script=(ROOT/'tools/ci_rc248_stage_fit_chromium.py').read_text(encoding='utf8')
        self.assertIn('stage[\'scrollHeight\'] <= stage[\'clientHeight\']+3',script)
        self.assertIn('slide[\'y\']+slide[\'h\'] <= stage[\'y\']+stage[\'h\']+1.5',script)

if __name__=='__main__':
    unittest.main()
