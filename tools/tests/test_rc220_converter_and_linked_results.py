"""RC220 integration contract: server admin PDF gate and independently styled result sources."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text()
UI=(ROOT/'apps/web/src/main.tsx').read_text()
STYLE=(ROOT/'apps/web/src/style.css').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()
RESULTS=(ROOT/'apps/web/src/widget-results.ts').read_text()
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text()

class RC220ConversionAndResults(unittest.TestCase):
 def test_administration_has_a_discoverable_fail_closed_converter_control(self):
  self.assertIn('Convertitore PDF / PowerPoint (worker isolato)',UI)
  self.assertIn("request('/admin/converter','PUT',{enabled:true})",UI)
  self.assertIn('QUORIVIO_ENABLE_CONVERTER=true',UI)
  self.assertIn("app.get('/api/admin/converter',requireAuth,requireAdmin",API)
  self.assertIn("app.put('/api/admin/converter',requireAuth,requireAdmin",API)
  self.assertIn('converterDeploymentConfigured', (ROOT/'apps/api/src/converter-admission.ts').read_text())
  self.assertIn('converterAdmissionState().then(state=>state.enabled)',API)
  self.assertIn('conversion_worker_not_configured',API)
 def test_source_sections_are_independent_and_legacy_is_supported(self):
  self.assertIn('showSourceQuestion?:boolean',DOMAIN)
  self.assertIn('showSourceTitle?:boolean',DOMAIN)
  self.assertIn('showSourceAnswers?:boolean',DOMAIN)
  self.assertIn('resultSourceTitleVisible(result)',UI)
  self.assertIn('resultSourceAnswersVisible(result)',UI)
  self.assertIn('showSourceTitle:e.target.checked',UI)
  self.assertIn('showSourceAnswers:e.target.checked',UI)
  self.assertIn('showSourceQuestion===true',UI)
  self.assertIn('showSourceTitle??result.showSourceQuestion===true',RESULTS)
 def test_question_color_and_bullets_render_without_grading_keys(self):
  self.assertIn('sourceQuestionColor',DOMAIN)
  self.assertIn('Colore testo domanda nelle statistiche',UI)
  self.assertIn('linked-source-question-prompt',UI)
  self.assertIn('linked-source-answer',UI)
  self.assertIn('font-weight:800!important',STYLE)
  self.assertNotIn('correctOptionIds',UI.split('function LinkedResultSourceQuestion(',1)[1].split('/** The exact same chart',1)[0])
 def test_mutations_are_detected(self):
  self.assertNotIn("app.put('/api/admin/converter',requireAuth,requireAdmin",API.replace("app.put('/api/admin/converter',requireAuth,requireAdmin", "app.put('/api/admin/converter',requireAuth"))
  self.assertNotIn('showSourceAnswers:e.target.checked',UI.replace('showSourceAnswers:e.target.checked','showSourceAnswers:true'))
  self.assertIn('tools.tests.test_rc220_converter_and_linked_results',WORKFLOW)

if __name__=='__main__':unittest.main()
