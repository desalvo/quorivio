"""Fail-closed contracts for question-scoped revisions and legacy schema migration."""
import importlib.util
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text(encoding='utf8')
MIGRATION=(ROOT/'apps/api/src/schema.sql').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
WYSIWYG=(ROOT/'apps/web/src/widget-rich-editor.tsx').read_text(encoding='utf8')
BROWSER=(ROOT/'tools/ci_browser_rich_text_offline.py').read_text(encoding='utf8')
LIVE=(ROOT/'tools/ci_independent_widget_questions_postgres.py').read_text(encoding='utf8')

class QuestionRevisionMigrationRC(unittest.TestCase):
    def test_legacy_migration_preserves_unique_and_question_id(self):
        spec=importlib.util.spec_from_file_location('q_migrate',ROOT/'tools/ci_question_schema_migration_postgres.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for clause in module.migration_script().splitlines():
            self.assertIn(clause,MIGRATION)
        self.assertIn('CREATE TEMP TABLE widget_answers', (ROOT/'tools/ci_question_schema_migration_postgres.py').read_text())
        self.assertIn('ROLLBACK;', (ROOT/'tools/ci_question_schema_migration_postgres.py').read_text())
    def test_pg_migration_requires_disposable_loopback_and_explicit_opt_in(self):
        script=(ROOT/'tools/ci_question_schema_migration_postgres.py').read_text()
        self.assertIn('QUORIVIO_CI_MULTI_QUESTION_TEST',script)
        self.assertIn("('localhost','127.0.0.1')",script)
        self.assertIn("'-v','ON_ERROR_STOP=1'",script)
    def test_workflow_executes_real_postgresql_upgrade_and_question_acceptance(self):
        self.assertIn('python3 tools/ci_question_schema_migration_postgres.py',WORKFLOW)
        self.assertIn('python3 tools/ci_independent_widget_questions_postgres.py',WORKFLOW)
        self.assertLess(WORKFLOW.index('ci_question_schema_migration_postgres.py'),WORKFLOW.index('ci_independent_widget_questions_postgres.py'))
    def test_answer_and_ranking_use_question_specific_revisions(self):
        self.assertGreaterEqual(API.count('questionRevisionAtHistory(rev.rows,questionId)'),2)
        self.assertIn('ORDER BY revision',API)
        self.assertIn('question_id=$4 AND revision=$5',API)
        self.assertIn('AND w.question_id=$4',API)
    def test_postgres_acceptance_covers_unaffected_questions_after_revision(self):
        self.assertIn("primary_retry=answer(one,'',{'option_id':'no'})",LIVE)
        self.assertIn("secondary_retry=answer(one,'sub2'",LIVE)
        self.assertIn("assert primary_retry['already_submitted']",LIVE)
        self.assertIn("assert secondary_retry['already_submitted']",LIVE)
    def test_live_editing_uses_uncontrolled_text_nodes_to_prevent_duplicate_input(self):
        self.assertIn('el.replaceChildren(fragment)',WYSIWYG)
        self.assertIn('onCompositionStart=',WYSIWYG)
        self.assertIn('onCompositionEnd=',WYSIWYG)
        self.assertIn("assert await page.locator('[data-test=json]')",BROWSER)
        self.assertIn("'Alpha beta!あ'",BROWSER)

if __name__=='__main__':unittest.main()
