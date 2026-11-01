#!/usr/bin/env python3
"""Real PostgreSQL acceptance: multiple answerable questions in one widget.

Runs only against a disposable loopback CI session with explicit opt-in, tests
legacy question_id='', independent subquestion IDs, idempotence and statistics.
"""
import os
import http.cookiejar
from urllib.request import HTTPCookieProcessor,build_opener
from urllib.parse import urlsplit
from ci_audience_moderation_postgres import BASE,TOKEN,request,visitor

def run():
 url=urlsplit(BASE)
 if url.scheme!='http' or url.hostname not in ('localhost','127.0.0.1') or not url.port:
  raise RuntimeError('PostgreSQL question acceptance requires disposable loopback')
 if os.environ.get('QUORIVIO_CI_MULTI_QUESTION_TEST')!='1' or not TOKEN or len(TOKEN)<32:
  raise RuntimeError('Explicit opt-in and ephemeral staging load token required')
 admin=build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
 request(admin,'POST','/api/auth/login',{'email':os.environ['QUORIVIO_CI_ADMIN_EMAIL'],'password':os.environ['QUORIVIO_CI_NEW_PASSWORD']})
 session=request(admin,'POST','/api/sessions',{'title':'CI independent widget questions'},201)
 sid,code=session['id'],session['join_code']
 activity=request(admin,'POST',f'/api/sessions/{sid}/activities',{'title':'Question group','type':'poll','options':[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}]},201)
 aid=activity['id']
 widget={'id':'multi1','kind':'question','label':'Primary answer','answerMode':'single','options':[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}],
  'questions':[{'id':'sub1','label':'Independent checkbox question','answerMode':'multiple','options':[{'id':'a','label':'A'},{'id':'b','label':'B'}]},
               {'id':'sub2','label':'Independent free text','answerMode':'text'}],
  'textMarks':[{'field':'question:sub1:label','start':0,'end':11,'style':{'bold':True}}],
  'position':{'x':8,'y':10,'width':50,'height':65}}
 result={'id':'results1','kind':'results-button','label':'Answers to sub1','targetWidgetId':'multi1','targetQuestionId':'sub1'}
 document={'page_design':{'widgets':[widget,result]},'result_design':{},'expected_design_revision':1}
 patch=request(admin,'PATCH',f'/api/sessions/{sid}/activities/{aid}/design',document)
 assert patch['ok'] is True
 persisted=request(admin,'GET',f'/api/sessions/{sid}')['activities'][0]['page_design']['widgets']
 assert persisted[0]['questions']==widget['questions'] and persisted[0]['textMarks']==widget['textMarks']
 assert persisted[1]['targetQuestionId']=='sub1'
 request(admin,'POST',f'/api/sessions/{sid}/status',{'status':'active'})
 request(admin,'POST',f'/api/sessions/{sid}/activities/{aid}/open',{})
 one,two=visitor(code,1101),visitor(code,1102)
 endpoint=f'/api/join/{code}/activities/{aid}/widgets/multi1/respond'
 def answer(client,question_id,payload):
  return request(client,'POST',endpoint,{**payload,'question_id':question_id})
 first=answer(one,'',{'option_id':'yes'})
 assert first['ok'] and first['question_id']=='' and not first['already_submitted']
 second=answer(one,'sub1',{'option_ids':['a','b']})
 third=answer(one,'sub2',{'text':'Independent answer'})
 assert second['question_id']=='sub1' and third['question_id']=='sub2' and not second['already_submitted'] and not third['already_submitted']
 assert answer(one,'sub1',{'option_ids':['b']})['already_submitted'] is True
 assert answer(two,'sub1',{'option_ids':['b']})['already_submitted'] is False
 assert answer(two,'',{'option_id':'no'})['already_submitted'] is False
 request(one,'POST',endpoint,{'question_id':'missing','text':'oops'},expected=404)
 request(one,'POST',endpoint,{'question_id':'../../bad','text':'oops'},expected=400)
 request(one,'POST',endpoint,{'question_id':'sub1','option_ids':['foreign']},expected=400)
 stats=f'/api/sessions/{sid}/widget-answers/detail?activity_id={aid}&widget_id=multi1'
 primary=request(admin,'GET',stats)
 checks=request(admin,'GET',stats+'&question_id=sub1')
 free=request(admin,'GET',stats+'&question_id=sub2')
 assert primary['revisions'][0]['responses']==2 and primary['revisions'][0]['options']=={'yes':1,'no':1},primary
 assert checks['revisions'][0]['responses']==2 and checks['revisions'][0]['options']=={'a':1,'b':2},checks
 assert free['revisions'][0]['responses']==1 and free['revisions'][0]['texts']==1,free
 request(one,'GET',stats+'&question_id=sub1',expected=401)
 # In a live page, a new answer definition creates a new revision without
 # overwriting the old responses. Existing IDs keep historic interpretability.
 current=request(admin,'GET',f'/api/sessions/{sid}')['activities'][0]
 newer={**widget,'questions':[{**widget['questions'][0],'options':[{'id':'a','label':'A'},{'id':'b','label':'B revised'}]},widget['questions'][1]]}
 patch=request(admin,'PATCH',f'/api/sessions/{sid}/activities/{aid}/design',{'page_design':{'widgets':[newer,result]},'result_design':{},'expected_design_revision':current['design_revision']})
 assert patch['ok']
 assert answer(two,'sub1',{'option_ids':['a']})['revision']==2
 # Editing only sub1 must not invalidate previously committed answers to the
 # independent primary question or sub2, nor permit another vote in either.
 primary_retry=answer(one,'',{'option_id':'no'})
 assert primary_retry['already_submitted'] and primary_retry['revision']==1,primary_retry
 secondary_retry=answer(one,'sub2',{'text':'Should remain unchanged'})
 assert secondary_retry['already_submitted'] and secondary_retry['revision']==1,secondary_retry
 preserved=request(admin,'GET',stats)
 assert preserved['revisions'][0]['responses']==2,preserved
 # A separate primary edit changes only its own revision, not sub1's score.
 newest=request(admin,'GET',f'/api/sessions/{sid}')['activities'][0]
 changed_primary={**newer,'options':[{'id':'yes','label':'Definitely'},{'id':'no','label':'No'}]}
 patch=request(admin,'PATCH',f'/api/sessions/{sid}/activities/{aid}/design',{'page_design':{'widgets':[changed_primary,result]},'result_design':{},'expected_design_revision':newest['design_revision']})
 assert patch['ok']
 assert answer(one,'',{'option_id':'yes'})['revision']==3
 assert answer(two,'sub1',{'option_ids':['b']})['revision']==2
 historic=request(admin,'GET',stats+'&question_id=sub1')
 assert [r['revision'] for r in historic['revisions']]==[1,2],historic
 print('PASS PostgreSQL independent widget questions: 3 question IDs, 2 participants, idempotence, presenter-only scoped stats, legacy data, revision isolation')
if __name__=='__main__':run()
