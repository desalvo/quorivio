"""RC108: five-question widgets must export as readable, editable public PPTX text."""
from __future__ import annotations
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from pptx_portable import portable_to_pptx, pptx_to_portable
from pptx import Presentation
from pptx.enum.text import MSO_AUTO_SIZE


def group(kind='question'):
    return {
        'id': 'survey1', 'kind': kind, 'label': 'Introduzione',
        'description': 'Rispondi alle domande',
        'options': [{'id':'topA','label':'Sì'}],
        'position': {'x': 5, 'y':5, 'width':90, 'height':85},
        'style': {'fontFamily':'Arial','fontSize':18,'color':'#000000'},
        'questions': [
            {'id':'first','label':'Quale ambito?', 'description':'Scegli uno', 'answerMode':'single',
             'options':[{'id':'yes','label':'Computer'}, {'id':'no','label':'Internet'}],
             'correctOptionId':'yes'},
            {'id':'second','label':'Come migliorare?', 'answerMode':'text', 'options': []},
        ],
        'textMarks': [
            {'field':'question:first:label','start':0,'end':5,'style':{'bold':True}},
            {'field':'question:first:option:no','start':0,'end':8,'style':{'italic':True}},
            {'field':'question:second:label','start':0,'end':4,'style':{'color':'#FF0000'}},
            {'field':'question:first:description','start':0,'end':5,'style':{'underline':True}},
        ]
    }


def definition(widget):
    return {'format':'quorivio-session','version':1,'session':{'title':'Prova'},
            'activities':[{'type':'slide','title':'Pagina 1','page_design':{'widgets':[widget]}}]}


class GroupedQuestionPptx(unittest.TestCase):
    def export(self, widget):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        dest=Path(temp.name)/'deck.pptx'
        portable_to_pptx(definition(widget),dest)
        return dest, Presentation(dest).slides[0].shapes[0]

    def test_group_and_subquestions_all_visible_as_editable_text(self):
        _, shape=self.export(group())
        self.assertEqual(shape.text,
          'Introduzione\nRispondi alle domande\nSì\n\nQuale ambito?\nScegli uno\nComputer\nInternet\n\nCome migliorare?')
        self.assertTrue(shape.has_text_frame)
        self.assertTrue(shape.text_frame.word_wrap)
        self.assertEqual(shape.text_frame.auto_size,MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE)
        self.assertEqual(len(shape.text_frame.paragraphs),10)

    def test_nested_question_marks_target_correct_independent_fields(self):
        _,shape=self.export(group())
        pars=shape.text_frame.paragraphs
        self.assertTrue(pars[4].runs[0].font.bold)
        self.assertFalse(bool(pars[6].runs[0].font.italic))
        self.assertTrue(pars[7].runs[0].font.italic)
        self.assertEqual(str(pars[9].runs[0].font.color.rgb),'FF0000')
        self.assertTrue(pars[5].runs[0].font.underline)

    def test_answer_keys_are_not_in_public_pptx_content(self):
        w=group();w['questions'][0]['correctOptionId']='yes'
        path,shape=self.export(w)
        self.assertNotIn('correctOptionId', '\n'.join(s.text for s in Presentation(path).slides[0].shapes if s.has_text_frame))
        # No answer ids or answer-key metadata are emitted in the OOXML archive.
        import zipfile
        with zipfile.ZipFile(path) as z:
            content=z.read('ppt/slides/slide1.xml')
        self.assertNotIn(b'correctOptionId',content)
        self.assertNotIn(b'correctOptionIds',content)
        self.assertNotIn(b'"yes"',content)

    def test_import_has_plain_editable_fallback_not_false_interactivity(self):
        path,_=self.export(group())
        restored=pptx_to_portable(path)
        widgets=restored['activities'][0]['page_design']['widgets']
        self.assertEqual(len(widgets),1)
        self.assertEqual(widgets[0]['kind'],'text')
        self.assertIn('Come migliorare?',widgets[0]['description'])
        self.assertNotIn('questions',widgets[0])

    def test_nested_mark_without_group_is_rejected(self):
        w=group()
        del w['questions']
        with tempfile.TemporaryDirectory() as d,self.assertRaisesRegex(ValueError,'Orphaned'):
            portable_to_pptx(definition(w),Path(d)/'no-group.pptx')

    def test_timed_quiz_group_exports(self):
        w=group('timed-quiz'); w['questions'][1]['answerMode']='single';w['questions'][1]['options']=[{'id':'c','label':'A'},{'id':'d','label':'B'}]
        _,s=self.export(w)
        self.assertIn('Come migliorare?',s.text)
        self.assertIn('\nA\nB',s.text)

    def test_reject_duplicate_ids_and_bad_member_shape(self):
        for mutation in ('duplicate','control','too_many','unknown','bad_mode','bad_options','bad_correct'):
            with self.subTest(mutation=mutation):
                w=group()
                if mutation=='duplicate':w['questions'][1]['id']='first'
                elif mutation=='control':w['questions'][0]['label']='Bad\x01label'
                elif mutation=='too_many':w['questions']=w['questions']*3
                elif mutation=='unknown':w['questions'][0]['publicCredential']='secret'
                elif mutation=='bad_mode':w['questions'][0]['answerMode']='whatever'
                elif mutation=='bad_options':w['questions'][0]['options']=[{'id':'same','label':'A'},{'id':'same','label':'B'}]
                else:w['questions'][0]['correctOptionId']='wrong-id'
                with tempfile.TemporaryDirectory() as d, self.assertRaises(ValueError):
                    portable_to_pptx(definition(w),Path(d)/'bad.pptx')

    def test_orphaned_and_overrun_nested_marks_fail_closed(self):
        for field, end in [('question:missing:label',2),('question:first:label',500),('question:first:option:missing',2)]:
            with self.subTest(field=field):
                w=group()
                w['textMarks']=[{'field':field,'start':0,'end':end,'style':{'bold':True}}]
                with tempfile.TemporaryDirectory() as d,self.assertRaises(ValueError):
                    portable_to_pptx(definition(w),Path(d)/'bad.pptx')

    def test_large_group_fails_instead_of_silently_truncating(self):
        w=group();w['questions']=[]
        for index in range(5):
            w['questions'].append({'id':f'q{index}', 'label':'Q'*240,
                  'description':'D'*500,'answerMode':'single',
                  'options':[{'id':f'o{j}','label':'X'*160} for j in range(12)]})
        w['textMarks']=[]
        with tempfile.TemporaryDirectory() as d,self.assertRaisesRegex(ValueError,'quota'):
            portable_to_pptx(definition(w),Path(d)/'oversize.pptx')

    def test_emoji_utf16_marks_keep_unicode_intact(self):
        w=group();w['questions'][0]['label']='A🎤B'
        w['textMarks']=[{'field':'question:first:label','start':3,'end':4,'style':{'bold':True}}]
        _,s=self.export(w)
        self.assertIn('A🎤B',s.text)
        p=s.text_frame.paragraphs[4]
        self.assertEqual([(r.text,r.font.bold) for r in p.runs],[('A🎤',None),('B',True)])

if __name__=='__main__': unittest.main()
