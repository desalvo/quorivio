"""RC165 regression: Chromium audience fixture must exercise authored widgets.

The default poll created by the API contains a Title only; RC160 deliberately
removed standalone question and audience-Q&A panels. The actual browser test
must author question controls, submit through widget endpoints and retain the
independent real-PostgreSQL legacy moderation acceptance.
"""
from __future__ import annotations
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT=Path(__file__).resolve().parents[2]
BROWSER=(ROOT/'tools/ci_browser_participant.py').read_text(encoding='utf8')
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
MODERATION=(ROOT/'tools/ci_audience_moderation_postgres.py').read_text(encoding='utf8')


def run_fixture(text: str=BROWSER):
    """Execute only prepare(), using an isolated fake HTTP API and no browser."""
    tree=ast.parse(text)
    prepare=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='prepare')
    calls=[]
    title={'id':'page-title','kind':'title','label':'CI browser poll',
           'position':{'x':8,'y':3,'width':84,'height':12,'rotation':0}}
    page={'id':'activity-test','page_design':{'widgets':[title]},'result_design':{},'design_revision':1}
    def api(_admin,method,path,body=None,expected=200):
        calls.append((method,path,body,expected))
        if method=='POST' and path=='/api/sessions':
            return {'id':'session-test','join_code':'short','join_url':'http://127.0.0.1:8080/join/long-secret'}
        if method=='POST' and path.endswith('/activities'):
            return {'id':'activity-test'}
        if method=='GET' and path=='/api/sessions/session-test':
            return {'activities':[page]}
        return {'ok':True}
    ns={'BASE':'http://127.0.0.1:8080','WEB':'http://127.0.0.1:8080',
        'os':SimpleNamespace(environ={'QUORIVIO_CI_ADMIN_EMAIL':'ci@example.invalid','QUORIVIO_CI_NEW_PASSWORD':('X'*24)}),
        'http':SimpleNamespace(cookiejar=SimpleNamespace(CookieJar=lambda:object())),
        'HTTPCookieProcessor':lambda x:x,'build_opener':lambda x:object(),
        'api':api,'QUESTION_WIDGET':'ci-browser-question','RATING_WIDGET':'ci-browser-rating','TOPIC_WIDGET':'ci-browser-topic',
        'GRAPHIC_LINE':'ci-browser-line','GRAPHIC_SHAPE':'ci-browser-shape',
        'PRESENTER_CHART':'ci-browser-presenter-result','PRESENTER_COUNT':'ci-browser-presenter-count',
        'FOOTER_WIDGET':'ci-browser-footer',
        'validate_disposable_origin':lambda value:value}
    exec(compile(ast.Module(body=[prepare],type_ignores=[]),str(ROOT/'tools/ci_browser_participant.py'),'exec'),ns)
    result=ns['prepare']()
    patch=next((payload for method,path,payload,_ in calls if method=='PATCH' and path.endswith('/design')),None)
    return result,calls,patch


class RC165AuthoredParticipantChromium(unittest.TestCase):
    def test_real_fixture_provisions_widgets_before_activation(self):
        (_,sid,code,secret,aid),calls,patch=run_fixture()
        self.assertEqual((sid,code,secret,aid),('session-test','short','long-secret','activity-test'))
        self.assertIsInstance(patch,dict)
        self.assertEqual(patch['expected_design_revision'],1)
        widgets=patch['page_design']['widgets']
        self.assertEqual([w['kind'] for w in widgets],['title','question','rating','topic-question','line','shape','results-button','participant-count','footer'])
        self.assertEqual(widgets[1]['answerMode'],'single')
        self.assertEqual([x['id'] for x in widgets[1]['options']],['yes','no'])
        self.assertEqual([x['id'] for x in widgets],['page-title','ci-browser-question','ci-browser-rating','ci-browser-topic','ci-browser-line','ci-browser-shape','ci-browser-presenter-result','ci-browser-presenter-count','ci-browser-footer'])
        design_index=next(i for i,x in enumerate(calls) if x[0]=='PATCH')
        active_index=next(i for i,x in enumerate(calls) if x[1].endswith('/status'))
        self.assertLess(design_index,active_index)
        self.assertEqual(calls[-1][1],'/api/sessions/session-test/activities/activity-test/open')

    def test_negative_missing_authored_question_fails(self):
        broken=BROWSER.replace("'id':QUESTION_WIDGET,'kind':'question'", "'id':QUESTION_WIDGET,'kind':'text'",1)
        self.assertNotEqual(broken,BROWSER)
        _,_,patch=run_fixture(broken)
        self.assertNotIn('question',[w['kind'] for w in patch['page_design']['widgets']])
        self.assertFalse(any(w['kind']=='question' for w in patch['page_design']['widgets']))

    def test_real_browser_asserts_widget_answers_privacy_and_idempotency(self):
        for fragment in ('get_by_role(\'button\',name=\'Diapositiva 16:9\')',
                         'get_by_role(\'radio\',name=choice',
                         'widget-answers',"row['responses']==2",'Risposta già registrata',
                         "get_by_role('region',name='Strumenti interattivi').count()==0", 
                         'topic-widgets/','get_by_role(\'button\',name=\'Invia domanda\''):
            self.assertIn(fragment,BROWSER)
        self.assertNotIn("get_by_role('group',name='Opzioni di risposta').get_by_role('button'",BROWSER)
        self.assertNotIn('<AudienceExtensions',UI[UI.index('{joinPath?<main'):UI.index('publicPath?<PresenterLiveScreen')])

    def test_separate_legacy_moderation_is_not_silently_dropped(self):
        for contract in ('ThreadPoolExecutor(max_workers=12)',"{'status':'approved'}",
                         "{'status':'rejected'}",'already_voted','total_pages'):
            self.assertIn(contract,MODERATION)
        self.assertIn('python3 tools/ci_audience_moderation_postgres.py',CI)
        self.assertIn('python3 tools/ci_browser_participant.py',CI)

    def test_preflight_precedes_npm_and_preserves_real_chromium_job(self):
        self.assertIn('tools.tests.test_rc165_authored_participant_chromium',CI)
        self.assertLess(CI.index('tools.tests.test_rc165_authored_participant_chromium'),CI.index('npm ci --ignore-scripts'))
        self.assertIn('Chromium participant UI and PostgreSQL lifecycle (opt-in)',CI)

if __name__=='__main__':unittest.main()
