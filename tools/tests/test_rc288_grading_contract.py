"""RC288: the historical RC221 grading test must match the modern R toggle.

Guard against reinstating the obsolete footer-overlapping strip or weakening
privacy, result schema, click functionality, or independent text styles.
"""
from pathlib import Path
import unittest
from tools.tests.test_rc221_pdf_editable_and_results import assert_private_grading_contract

ROOT=Path(__file__).resolve().parents[2]
WEB=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC288GradingContract(unittest.TestCase):
 def test_actual_editor_exposes_conditional_r_without_overlay(self):
  assert_private_grading_contract(WEB,DOMAIN)
  self.assertIn('result-answer-key-toggle',WEB)
  self.assertIn('aria-pressed={truthVisible}',WEB)
  self.assertIn('onClick={e=>{e.stopPropagation();setTruthVisible(v=>!v)}}',WEB)
  self.assertIn('Solo per il presentatore',WEB)
 def test_regression_fails_when_r_toggle_disappears(self):
  with self.assertRaisesRegex(AssertionError,'result-answer-key-toggle'):
   assert_private_grading_contract(WEB.replace("className={'result-answer-key-toggle'", "className={'missing-r-control'"),DOMAIN)
 def test_regression_fails_if_overlapping_strip_returns(self):
  with self.assertRaisesRegex(AssertionError,'obsolete footer-overlapping'):
   assert_private_grading_contract(WEB+'Evidenzia le risposte vere sotto la widget risultati',DOMAIN)
 def test_regression_fails_if_private_key_or_style_schema_removed(self):
  for field in ('showCorrectAnswers?:boolean','resultTextStyles?:Record'):
   with self.subTest(field=field),self.assertRaisesRegex(AssertionError,'missing private grading schema'):
    assert_private_grading_contract(WEB,DOMAIN.replace(field,''))
 def test_regression_fails_when_r_is_not_conditioned_on_key(self):
  with self.assertRaisesRegex(AssertionError,'hasKey&&<button'):
   assert_private_grading_contract(WEB.replace('hasKey&&<button','true&&<button'),DOMAIN)
 def test_ci_runs_modern_contract_before_legacy_rc221(self):
  current='python3 -m unittest tools.tests.test_rc288_grading_contract -q'
  legacy='python3 -m unittest tools.tests.test_rc221_pdf_editable_and_results -q'
  self.assertEqual(CI.count(current),1)
  self.assertLess(CI.index(current),CI.index(legacy))

if __name__=='__main__':unittest.main()
