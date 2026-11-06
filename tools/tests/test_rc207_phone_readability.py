"""Dependency-free RC207 preflight prevents 1280px typography in the 390px stage."""
from __future__ import annotations
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
CSS=(ROOT/'apps/web/src/style.css').read_text()
ANS=(ROOT/'apps/web/src/widget-answer-style.ts').read_text()
MARKS=(ROOT/'apps/web/src/widget-text-marks.ts').read_text()
RICH=(ROOT/'apps/web/src/widget-rich-editor.tsx').read_text()
MOBILE=(ROOT/'apps/web/src/mobile-page-layout.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()


def phone_contract(css:str,answers:str,marks:str,rich:str,mobile:str,ci:str)->None:
    for token in ('--q-phone-answer-font-size','--q-phone-submit-font-size',
                  '--q-phone-submit-min-height','--q-phone-answer-height'):
        if token not in answers or token not in css:
            raise AssertionError('Missing phone pixel-sized answer control: '+token)
    for selector in ('data-canvas-device="phone"','rehearsal-phone-stage','audience-widget-layout.stage-phone'):
        if css.count(selector)<5:
            raise AssertionError('Missing shared phone surface: '+selector)
    if 'min-height:44px!important;align-items:center!important' not in css:
        raise AssertionError('Answer choices are not touch-readable')
    if "'--q-inline-phone-font-size'" not in marks or 'setProperty(\'--q-inline-phone-font-size\'' not in rich:
        raise AssertionError('Rich inline custom font still shrinks to 390/1280')
    if 'Math.ceil(Math.max(1,label.length)/32)*26+12' not in mobile:
        raise AssertionError('Long phone answers are clipped by old automatic heights')
    if 'python3 tools/ci_rc207_phone_readability_chromium.py' not in ci:
        raise AssertionError('Real browser regression is missing from CI')


class RC207PhoneReadable(unittest.TestCase):
    def test_editor_rehearsal_live_and_inline_readable(self):
        phone_contract(CSS,ANS,MARKS,RICH,MOBILE,CI)

    def test_missing_public_phone_stage_fails_closed(self):
        with self.assertRaisesRegex(AssertionError,'surface'):
            phone_contract(CSS.replace('audience-widget-layout.stage-phone','no-public-stage'),ANS,MARKS,RICH,MOBILE,CI)

    def test_accidentally_omitted_px_control_fails_closed(self):
        with self.assertRaisesRegex(AssertionError,'control'):
            phone_contract(CSS,ANS.replace("'--q-phone-answer-font-size'", "'--lost-phone-answer-size'"),MARKS,RICH,MOBILE,CI)

    def test_phone_choice_height_and_browser_job_required(self):
        with self.assertRaisesRegex(AssertionError,'heights'):
            phone_contract(CSS,ANS,MARKS,RICH,MOBILE.replace('Math.ceil(Math.max(1,label.length)/32)*26+12','1'),CI)
        with self.assertRaisesRegex(AssertionError,'browser'):
            phone_contract(CSS,ANS,MARKS,RICH,MOBILE,CI.replace('python3 tools/ci_rc207_phone_readability_chromium.py','echo omitted'))


if __name__=='__main__':unittest.main()
