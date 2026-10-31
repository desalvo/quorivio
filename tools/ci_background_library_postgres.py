#!/usr/bin/env python3
"""Real PostgreSQL 18 / HTTP / filesystem acceptance of presenter-owned backgrounds.

Runs only against the disposable CI server after ci_portable_http.py rotates admin password.
No customer files, tokens or secrets are written to CI logs.
"""
import base64
import http.cookiejar
import json
import os
from urllib.error import HTTPError
from urllib.request import build_opener, HTTPCookieProcessor, Request
from ci_http_isolation import ci_load_headers

HOST=os.environ.get('QUORIVIO_CI_BASE_URL','http://127.0.0.1:8080')
PNG=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO6X7e8AAAAASUVORK5CYII=')

def session():return build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
def req(op,method,url,payload=None,expected=200,mime='application/json'):
 if isinstance(payload,(dict,list)):payload=json.dumps(payload).encode('utf8')
 headers={'Content-Type':mime} if payload is not None else {}
 headers.update(ci_load_headers(HOST))
 try:
  with op.open(Request(HOST+url,data=payload,headers=headers,method=method),timeout=20) as rsp:status,body=rsp.status,rsp.read()
 except HTTPError as e:status,body=e.code,e.read()
 assert status==expected,(method,url,status,expected)
 if not body:return None
 return json.loads(body) if body[:1] in (b'{',b'[') else body

def run():
 ci_load_headers(HOST)  # fail before any API request unless disposable
 a=session();email=os.environ['QUORIVIO_CI_ADMIN_EMAIL'];password=os.environ['QUORIVIO_CI_NEW_PASSWORD']
 req(a,'POST','/api/auth/login',{'email':email,'password':password})
 shared=req(a,'POST','/api/sessions',{'title':'CI background owner session'},201)['id']
 saved=req(a,'POST',f'/api/sessions/{shared}/backgrounds',PNG,201,'image/png')
 assert saved['background_id']!=saved['id']
 original=saved['background_id']
 assert req(a,'GET',f'/api/sessions/{shared}/assets/{saved["id"]}')==PNG
 assert req(a,'GET',f'/api/sessions/{shared}/backgrounds/{original}/image')==PNG
 private=req(a,'GET',f'/api/sessions/{shared}/backgrounds')
 assert any(b['id']==original and b['mine'] for b in private)
 another=req(a,'POST','/api/sessions',{'title':'CI background reuse'},201)['id']
 reused=req(a,'POST',f'/api/sessions/{another}/backgrounds/{original}/use',expected=201)
 assert reused['background_id']==original and reused['id']!=saved['id']
 assert req(a,'GET',f'/api/sessions/{another}/assets/{reused["id"]}')==PNG
 # A noncollaborating presenter cannot access this library through another session.
 b=session();collab_email='ci-background-collab@example.invalid';initial='ci-background-initial-strong-password';changed='ci-background-rotated-strong-password'
 user=req(a,'POST','/api/admin/users',{'email':collab_email,'temporary_password':initial,'role':'presenter'},201)
 req(a,'PATCH',f'/api/admin/users/{user["id"]}',{'role':'presenter','approved':True})
 req(b,'POST','/api/auth/login',{'email':collab_email,'password':initial})
 req(b,'POST','/api/auth/change-password',{'current_password':initial,'new_password':changed})
 req(b,'POST','/api/auth/login',{'email':collab_email,'password':changed})
 private_b=req(b,'POST','/api/sessions',{'title':'CI separate presenter'},201)['id']
 req(b,'POST',f'/api/sessions/{private_b}/backgrounds/{original}/use',expected=404)
 req(a,'POST',f'/api/sessions/{shared}/presenters',{'email':collab_email},201)
 offered=req(b,'GET',f'/api/sessions/{private_b}/backgrounds')
 assert any(bg['id']==original and not bg['mine'] for bg in offered)
 borrowed=req(b,'POST',f'/api/sessions/{private_b}/backgrounds/{original}/use',expected=201)
 assert borrowed['background_id']!=original
 req(a,'DELETE',f'/api/sessions/{shared}/presenters/{user["id"]}',expected=204)
 # The borrowed file is now independently owned even after revocation.
 owned=req(b,'GET',f'/api/sessions/{private_b}/backgrounds')
 assert any(bg['id']==borrowed['background_id'] and bg['mine'] for bg in owned)
 copied=req(b,'POST',f'/api/sessions/{private_b}/backgrounds/{borrowed["background_id"]}/use',expected=201)
 assert req(b,'GET',f'/api/sessions/{private_b}/assets/{copied["id"]}')==PNG
 req(b,'GET',f'/api/sessions/{shared}/backgrounds/{original}/image',expected=404)
 print('PASS presenter-owned background upload, reuse, private access, collaborator independent copy and revocation (disposable CI)')

if __name__=='__main__':run()
