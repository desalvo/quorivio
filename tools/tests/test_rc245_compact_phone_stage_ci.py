"""RC245: real public phone stage must remain compact *and* readable.

The old RC217/207 floor was 278px, but RC241 deliberately removed 40px of
unused question header. Keep all real Chromium and planner safeguards.
"""
from __future__ import annotations
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
BROWSER=(ROOT/'tools/ci_browser_participant.py').read_text(encoding='utf8')
HISTORICAL=(ROOT/'tools/tests/test_rc217_public_phone_stage_ci.py').read_text(encoding='utf8')
PLANNER=(ROOT/'apps/web/src/mobile-page-layout.ts').read_text(encoding='utf8')
CHROMIUM=(ROOT/'tools/ci_rc245_compact_phone_chromium.py').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

def contract(browser=BROWSER,historical=HISTORICAL,planner=PLANNER,chromium=CHROMIUM,workflow=WORKFLOW):
 ast.parse(browser)
 ast.parse(historical)
 ast.parse(chromium)
 if "geometry['questionHeight']>=278-1" in browser or "geometry['questionHeight']>=278-1" in historical:
  raise AssertionError('obsolete 278px fixed phone question floor')
 for token in (
  "geometry['questionHeight']>=150+44*geometry['choiceCount']-1",
  "geometry['choiceCount']==2",
  "all(height>=43.5 for height in geometry['choiceHeights'])",
  "all(size>=17.5 for size in geometry['choiceFontSizes'])",
  "abs(geometry['height']-geometry['expectedHeight'])<2",
  "all(abs(gap-8)<2 for gap in geometry['gaps'])",
  "not {'results-button','participant-count'}.intersection(geometry['kinds'])",
 ):
  if token not in browser:raise AssertionError('public phone invariant missing: '+token)
 if "geometry['questionHeight']>=150+44*geometry['choiceCount']-1" not in historical:
  raise AssertionError('historical RC217 negative mutation does not protect new minimum')
 if '(options.length?150:190)+optionSpace' not in planner or 'Math.max(44,Math.ceil(Math.max(1,label.length)/32)*26+12)' not in planner:
  raise AssertionError('compact planner or 44px choice rows lost')
 if "assert abs(measurements['height']-238)<1.5" not in chromium or "row['height']>=43.5 and row['font']>=17.5" not in chromium:
  raise AssertionError('independent real Chromium readability fixture lost')
 if 'python3 -m unittest tools.tests.test_rc245_compact_phone_stage_ci -q' not in workflow or 'python3 tools/ci_rc245_compact_phone_chromium.py' not in workflow:
  raise AssertionError('RC245 early and real browser gates required')
 if 'python3 tools/ci_browser_participant.py' not in workflow:
  raise AssertionError('authenticated real PostgreSQL/React acceptance was removed')
 if workflow.index('tools.tests.test_rc245_compact_phone_stage_ci')>workflow.index('npm ci --ignore-scripts'):
  raise AssertionError('RC245 regression must run before npm')
 return True

class RC245CompactPhoneRegression(unittest.TestCase):
 def test_real_public_stage_and_early_ci(self):self.assertTrue(contract())
 def test_negative_old_fixed_floor(self):
  with self.assertRaisesRegex(AssertionError,'obsolete'):
   contract(browser=BROWSER.replace("geometry['questionHeight']>=150+44*geometry['choiceCount']-1","geometry['questionHeight']>=278-1"))
 def test_negative_touch_size_and_font(self):
  for token in ("all(height>=43.5 for height in geometry['choiceHeights'])", "all(size>=17.5 for size in geometry['choiceFontSizes'])"):
   with self.subTest(token=token),self.assertRaisesRegex(AssertionError,'invariant'):
    contract(browser=BROWSER.replace(token,'True'))
 def test_negative_missing_public_private_widget_filter(self):
  with self.assertRaisesRegex(AssertionError,'invariant'):
   contract(browser=BROWSER.replace("not {'results-button','participant-count'}.intersection(geometry['kinds'])",'True'))
 def test_negative_empty_browser_coverage(self):
  with self.assertRaisesRegex(AssertionError,'Chromium'):
   contract(chromium=CHROMIUM.replace("row['height']>=43.5 and row['font']>=17.5",'True'))
 def test_negative_missing_real_postgres_browser(self):
  with self.assertRaisesRegex(AssertionError,'authenticated'):
   contract(workflow=WORKFLOW.replace('python3 tools/ci_browser_participant.py','echo browser omitted'))

if __name__=='__main__':unittest.main()
