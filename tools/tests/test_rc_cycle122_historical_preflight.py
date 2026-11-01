"""RC122: historical CI tests verify semantics, not fixed line adjacency/offset."""
import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def postgres_acceptance_commands(workflow: str) -> list[str]:
    match=re.search(r'(?ms)^      - name: Chromium editor PostgreSQL persistence and conflict acceptance \(opt-in\)\n(.*?)(?=^      - name:|\Z)',workflow)
    if match is None:
        raise ValueError('missing real Chromium/PostgreSQL acceptance')
    return re.findall(r'(?m)^          python3 (tools/ci_[a-z0-9_]+\.py)\s*$',match.group(1))


def check_order(workflow: str) -> bool:
    commands=postgres_acceptance_commands(workflow)
    required=['tools/ci_widget_title_menu.py','tools/ci_browser_editor_conflict_visibility.py','tools/ci_browser_editor_postgres.py']
    return all(cmd in commands for cmd in required) and [commands.index(cmd) for cmd in required] == sorted(commands.index(cmd) for cmd in required)


def check_score(handoff: str, score: float) -> bool:
    return f'{score:.2f}%' in handoff.split('\n---\n',1)[0]


class RC122HistoricalPreflight(unittest.TestCase):
    def test_workflow_retains_preflights_before_real_database_browser(self):
        self.assertTrue(check_order((ROOT/'.github/workflows/ci.yml').read_text()))

    def test_preflights_can_be_inserted_without_rejecting_valid_workflow(self):
        flow=(ROOT/'.github/workflows/ci.yml').read_text()
        old='          python3 tools/ci_browser_editor_conflict_visibility.py\n'
        self.assertIn(old,flow)
        self.assertTrue(check_order(flow.replace(old,old+'          python3 tools/ci_example_extra_guard.py\n',1)))

    def test_missing_or_misordered_real_browser_fails_closed(self):
        flow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertFalse(check_order(flow.replace('          python3 tools/ci_browser_editor_postgres.py','          python3 tools/ci_fake_browser.py',1)))
        self.assertFalse(check_order(flow.replace('          python3 tools/ci_widget_title_menu.py\n','',1)))
        old='          python3 tools/ci_widget_title_menu.py\n          python3 tools/ci_browser_editor_conflict_visibility.py\n'
        new='          python3 tools/ci_browser_editor_conflict_visibility.py\n          python3 tools/ci_widget_title_menu.py\n'
        self.assertIn(old,flow)
        self.assertFalse(check_order(flow.replace(old,new,1)))

    def test_english_handoff_uses_current_ledger_score_not_position(self):
        from rc_gate_audit import audit
        handoff=(ROOT/'docs/COMPLETION_HANDOFF.md').read_text()
        score=audit()['score']
        self.assertTrue(check_score(handoff,score))
        # Simulate a longer status paragraph without changing the score.
        self.assertTrue(check_score(handoff.replace('**Certified completion:**',('Additional verified context. '*150)+'**Certified completion:**',1),score))
        self.assertFalse(check_score(handoff.split('\n---\n',1)[0].replace(f'{score:.2f}%', 'unknown')+'\n---\n'+handoff,score))

    def test_historical_probes_keep_order_and_dynamic_score(self):
        old_title=(ROOT/'tools/tests/test_ci_browser_editor_readonly_title.py').read_text()
        old_heartbeat=(ROOT/'tools/tests/test_live_heartbeat_cycle56.py').read_text()
        self.assertIn("self.assertLess(commands.index('tools/ci_widget_title_menu.py')",old_title)
        self.assertIn("audit()['score']",old_heartbeat)
        self.assertNotIn("d[:1300]",old_heartbeat)

if __name__=='__main__':unittest.main()
