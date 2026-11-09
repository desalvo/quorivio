"""RC275: preserve common source renderer with truth toggle and no premature key exposure."""
import unittest
from pathlib import Path
from tools.tests.test_rc196_frontend_results_types import frontend_contract
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class LinkedSourceTruthContract(unittest.TestCase):
 def test_truth_toggle_flows_to_shared_source_renderer(self):
  chart=UI.split('function LinkedResultChart(',1)[1].split('function ',1)[0]
  self.assertIn('const [truthVisible,setTruthVisible]=useState(widget.showCorrectAnswers===true)',chart)
  self.assertIn('const viewWidget={...widget,showCorrectAnswers:hasKey&&truthVisible}',chart)
  self.assertIn('<LinkedResultSourceQuestion result={viewWidget} source={source}/>',chart)
  self.assertIn('setTruthVisible(v=>!v)',chart)
  self.assertIn('aria-pressed={truthVisible}',chart)
  self.assertIn('resultHasAnswerKey(source,widget.targetQuestionId',chart)
  self.assertNotIn('<LinkedResultSourceQuestion result={widget} source={source}/>',chart)
 def test_rejects_loss_of_truth_bridge(self):
  self.assertFalse(frontend_contract(UI.replace('<LinkedResultSourceQuestion result={viewWidget} source={source}/>','<LinkedResultSourceQuestion result={widget} source={source}/>',1)))
  self.assertFalse(frontend_contract(UI.replace('const viewWidget={...widget,showCorrectAnswers:hasKey&&truthVisible}','const viewWidget=widget',1)))
 def test_same_chart_live_and_rehearsal(self):
  self.assertIn('sourceWidgets} rows={rows} emptyLabel="live"',UI)
  self.assertIn('sourceWidgets} rows={rows} emptyLabel="simulazione"',UI)
 def test_public_question_renderer_does_not_embed_private_key(self):
  source=UI.split('function LinkedResultSourceQuestion(',1)[1].split('/** The exact same chart',1)[0]
  self.assertNotIn('correctOptionIds',source)
 def test_ci_runs_compat_contract_before_build(self):
  marker='RC275 linked-result source and truth toggle regression before npm'
  self.assertIn(marker,CI)
  self.assertLess(CI.index(marker),CI.index('run: npm ci --ignore-scripts'))
  self.assertIn('python3 -m unittest tools.tests.test_rc275_source_renderer_contract',CI)
if __name__=='__main__':unittest.main()
