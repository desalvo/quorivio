"""Topic result charts: source scoped, presenter only, rehearsal explicitly unsaved."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()
CLIENT=(ROOT/'apps/web/src/main.tsx').read_text()
REHEARSAL=(ROOT/'apps/web/src/widget-results.ts').read_text()
PG=(ROOT/'tools/ci_timed_widgets_postgres.py').read_text()
class TopicLinkedResultsRC(unittest.TestCase):
 def test_domain_rejects_out_of_page_invalid_or_unsupported_links(self):
  self.assertIn("['question','timed-quiz','rating','reactions','topic-question'].includes(target.kind)",DOMAIN)
  self.assertIn("w.kind==='results-button'",CLIENT)
 def test_live_topic_count_is_scoped_to_authorized_presenter_and_widget(self):
  endpoint=API.split("app.get('/api/sessions/:id/activities/:aid/topic-widgets/:wid/stats'",1)[1].split("// Resolve the correct answer",1)[0]
  self.assertIn('requireAuth',endpoint)
  self.assertIn('owner(req.params.id,auth(req)!)',endpoint)
  self.assertIn('session_id=$1 AND activity_id=$2 AND widget_id=$3',endpoint)
  self.assertIn('count(*)::int',endpoint)
  self.assertIn("res.json({total:result.rows[0].total})",endpoint)
  self.assertNotIn('p.pseudonym',endpoint)
  self.assertIn('Cache-Control',endpoint)
  self.assertIn('next=topicQuestionRows(data.total)',CLIENT)
  self.assertNotIn('count:0}]; // Topic moderation',CLIENT)
 def test_preview_has_interaction_without_network_writes(self):
  block=CLIENT.split('function SessionRehearsal(',1)[1].split('const editorWidgetKinds',1)[0]
  self.assertIn('setTopicSubmissions(',block)
  self.assertIn('Invia domanda di prova',block)
  self.assertIn("sampleStatisticRows(linkedStatisticSource(w,widgets)!,seed,submittedAnswers",block)
  self.assertIn('setTopicSubmissions({})',block)
  self.assertNotIn("request('/join/",block)
  self.assertIn('topicQuestionRows',REHEARSAL)
 def test_ci_postgresql_acceptance_contains_linked_result(self):
  self.assertIn("'targetWidgetId':'topic1'",PG)
  self.assertIn("assert page['total']==10",PG)
if __name__=='__main__':unittest.main()
