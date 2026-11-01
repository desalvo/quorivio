"""RC104 real editable PPTX run fidelity for widget rich text and master text."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from pptx_portable import portable_to_pptx,pptx_to_portable
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt


def mark(field,start,end,**style):
    return {'field':field,'start':start,'end':end,'style':style}


def doc(widgets, master=None):
    session={'title':'Demo'}
    if master is not None: session['theme']={'master':master}
    return {'format':'quorivio-session','version':1,'session':session,
            'activities':[{'type':'slide','title':'Titolo pagina',
                           'page_design':{'widgets':widgets}}]}


def widget(kind,label,marks=None,**extra):
    return {'kind':kind,'id':'widget1','label':label,
            'position':{'x':5,'y':5,'width':80,'height':30},
            'style':{'fontFamily':'Arial','fontSize':20,'color':'#000000'},
            'textMarks':marks or [],**extra}


class RichTextNativePowerPoint(unittest.TestCase):
    def rendered(self,definition):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path=Path(tmp.name)/'export.pptx'
        portable_to_pptx(definition,path)
        return path,Presentation(path)

    def test_selected_runs_have_own_bold_italic_font_color_and_strikethrough(self):
        data=doc([widget('text','ABC DEF',[
            mark('label',0,3,bold=True,color='#FF0080'),
            mark('label',4,7,italic=True,fontFamily='Georgia',fontSize=32,strikethrough=True)
        ])])
        _,pptx=self.rendered(data)
        shape=pptx.slides[0].shapes[0]
        self.assertEqual(shape.text,'ABC DEF')
        runs=shape.text_frame.paragraphs[0].runs
        self.assertEqual([r.text for r in runs],['ABC',' ','DEF'])
        self.assertTrue(runs[0].font.bold)
        self.assertEqual(str(runs[0].font.color.rgb),'FF0080')
        self.assertFalse(bool(runs[1].font.bold))
        self.assertTrue(runs[2].font.italic)
        self.assertEqual(runs[2].font.name,'Georgia')
        self.assertEqual(runs[2].font.size.pt,32)
        self.assertEqual(runs[2].font._rPr.get('strike'),'sngStrike')

    def test_uniform_default_title_bold_can_be_disabled_on_range(self):
        title=widget('title','Titolo pagina',[mark('label',0,6,bold=False)],titleFollowPage=True)
        title['style']={'fontFamily':'Arial','fontSize':24,'color':'#000000'}
        _,deck=self.rendered(doc([title]))
        runs=deck.slides[0].shapes[0].text_frame.paragraphs[0].runs
        self.assertEqual(''.join(run.text for run in runs),'Titolo pagina')
        self.assertFalse(runs[0].font.bold)
        self.assertTrue(runs[1].font.bold)

    def test_inherited_footer_and_global_scheme_marking(self):
        footer=widget('footer','Demo',[mark('label',0,4,italic=True,color='#112233')],footerShowPageNumber=False)
        _,deck=self.rendered(doc([],master={'widgets':[footer]}))
        self.assertEqual(deck.slides[0].shapes[0].text,'Demo')
        run=deck.slides[0].shapes[0].text_frame.paragraphs[0].runs[0]
        self.assertTrue(run.font.italic)
        self.assertEqual(str(run.font.color.rgb),'112233')

    def test_description_and_quiz_options_are_independent_fields(self):
        note=widget('postit','Label',[mark('description',0,4,bold=True)],description='Detail')
        opts=[{'id':'A','label':'Yes'},{'id':'B','label':'No'}]
        quiz=widget('question','Choose',[mark('option:B',0,2,underline=True)],options=opts)
        _,deck=self.rendered(doc([note,quiz]))
        first=deck.slides[0].shapes[0]
        second=deck.slides[0].shapes[1]
        self.assertEqual(first.text,'Label\nDetail')
        self.assertTrue(first.text_frame.paragraphs[1].runs[0].font.bold)
        self.assertFalse(bool(first.text_frame.paragraphs[0].runs[0].font.bold))
        self.assertEqual(second.text,'Choose\nYes\nNo')
        self.assertTrue(second.text_frame.paragraphs[2].runs[0].font.underline)
        self.assertFalse(bool(second.text_frame.paragraphs[1].runs[0].font.underline))

    def test_surrogate_offsets_do_not_emit_half_unicode_characters(self):
        text='A🎤B'
        _,deck=self.rendered(doc([widget('text',text,[mark('label',3,4,bold=True)])]))
        shape=deck.slides[0].shapes[0]
        self.assertEqual(shape.text,text)
        self.assertEqual([(r.text,r.font.bold) for r in shape.text_frame.paragraphs[0].runs],
                         [('A🎤',None),('B',True)])

    def test_malformed_marks_fail_closed_even_when_imported_via_scheme(self):
        bad=[mark('label',0,1,color='red'),mark('label',0,1,fontFamily='https://evil'),
             mark('label',0,1,fontSize=float('nan')),
             mark('label',0,1,bold=1),mark('label',0,1,arbitrary='payload'),
             {'field':'label','start':True,'end':2,'style':{'bold':True}},
             mark('option:<script>',0,2,bold=True)]
        for entry in bad:
            with self.subTest(entry=entry),tempfile.TemporaryDirectory() as d:
                with self.assertRaises(ValueError):
                    portable_to_pptx(doc([widget('text','hi',[entry])]),Path(d)/'bad.pptx')
                footer=widget('footer','Demo',[entry],footerShowPageNumber=False)
                with self.assertRaises(ValueError):
                    portable_to_pptx(doc([],master={'widgets':[footer]}),Path(d)/'bad2.pptx')

    def test_import_rich_pptx_restores_description_marks_and_roundtrip(self):
        p=Presentation()
        s=p.slides.add_slide(p.slide_layouts[6])
        box=s.shapes.add_textbox(100000,100000,4000000,800000)
        frame=box.text_frame
        first=frame.paragraphs[0].add_run(); first.text='Normal ';first.font.name='Arial';first.font.size=Pt(18)
        second=frame.paragraphs[0].add_run();second.text='Bold'; second.font.bold=True
        second.font.color.rgb=RGBColor(12,34,56)
        third=frame.add_paragraph().add_run();third.text='Other';third.font.italic=True
        third.font.name='Georgia'
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'input.pptx';p.save(source)
            restored=pptx_to_portable(source)
            w=restored['activities'][0]['page_design']['widgets'][0]
            self.assertEqual(w['description'],'Normal Bold\nOther')
            self.assertEqual(w['textMarks'][0]['field'],'description')
            self.assertIn('bold',w['textMarks'][0]['style'])
            target=Path(d)/'export.pptx'
            portable_to_pptx(restored,target)
            t=Presentation(target).slides[0].shapes[0]
            self.assertEqual(t.text,'Normal Bold\nOther')
            self.assertTrue(t.text_frame.paragraphs[0].runs[-1].font.bold)
            self.assertEqual(str(t.text_frame.paragraphs[0].runs[-1].font.color.rgb),'0C2238')
            self.assertTrue(t.text_frame.paragraphs[1].runs[0].font.italic)

if __name__=='__main__': unittest.main()
