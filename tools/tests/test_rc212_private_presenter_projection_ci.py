"""RC212: producer may compute a presenter ordinal but must never export its ID."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
API = (ROOT / 'apps/api/src/server.ts').read_text(encoding='utf8')
RC185 = (ROOT / 'tools/tests/test_rc185_cross_page_projection.py').read_text(encoding='utf8')
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')

def check_private_presenter_projection(source: str) -> None:
    start = source.index('function participantSnapshot(')
    end = source.index('\nconst webRoot=', start)
    function = source[start:end]
    if 'const presenterId=data.session.presenter_activity_id||data.session.current_activity_id' not in function:
        raise AssertionError('presenter page source is missing')
    if 'presenter_page_number:presenterNumber' not in function:
        raise AssertionError('public presenter page ordinal is missing')
    public = function.split('return {session:', 1)[1]
    if 'presenter_activity_id' in public or 'presenterId' in public:
        raise AssertionError('private presenter activity leaked to participants')
    if 'published?[publicActivity(published)]:[]' not in public:
        raise AssertionError('public page scope has expanded')
    if 'current_activity_id:published?aid:null' not in public:
        raise AssertionError('unpublished page could be exposed')

class RC212PrivatePresenterProjectionCI(unittest.TestCase):
    def test_public_projection_is_private_and_has_shared_page_number(self):
        check_private_presenter_projection(API)
        self.assertIn("API.index('\\nconst webRoot=', start)", RC185)
        self.assertIn("self.assertNotIn('presenter_activity_id', public_response)", RC185)

    def test_negative_mutations_reject_presenter_id_leak_or_public_page_expansion(self):
        mutations = (
            API.replace('presenter_page_number:presenterNumber}',
                        'presenter_page_number:presenterNumber,presenter_activity_id:presenterId}', 1),
            API.replace('presenter_page_number:presenterNumber}',
                        'presenter_page_number:presenterNumber,presenterId}', 1),
            API.replace('published?[publicActivity(published)]:[]',
                        'data.activities', 1),
            API.replace('current_activity_id:published?aid:null',
                        'current_activity_id:presenterId', 1),
        )
        for broken in mutations:
            self.assertNotEqual(API, broken)
            with self.assertRaises(AssertionError):
                check_private_presenter_projection(broken)

    def test_registered_early_ci_contract(self):
        self.assertIn('tools.tests.test_rc212_private_presenter_projection_ci', CI)
        self.assertIn('apps/api/test/rc212-participant-snapshot.test.ts', CI)
        self.assertIn('tools.tests.test_rc185_cross_page_projection', CI)

if __name__ == '__main__':
    unittest.main()
