"""RC71 conservative source contracts; live proof remains in disposable GitHub PostgreSQL job."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class RC71LiveSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = (ROOT/'apps/api/src/server.ts').read_text()
        cls.web = (ROOT/'apps/web/src/main.tsx').read_text()
        cls.domain = (ROOT/'apps/api/src/domain.ts').read_text()
        cls.ci = (ROOT/'.github/workflows/ci.yml').read_text()

    def test_page_clock_is_not_refreshed_on_revisit(self):
        self.assertIn('opened_at=COALESCE(opened_at,now())', self.api)

    def test_timer_restart_is_authenticated_and_locked(self):
        target = self.api.split("app.post('/api/sessions/:id/activities/:aid/restart-timer'",1)[1].split("app.post('/api/sessions/:id/reset-to-ready'",1)[0]
        for term in ('requireAuth','RESTART_PAGE_TIMER','FOR UPDATE','page_not_live','live_timer_not_found','UPDATE activities SET opened_at=now()','COMMIT'):
            self.assertIn(term,target)

    def test_timer_restart_erases_results_and_private_file_outbox(self):
        target=self.api.split("app.post('/api/sessions/:id/activities/:aid/restart-timer'",1)[1].split("app.post('/api/sessions/:id/reset-to-ready'",1)[0]
        for table in ('responses','widget_answers','page_reactions','page_ratings','audience_words','audience_questions','topic_widget_questions'):
            self.assertIn("'"+table+"'",target)
        self.assertIn('session_asset_file_cleanup_jobs',target)

    def test_reset_is_owner_only_with_confirmation_and_preserves_activity_structure(self):
        target=self.api.split("app.post('/api/sessions/:id/reset-to-ready'",1)[1].split("app.post('/api/sessions/:id/activities/:aid/close'",1)[0]
        for term in ('requireAuth','owner_id=$2 FOR UPDATE','RESET_SESSION_RESULTS','DELETE FROM participants','DELETE FROM live_connections','session_asset_file_cleanup_jobs','status=\'pending\',opened_at=NULL',"status='ready'",'join_secret=$3'):
            self.assertIn(term,target)
        self.assertNotIn('DELETE FROM activities',target)

    def test_two_distinct_qrs_and_live_only_controls(self):
        self.assertIn('/api/sessions/:id/presenter-qr',self.api)
        self.assertIn('requireAuth',self.api.split("app.get('/api/sessions/:id/presenter-qr'",1)[1].split('});',1)[0])
        self.assertIn('/api/sessions/${selected}/qr?format=svg',self.web)
        self.assertIn('/api/sessions/${selected}/presenter-qr',self.web)
        self.assertIn('Riporta a non avviata',self.web)

    def test_widget_appearance_preserves_bounded_reaction_size_and_custom_profile_text(self):
        self.assertIn('reactionIconSize?:number',self.domain)
        self.assertIn('w.reactionIconSize<=96',self.domain)
        self.assertIn('Testo opzionale profilo presentatore',self.web)
        self.assertIn('Dimensione icone reazioni',self.web)
        self.assertIn('presenter-profile-custom-text',self.web)

    def test_cloud_counts_are_square_bracketed(self):
        for val in ('<small> [{count}]</small>','{w.word} [{w.count}]',"chart==='cloud'?`[${r.count}]`"):
            self.assertIn(val,self.web)

    def test_file_picker_remains_mounted_while_context_menu_closes(self):
        self.assertIn('backgroundFileRef=useRef<HTMLInputElement>',self.web)
        self.assertIn('ref={backgroundFileRef}',self.web)
        self.assertIn('void onBackgroundUpload(file)',self.web)

    def test_disposable_postgres_job_is_always_on_without_publishing(self):
        self.assertIn('python3 tools/ci_rc71_lifecycle_postgres.py',self.ci)
        self.assertIn('python3 tools/verify_rc_cycle71_inventory.py',self.ci)
        self.assertNotIn('publish_latest=true',self.ci)


if __name__ == '__main__':
    unittest.main()
