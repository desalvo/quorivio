import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]
class Phase2UiRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.web = (ROOT/'apps/web/src/main.tsx').read_text()
        cls.api = (ROOT/'apps/api/src/server.ts').read_text()
        cls.smtp = (ROOT/'apps/api/src/smtp.ts').read_text()
    def test_nickname_login_uses_text_input(self):
        self.assertIn('type={registerMode?"email":"text"}', self.web)
        self.assertIn('lower(nickname)=$1', self.api)
    def test_primary_admin_nickname_protected(self):
        self.assertIn('is_primary_admin=false RETURNING id,nickname', self.api)
        self.assertIn('disabled={!!u.is_primary_admin}', self.web)
    def test_smtp_requires_tls_upgrade(self):
        self.assertIn('requireTLS:!c.secure',self.smtp)
        self.assertIn('senderName',self.smtp)
        self.assertIn('starttls',self.web)
    def test_user_and_session_pagination(self):
        for value in ['userPageSize','sessionPageSize','userSearch','sessionSearch']:
            self.assertIn(value,self.web)
    def test_cookie_notice_and_password_confirmation(self):
        self.assertIn('q_cookie_notice=ack',self.web)
        self.assertIn('newPassword!==confirmNewPassword',self.web)
