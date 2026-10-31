"""RC94 acceptance contracts for borderless widgets and editable native shapes."""
from pathlib import Path
import tempfile
import unittest
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from pptx_portable import portable_to_pptx,pptx_to_portable,_validate_export_input
from pptx import Presentation
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE as S
from pptx.enum.dml import MSO_FILL

class RC94WidgetShapes(unittest.TestCase):
    def deck(self,shape,width):
        return {'format':'quorivio-session','version':1,'session':{'title':'Stage'},
          'activities':[{'type':'slide','title':'Forme','page_design':{'widgets':[
            {'id':'widget-one','kind':'postit','label':'Forma',
             'style':{'shapeType':shape,'strokeWidth':width,'strokeColor':'#aabbcc','fillNone':True},
             'position':{'x':20,'y':20,'width':55,'height':40,'rotation':0}}]}}]}
    def test_zero_border_is_valid_and_native_line_is_hidden(self):
        with tempfile.TemporaryDirectory() as d:
            target=Path(d)/'zero.pptx';portable_to_pptx(self.deck('diamond',0),target)
            shape=Presentation(target).slides[0].shapes[0]
            self.assertEqual(shape.line.fill.type,MSO_FILL.BACKGROUND)
    def test_native_editable_shapes_are_not_rectangles(self):
        names={'triangle':S.ISOSCELES_TRIANGLE,'diamond':S.DIAMOND,
               'hexagon':S.HEXAGON,'cloud':S.CLOUD,'speech':S.RECTANGULAR_CALLOUT,
               'rounded-rectangle':S.ROUNDED_RECTANGLE,'circle':S.OVAL}
        with tempfile.TemporaryDirectory() as d:
            for name,expected in names.items():
                with self.subTest(shape=name):
                    path=Path(d)/f'{name}.pptx'
                    portable_to_pptx(self.deck(name,2),path)
                    self.assertEqual(Presentation(path).slides[0].shapes[0].auto_shape_type,expected)
                    imported=pptx_to_portable(path)['activities'][0]['page_design']['widgets'][0]['style']
                    if name not in ('circle',):
                        self.assertEqual(imported.get('shapeType', 'rounded-rectangle' if imported.get('rounded') else None),name)
    def test_negative_and_nonfinite_border_rejected(self):
        for invalid in (-0.001,12.5,float('nan'),float('inf'),True):
            with self.subTest(border=invalid),self.assertRaises(ValueError):
                _validate_export_input(self.deck('diamond',invalid))
    def test_frontend_uses_portaled_floating_menu_and_shared_vector_outline(self):
        src=(ROOT/'apps/web/src/main.tsx').read_text()
        self.assertIn('floatingWidgetMenuPosition(rect,window.innerWidth,window.innerHeight,y)',src)
        self.assertIn('contextWidget===w.id&&createPortal(',src)
        self.assertEqual(src.count('<WidgetShapeOutline style={w.style}/>'),5)
        css=(ROOT/'apps/web/src/style.css').read_text()
        self.assertIn('.widget-vector-outline{position:absolute!important',css)

if __name__=='__main__':unittest.main()
