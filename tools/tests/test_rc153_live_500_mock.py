"""Local mock-only HTTP integration of the real 500-answer CLI; never accesses a real server."""
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
import asyncio
import importlib.util
import json
import os
import unittest
from unittest.mock import patch
from uuid import uuid4

try:
 from aiohttp import web
except ImportError:
 web=None
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('live_500_answers',ROOT/'tools/live_500_answers.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

@unittest.skipUnless(web is not None,'Requires aiohttp optional integration dependency')
class RC153MockAnswerLoad(unittest.IsolatedAsyncioTestCase):
 async def asyncSetUp(self):
  self.sid=str(uuid4());self.aid=str(uuid4());self.code='demo_mock_123456';self.voters=set();self.joined=set();self.fake_bad_report=False;self.presence=set();self.observers=set();self.reset_calls=0;self.status='active';self.current_activity=self.aid
  async def sessions(req):
   return web.json_response({'items':[{'id':self.sid,'demo_template_key':mod.DEMO_KEY,'access_role':'owner','join_url':'/join/'+self.code}], 'total':1})
  async def snapshot(req):
   return web.json_response({'session':{'id':self.sid,'demo_template_key':mod.DEMO_KEY,'status':self.status,'current_activity_id':self.current_activity,'join_url':'/join/'+self.code},'activities':[{'id':self.aid,'type':'poll','title':mod.DEMO_QUESTION,'options':[{'id':k,'label':k} for k in sorted(mod.OPTIONS)],'page_design':{'widgets':[{'id':mod.WIDGET_ID,'kind':'question','answerMode':'single','options':[{'id':k,'label':k} for k in sorted(mod.OPTIONS)]}]}}]})
  async def report(req):
   valid=len(self.voters) - (1 if self.fake_bad_report and self.voters else 0)
   if not valid:return web.json_response([])
   return web.json_response([{'activity_id':self.aid,'widget_id':mod.WIDGET_ID,'question_id':'','revision':1,'answer_mode':'single','responses':valid}])
  async def join_get(req):
   return web.json_response({'session':{'id':self.sid},'activity':{'id':self.current_activity}})
  async def join_post(req):
   info=await req.json();name=info.get('pseudonym')
   if not name or name in self.joined:return web.json_response({'error':'invalid_join'},status=400)
   self.joined.add(name)
   r=web.json_response({'ok':True});r.set_cookie('q_part_'+self.sid,name,path='/')
   return r
  async def answer(req):
   who=req.cookies.get('q_part_'+self.sid,'')
   data=await req.json()
   if not who or who not in self.joined or data.get('question_id')!='' or data.get('option_id') not in mod.OPTIONS:
    return web.json_response({'error':'invalid_answer'},status=400)
   dup=who in self.voters
   self.voters.add(who)
   return web.json_response({'ok':True,'already_submitted':dup})
  async def reset(req):
   self.reset_calls+=1
   if (await req.json()).get('confirmation')!='RESET_SESSION_RESULTS':return web.json_response({'error':'confirm'},status=400)
   self.voters.clear();self.joined.clear();self.status='ready';self.current_activity=None;self.code='demo_new_mock_12345678'
   return web.json_response({'ok':True,'status':'ready'})
  async def status(req):
   self.status=(await req.json())['status']
   return web.json_response({'ok':True})
  async def open_question(req):
   self.current_activity=self.aid
   return web.json_response({'ok':True})
  async def live(req):
   ws=web.WebSocketResponse(heartbeat=20);await ws.prepare(req)
   cookie=req.cookies.get('q_part_'+self.sid,'')
   if cookie:
    self.presence.add(cookie)
    await ws.send_json({'type':'snapshot','data':{'session':{'id':self.sid}}})
   else:
    self.observers.add(ws)
    await ws.send_json({'type':'snapshot','data':{'connected_participants':len(self.presence)}})
   for observer in list(self.observers):
    if not observer.closed:
     await observer.send_json({'type':'snapshot','data':{'connected_participants':len(self.presence)}})
   try:
    async for _ in ws:pass
   finally:
    if cookie:self.presence.discard(cookie)
    else:self.observers.discard(ws)
   return ws
  app=web.Application()
  app.router.add_get('/api/sessions',sessions)
  app.router.add_get('/live',live)
  app.router.add_post('/api/sessions/{sid}/status',status)
  app.router.add_post('/api/sessions/{sid}/activities/{aid}/open',open_question)
  app.router.add_post('/api/sessions/{sid}/reset-to-ready',reset)
  app.router.add_get('/api/sessions/{sid}',snapshot)
  app.router.add_get('/api/sessions/{sid}/widget-answers',report)
  app.router.add_get('/api/join/{code}',join_get)
  app.router.add_post('/api/join/{code}',join_post)
  app.router.add_post('/api/join/{code}/activities/{aid}/widgets/{wid}/respond',answer)
  self.runner=web.AppRunner(app,access_log=None);await self.runner.setup()
  self.site=web.TCPSite(self.runner,'127.0.0.1',0);await self.site.start()
  self.port=self.site._server.sockets[0].getsockname()[1]
 async def asyncTearDown(self):
  await self.runner.cleanup()
 async def test_25_independent_voters_and_database_delta(self):
  args=['--base-url',f'http://127.0.0.1:{self.port}','--confirm-host','127.0.0.1',
        '--confirm-run','--users','25','--concurrency','20','--ramp-seconds','0']
  out=StringIO()
  with patch.dict(os.environ,{'QUORIVIO_LOAD_PRESENTER_COOKIE':'q_auth='+'A'*50,'QUORIVIO_LOAD_TEST_TOKEN':'B'*40}), redirect_stdout(out):
   await mod.main(args)
  data=json.loads(out.getvalue())
  self.assertTrue(data['passed'])
  self.assertEqual(data['server_confirmed_new_responses'],25)
  self.assertEqual(data['joined_new'],25)
  self.assertEqual(len(self.joined),25)
  self.assertEqual(len(self.voters),25)
  self.assertNotIn(self.code,out.getvalue())
  self.assertNotIn('A'*50,out.getvalue())
 async def test_500_real_http_submissions_against_disposable_mock(self):
  args=['--base-url',f'http://127.0.0.1:{self.port}','--confirm-host','127.0.0.1',
        '--confirm-run','--users','500','--concurrency','80','--ramp-seconds','0']
  out=StringIO()
  with patch.dict(os.environ,{'QUORIVIO_LOAD_PRESENTER_COOKIE':'q_auth='+'A'*50,'QUORIVIO_LOAD_TEST_TOKEN':'B'*40}), redirect_stdout(out):
   await mod.main(args)
  result=json.loads(out.getvalue())
  self.assertTrue(result['passed'])
  self.assertEqual(result['responses_acknowledged'],500)
  self.assertEqual(result['server_confirmed_new_responses'],500)
  self.assertEqual(len(self.voters),500)
  self.assertEqual(len(self.joined),500)

 async def test_presenter_can_observe_every_connected_person_via_websocket(self):
  args=['--base-url',f'http://127.0.0.1:{self.port}','--confirm-host','127.0.0.1',
        '--confirm-run','--users','7','--concurrency','7','--ramp-seconds','0',
        '--live-presence','--hold-seconds','0.6']
  out=StringIO()
  with patch.dict(os.environ,{'QUORIVIO_LOAD_PRESENTER_COOKIE':'q_auth='+'A'*50,'QUORIVIO_LOAD_TEST_TOKEN':'B'*40}),redirect_stdout(out):
   await mod.main(args)
  report=json.loads(out.getvalue())
  self.assertTrue(report['passed'])
  self.assertEqual(report['presenter_peak_connected'],7)
  self.assertEqual(report['responses_acknowledged'],7)
  self.assertEqual(len(self.presence),0)
  self.assertNotIn(self.code,out.getvalue())

 async def test_reset_rotates_join_code_and_allows_rerun(self):
  # The official demo is reset via the normal owner's session lifecycle.
  args=['--base-url',f'http://127.0.0.1:{self.port}','--confirm-host','127.0.0.1',
        '--confirm-run','--users','4','--concurrency','4','--ramp-seconds','0',
        '--reset-before','--open-test-question']
  out=StringIO()
  with patch.dict(os.environ,{'QUORIVIO_LOAD_PRESENTER_COOKIE':'q_auth='+'A'*50,'QUORIVIO_LOAD_TEST_TOKEN':'B'*40}),redirect_stdout(out):
   await mod.main(args)
  self.assertEqual(self.reset_calls,1)
  self.assertEqual(len(self.voters),4)
  self.assertEqual(self.status,'active')
  self.assertEqual(json.loads(out.getvalue())['server_confirmed_new_responses'],4)

 async def test_mismatched_server_report_fails_closed(self):
  self.fake_bad_report=True
  args=['--base-url',f'http://127.0.0.1:{self.port}','--confirm-host','127.0.0.1',
        '--confirm-run','--users','3','--concurrency','3','--ramp-seconds','0']
  out=StringIO()
  # Report intentionally subtracts one only *after* a vote exists.
  with patch.dict(os.environ,{'QUORIVIO_LOAD_PRESENTER_COOKIE':'q_auth='+'A'*50,'QUORIVIO_LOAD_TEST_TOKEN':'B'*40}), redirect_stdout(out):
   with self.assertRaises(SystemExit) as error:await mod.main(args)
  self.assertEqual(error.exception.code,2)
  self.assertFalse(json.loads(out.getvalue())['passed'])

if __name__=='__main__':unittest.main()
