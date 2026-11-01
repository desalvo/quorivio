"""RC91 regression: footer-number stage pinning, master draft safety and PPTX style parity."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
PPTX=(ROOT/'tools/pptx_portable.py').read_text()

class GlobalMasterRegressions(unittest.TestCase):
 def test_footer_number_is_pinned_to_canvas_in_all_four_surfaces(self):
  self.assertIn('position:absolute!important;right:10px!important;bottom:10px!important;',CSS)
  self.assertIn('pointer-events:none!important',CSS)
  self.assertIn('function SlideCanvasNumber',UI)
  self.assertIn('pageNumber={slidePageNumber(snapshot.activities,activity.id)}',UI)
  self.assertIn('pageNumber={page+1}',UI)
  self.assertIn('pageNumber={pageNumber}',UI)
  self.assertIn('pageNumber={Number(entry.activity.position)+1}',UI)
  self.assertEqual(UI.count('className="slide-footer-number"'),0)
  self.assertIn('className="slide-canvas-page-number"',UI)
  self.assertIn('style={{fontFamily:item.fontFamily,fontSize:item.fontSize,color:item.color',UI)
  self.assertIn('data-custom-number=',UI)
  self.assertIn('slide-canvas-page-number[data-custom-number="true"]',CSS)
 def test_editor_works_with_selection_and_persistent_schema(self):
  for text in ('slide-scheme-layout','slide-scheme-inspector','onInspectWidget={setSchemaInspected}',
               'Mostra nome della sessione','Numero pagina (10 px dal bordo del canvas)',
               'Segui il titolo della pagina','Rimuovi dallo schema','Modifiche non salvate'):
   self.assertIn(text,UI)
  self.assertIn('schemaBaseline.current=JSON.stringify(canonical)',UI)
  self.assertIn('JSON.stringify(schemaStoredWidgets(fresh.session.theme?.master?.widgets))!==schemaBaseline.current',UI)
  self.assertIn('function confirmSchemaNavigation()',UI)
  self.assertIn('onClick={()=>navigateDashboard(key)}',UI)
  self.assertIn("onClick={()=>navigateDashboard('session')}",UI)
 def test_native_pptx_inherits_scheme_with_absolute_number_and_local_title_override(self):
  import tempfile
  from pptx import Presentation
  from pptx.util import Inches
  from tools.pptx_portable import portable_to_pptx
  scheme=[{'id':'schema-title','kind':'title','label':'','titleFollowPage':True,
           'style':{'fontSize':34,'fontFamily':'Georgia','color':'#173456'},
           'position':{'x':8,'y':3,'width':84,'height':12}},
          {'id':'schema-footer','kind':'footer','footerShowSessionTitle':True,
           'footerShowPageNumber':True,'style':{'fontSize':21,'color':'#206080'},
           'position':{'x':28,'y':54,'width':40,'height':8}}]
  data={'format':'quorivio-session','version':1,
        'session':{'title':'Sessione','theme':{'master':{'titleStyle':{'fontSize':80,'color':'#ffffff'},'widgets':scheme}}},
        'activities':[{'title':'Slide A','page_design':{'widgets':[]}},
                      {'title':'Slide B','page_design':{'widgets':[{'id':'title-local','kind':'title',
                          'titleUseMaster':False,'titleFollowPage':True,
                          'style':{'fontSize':29,'color':'#224466'},
                          'position':{'x':4,'y':4,'width':80,'height':14}}]}}]}
  with tempfile.TemporaryDirectory() as d:
   output=Path(d)/'master.pptx';portable_to_pptx(data,output)
   prs=Presentation(output)
   self.assertEqual(len(prs.slides),2)
   first=next(shape for shape in prs.slides[0].shapes if shape.has_text_frame and shape.text=='Slide A')
   self.assertEqual(first.text_frame.paragraphs[0].runs[0].font.name,'Georgia')
   self.assertEqual(str(first.text_frame.paragraphs[0].runs[0].font.color.rgb),'173456')
   second=next(shape for shape in prs.slides[1].shapes if shape.has_text_frame and shape.text=='Slide B')
   self.assertEqual(str(second.text_frame.paragraphs[0].runs[0].font.color.rgb),'224466')
   for number,slide in enumerate(prs.slides,1):
    numbered=[shape for shape in slide.shapes if shape.has_text_frame and shape.text==str(number)]
    self.assertEqual(len(numbered),1)
    shape=numbered[0]
    self.assertLessEqual(abs(shape.left-(prs.slide_width-Inches(1.2)-Inches(10/96))),2)
    self.assertLessEqual(abs(shape.top-(prs.slide_height-Inches(.38)-Inches(10/96))),2)
    self.assertEqual(str(shape.text_frame.paragraphs[0].runs[0].font.color.rgb),'206080')

 def test_pptx_uses_widget_style_override_and_canvas_relative_page_number(self):
  self.assertIn("**master_style, **style",PPTX)
  self.assertIn('inset = Inches(10/96)',PPTX)
  self.assertIn('if (widget.get(\'kind\') == \'footer\' and all',PPTX)
  self.assertNotIn("'textAlign':'center', **master_style}",PPTX)

if __name__=='__main__':unittest.main()
