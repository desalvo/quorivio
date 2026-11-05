"""RC167: real-authenticated audience, preview and CI diagnostic parity.

Negative cases guard against ghost presenter widgets, caption leaks, CI URL
user-info attacks and the accidental publication of join secrets in artifacts.
"""
from __future__ import annotations
import ast
from types import SimpleNamespace
from urllib.parse import urlsplit
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
UI=(ROOT/'apps/web/src/main.tsx').read_text(encoding='utf8')
POLICY=(ROOT/'apps/web/src/live-slide-policy.ts').read_text(encoding='utf8')
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
SCRIPT=(ROOT/'tools/ci_browser_participant.py').read_text(encoding='utf8')
# Import only pure functions from the fixture AST: the early CI preflight runs
# before Playwright is installed and must never require network/browser packages.
fixture_ast=ast.parse(SCRIPT)
functions=[node for node in fixture_ast.body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))
           and node.name in ('validate_disposable_origin','capture')]
browser_ns={'urlsplit':urlsplit,'Path':Path,'ARTIFACTS':Path('/tmp/no-artifacts')}
exec(compile(ast.Module(body=functions,type_ignores=[]),'<isolated browser functions>','exec'),browser_ns)
browser=SimpleNamespace(validate_disposable_origin=browser_ns['validate_disposable_origin'],capture=browser_ns['capture'])

