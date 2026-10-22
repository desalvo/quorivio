import pathlib
import unittest
ROOT = pathlib.Path(__file__).resolve().parents[2]

class FieldValidationContracts(unittest.TestCase):
    def test_primary_admin_protected_and_nickname_supported(self):
        api = (ROOT/'apps/api/src/server.ts').read_text()
        schema = (ROOT/'apps/api/src/schema.sql').read_text()
        self.assertIn('primary_admin_immutable', api)
        self.assertIn("nickname='admin'", api)
        self.assertIn('lower(nickname)=$1', api)
        self.assertIn('users_nickname_unique', schema)
        self.assertIn('users_one_primary_admin', schema)

    def test_smtps_configuration_protected(self):
        api = (ROOT/'apps/api/src/server.ts').read_text()
        store = (ROOT/'apps/api/src/smtp-store.ts').read_text()
        self.assertIn("app.put('/api/admin/smtp',requireAuth,requireAdmin", api)
        self.assertIn('aes-256-gcm', store)
        self.assertIn('password_configured', store)
        self.assertIn('smtp_required_before_mfa', api)
        self.assertIn("res.setHeader('Cache-Control','no-store, private')", api)

    def test_schedule_multi_dates(self):
        api = (ROOT/'apps/api/src/server.ts').read_text()
        schema = (ROOT/'apps/api/src/schema.sql').read_text()
        self.assertIn('session_schedule_dates', schema)
        self.assertIn("app.put('/api/sessions/:id/schedule'", api)
        self.assertIn('new Set(dates).size', api)

    def test_arm64_clamav_and_web_sections(self):
        self.assertIn('clamav/clamav:stable-debian', (ROOT/'compose.yaml').read_text())
        ui = (ROOT/'apps/web/src/main.tsx').read_text()
        self.assertIn("dashboardPage==='users'", ui)
        self.assertIn("dashboardPage==='settings'", ui)
        self.assertIn('Approvato', ui)
        self.assertIn('otpauth_url', ui)

if __name__ == '__main__': unittest.main()
