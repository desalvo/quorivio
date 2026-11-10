"""RC299 release preflight: real audience and presenter end-to-end, no mocks."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'tools/ci_rc299_real_votes_pg_chromium.py'
WORKFLOW=ROOT/'.github/workflows/ci.yml'
MAIN=ROOT/'apps/web/src/main.tsx'

class RealVotesPieAcceptance(unittest.TestCase):
    def test_python_compiles_and_real_vote_submission_is_required(self):
        code=SCRIPT.read_text(encoding='utf8')
        compile(code,str(SCRIPT),'exec')
        for marker in (
            'validate_disposable_origin(BASE)',
            'await persisted_case(admin,TITLE_ON,True)',
            "await question.get_by_role('radio'",
            "'Invia risposta'", "'Risposta registrata'",
            "'/screen/'+sid", "data['responses']==3",
            "get_by_role('list',name='Percentuali delle risposte')",
            "f\"{OPTIONS[0]['label']}: 2 risposte, 67%\"",
            "f\"{OPTIONS[1]['label']}: 1 risposta, 33%\"",
            'RC299 PASS: private aggregates remain inaccessible',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker,code)
        for forbidden in ('page.route(', 'route.fulfill(', 'set_content(', 'mock_fetch(', 'sampleStatisticRows('):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden,code)

    def test_ci_requires_live_browser_after_postgres_before_manuals(self):
        yaml=WORKFLOW.read_text(encoding='utf8')
        self.assertIn('python3 -m unittest tools.tests.test_rc299_real_votes_pg -q',yaml)
        self.assertIn('name: RC299 real participant votes to live presenter PostgreSQL pie',yaml)
        self.assertIn('python3 tools/ci_rc299_real_votes_pg_chromium.py',yaml)
        self.assertLess(yaml.index('name: RC298 real PostgreSQL and compiled React'),
                        yaml.index('name: RC299 real participant votes'))
        self.assertLess(yaml.index('name: RC299 real participant votes'),
                        yaml.index('name: Capture real app screenshots for the manuals'))

    def test_svg_tooltips_announce_real_source_text_counts_and_optional_percentages(self):
        ui=MAIN.read_text(encoding='utf8')
        self.assertIn("data[r.index-1]?.label||('Opzione '+r.index)",ui)
        self.assertIn("r.count===1?'risposta':'risposte'",ui)
        self.assertIn("widget.pieShowPercentages===true?",ui)
        self.assertIn("resultPiePercent(r.share)",ui)

if __name__=='__main__':
    unittest.main()