class RC167LivePreviewFidelity(unittest.TestCase):
 def test_shared_policy_is_used_in_all_projection_surfaces(self):
  self.assertIn('participantVisibleWidgets',POLICY)
  self.assertIn("'results-button', 'participant-count'",POLICY)
  self.assertIn("'line', 'shape'",POLICY)
  self.assertIn("if (widget.kind === 'qr') return widget.showTitle === true",POLICY)
  self.assertEqual(UI.count('data-show-title={widgetTitleVisible(w)}'),4)
  # RC176 introduced a third, accessible DOM-reading mode. The older two-way
  # phone/desktop selector must never regress to discarding reading-mode widgets.
  mode_selector='(audiencePortrait?audiencePhoneLayout.widgets:participantReadingMode?audienceReadingWidgets:audienceVisibleWidgets)'
  self.assertIn(mode_selector,UI)
  self.assertIn('const audienceVisibleWidgets=participantVisibleWidgets(audienceAuthoredWidgets)',UI)
  self.assertIn('const audienceReadingWidgets=participantReadingWidgets(audienceAuthoredWidgets)',UI)
  self.assertIn('const audiencePhoneLayout=participantPhoneLayout(audienceAuthoredWidgets',UI)
  self.assertIn('mobile?participantPhoneLayout(viewWidgets,viewActivity?.page_design?.mobile).widgets:participantVisibleWidgets(viewWidgets)',UI)
  self.assertIn("(w.kind==='shape'||w.kind==='line')?null:",UI)
  self.assertNotIn('CI_PRIVATE_LINE_CAPTION',UI)

 def test_negative_ghost_and_caption_mutations_fail_the_contract(self):
  broken=POLICY.replace("['results-button', 'participant-count']", "['participant-count']",1)
  self.assertNotIn("'results-button', 'participant-count'",broken)
  broken=POLICY.replace("if (LABELLESS_GRAPHICS.has(widget.kind)) return false;", "if (LABELLESS_GRAPHICS.has(widget.kind)) return true;",1)
  self.assertNotIn('if (LABELLESS_GRAPHICS.has(widget.kind)) return false;',broken)
  self.assertNotIn("(w.kind==='shape'||w.kind==='line')?(w.showTitle===false?null:",UI)
  selector='(audiencePortrait?audiencePhoneLayout.widgets:participantReadingMode?audienceReadingWidgets:audienceVisibleWidgets)'
  self.assertIn(selector,UI)
  # Mutating out the accessible mode is a contract violation even when the
  # obsolete two-way phone selector still renders something on screen.
  without_reading=UI.replace(selector,'(audiencePortrait?audiencePhoneLayout.widgets:audienceVisibleWidgets)',1)
  self.assertNotIn(selector,without_reading)
  self.assertIn('participantReadingMode?audienceReadingWidgets:',selector)

 def test_real_disposable_chromium_owns_graphics_and_privacy(self):
  for marker in ('GRAPHIC_LINE=', 'GRAPHIC_SHAPE=', 'PRESENTER_CHART=', 'PRESENTER_COUNT=',
                 'svg.widget-graphic-line','svg.widget-graphic-shape',
                 'CI_PRIVATE_LINE_CAPTION','CI_PRIVATE_SHAPE_CAPTION',
                 'presenter-only widget shell visible to audience',
                 "data-show-title','false'", "get_by_role('button',name='Diapositiva 16:9')"):
   self.assertIn(marker,SCRIPT)
  self.assertIn('python3 tools/ci_browser_participant.py',CI)

 def test_loopback_origin_rejects_userinfo_and_non_loopback(self):
  valid=browser.validate_disposable_origin
  self.assertEqual(valid('http://127.0.0.1:8080'),'http://127.0.0.1:8080')
  self.assertEqual(valid('http://localhost:5173/'),'http://localhost:5173')
  for origin in ('http://127.0.0.1:8080@external.example',
                 'http://localhost:8080@external.example',
                 'http://127.0.0.1:8080.evil.invalid',
                 'http://127.0.0.1:8080/join/secret',
                 'http://127.0.0.1:8080/?x=1',
                 'https://127.0.0.1:8080',
                 'http://127.0.0.1:8080#fragment',
                 'http://user:pw@localhost:8080',
                 'http://localhost:bad',
                 'http://localhost',
                 'http://[::1]:8080'):
   with self.subTest(origin=origin),self.assertRaises(ValueError):valid(origin)

 def test_diagnostics_do_not_write_raw_page_or_url(self):
  self.assertNotIn("await page.content()",SCRIPT)
  self.assertNotIn("'URL: '+page.url",SCRIPT)
  self.assertNotIn("repr(errors)",SCRIPT)
  self.assertIn("mask=[page.locator('.participant-access-qr')]",SCRIPT)
  self.assertIn('len(errors)',SCRIPT)
  self.assertIn('paths and response payload intentionally suppressed',SCRIPT)

 def test_early_preflight_and_inventories(self):
  self.assertIn('tools.tests.test_rc167_live_preview_fidelity',CI)
  self.assertLess(CI.index('tools.tests.test_rc167_live_preview_fidelity'),CI.index('npm install --ignore-scripts'))
  self.assertIn('python3 tools/verify_rc_cycle166_inventory.py --historical',CI)
  self.assertIn('python3 tools/verify_rc_cycle167_inventory.py',CI)

class RC167FailureArtifacts(unittest.IsolatedAsyncioTestCase):
 async def test_unsafe_join_token_and_raw_error_never_enter_diagnostics(self):
  class FakePage:
   def locator(self,selector):return object()
   async def screenshot(self,**kwargs):Path(kwargs['path']).write_bytes(b'PNG test double')
   @property
   def url(self):raise AssertionError('join URL must not be consulted')
   async def content(self):raise AssertionError('HTML must not be consulted')
  with tempfile.TemporaryDirectory() as directory:
   with patch.dict(browser_ns,{'ARTIFACTS':Path(directory)}):
    await browser.capture(FakePage(),'participant-redacted',['secret-cookie=LEAK_VALUE'])
   files=list(Path(directory).iterdir())
   self.assertEqual({file.suffix for file in files},{'.txt','.png'})
   report=(Path(directory)/'participant-redacted.txt').read_text()
   self.assertIn('Page errors (count only): 1',report)
   self.assertNotIn('LEAK_VALUE',report)
   self.assertNotIn('/join/',report)

if __name__=='__main__':unittest.main()
