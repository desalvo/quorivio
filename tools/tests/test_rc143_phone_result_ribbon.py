"""RC143: visible formatting panel, stable top results, phone stage geometry."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()

class RC143PhoneResultsRibbon(unittest.TestCase):
 def test_ribbon_close_is_visible_and_persisted_selection(self):
  for marker in ('aria-label="Chiudi Formato widget"','setRibbonDismissed(true)','new ResizeObserver(constrain)','observer?.observe(panel.current)',
                 'flex-wrap:wrap!important;align-content:flex-start!important','overflow-x:hidden!important;overflow-y:auto!important'):
   self.assertIn(marker,MAIN+CSS)
 def test_cloud_top_five_are_configurable_and_wrappable(self):
  for marker in ('topResultRows(', 'splitResultLabel(', 'resultTopCount??5', 'Numero risultati principali',
                 'resultTopCount?:number','w.resultTopCount>=1&&w.resultTopCount<=20'):
   self.assertIn(marker,MAIN+DOMAIN)
  self.assertIn('white-space:normal!important',CSS)
  self.assertIn('linked-result-final',MAIN)
 def test_phone_independent_stage_and_no_desktop_background(self):
  for marker in ('PhoneRehearsalStage','renderSlide(\'participant\',true)','width:390px!important;height:100%!important',
                 'mobilePageWidgets(viewWidgets,viewActivity?.page_design?.mobile)','position:absolute!important;left:var(--stage-x)!important'):
   self.assertIn(marker,MAIN+CSS)
  self.assertIn('participantPhoneLayout(viewWidgets,viewActivity?.page_design?.mobile).widgets',MAIN)
  self.assertIn("const viewActivity=viewer==='presenter'?activity:audienceActivity",MAIN)
  self.assertNotIn('rehearsal-phone-frame">{renderSlide(\'participant\')}',MAIN)
 def test_existing_preview_modes_still_operate(self):
  for marker in ('Presentatore','Partecipante','Affiancate','Smartphone',"mode==='both'&&participantDevice==='phone'"):
   self.assertIn(marker,MAIN)

if __name__=='__main__':unittest.main()
