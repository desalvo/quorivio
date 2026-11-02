"""RC99: checks that historic CI contracts protect the *current* editor architecture.

This preflight does not require python-pptx or a Node dependency installation.
The complete native PowerPoint round-trip remains in the post-dependency suite.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
UI = (ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')

class Cycle99CiContract(unittest.TestCase):
    def test_real_canvas_receives_session_media_and_join_code(self):
        calls = re.findall(r'<WidgetCanvas\b[\s\S]*?/>', UI)
        self.assertTrue(any(all(item in call for item in (
            'assets={assets}', 'backgrounds={backgrounds}', 'sessionId={selected}',
            'joinCode={snap.session.join_code}', 'onUpload={uploadWidgetMedia}',
            'assetBusy={assetBusy}', 'onBackgroundSelect=', 'onBackgroundUpload=',
        )) for call in calls))

    def test_dashboard_uses_guarded_navigation_and_stage_subscribes_live(self):
        self.assertIn('onClick={()=>navigateDashboard(key)}', UI)
        self.assertIn('if(confirmSchemaNavigation())setDashboardPage(page)', UI)
        self.assertIn('useLive(sessionId,setData,setConnection)', UI)
        self.assertIn('useLive(entry?.session?.id,', UI)

    def test_title_footer_and_selected_text_share_rich_editor(self):
        self.assertIn("w.kind==='footer'?widgetDisplay(w,{sessionTitle,pageNumber}).center",UI)
        self.assertIn('active={editing===w.id}', UI)
        self.assertIn('formatSelectedOrEntireField(w.textMarks||[]',UI)
        self.assertIn('applyAllWidgetTypeface(w,changes as InlineStyle)',UI)
        self.assertIn('applySelectionInlineStyle(marks,field,text,from,to,style)',(ROOT/'apps/web/src/widget-text-marks.ts').read_text())
        self.assertIn("onSelection={r=>recordTextSelection(w.id,'label',r)}",UI)

    def test_pptx_explicit_rgb_stroke_does_not_inherit_widget_borderless_default(self):
        source = (ROOT/'tools/pptx_portable.py').read_text(encoding='utf-8')
        self.assertIn("style['strokeColor'] = '#' + str(line.color.rgb)", source)
        self.assertIn("style['strokeWidth'] = width", source)
        self.assertIn('else 1.0', source)
        self.assertIn('box.line.fill.background()', source)

if __name__=='__main__':
    unittest.main()
