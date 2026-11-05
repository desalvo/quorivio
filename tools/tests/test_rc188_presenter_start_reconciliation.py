"""RC188 fail-closed regression for RC92 startup under RC185 independent routing.

Tests both real routing semantics and transactional startup contracts, never the
outdated assumption that the first activity is projected on both screens.
"""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]
SERVER = (ROOT / 'apps/api/src/server.ts').read_text(encoding='utf8')
ROUTING = (ROOT / 'apps/api/src/presentation-routing.ts').read_text(encoding='utf8')
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
START = SERVER.split("app.post('/api/sessions/:id/presentation/ensure-first-page'", 1)[1].split(
    "app.post('/api/sessions/:id/activities/:aid/open'", 1)[0]


def startup_contract(route: str) -> bool:
    return all(token in route for token in (
        "await cx.query('BEGIN')",
        'FOR UPDATE',
        'if(session.current_activity_id)',
        'SELECT id,page_design FROM activities WHERE session_id=$1 ORDER BY position,id',
        'const presenter=firstPresenterPage(pages)',
        'const audience=audienceForPresenter(pages,presenter)',
        "UPDATE activities SET status='closed' WHERE session_id=$1 AND status='open'",
        "UPDATE activities SET status='open',opened_at=COALESCE(opened_at,now()) WHERE id=$1",
        'current_activity_id=$1,presenter_activity_id=$3',
        "await cx.query('COMMIT');begun=false;await broadcast(req.params.id)",
    )) and 'ORDER BY position,id LIMIT 1' not in route


class RC188PresenterStart(unittest.TestCase):
    def test_first_page_uses_ordered_pages_and_visibility_policy(self):
        self.assertTrue(startup_contract(START))
        self.assertIn('return pages.filter(p=>p.page_design?.presenterHidden!==true)', ROUTING)
        self.assertIn('return presenterPages(pages)[0]||null', ROUTING)
        self.assertIn('const id=presenter.page_design?.audiencePageId||presenter.id', ROUTING)
        self.assertIn('return pages.find(p=>p.id===id)||null', ROUTING)

    def test_old_limit_one_or_missing_atomic_transition_is_rejected(self):
        old = START.replace(
            'SELECT id,page_design FROM activities WHERE session_id=$1 ORDER BY position,id',
            'SELECT id,page_design FROM activities WHERE session_id=$1 ORDER BY position,id LIMIT 1',
        )
        self.assertNotEqual(old, START)
        self.assertFalse(startup_contract(old))
        old = START.replace('const presenter=firstPresenterPage(pages)', 'const presenter=pages[0]')
        self.assertNotEqual(old, START)
        self.assertFalse(startup_contract(old))
        old = START.replace('current_activity_id=$1,presenter_activity_id=$3', 'current_activity_id=$1')
        self.assertNotEqual(old, START)
        self.assertFalse(startup_contract(old))

    def test_existing_projection_is_never_restarted(self):
        prior = START.index('if(session.current_activity_id)')
        close = START.index("UPDATE activities SET status='closed'")
        self.assertLess(prior, close)
        self.assertIn('changed:false', START[prior:close])
        self.assertIn('const aid=audience.id', START)
        self.assertIn("res.status(409).json({error:'audience_page_missing'})", START)

    def test_behavioral_routing_uses_real_typescript_policy(self):
        # No installation or mocks: verify exported routing on Node's native
        # TS stripper. Invalid cross-session target cannot be selected.
        js = """import {firstPresenterPage,audienceForPresenter} from './apps/api/src/presentation-routing.ts';
        import assert from 'node:assert/strict';
        const q={id:'q',page_design:{presenterHidden:true}};
        const chart={id:'chart',page_design:{audiencePageId:'q'}};
        const outro={id:'outro',page_design:{}};
        assert.equal(firstPresenterPage([q,chart,outro]),chart);
        assert.equal(audienceForPresenter([q,chart,outro],chart),q);
        assert.equal(firstPresenterPage([q]),null);
        assert.equal(audienceForPresenter([chart],chart),null);
        assert.equal(audienceForPresenter([q,outro],outro),outro);
        """
        subprocess.run(['node', '--experimental-strip-types', '--input-type=module', '-e', js],
                       cwd=ROOT, check=True, capture_output=True, text=True, timeout=15)

    def test_preflight_runs_before_historical_rc92_and_npm(self):
        early = WORKFLOW.index('test_rc188_presenter_start_reconciliation')
        old = WORKFLOW.index('test_rc92_presenter_stage')
        install = WORKFLOW.index('name: Install reproducibly')
        self.assertLess(early, old)
        self.assertLess(early, install)


if __name__ == '__main__':
    unittest.main()
