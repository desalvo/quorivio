#!/usr/bin/env python3
"""Real PostgreSQL HTTP acceptance for versioned page authoring.

Creates disposable sessions on localhost only. The two concurrent saves deliberately
use separate authenticated cookie jars, and exactly one must win the CAS.
"""
from concurrent.futures import ThreadPoolExecutor
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.error import HTTPError
import json
import os
from urllib.parse import urlsplit

BASE=os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')
assert urlsplit(BASE).hostname in ('localhost','127.0.0.1') and urlsplit(BASE).scheme=='http', 'Only disposable local CI servers are allowed'
EMAIL=os.environ['QUORIVIO_CI_ADMIN_EMAIL']
PASSWORD=os.environ['QUORIVIO_CI_NEW_PASSWORD']
TOKEN=os.environ.get('QUORIVIO_CI_LOAD_TOKEN')

def client():return build_opener(HTTPCookieProcessor(CookieJar()))
def api(c,method,path,body=None,status=200):
 data=json.dumps(body).encode() if body is not None else None
 headers={'Content-Type':'application/json',**({'X-Quorivio-Load-Token':TOKEN} if TOKEN else {})}
 req=Request(BASE+path,data=data,headers=headers,method=method)
 try:
  with c.open(req,timeout=20) as r:actual,payload=r.status,r.read()
 except HTTPError as e:actual,payload=e.code,e.read()
 assert actual==status,(method,path,actual,status,payload[:250])
 return json.loads(payload) if payload else None

def design(label='Base',color='#FFFFFF'):
 return {'page_design':{'backgroundColor':color,'widgets':[{'id':'ci-text','kind':'text','label':label,'position':{'x':10,'y':10,'width':30,'height':20}}]},'result_design':{'widgets':[]}}

def run():
 a,b,anon=client(),client(),client()
 for c in (a,b):api(c,'POST','/api/auth/login',{'email':EMAIL,'password':PASSWORD})
 assert api(anon,'GET','/api/sessions',status=401)['error']=='authentication_required'
 session=api(a,'POST','/api/sessions',{'title':'CI versioned editor PostgreSQL'},201)
 sid=session['id'];path=f'/api/sessions/{sid}'
 activity=api(a,'POST',path+'/activities',{'title':'Versioned layout','type':'poll','options':[{'id':'yes','label':'Yes'},{'id':'no','label':'No'}]},201)
 aid=activity['id'];edit=f'{path}/activities/{aid}/design'
 snapshot=api(a,'GET',path);assert next(x for x in snapshot['activities'] if x['id']==aid)['design_revision']==1
 assert api(anon,'PATCH',edit,design(),401)['error']=='authentication_required'
 legacy=api(a,'PATCH',edit,design('Legacy'));assert legacy['design_revision']==2
 saved=api(a,'GET',path)['activities'][0];assert saved['page_design']['widgets'][0]['label']=='Legacy' and saved['design_revision']==2
 next1=api(a,'PATCH',edit,{**design('First','#DDEEFF'),'expected_design_revision':2});assert next1['design_revision']==3
 conflict=api(b,'PATCH',edit,{**design('Stale'),'expected_design_revision':2},409)
 assert conflict['error']=='design_revision_conflict' and conflict['current_design_revision']==3
 current=api(a,'GET',path)['activities'][0];assert current['page_design']['widgets'][0]['label']=='First' and current['design_revision']==3
 for bad in (None,0,-1,1.5,'3',True,{},[],2**60):
  response=api(a,'PATCH',edit,{**design('Bad'),'expected_design_revision':bad},400)
  assert response['error']=='invalid_design_revision',bad
 assert api(a,'GET',path)['activities'][0]['design_revision']==3
 invalid=design('Invalid');invalid['page_design']['widgets'][0]['position']['width']=-5
 assert api(a,'PATCH',edit,{**invalid,'expected_design_revision':3},400)['error']=='invalid_page_design'
 assert api(a,'GET',path)['activities'][0]['design_revision']==3
 duplicate=design('Duplicate');duplicate['page_design']['widgets'].append(dict(duplicate['page_design']['widgets'][0]))
 assert api(a,'PATCH',edit,{**duplicate,'expected_design_revision':3},400)['error']=='invalid_page_design'
 invalid_style=design('Invalid style');invalid_style['page_design']['widgets'][0]['style']={'strokeDash':'not-a-pattern'}
 assert api(a,'PATCH',edit,{**invalid_style,'expected_design_revision':3},400)['error']=='invalid_page_design'
 # Legitimate new editable shape style survives the database roundtrip.
 valid=design('Styled','#123456');valid['page_design']['widgets'][0]['style']={'fillNone':True,'strokeWidth':2.5,'strokeDash':'dot','strokeColor':'#445566'}
 styled=api(a,'PATCH',edit,{**valid,'expected_design_revision':3});assert styled['design_revision']==4
 assert api(a,'GET',path)['activities'][0]['page_design']['widgets'][0]['style']==valid['page_design']['widgets'][0]['style']
 # A separate activity starts its own revision, unaffected by this page.
 second=api(a,'POST',path+'/pages',{'title':'Independent'},201)
 second_path=f'{path}/activities/{second["id"]}/design'
 assert next(x for x in api(a,'GET',path)['activities'] if x['id']==second['id'])['design_revision']==1
 assert api(b,'PATCH',second_path,{**design('Second'),'expected_design_revision':1})['design_revision']==2
 assert api(a,'GET',path)['activities'][0]['design_revision']==4
 # Concurrent writers with identical versions: PostgreSQL FOR UPDATE must serialize.
 def save(c,label):
  req={**design(label),'expected_design_revision':4}
  data=json.dumps(req).encode()
  request=Request(BASE+edit,data=data,method='PATCH',headers={'Content-Type':'application/json',**({'X-Quorivio-Load-Token':TOKEN} if TOKEN else {})})
  try:
   with c.open(request,timeout=20) as response:return response.status,json.loads(response.read())
  except HTTPError as e:return e.code,json.loads(e.read())
 with ThreadPoolExecutor(max_workers=2) as pool:
  f1=pool.submit(save,a,'Winner A');f2=pool.submit(save,b,'Winner B')
  results=[f1.result(),f2.result()]
 assert sorted(s for s,_ in results)==[200,409],results
 assert next(x for s,x in results if s==200)['design_revision']==5
 assert next(x for s,x in results if s==409)['current_design_revision']==5
 winner=api(a,'GET',path)['activities'][0]
 assert winner['design_revision']==5 and winner['page_design']['widgets'][0]['label'] in ('Winner A','Winner B')
 assert api(b,'PATCH',edit,{**design('Retry'),'expected_design_revision':5})['design_revision']==6
 assert api(a,'GET',path)['activities'][0]['page_design']['widgets'][0]['label']=='Retry'
 # Closed sessions never accept authoring, even with a current revision.
 api(a,'POST',path+'/status',{'status':'closed'})
 assert api(b,'PATCH',edit,{**design('Closed'),'expected_design_revision':6},409)['error']=='session_closed'
 assert api(a,'GET',path)['activities'][0]['design_revision']==6
 print('PASS PostgreSQL editor CAS: authenticated persistence, 10 invalid versions, stale conflict, validation, shape fidelity, independent pages, simultaneous writers, retry and closed-session guard')

if __name__=='__main__':run()
