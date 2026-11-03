"""RC114 regression: legacy preflight must protect current safe background upload and answer styles."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')


def background_contract(source:str)->bool:
    # Only the chosen image’s onChange handler matters; unrelated menu actions
    # are intentionally allowed to close the same menu.
    start=source.find('onBackgroundUpload(file).then(')
    if start < 0: return False
    end=source.find('.finally(()=>setBackgroundUploading(false))',start)
    if end < 0: return False
    chunk=source[start:end]
    return bool(re.search(r'onBackgroundUpload\(file\)\.then\(applied=>\{if\(applied\)\{[^}]*setBackgroundMenu\(false\)',chunk)) and all(x in chunk for x in (
        "else setBackgroundUploadStatus('Caricamento annullato:",
        ".catch(error=>{setBackgroundUploadStatus('Caricamento non riuscito:",
    )) and 'then(()=>setBackgroundMenu(false))' not in chunk


def answer_contract(ui:str,domain:str)->bool:
    if not all(x in ui for x in (
        'answerInputStyle(widget.style)',
        'answerInputStyle(marks.style)',
        'answerInputStyle(w.style)',
        'answerOptionStyle(marks.style)',
        'Colore sfondo casella risposta libera',
    )):return False
    if 'answerFillColor?:string' not in domain:return False
    allowed=domain.find("'fillColor','answerFillColor','answerFontFamily'")
    validation=domain.find("['fillColor','answerFillColor','strokeColor','gradientEndColor'].every")
    return allowed>=0 and validation>=0


class RC114EditorPreflight(unittest.TestCase):
    def test_upload_success_closes_failure_stays_open(self):
        self.assertTrue(background_contract(MAIN))
        self.assertIn('setBackgroundMenu(true);setBackgroundUploading(true)',MAIN)
        self.assertIn("onBackgroundUpload={file=>uploadBackground(file,false,canvasDevice==='phone')}", MAIN)
        self.assertIn('if(forMobile){setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));}', MAIN)
        self.assertIn("else{setQuestionBackgroundAsset(applied.id);setQuestionBackground('')}", MAIN)
        self.assertIn('setQuestionBackgroundAsset(applied.id)',MAIN)

    def test_must_fail_closed_if_errors_are_silently_dismissed(self):
        self.assertFalse(background_contract(MAIN.replace('if(applied){','if(true){',1)))
        self.assertFalse(background_contract(MAIN.replace("else setBackgroundUploadStatus('Caricamento annullato:","else void 0 /* error hidden */",1)))
        self.assertFalse(background_contract(MAIN.replace(".catch(error=>{setBackgroundUploadStatus('Caricamento non riuscito:",".catch(error=>{void 0 /* error hidden */",1)))

    def test_answer_background_formatting_remains_validated_and_shared(self):
        self.assertTrue(answer_contract(MAIN,DOMAIN))

    def test_must_fail_closed_if_answer_color_validation_disappears(self):
        self.assertFalse(answer_contract(MAIN,DOMAIN.replace("['fillColor','answerFillColor','strokeColor','gradientEndColor'].every", "['fillColor','strokeColor','gradientEndColor'].every",1)))
        self.assertFalse(answer_contract(MAIN.replace('answerInputStyle(marks.style)','',1),DOMAIN))

    def test_floating_context_is_not_an_automatic_properties_popup(self):
        self.assertIn('openWidgetContextMenu(widgetId,widget,e.clientX,e.clientY)',MAIN)
        self.assertIn('onInspectWidget?.(w.id)',MAIN)
        self.assertNotIn('setContextWidget(onInspectWidget?null:w.id)',MAIN)

    def test_graphic_icons_match_insertable_kinds_not_legacy_separator(self):
        kinds=MAIN[MAIN.index('const editorWidgetKinds='):MAIN.index(' as const;',MAIN.index('const editorWidgetKinds='))]
        insertable=re.findall(r"'([a-z-]+)'",kinds)
        start=MAIN.index('const icons:Record<string,React.ReactNode>=')
        mapping=MAIN[start:MAIN.index('return <>{icons[kind]',start)]
        icons=re.findall(r"(?:[a-z-]+|'[a-z-]+'):<([A-Za-z0-9]+) size=\{21\}",mapping)
        self.assertNotIn('divider',insertable)
        self.assertIn('shape',insertable)
        self.assertIn('line',insertable)
        self.assertEqual(len(icons),len(insertable))
        self.assertEqual(len(icons),len(set(icons)))

    def test_preflight_runs_before_npm_and_current_inventory_is_only_current(self):
        self.assertIn('test_rc_cycle114_editor_preflight',CI)
        self.assertLess(CI.index('test_rc_cycle114_editor_preflight'),CI.index('npm install --ignore-scripts'))
        self.assertIn('verify_rc_cycle113_inventory.py --historical',CI)
        self.assertIn('verify_rc_cycle114_inventory.py',CI)

if __name__=='__main__':unittest.main()
