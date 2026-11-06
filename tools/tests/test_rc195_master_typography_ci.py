"""RC195: test real centralized default contract, not an obsolete main.tsx literal."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MASTER=(ROOT/'apps/web/src/slide-master.ts').read_text()
UI=(ROOT/'apps/web/src/main.tsx').read_text()
STAGE=(ROOT/'apps/web/src/stage-widget-typography.ts').read_text()
APPEARANCE=(ROOT/'apps/web/src/widget-appearance.ts').read_text()
DEFAULTS=(ROOT/'apps/web/src/widget-typography-defaults.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()
RC161=(ROOT/'tools/tests/test_rc161_master_background_graphics.py').read_text()

class RC195MasterTypographyCI(unittest.TestCase):
 def test_legacy_rc161_uses_central_contract_instead_of_inline_literal(self):
  self.assertIn('DEFAULT_TITLE_STYLE',RC161)
  self.assertIn('DEFAULT_FOOTER_STYLE',RC161)
  self.assertNotIn('self.assertIn("fontFamily:\'Arial\'",UI)',RC161)
  self.assertIn('tools.tests.test_rc161_master_background_graphics',CI)
  self.assertIn('tools.tests.test_rc195_master_typography_ci',CI)

 def test_default_families_inherited_without_resetting_custom_theme_or_widget(self):
  self.assertIn("DEFAULT_TITLE_STYLE={fontFamily:'Arial'",MASTER)
  self.assertIn("DEFAULT_FOOTER_STYLE={fontFamily:'Arial'",MASTER)
  self.assertIn('...DEFAULT_TITLE_STYLE,...(w.titleUseMaster!==false?context.masterTitleStyle:{}),...w.style',MASTER)
  self.assertIn("fontFamily:style?.fontFamily||'Arial'",APPEARANCE)
  self.assertIn('widgetTextDefaults(widget.kind,widget.style)',STAGE)
  self.assertIn("widget.kind==='title'?widgetDisplay(widget,context).style",STAGE)
  self.assertIn('widgetTextDefaults(w.kind,w.style)',UI)
  self.assertIn("answerFontFamily:style?.answerFontFamily||style?.fontFamily||'Arial'",DEFAULTS)

 def test_historical_presentation_contracts_follow_independent_page_routing(self):
  ui=UI;typography=STAGE
  checks={
   'tools/tests/test_rc144_mobile_rating.py':"mobile?{backgroundImage:viewActivity?.page_design?.mobile?.backgroundAssetId?",
   'tools/tests/test_rc167_live_preview_fidelity.py':'mobile?participantPhoneLayout(viewWidgets,viewActivity?.page_design?.mobile).widgets',
   'tools/tests/test_rc168_phone_preview_parity.py':'height={participantPhoneLayout(widgets,audienceActivity?.page_design?.mobile).height}',
   'tools/tests/test_rc169_rating_typography_parity.py':"widget.kind==='title'?widgetDisplay(widget,context).style:widgetTextDefaults(widget.kind,widget.style)",
   'tools/tests/test_rc131_stage_collision_contract.py':"const resolved=widget.kind==='title'?widgetDisplay(widget,context).style:widgetTextDefaults(widget.kind,widget.style)",
   'tools/tests/test_rehearsal_timed_deadline_20261028.py':'[audienceActivity?.id,seed]',
   'tools/tests/test_rc91_scheme_stage.py':'pageNumber={viewPageNumber}',
  }
  for file,contract in checks.items():
   self.assertIn(contract,(ROOT/file).read_text(),file)
  for contract in ('[audienceActivity?.id,seed]','viewPageNumber=slidePageNumber(activities,activity.id)',
    'mobile?participantPhoneLayout(viewWidgets,viewActivity?.page_design?.mobile).widgets',
    'height={participantPhoneLayout(widgets,audienceActivity?.page_design?.mobile).height}'):
   self.assertIn(contract,ui)
  self.assertIn("const resolved=widget.kind==='title'?widgetDisplay(widget,context).style:widgetTextDefaults(widget.kind,widget.style)",typography)

 def test_negative_mutations_reject_incorrect_phone_and_timer_contract(self):
  for old,new in [('[audienceActivity?.id,seed]','[activity?.id,seed]'),
                  ('viewPageNumber=slidePageNumber(activities,activity.id)','viewPageNumber=page+1'),
                  ('viewPageNumber=slidePageNumber(activities,activity.id)','viewPageNumber=slidePageNumber(activities,viewActivity.id)'),
                  ('participantPhoneLayout(viewWidgets,viewActivity?.page_design?.mobile).widgets','participantVisibleWidgets(viewWidgets)')]:
   self.assertIn(old,UI)
   self.assertNotIn(old,UI.replace(old,new,1))

 def test_negative_mutations_detect_arial_loss_and_custom_override_loss(self):
  damaged=MASTER.replace("DEFAULT_TITLE_STYLE={fontFamily:'Arial'","DEFAULT_TITLE_STYLE={fontFamily:'Helvetica'")
  self.assertNotIn("DEFAULT_TITLE_STYLE={fontFamily:'Arial'",damaged)
  damaged=MASTER.replace('...w.style}:w.style||{}','}:w.style||{}')
  self.assertNotIn('...w.style}:w.style||{}',damaged)
  damaged=APPEARANCE.replace("fontFamily:style?.fontFamily||'Arial'","fontFamily:'Arial'")
  self.assertNotIn("fontFamily:style?.fontFamily||'Arial'",damaged)
  damaged=STAGE.replace("widget.kind==='title'?widgetDisplay(widget,context).style",'widget.style')
  self.assertNotIn("widget.kind==='title'?widgetDisplay(widget,context).style",damaged)

if __name__=='__main__':unittest.main()
