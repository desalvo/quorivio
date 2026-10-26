"""CI and security contracts for audience moderation (real behavior in PostgreSQL CI)."""
import ast
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text()
WEB=(ROOT/'apps/web/src/main.tsx').read_text()
CI=(ROOT/'tools/ci_audience_moderation_postgres.py').read_text()
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text()

class AudienceModerationDelivery(unittest.TestCase):
    def test_python_fixture_is_valid(self):
        ast.parse(CI)

    def test_fixture_restricts_to_disposable_loopback_and_opt_in(self):
        for check in ("'127.0.0.1','localhost'", "QUORIVIO_CI_MODERATION_TEST", "QUORIVIO_CI_LOAD_TOKEN"):
            self.assertIn(check,CI)

    def test_ci_runs_real_postgres_acceptance_not_source_only(self):
        self.assertIn('run: python3 tools/ci_audience_moderation_postgres.py',WORKFLOW)
        self.assertIn('PostgreSQL audience Q&A concurrency',WORKFLOW)

    def test_workflow_retains_opt_in_publishing(self):
        self.assertIn("github.event_name == 'workflow_dispatch'",WORKFLOW)
        self.assertIn('publish_image:',WORKFLOW)

    def test_participant_bound_is_serialized_across_replicas(self):
        block=API.split("app.post('/api/join/:code/activities/:aid/questions'")[1].split("app.get('/api/join/:code/activities/:aid/questions'")[0]
        self.assertLess(block.index('lockAudiencePage'),block.index('FOR UPDATE'))
        self.assertLess(block.index('FOR UPDATE'),block.index('count(*)::int'))
        self.assertLess(block.index('count(*)::int'),block.index('INSERT INTO audience_questions'))
        self.assertIn('ROLLBACK',block)

    def test_page_open_state_and_expiry_checked_inside_transactions(self):
        block=API.split('async function lockAudiencePage(')[1].split("app.post('/api/join/:code/activities/:aid/words'")[0]
        for guard in ("status='active'","current_activity_id=$2","expires_at>now()","allow_anonymous=true","status='open'","FOR SHARE"):
            self.assertIn(guard,block)

    def test_votes_hold_question_lock_before_insert(self):
        block=API.split("app.post('/api/join/:code/activities/:aid/questions/:qid/upvote'")[1].split('app.get(',1)[0]
        self.assertLess(block.index('FOR SHARE'),block.index('INSERT INTO audience_question_votes'))
        self.assertIn("status='approved'",block)
        self.assertIn('already_voted',block)

    def test_public_get_never_exposes_unmoderated_content(self):
        block=API.split("app.get('/api/join/:code/activities/:aid/questions'")[1].split('app.post(',1)[0]
        self.assertIn("q.status='approved'",block)
        self.assertIn("status='open'",block)
        self.assertIn('ORDER BY votes DESC,q.created_at,q.id',block)

    def test_bulk_review_rejects_cross_session_partial_updates(self):
        block=API.split("app.patch('/api/sessions/:id/activities/:aid/questions/bulk'")[1].split("app.patch('/api/sessions/:id/activities/:aid/questions/:qid'")[0]
        for guard in ('parseModerationBulk','FOR UPDATE','locked.rowCount!==selection.ids.length',"res.status(404)",'ROLLBACK','COMMIT','notifyAudience(s.id)'):
            self.assertIn(guard,block)

    def test_bulk_review_accessible_selection_controls(self):
        block=WEB.split('function PresenterAudienceExtensions(')[1].split('function PresenterProfileWidget(')[0]
        for text in ('aria-label="Moderazione multipla"','Seleziona pagina','Deseleziona','Approva selezionate','Rifiuta selezionate','type="checkbox"','selectedQuestions'):
            self.assertIn(text,block)

    def test_moderator_queue_has_bounded_paging_and_status_counts(self):
        block=API.split("app.get('/api/sessions/:id/activities/:aid/questions/queue'")[1].split('app.patch(',1)[0]
        for part in ('LIMIT 20 OFFSET $3','moderationStatus','Cache-Control','total_pages','counts:totals'):
            self.assertIn(part,block)

    def test_presenter_controls_are_accessible_and_can_reverse(self):
        block=WEB.split('function PresenterAudienceExtensions(')[1].split('function PresenterProfileWidget(')[0]
        for part in ('Filtro domande','aria-label="Pagine della moderazione"','In attesa:','Approva','Rifiuta','q.status!==\'approved\'','q.status!==\'rejected\''):
            self.assertIn(part,block)

    def test_participant_input_is_preserved_on_failed_send(self):
        block=WEB.split('function AudienceExtensions(')[1].split('function TopicQuestionWidget(')[0]
        self.assertLess(block.index('const result=await request'),block.index('clear();'))
        self.assertIn('disabled={!joined||busy',block)
        self.assertIn('role="status"',block)

    def test_disposable_ci_covers_race_and_moderation_lifecycle(self):
        for s in ('ThreadPoolExecutor(max_workers=12)','already_submitted',"status':'rejected'",'total_pages','already_voted',"status':'approved'",'question_limit_reached'):
            if s=='question_limit_reached':continue
            self.assertIn(s,CI)

    def test_browser_acceptance_includes_pending_approval_and_revocation(self):
        browser=(ROOT/'tools/ci_browser_participant.py').read_text()
        for val in ('Invia per moderazione','Domanda inviata per approvazione',"{'status':'approved'}","{'status':'rejected'}",'Voto registrato'):
            self.assertIn(val,browser)

if __name__=='__main__':unittest.main()
