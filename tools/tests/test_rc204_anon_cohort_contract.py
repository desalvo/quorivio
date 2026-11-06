"""RC204 fail-closed pre-install acceptance: anonymous statistics need independent cohorts.

This early check runs without npm/pptx/Pillow; executable Node tests run later
with the normal API test suite. Prevents reverting the privacy threshold silently.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXPORT = (ROOT / 'apps/api/src/statistics-export.ts').read_text(encoding='utf8')
SERVER = (ROOT / 'apps/api/src/server.ts').read_text(encoding='utf8')
WEB = (ROOT / 'apps/web/src/main.tsx').read_text(encoding='utf8')
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')


def validate_export(source: str) -> None:
    required = (
        'ANONYMOUS_MIN_PARTICIPANTS=5',
        'const participant=String(x.participantId||\'\').trim()',
        'if(!participant)continue',
        'participants:new Set([participant])',
        'found.participants.add(participant)',
        '.filter(x=>x.participants.size>=ANONYMOUS_MIN_PARTICIPANTS)',
        'String(x.participants.size)',
        'x.isFreeText?omitted:x.answer',
    )
    for fragment in required:
        if fragment not in source:
            raise AssertionError('RC204 anonymity protection missing: ' + fragment)


class RC204AnonymousCohortContract(unittest.TestCase):
    def test_deidentification_and_default_api_permissions(self):
        validate_export(EXPORT)
        self.assertIn("const anonymize=requested!=='0'", SERVER)
        self.assertIn('if(!anonymize&&session.owner_id!==auth(req))', SERVER)
        self.assertIn('`quorivio-statistiche-anonime.${format}`', SERVER)
        self.assertIn('X-Content-Type-Options', SERVER)
        self.assertIn('almeno 5 partecipanti distinti', WEB)

    def test_reverting_threshold_fails_before_npm(self):
        with self.assertRaises(AssertionError):
            validate_export(EXPORT.replace('ANONYMOUS_MIN_PARTICIPANTS=5', 'ANONYMOUS_MIN_PARTICIPANTS=1'))

    def test_reverting_unique_count_fails_before_npm(self):
        with self.assertRaises(AssertionError):
            validate_export(EXPORT.replace('String(x.participants.size)', 'String(x.count)'))

    def test_ci_runs_guard_and_real_node_behavior(self):
        self.assertIn('tools.tests.test_rc204_anon_cohort_contract', CI)
        self.assertTrue((ROOT / 'apps/api/test/rc204-anonymized-cohorts.test.ts').is_file())
        self.assertIn('run: npm test', CI)


if __name__ == '__main__':
    unittest.main()
