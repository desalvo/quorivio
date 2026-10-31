"""Guard the exact TypeScript drift that broke GitHub standard CI 41099464679."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]


class FrontendEditorCompileContract(unittest.TestCase):
    def test_the_editor_uses_page_design_permission_flags(self):
        main=(ROOT/'apps/web/src/main.tsx').read_text()
        contract=(ROOT/'apps/web/src/widget-style-contract.ts').read_text()
        domain=(ROOT/'apps/api/src/domain.ts').read_text()
        self.assertIn("type EditorWidgetPermissionFields = Pick<NonNullable<PageDesign['widgets']>[number], 'allowAnswerChange' | 'showEmail' | 'titleFollowPage' | 'titleUseMaster' | 'footerShowSessionTitle' | 'footerShowPageNumber'>",main)
        self.assertIn('style?:WidgetTextStyle} & EditorWidgetPermissionFields>([]));',main)
        self.assertIn("PersistedAnswerChangeFlag=Assert<Equal<StoredPageWidget['allowAnswerChange'],boolean|undefined>>",contract)
        self.assertIn("PersistedProfileEmailFlag=Assert<Equal<StoredPageWidget['showEmail'],boolean|undefined>>",contract)
        self.assertIn('allowAnswerChange?:boolean',domain)
        self.assertIn('showEmail?:boolean',domain)

    def test_both_editor_controls_match_the_stored_permission_keys(self):
        main=(ROOT/'apps/web/src/main.tsx').read_text()
        self.assertIn('w.allowAnswerChange===true',main)
        self.assertIn('w.showEmail===true',main)


if __name__ == '__main__': unittest.main()
