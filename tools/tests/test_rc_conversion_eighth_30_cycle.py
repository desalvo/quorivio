"""30 independent regression scenarios: editable native PowerPoint shape paints."""
import copy
import math
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pptx_portable import (_native_shape_paint, _validate_export_input,
                           inspect_pptx_fidelity, portable_to_pptx, pptx_to_portable)
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE_DASH_STYLE, MSO_FILL
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt
from PIL import Image, ImageChops, ImageStat

# These are distinct visible PowerPoint presentations, not just source-text assertions.
STYLES = [
    {'strokeColor':'#124b7b','strokeWidth':0.25,'fillColor':'#f1bb99'},
    {'strokeColor':'#9a3412','strokeWidth':1,'fillColor':'#ffffff'},
    {'strokeColor':'#005522','strokeWidth':2,'fillColor':'#aaffcc'},
    {'strokeColor':'#1b2a55','strokeWidth':4,'fillColor':'#eeeeff'},
    {'strokeColor':'#711188','strokeWidth':8,'fillColor':'#eeddee'},
    {'strokeColor':'#000000','strokeWidth':1.5,'strokeDash':'dash','fillColor':'#fff9dd'},
    {'strokeColor':'#331166','strokeWidth':3,'strokeDash':'dash','fillColor':'#ffffee'},
    {'strokeColor':'#1a5588','strokeWidth':2,'strokeDash':'dot','fillColor':'#eeeeff'},
    {'strokeColor':'#009999','strokeWidth':4,'strokeDash':'dot','fillNone':True},
    {'strokeNone':True,'fillColor':'#ffcc33'},
    {'strokeNone':True,'fillNone':True},
    {'strokeColor':'#dd3344','strokeWidth':6,'strokeDash':'solid','fillNone':True},
]
SHAPES = [MSO_SHAPE.RECTANGLE, MSO_SHAPE.ROUNDED_RECTANGLE, MSO_SHAPE.OVAL, MSO_SHAPE.ISOSCELES_TRIANGLE]

