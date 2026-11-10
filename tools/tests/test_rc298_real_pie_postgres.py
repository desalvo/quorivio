"""RC298: no-mock, disposable-server preflight for real pie accessibility acceptance."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools/ci_rc298_real_pie_pg_chromium.py"
WORKFLOW = ROOT / ".github/workflows/ci.yml"


class RealPiePostgresAcceptance(unittest.TestCase):
    def test_compiles_before_network_and_database_tests(self):
        compile(SCRIPT.read_bytes(), str(SCRIPT), "exec")

    def test_disposable_postgresql_and_native_react_are_required(self):
        source = SCRIPT.read_text(encoding="utf8")
        for marker in (
            "validate_disposable_origin(BASE)",
            "QUORIVIO_CI_LOAD_TOKEN",
            "'/api/sessions'",
            "expected_design_revision",
            "await open_editor(page, TITLE_ON)",
            "await open_editor(hidden, TITLE_OFF)",
            "await call(context, 'GET', f'/api/sessions/{sid}')",
            "get_by_role('switch', name='Modifica layout Smartphone')",
            "get_by_role('list', name='Percentuali delle risposte')",
            "get_by_role('button', name='Partecipante', exact=True)",
            "data-pie-size",
            "result['pieShowPercentages'] is percentages",
            "result['targetWidgetId'] == QUESTION",
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker, source)
        for forbidden in ("page.route(", "route.fulfill(", "set_content(", "mock_fetch(", "http://example.com"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)

    def test_mandatory_ci_runs_against_real_postgresql_and_browser(self):
        ci = WORKFLOW.read_text(encoding="utf8")
        self.assertIn("name: RC298 real PostgreSQL and compiled React pie accessibility acceptance", ci)
        self.assertIn("python3 tools/ci_rc298_real_pie_pg_chromium.py", ci)
        start = ci.index("name: RC158 prepare Chromium")
        run = ci.index("name: RC298 real PostgreSQL and compiled React pie accessibility acceptance")
        manual = ci.index("name: Capture real app screenshots for the manuals")
        self.assertLess(start, run)
        self.assertLess(run, manual)
        self.assertIn("python3 -m unittest tools.tests.test_rc298_real_pie_postgres -q", ci)


if __name__ == "__main__":
    unittest.main()
