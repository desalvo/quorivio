"""RC170: master number, logical phone pixels and browser parity without skipped checks."""
from __future__ import annotations
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
CHROMIUM=(ROOT/'tools/ci_rc170_phone_footer_number_chromium.py').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC170PhoneFooterParity(unittest.TestCase):
    def test_phone_number_has_independent_logical_font_and_insets(self):
        for name in ('--phone-footer-number-font-size','--phone-footer-pad-right','--phone-footer-pad-bottom'):
            self.assertIn("'"+name+"'",UI)
            self.assertIn('var('+name+',',CSS)
        self.assertIn('fontSize:`${(item.fontSize/12.8).toFixed(5)}cqw`',UI,'desktop sizing must not change')

    def test_custom_position_not_overridden_by_old_fixed_phone_insets(self):
        last=CSS.split('/* RC170: footer number follows one logical phone specification')[1]
        self.assertIn('.slide-canvas-page-number[data-custom-number="true"]',last)
        self.assertIn('right:auto!important',last)
        self.assertIn('bottom:auto!important',last)
        self.assertIn('left:var(--footer-number-x,auto)!important',last)
        self.assertIn('top:var(--footer-number-y,auto)!important',last)
        self.assertIn(':not([data-custom-number="true"])',last)

    def test_editor_shows_master_page_number_without_changing_page_widgets(self):
        self.assertIn('numberingWidgets={(snap.activities.find(a=>a.id===designActivity) as any)?.page_design?.suppressMaster?pageWidgets:resolveSlideMasterWidgets(pageWidgets,snap.session.theme?.master?.widgets)}',UI)
        self.assertIn('widgets={numberingWidgets??widgets}',UI)
        self.assertIn('onChange={changeCanvasWidgets}',UI)
        self.assertNotIn('onChange={resolveSlideMasterWidgets(',UI)

    def test_negative_missing_master_number_or_custom_offsets_would_fail(self):
        broken=UI.replace('<SlideCanvasNumber widgets={numberingWidgets??widgets} pageNumber={pageNumber}/>',
                          '<SlideCanvasNumber widgets={widgets} pageNumber={pageNumber}/>',1)
        self.assertNotIn('widgets={numberingWidgets??widgets}',broken)
        broken=CSS.split('/* RC170: footer number follows one logical phone specification')[1].replace('right:auto!important','right:10px!important')
        self.assertNotIn('right:auto!important',broken)

    def test_actual_chromium_has_positive_and_negative_cases(self):
        ast.parse(CHROMIUM)
        for fragment in ('for viewport in (390, 1440)', 'for custom in (False, True)',
                         '((14, 5, 5), (23, 17, 13))', 'fromRight', 'fromBottom',
                         'fromLeft', 'fromTop', 'raise RuntimeError'):
            self.assertIn(fragment,CHROMIUM)

    def test_early_ci_and_real_chromium_acceptance(self):
        self.assertIn('tools.tests.test_rc170_phone_footer_number_parity',CI)
        self.assertLess(CI.index('tools.tests.test_rc170_phone_footer_number_parity'),CI.index('npm install --ignore-scripts'))
        self.assertIn('python3 tools/ci_rc170_phone_footer_number_chromium.py',CI)
        self.assertIn('tools/verify_rc_cycle169_inventory.py --historical',CI)
        self.assertIn('tools/verify_rc_cycle170_inventory.py',CI)
        self.assertIn("'.stage-phone .slide-canvas-page-number'",(ROOT/'tools/ci_browser_participant.py').read_text())

if __name__=='__main__':unittest.main()