class EighthConversion30(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='quorivio-native-paints-')
        cls.root=Path(cls.tmp.name)
        deck=Presentation()
        deck.slide_width,deck.slide_height=Inches(13.333),Inches(7.5)
        for i,style in enumerate(STYLES):
            slide=deck.slides.add_slide(deck.slide_layouts[6])
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb=RGBColor(245,245,245)
            box=slide.shapes.add_shape(SHAPES[i%len(SHAPES)], Inches(2.5), Inches(1.25), Inches(8), Inches(4.7))
            if style.get('fillNone'):
                box.fill.background()
            else:
                box.fill.solid()
                box.fill.fore_color.rgb=RGBColor.from_string(style['fillColor'][1:])
            if style.get('strokeNone'):
                box.line.fill.background()
            else:
                box.line.color.rgb=RGBColor.from_string(style['strokeColor'][1:])
                box.line.width=Pt(style['strokeWidth'])
                box.line.dash_style={'solid':MSO_LINE_DASH_STYLE.SOLID,'dash':MSO_LINE_DASH_STYLE.DASH,
                                     'dot':MSO_LINE_DASH_STYLE.ROUND_DOT}[style.get('strokeDash','solid')]
        cls.source=cls.root/'original.pptx'
        cls.output=cls.root/'roundtrip.pptx'
        deck.save(cls.source)
        cls.portable=pptx_to_portable(cls.source)
        portable_to_pptx(cls.portable,cls.output)
        cls.report=inspect_pptx_fidelity(cls.source)
        cls.rendered={}
        cls.render_available=bool(shutil.which('libreoffice') and shutil.which('pdftoppm'))
        if cls.render_available:
            for source in (cls.source,cls.output):
                result=subprocess.run(['libreoffice','-env:UserInstallation=file://'+str(cls.root/('lo-'+source.stem)),
                    '--headless','--convert-to','pdf','--outdir',str(cls.root),str(source)],
                    capture_output=True,text=True,timeout=90)
                if result.returncode or not source.with_suffix('.pdf').is_file():
                    raise AssertionError('LibreOffice render failed: '+result.stderr)
                subprocess.run(['pdftoppm','-f','1','-l','12','-scale-to','480','-png',
                    str(source.with_suffix('.pdf')),str(cls.root/source.stem)],
                    check=True,capture_output=True,timeout=90)
                cls.rendered[source.stem]=sorted(cls.root.glob(source.stem+'-*.png'))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def _visual(self,i):
        self.assertTrue(self.render_available,'LibreOffice and Poppler required for visual acceptance')
        self.assertEqual(len(self.rendered['original']),12)
        self.assertEqual(len(self.rendered['roundtrip']),12)
        with Image.open(self.rendered['original'][i]) as a,Image.open(self.rendered['roundtrip'][i]) as b:
            self.assertEqual(a.size,b.size)
            difference=ImageChops.difference(a.convert('RGB'),b.convert('RGB'))
            self.assertLess(sum(ImageStat.Stat(difference).mean)/3,16,
                f'Visual drift on paint slide {i+1}')

    def test_01_visual_thin_stroke(self): self._visual(0)
    def test_02_visual_default_stroke(self): self._visual(1)
    def test_03_visual_two_pt_stroke(self): self._visual(2)
    def test_04_visual_four_pt_stroke(self): self._visual(3)
    def test_05_visual_eight_pt_stroke(self): self._visual(4)
    def test_06_visual_dashed_stroke(self): self._visual(5)
    def test_07_visual_wide_dash(self): self._visual(6)
    def test_08_visual_dotted_stroke(self): self._visual(7)
    def test_09_visual_dotted_transparent_fill(self): self._visual(8)
    def test_10_visual_no_outline(self): self._visual(9)
    def test_11_visual_no_fill_no_outline(self): self._visual(10)
    def test_12_visual_solid_outline_transparent_fill(self): self._visual(11)

    def _widget(self,i):
        return self.portable['activities'][i]['page_design']['widgets'][0]

    def test_13_all_shapes_stay_editable(self):
        self.assertTrue(all(self._widget(i)['kind']=='postit' for i in range(12)))
    def test_14_native_widths_survive_import(self):
        for i,s in enumerate(STYLES):
            if 'strokeWidth' in s:
                self.assertAlmostEqual(self._widget(i)['style']['strokeWidth'],s['strokeWidth'],places=2)
    def test_15_native_widths_survive_export(self):
        for i,slide in enumerate(Presentation(self.output).slides):
            if 'strokeWidth' in STYLES[i]:
                self.assertAlmostEqual(slide.shapes[0].line.width.pt,STYLES[i]['strokeWidth'],places=2)
    def test_16_native_dash_survives_import(self):
        for i,s in enumerate(STYLES):
            if 'strokeDash' in s:self.assertEqual(self._widget(i)['style']['strokeDash'],s['strokeDash'])
    def test_17_native_dash_survives_export(self):
        enum={'solid':MSO_LINE_DASH_STYLE.SOLID,'dash':MSO_LINE_DASH_STYLE.DASH,'dot':MSO_LINE_DASH_STYLE.ROUND_DOT}
        for i,slide in enumerate(Presentation(self.output).slides):
            if 'strokeDash' in STYLES[i]:self.assertEqual(slide.shapes[0].line.dash_style,enum[STYLES[i]['strokeDash']])
    def test_18_no_fill_is_editable(self):
        for i in (8,10,11):self.assertIs(self._widget(i)['style']['fillNone'],True)
    def test_19_no_stroke_is_editable(self):
        for i in (9,10):self.assertIs(self._widget(i)['style']['strokeNone'],True)
    def test_20_no_fill_roundtrips_to_native(self):
        slides=list(Presentation(self.output).slides)
        for i in (8,10,11):self.assertEqual(slides[i].shapes[0].fill.type,MSO_FILL.BACKGROUND)
    def test_21_no_stroke_roundtrips_to_native(self):
        slides=list(Presentation(self.output).slides)
        for i in (9,10):self.assertEqual(slides[i].shapes[0].line.fill.type,MSO_FILL.BACKGROUND)
    def test_22_shape_geometry_is_retained(self):
        for i,slide in enumerate(Presentation(self.output).slides):
            self.assertEqual(slide.shapes[0].auto_shape_type,SHAPES[i%len(SHAPES)])
    def test_23_fidelity_report_is_not_false_lossy(self):
        self.assertEqual(self.report['unsupported_shape_outlines'],0)
        self.assertFalse(self.report['lossy'],self.report)
    def test_24_export_rejects_negative_stroke_width(self): self._invalid_width(-1)
    def test_25_export_rejects_zero_stroke_width(self): self._invalid_width(0)
    def test_26_export_rejects_oversized_stroke_width(self): self._invalid_width(12.01)
    def test_27_export_rejects_nan_stroke_width(self): self._invalid_width(float('nan'))
    def test_28_export_rejects_boolean_stroke_width(self): self._invalid_width(True)
    def _invalid_width(self,value):
        bad=copy.deepcopy(self.portable)
        bad['activities'][0]['page_design']['widgets'][0]['style']['strokeWidth']=value
        with self.assertRaises(ValueError):_validate_export_input(bad)
    def test_29_export_rejects_unknown_dash(self):
        bad=copy.deepcopy(self.portable)
        bad['activities'][0]['page_design']['widgets'][0]['style']['strokeDash']='dash-dot-dot'
        with self.assertRaises(ValueError):_validate_export_input(bad)
    def test_30_export_rejects_string_no_fill(self):
        bad=copy.deepcopy(self.portable)
        bad['activities'][0]['page_design']['widgets'][0]['style']['fillNone']='true'
        with self.assertRaises(ValueError):_validate_export_input(bad)

if __name__=='__main__':unittest.main()
