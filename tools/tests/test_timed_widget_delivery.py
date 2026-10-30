"""CI safeguards for timed widget and topic question acceptance."""
import os
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
SOURCE=(ROOT/'tools/ci_timed_widgets_postgres.py').read_text()
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text()
UI=(ROOT/'apps/web/src/main.tsx').read_text()

class TimedWidgetDelivery(unittest.TestCase):
    def test_ci_runs_postgres_and_is_not_optional(self):
        self.assertIn('PostgreSQL timed-widget fairness, retry and topic concurrency acceptance',WORKFLOW)
        self.assertIn('run: python3 tools/ci_timed_widgets_postgres.py',WORKFLOW)
        self.assertIn("QUORIVIO_CI_TIMED_TEST: '1'",WORKFLOW)
    def test_acceptance_requires_explicit_loopback_staging(self):
        self.assertIn("address.hostname not in ('127.0.0.1','localhost')",SOURCE)
        self.assertIn("QUORIVIO_CI_TIMED_TEST",SOURCE)
        self.assertIn('len(TOKEN) < 32',SOURCE)
        self.assertIn('Refusing to rewrite ranking times outside disposable CI database',SOURCE)
    def test_actual_database_equal_time_rank_fixture(self):
        self.assertIn('UPDATE widget_answers SET elapsed_ms=CASE',SOURCE)
        self.assertIn("[r['rank'] for r in ranks]==[1,1,3]",SOURCE)
    def test_full_concurrency_more_than_pool(self):
        self.assertGreaterEqual(SOURCE.count('max_workers=12'),2)
        self.assertIn('outcomes.count(201)==10 and outcomes.count(429)==2',SOURCE)
        self.assertIn("sum(not x['already_submitted'] for x in submissions)==1",SOURCE)
    def test_ui_tied_ranks_are_not_react_key_collisions(self):
        self.assertNotIn('key={r.rank}',UI)
        self.assertIn('value={Number(r.rank)}',UI)
        self.assertIn('aria-label="Posizioni a pari merito"',UI)
    def test_widget_ui_rejects_double_submit(self):
        start=UI.index('function QuestionWidget(')
        end=UI.index('function SessionRehearsal(',start)
        content=UI[start:end]
        self.assertIn('if(busy||(submitted&&widget.allowAnswerChange!==true))return;',content)
        self.assertIn('aria-busy={busy}',content)
        self.assertIn('role="status" aria-live="polite"',content)

if __name__=='__main__': unittest.main()
