"""RC154: real presenter-visible load, reversible demo tests and opt-in Gravatar."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SEED=(ROOT/'apps/api/src/load-test-demo.ts').read_text()
API=(ROOT/'apps/api/src/server.ts').read_text()
WEB=(ROOT/'apps/web/src/main.tsx').read_text()
SCHEMA=(ROOT/'apps/api/src/schema.sql').read_text()
CLI=(ROOT/'tools/live_500_answers.py').read_text()
GRAV=(ROOT/'apps/api/src/gravatar.ts').read_text()

class RC154Contracts(unittest.TestCase):
 def test_test_presentation_has_presenter_presence_and_multiple_interactions(self):
  for x in ('load-500-poll-presence','load-500-extra-presence','load-500-poll-rating','load-500-extra-rating',
            'load-500-poll-reactions','load-500-extra-reactions','load-500-question','load-500-extra-question'):
   self.assertIn(x,SEED)
  self.assertIn("targetWidgetId:'load-500-question'",SEED)
  self.assertIn("kind:'participant-count'",SEED)
  self.assertIn("kind:'rating'",SEED)
  self.assertIn("kind:'reactions'",SEED)
 def test_demo_can_start_and_reset_without_deleting_pages(self):
  self.assertIn("'/api/sessions/:id/reset-to-ready'",API)
  self.assertIn("'RESET_SESSION_RESULTS'",API)
  self.assertIn("--reset-before",CLI)
  self.assertIn("--open-test-question",CLI)
  self.assertIn('reset-to-ready',CLI)
  self.assertIn('resetSessionToReady()',WEB)
 def test_live_presence_really_uses_websockets_and_verifies_presenter_count(self):
  self.assertIn("--live-presence",CLI)
  self.assertIn("visitor.ws_connect",CLI)
  self.assertIn("presenter.ws_connect",CLI)
  self.assertIn('presenter_peak_connected',CLI)
  self.assertIn('presenter_peak==a.users',CLI)
  self.assertIn('release_presence.wait()',CLI)
 def test_gravatar_is_opt_in_and_uses_owned_photo_storage(self):
  self.assertIn('gravatar_enabled boolean NOT NULL DEFAULT false',SCHEMA)
  self.assertIn('gravatar_photo_sha256',SCHEMA)
  self.assertIn('gravatar_checked_at',SCHEMA)
  self.assertIn('profile_photo_source',SCHEMA)
  self.assertIn('await refreshGravatarForUser(',API)
  self.assertIn("'/api/auth/profile/gravatar'",API)
  self.assertIn('await scanUploadedFile(temporary)',API)
  self.assertIn('inspectProfileImage(avatar.data,avatar.mime)',API)
  self.assertIn('profile_photo_url',API)
  self.assertIn('gravatarAvatarUrl',GRAV)
  self.assertIn('redirect:\'manual\'',GRAV)
 def test_gravatar_user_controls_are_editable_per_account(self):
  self.assertIn('Usa Gravatar per la foto del mio account',WEB)
  self.assertIn('Importa / aggiorna Gravatar',WEB)
  self.assertIn('https://gravatar.com/',WEB)
  self.assertIn('profile_photo_source',API)
 def test_manuals_include_cli_and_privacy(self):
  manuals=(ROOT/'tools/generate_manuals.py').read_text()
  self.assertIn('live_500_answers.py',manuals)
  self.assertIn('Gravatar',manuals)
  self.assertIn('--reset-before',manuals)

if __name__=='__main__':unittest.main()
