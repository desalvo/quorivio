"""RC163: protect the TypeScript shape of the editor and narrowed widget rail.

The errors were exposed by the RC162 GitHub tsc build. The checks run before npm
so a missing field or impossible branch cannot waste long CI stages again.
"""
from __future__ import annotations
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def has_editor_history_qr_field(ui: str, domain: str) -> bool:
    marker='type EditorWidgetPermissionFields = Pick<'
    if marker not in ui: return False
    declaration=ui.split(marker,1)[1].split('>;',1)[0]
    return "'showQrUrl'" in declaration and 'showQrUrl?:boolean' in domain


def has_reachable_widget_icon_branch(ui: str) -> bool:
    marker="editorWidgetKinds.map(k=>k==='shape'||k==='line'?<GraphicInsertTool"
    if marker not in ui: return False
    block=ui.split(marker,1)[1].split('</EditorIconTool>',1)
    if len(block)!=2: return False
    icon=block[0].split(':<EditorIconTool',1)
    if len(icon)!=2:return False
    non_graphic=icon[1]
    return ("fillNone:true,shapeType:'rectangle'" in non_graphic
        and "k==='shape'" not in non_graphic
        and "k==='line'" not in non_graphic
        and 'GraphicInsertTool' in ui
        and 'graphicStyle(k,preset,options)' in ui)


class RC163FrontendTypescriptBuild(unittest.TestCase):
    def test_widget_history_type_includes_persisted_qr_url_flag(self):
        self.assertTrue(has_editor_history_qr_field(UI,DOMAIN))
        self.assertIn('w.showQrUrl!==false', UI)
        self.assertIn('showQrUrl:e.target.checked', UI)
    def test_no_unreachable_graphics_checks_in_non_graphic_branch(self):
        self.assertTrue(has_reachable_widget_icon_branch(UI))
        self.assertIn("k==='shape'||k==='line'?<GraphicInsertTool", UI)
    def test_negative_missing_type_is_detected(self):
        marker="'showTitle' | 'showQrUrl' | 'autoFit'"
        self.assertIn(marker,UI)
        self.assertFalse(has_editor_history_qr_field(UI.replace(marker,"'showTitle' | 'autoFit'",1),DOMAIN))
    def test_negative_impossible_shape_or_line_compares_are_detected(self):
        marker="fillNone:true,shapeType:'rectangle'"
        # Mutate only the non-graphic icon branch, not an earlier occurrence
        # elsewhere in the main editor.
        prefix,tail=UI.split(':<EditorIconTool',1)
        self.assertIn(marker,tail)
        for replacement in ["fillNone:k!=='shape',shapeType:'rectangle'",
                            "fillNone:true,shapeType:'rectangle',...(k==='line'?{strokeWidth:2}:{})"]:
            self.assertFalse(has_reachable_widget_icon_branch(prefix+':<EditorIconTool'+tail.replace(marker,replacement,1)))
    def test_ci_runs_contract_early_and_tracks_current_inventory(self):
        self.assertIn('test_rc163_frontend_typescript_build',WORKFLOW)
        self.assertIn('verify_rc_cycle162_inventory.py --historical',WORKFLOW)
        self.assertIn('verify_rc_cycle163_inventory.py',WORKFLOW)
        self.assertLess(WORKFLOW.index('test_rc163_frontend_typescript_build'),WORKFLOW.index('npm run build'))

if __name__=='__main__':unittest.main()
