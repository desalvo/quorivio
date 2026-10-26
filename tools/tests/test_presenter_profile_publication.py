"""Regression contracts for public profile photos and atomic profile saving."""
import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text()
WEB=(ROOT/'apps/web/src/main.tsx').read_text()
HELPER=(ROOT/'apps/api/src/profile-photo.ts').read_text()

class PresenterProfilePublicationTests(unittest.TestCase):
    def test_public_projection_is_used_for_anonymous_profile_list(self):
        route=API.split("app.get('/api/join/:code/presenter-profiles'",1)[1].split("app.get('/api/sessions/:id/presenter-profiles'",1)[0]
        self.assertIn('publicPresenterProfiles(profiles.rows,req.params.code)',route)
        self.assertIn("'Cache-Control','no-store'",route)
        self.assertNotIn('res.json(profiles.rows)',route)

    def test_public_photo_stays_scoped_to_presenter_and_public_session(self):
        route=API.split("app.get('/api/join/:code/presenters/:presenterId/photo'",1)[1].split("app.get('/api/join/:code/presenter-profiles'",1)[0]
        self.assertIn('publicSession(req.params.code)',route)
        self.assertIn('session_presenters',route)
        self.assertIn("'Cache-Control','no-store'",route)

    def test_widget_consumes_only_public_photo_url(self):
        widget=WEB.split('function PresenterProfileWidget',1)[1].split('function QuestionWidget',1)[0]
        self.assertIn('p.photo_url',widget)
        self.assertNotIn('p.profile_photo_url',widget)

    def test_private_photo_url_never_leaves_public_projection(self):
        self.assertIn('photo_url:profilePhotoId(row.profile_photo_url)',HELPER)
        self.assertNotIn('profile_photo_url:row.profile_photo_url',HELPER)
        self.assertIn('encodeURIComponent(code)',HELPER)

    def test_atomic_profile_save_updates_both_fields(self):
        route=API.split("app.patch('/api/auth/profile'",1)[1].split('// Security-sensitive helpdesk',1)[0]
        self.assertIn('FOR UPDATE',route)
        self.assertIn('BEGIN',route)
        self.assertIn('COMMIT',route)
        self.assertIn('ROLLBACK',route)
        self.assertIn('nickname=CASE WHEN',route)
        self.assertIn('display_name=CASE WHEN',route)
        self.assertIn('primary_admin_nickname_immutable',route)
        self.assertIn('nickname_already_taken',route)

    def test_legacy_presenter_patch_cannot_overwrite_photo(self):
        route=API.split("app.patch('/api/presenters/me/profile'",1)[1].split("app.get('/api/join/:code/presenters/",1)[0]
        self.assertIn('SET display_name=$2 WHERE id=$1',route)
        self.assertNotIn('SET display_name=$2,profile_photo_url',route)

    def test_one_save_button_updates_nickname_and_name(self):
        profile=WEB.split("dashboardPage==='profile'&&<section",1)[1].split("{dashboardPage!=='session'",1)[0]
        self.assertEqual(profile.count("'Salva profilo'}</button>"),1)
        self.assertNotIn('Salva nickname</button>',profile)
        self.assertNotIn('Carica profilo</button>',profile)
        self.assertIn("{nickname:nickname||null,display_name:profileName}",profile)

    def test_profile_auto_load_on_page_open(self):
        self.assertIn("dashboardPage!=='profile'||!me",WEB)
        self.assertIn("request<any>('/auth/profile').then",WEB)

if __name__=='__main__':unittest.main()
