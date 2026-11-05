"""RC197: prevent stale one-page rehearsal and font contracts in the late Python mega-suite."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
TYPO=(ROOT/'apps/web/src/stage-widget-typography.ts').read_text(encoding='utf-8')
RESULTS=(ROOT/'apps/web/src/widget-results.ts').read_text(encoding='utf-8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')

class RC197IntegrationContracts(unittest.TestCase):
 def test_presenter_audience_rehearsal_never_falls_back_to_shared_page(self):
  rehearsal=UI.split('function SessionRehearsal(',1)[1].split('const editorWidgetKinds=',1)[0]
  self.assertIn('const presenterPages=rehearsalPresenterPages(activities)',rehearsal)
  self.assertIn('const audienceActivity=rehearsalAudiencePage(activity,activities)',rehearsal)
  self.assertIn("const viewActivity=viewer==='presenter'?activity:audienceActivity",rehearsal)
  self.assertIn("const viewWidgets=viewer==='presenter'?presenterWidgets:widgets",rehearsal)
  self.assertIn('!viewWidgets.length&&<h2 className="rehearsal-empty-title">{viewActivity?.page_design?.header||viewActivity?.title}</h2>',rehearsal)
  self.assertIn('disabled={page>=presenterPages.length-1}',rehearsal)
  self.assertNotIn('REHEARSAL_REACTION_PREFIX+activity.id',rehearsal)
  self.assertIn('REHEARSAL_REACTION_PREFIX+audienceActivity.id',rehearsal)

 def test_phone_and_typography_preserve_current_view_and_custom_styles(self):
  self.assertIn('participantPhoneLayout(viewWidgets,viewActivity?.page_design?.mobile).widgets',UI)
  self.assertIn("widget.kind==='title'?widgetDisplay(widget,context).style:widgetTextDefaults(widget.kind,widget.style)",TYPO)
  self.assertIn('widgetTypographyStyle(resolved)',TYPO)
  self.assertNotIn("widget.kind==='title'?widgetDisplay(widget,context).style:widget.style",TYPO)
  self.assertIn('questions?:{id:string;label:string;description?:string;answerMode?:string;',RESULTS)

 def test_late_ci_legacy_gate_is_reconciled_early_before_npm(self):
  self.assertIn('RC197 reconcile Kubernetes Python integration contracts before npm',CI)
  self.assertIn('test_page_rename_preview_contract_20261027',CI)
  self.assertIn('test_rc143_phone_result_ribbon',CI)
  self.assertIn('test_rc75_typescript_ci',CI)
  self.assertIn('test_rc_presenter_linked_preview_20261028',CI)
  self.assertIn('test_rehearsal_send_parity_20261028',CI)
  self.assertIn('test_visual_parity_rehearsal_20261028',CI)
  self.assertLess(CI.index('RC197 reconcile Kubernetes Python integration contracts before npm'),CI.index('run: npm install --ignore-scripts --no-audit --no-fund'))

if __name__=='__main__':unittest.main()
