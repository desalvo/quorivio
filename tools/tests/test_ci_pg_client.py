"""Regression: CI backup/restore must use a PostgreSQL 18 client."""
import pathlib
import unittest

WORKFLOW = pathlib.Path(__file__).resolve().parents[2] / '.github' / 'workflows' / 'ci.yml'

class PostgreSQLClientCITests(unittest.TestCase):
    def test_ci_pins_pg18_client_and_preflights_both_utilities(self):
        content = WORKFLOW.read_text(encoding='utf-8')
        self.assertIn('postgres:18-alpine', content)
        self.assertIn('postgresql-client-18', content)
        self.assertIn('pg_dump --version', content)
        self.assertIn('pg_restore --version', content)
        self.assertIn('/usr/lib/postgresql/18/bin', content)
        self.assertNotIn('install -y -qq postgresql-client\n', content)

if __name__ == '__main__':
    unittest.main()
