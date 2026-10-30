"""Cycle 47 regression: the real PostgreSQL browser test must follow the portal."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]

class RealEditorPortalRegression(unittest.TestCase):
    def test_production_context_menu_is_portaled_outside_widgets(self):
        s=(ROOT/'apps/web/src/main.tsx').read_text()
        self.assertIn('createPortal(<div className="canvas-context-menu"',s)
        self.assertIn("aria-label={'Azioni widget '+w.kind}",s)
        self.assertIn("document.body",s)
        self.assertIn('onContextMenu=',s)

    def test_postgres_test_uses_document_scope_not_item_scope(self):
        src=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
        self.assertIn('async def edit_canvas_widget_title(page, canvas, title):',src)
        self.assertRegex(src,r"menu=page.get_by_role\('group',name='Azioni widget text',exact=True\)")
        self.assertNotIn("menu=item.get_by_role('group',name='Azioni widget text')",src)
        self.assertIn('await expect(menu).to_have_count(1)',src)
        self.assertIn('await expect(menu).to_be_visible()',src)
        self.assertIn("await menu.get_by_role('button',name='Modifica titolo').click()",src)
        self.assertIn('await expect(menu).to_have_count(0)',src)
        self.assertIn("await expect(field).to_have_attribute('contenteditable','false')",src)
        self.assertIn("await edit_canvas_widget_title(page,widgets,'Local second edit')",src)

    def test_isolated_chromium_fixture_mirrors_document_level_menu(self):
        src=(ROOT/'tools/ci_widget_title_menu.py').read_text()
        self.assertIn("const menu=document.querySelector('.canvas-context-menu')",src)
        self.assertIn("menu=page.get_by_role('group',name='Azioni widget text',exact=True)",src)
        self.assertIn('await expect(menu).to_have_count(1)',src)
        self.assertNotIn("menu=item.get_by_role('group',name='Azioni widget text')",src)
        self.assertIn('position:fixed',src)

    def test_ci_preserves_historical_integrity_and_checks_new_sources(self):
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('python3 tools/verify_rc_cycle46_inventory.py --historical',workflow)
        self.assertIn('python3 tools/verify_rc_cycle47_inventory.py --historical',workflow)
        self.assertIn('python3 tools/verify_rc_cycle48_inventory.py',workflow)
        self.assertLess(workflow.index('python3 tools/verify_rc_cycle48_inventory.py'),workflow.index('Detect credential leaks'))
        from verify_rc_cycle48_inventory import verify_source,load_inventory
        self.assertEqual(verify_source(),len(load_inventory()))

    def test_evidence_keeps_source_run_distinct_from_unverified_code(self):
        import json
        proof=json.loads((ROOT/'docs/validation/RC_CYCLE47_EDITOR_PORTAL_FAILURE_20261030.json').read_text())
        self.assertEqual(proof['source_run'],41115332748)
        self.assertEqual(proof['source_commit'],'5163e5a5b4685348810ef24067538967a1bbb536')
        self.assertTrue(proof['cycle46_included_uncommitted'])
        self.assertFalse(proof['new_changes_github_verified'])
        self.assertEqual((proof['formal_score'],proof['remaining_partial_gates']),(80.75,17))

    def test_existing_postgres_cas_and_explicit_field_resolution_retained(self):
        src=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()
        for marker in ('Conflitto di revisione','Confronta e riconcilia le modifiche',
                       'Applica riconciliazione alla bozza','Risolvi Widget pg-first · label',
                       "await choice.select_option('local')",'Local second edit',
                       'Remote results heading','Esporta layout JSON'):
            self.assertIn(marker,src)

if __name__ == '__main__': unittest.main()
