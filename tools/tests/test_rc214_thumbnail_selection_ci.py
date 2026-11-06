"""RC214: selection-aware thumbnail navigation and menu Escape focus regression.

RC213 full CI 42142002249 hit a historical pre-RC206 inline onClick literal.
This test checks both behaviors and rejects removing the modifier guard or the
unsaved-change navigation path. It also checks focus restoration after Escape.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
WORKFLOW=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
THUMB_START='className="page-editor-thumb"'
THUMB_END='<span className="page-editor-thumb-number"'


def thumbnail_markup(source:str)->str:
    start=source.find(THUMB_START)
    if start<0:raise AssertionError('thumbnail button not found')
    end=source.find(THUMB_END,start)
    if end<0:raise AssertionError('thumbnail content not found')
    return source[start:end]


def verify_thumbnail_click(source:str)->str:
    section=thumbnail_markup(source)
    # Explicit return from modifier branch prevents opening a different page.
    expected='onClick={e=>{if(e.ctrlKey||e.metaKey){setSelectedPageIds(v=>choosePageIds(v,a.id,true));return}setSelectedPageIds([a.id]);beginPageDesign(a)}}'
    if expected not in section:
        raise AssertionError('normal click must open page, Ctrl/Cmd+click only updates selection')
    if 'aria-pressed={selectedPageIds.includes(a.id)}' not in section:
        raise AssertionError('selected thumbnail state must remain accessible')
    if 'aria-current={designActivity===a.id?' not in section:
        raise AssertionError('active editing page must remain accessible')
    if 'if(pages[to]){beginPageDesign(pages[to]);requestAnimationFrame(' not in section:
        raise AssertionError('arrow navigation must still open the destination page')
    return section


def verify_menu_focus(source:str)->None:
    section=source[source.index('page-editor-thumb-menu-floating'):]
    expected="""const trigger=document.querySelector<HTMLButtonElement>('.page-editor-thumb-menu-trigger[aria-expanded="true"]');setPageThumbMenu('');requestAnimationFrame(()=>trigger?.focus())"""
    if expected not in section:
        raise AssertionError('Escape must capture trigger before closing portal and restore focus')


class RC214ThumbnailSelectionCI(unittest.TestCase):
    def test_selection_click_and_navigation(self):
        verify_thumbnail_click(UI)
        self.assertIn('aria-keyshortcuts="Alt+ArrowUp Alt+ArrowDown D R Backspace"',UI)
        self.assertIn('if(!confirmPageNavigation())return;',UI)

    def test_escape_focus_restoration(self):
        verify_menu_focus(UI)
        self.assertIn("if(e.key==='Escape'){e.preventDefault();e.stopPropagation();", UI)

    def test_mutations_fail_closed(self):
        block=verify_thumbnail_click(UI)
        for old,new in (
            ('e.ctrlKey||e.metaKey','e.ctrlKey'),
            ('choosePageIds(v,a.id,true)','choosePageIds(v,a.id,false)'),
            (';return}setSelectedPageIds([a.id])',';}setSelectedPageIds([a.id])'),
            (';beginPageDesign(a)}}',';}'),
            ('aria-pressed={selectedPageIds.includes(a.id)}','aria-pressed={false}'),
        ):
            self.assertIn(old,block)
            start=UI.index(THUMB_START)
            end=UI.index(THUMB_END,start)
            damaged=UI[:start]+UI[start:end].replace(old,new,1)+UI[end:]
            self.assertNotEqual(damaged,UI)
            with self.assertRaises(AssertionError):verify_thumbnail_click(damaged)
        focus='requestAnimationFrame(()=>trigger?.focus())'
        self.assertIn(focus,UI)
        with self.assertRaises(AssertionError):verify_menu_focus(UI.replace(focus,'requestAnimationFrame(()=>void 0)',1))

    def test_legacy_contracts_and_early_ci(self):
        for filename in ('test_editor_contextual_layout_v2.py','test_editor_thumbnail_keyboard_rc.py'):
            body=(ROOT/'tools/tests'/filename).read_text(encoding='utf8')
            self.assertNotIn("self.assertIn('onClick={()=>beginPageDesign(a)}'",body)
            self.assertIn('verify_thumbnail_click(',body)
        self.assertIn('tools.tests.test_rc214_thumbnail_selection_ci',WORKFLOW)
        self.assertIn('tools.tests.test_editor_thumbnail_keyboard_rc',WORKFLOW)
        self.assertIn('tools.tests.test_page_editor_followup',WORKFLOW)
        self.assertIn('tools.tests.test_editor_contextual_layout_v2',WORKFLOW)
        self.assertIn('tools.tests.test_rc213_page_order_state_ci',WORKFLOW)
        self.assertIn('./node_modules/.bin/tsc --noEmit -p apps/web/tsconfig.json',WORKFLOW)

if __name__=='__main__':unittest.main()
