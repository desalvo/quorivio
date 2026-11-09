"""RC159 early fail-closed UI and rate-budget contracts, including negative mutations."""
from __future__ import annotations
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
CSS=(ROOT/'apps/web/src/style.css').read_text(encoding='utf8')
RATING=(ROOT/'apps/web/src/rating-choices.tsx').read_text(encoding='utf8')
API=(ROOT/'apps/api/src/server.ts').read_text(encoding='utf8')
POLICY=(ROOT/'apps/api/src/api-rate-policy.ts').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

def controls_ok(ui, css):
 return all(t in ui for t in (
  "session-action-terminate\" onClick={()=>changeStatus('closed')}",
  "session-action-pause\" onClick={()=>changeStatus('paused')}",
  'session-action-reset\" title="Ritorna a non avviata:',
 )) and all(t in css for t in (
  'button.session-action-terminate{background:#ad2939',
  'button.session-action-pause{background:#b9f4ce',
  'button.session-action-reset{background:#b5e9ff',
 ))

def rating_ok(ui, rating, css):
 return all(t in ui for t in (
  'function RatingStageContent(',
  'size={widget.style?.ratingButtonSize}',
  'comment={demoRatingComments[w.id]',
  'comment={ratingComments[w.id]',
  'RatingCommentField value={comment}',
  '>Invia risposta</button>',
 )) and 'Invia risposta al widget' not in ui and all(t in rating for t in (
  'export function RatingCommentField(', 'maxLength={1000}',
  'readOnly={readOnly||!onChange}', 'aria-label="Commento facoltativo"',
 )) and '.rating-comment-input{display:block;' in css and 'background:#ffffff!important;color:#142b44!important' in css

def policy_ok(api,policy):
 return all(t in api for t in (
  'apiRateClass(req.method,req.path,uid)', 'apiRateBudget(rateClass)',
  'ON CONFLICT(client_hash,bucket) DO UPDATE SET hits=api_rate_windows.hits+1',
  'Number(r.rows[0].hits)>limit',
  "if(process.env.NODE_ENV!=='production'&&loadSecret",
  "res.status(503).json({error:'rate_limiter_unavailable'})",
 )) and all(t in policy for t in (
  "kind==='presenter-read'?360:kind==='presenter-navigation'?180:100",
  "if(!authenticatedUser)return 'default'",
  "if(method==='GET'", "if(method==='POST'",
 ))

class RC159PresenterControls(unittest.TestCase):
 def test_live_controls(self):self.assertTrue(controls_ok(UI,CSS))
 def test_live_rating_and_submit(self):self.assertTrue(rating_ok(UI,RATING,CSS))
 def test_live_policy_database_and_fail_closed(self):self.assertTrue(policy_ok(API,POLICY))
 def test_negative_colors_and_action_mapping(self):
  self.assertFalse(controls_ok(UI.replace("changeStatus('closed')","changeStatus('paused')",1),CSS))
  self.assertFalse(controls_ok(UI,CSS.replace('background:#ad2939','background:#bbff22',1)))
 def test_negative_comment_visibility(self):
  self.assertFalse(rating_ok(UI.replace('RatingCommentField value={comment}','div data-broken-comment',1),RATING,CSS))
  self.assertFalse(rating_ok(UI,RATING.replace('readOnly={readOnly||!onChange}','readOnly={false}',1),CSS))
  self.assertFalse(rating_ok(UI,RATING,CSS.replace('background:#ffffff!important;color:#142b44!important','background:black;color:white',1)))
 def test_negative_rate_guard(self):
  self.assertFalse(policy_ok(API.replace('Number(r.rows[0].hits)>limit','false',1),POLICY))
  self.assertFalse(policy_ok(API,POLICY.replace("if(!authenticatedUser)return 'default'",'// allow anyone',1)))
  self.assertFalse(policy_ok(API.replace("if(process.env.NODE_ENV!=='production'&&loadSecret",'if(loadSecret',1),POLICY))
 def test_ci_preflights_and_browser_acceptance(self):
  self.assertIn('tools.tests.test_rc159_presenter_controls',CI)
  self.assertIn('tools/ci_rc159_presenter_visual_chromium.py',CI)
  self.assertLess(CI.index('tools.tests.test_rc159_presenter_controls'),CI.index('npm ci --ignore-scripts'))

if __name__=='__main__':unittest.main()
