"""Regression for the admin dashboard navigation's TypeScript literal union."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class DashboardNavigationTypes(unittest.TestCase):
    def test_admin_only_sections_preserve_literal_types(self):
        ui = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf-8')
        self.assertIn("useState<'workspace'|'users'|'settings'|'sso'|'mfa'|'profile'>", ui)
        self.assertIn("([['users','Gestione utenti'],['settings','Impostazioni server']] as const)", ui)
        self.assertIn('onClick={()=>setDashboardPage(key)}', ui)


if __name__ == '__main__':
    unittest.main()
