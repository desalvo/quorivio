"""RC112 functional contracts for reusable slide masters and editable footer controls."""
from pathlib import Path
import tempfile,unittest
ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
DOMAIN=(ROOT/'apps/api/src/domain.ts').read_text()

class MasterRibbonAndFooter(unittest.TestCase):
 def test_scheme_widget_rail_and_real_shared_selection(self):
  for needle in ('slide-scheme-widget-rail','schemaWidgetKinds.map','insertSchemaWidget(kind)',
                 'onSelectionChange={ids=>','arrangeSchema(mode','slide-scheme-ribbon','slide-scheme-exit'):
   self.assertIn(needle,UI)
  self.assertIn('onChange={next=>setSchemaWidgets(masterWidgetTemplate(next))}',UI)
  self.assertIn('widgets.length>16',DOMAIN)
  self.assertIn("!validPageDesign({widgets})",DOMAIN)
 def test_shared_canvas_rulers_and_selected_only_handles(self):
  self.assertIn('.slide-scheme-workspace .widget-canvas-item[data-selected="true"] > .widget-resize-edge',CSS)
  self.assertIn('.editor-ux-v2 .canvas-ruler-horizontal{display:flex!important',CSS)
  self.assertIn('grid-template-columns:28px minmax(0,1fr)!important',CSS)
 def test_number_and_separator_remain_strictly_validated(self):
  for field in ('footerNumberX','footerNumberY','footerSeparator','footerSeparatorColor'):
   self.assertIn(field,DOMAIN)
   self.assertIn(field,UI)
  self.assertIn('data-custom-number=',UI)
 def test_native_pptx_custom_footer_position_and_hidden_number(self):
  from pptx import Presentation
  from tools.pptx_portable import portable_to_pptx
  footer={'id':'f','kind':'footer','footerShowPageNumber':True,'footerNumberX':35,'footerNumberY':60,'footerSeparatorColor':'#1479af',
          'position':{'x':0,'y':92,'width':100,'height':8,'rotation':0}}
  data={'format':'quorivio-session','version':1,'session':{'title':'School','theme':{'master':{'widgets':[footer]}}},'activities':[{'title':'Page 1','page_design':{'widgets':[]}}]}
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/'footer.pptx';portable_to_pptx(data,path)
   ppt=Presentation(path)
   number=[sh for sh in ppt.slides[0].shapes if sh.has_text_frame and sh.text=='1']
   self.assertEqual(len(number),1)
   self.assertLess(number[0].left,ppt.slide_width*0.35)
   self.assertGreater(number[0].top,ppt.slide_height*0.90)
   self.assertGreater(len(ppt.slides[0].shapes),2) # footer + page number + divider
   data['session']['theme']['master']['widgets'][0]['footerShowPageNumber']=False
   data['session']['theme']['master']['widgets'][0]['footerSeparator']=False
   other=Path(temp)/'footer-hidden.pptx';portable_to_pptx(data,other)
   ppt=Presentation(other)
   self.assertFalse(any(sh.has_text_frame and sh.text=='1' for sh in ppt.slides[0].shapes))

if __name__=='__main__':unittest.main()
