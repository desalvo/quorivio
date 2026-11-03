"""RC151: strict TypeScript guard mutations must actually edit the current Pick.

RC150 added fields after resultsOnly; RC115's historical hardcoded suffix
became a no-op and failed the negative acceptance test despite valid types.
"""
from pathlib import Path
import unittest

from tools.tests.test_rc_cycle115_typescript_strict import (
    editor_types, editor_permission_fields, remove_editor_permission,
)

ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class RC151StrictTypesMutation(unittest.TestCase):
    def test_extensible_permission_union_is_strictly_checked(self):
        self.assertTrue(editor_types(MAIN,DOMAIN))
        self.assertTrue({'showTitle','autoFit','position','resultTopCount'}.issubset(editor_permission_fields(MAIN)))

    def test_each_required_field_removal_mutates_code_and_fails(self):
        for field in ('showTitle','autoFit'):
            mutant=remove_editor_permission(MAIN,field)
            self.assertNotEqual(mutant,MAIN)
            self.assertNotIn(field,editor_permission_fields(mutant))
            self.assertFalse(editor_types(mutant,DOMAIN))

    def test_appending_other_fields_does_not_break_negative_mutation(self):
        extended=MAIN.replace(" | 'resultTopCount'>;", " | 'resultTopCount' | 'futurePermission'>;",1)
        self.assertNotEqual(extended,MAIN)
        self.assertTrue(editor_types(extended,DOMAIN))
        mutant=remove_editor_permission(extended,'autoFit')
        self.assertNotEqual(mutant,extended)
        self.assertFalse(editor_types(mutant,DOMAIN))

    def test_invalid_pick_and_shared_domain_are_rejected(self):
        self.assertFalse(editor_types(MAIN.replace('type EditorWidgetPermissionFields = Pick<', 'type EditorWidgetPermissionFields = any /* Pick<', 1),DOMAIN))
        self.assertFalse(editor_types(MAIN,DOMAIN.replace('autoFit?:boolean','autoFit?:string',1)))

    def test_ci_runs_historical_and_new_current_inventory(self):
        self.assertIn('tools.tests.test_rc_cycle115_typescript_strict',CI)
        self.assertIn('tools.tests.test_rc151_strict_types_mutation',CI)
        self.assertIn('tools/verify_rc_cycle150_inventory.py --historical',CI)
        self.assertIn('tools/verify_rc_cycle151_inventory.py',CI)
        self.assertLess(CI.index('test_rc151_strict_types_mutation'),CI.index('npm install --ignore-scripts'))
        self.assertIn('tsc --noEmit && vite build',(ROOT/'apps/web/package.json').read_text(encoding='utf8'))

if __name__=='__main__':
    unittest.main()
