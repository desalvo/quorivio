"""RC208: reopening an active owner session cannot require clearing browser cookies.

Dependency-free preflight, paired with executable Node state tests. No credentials,
tokens or session data are persisted as diagnostic artifacts.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
WEB=(ROOT/'apps/web/src/main.tsx').read_text()
RECOVERY=(ROOT/'apps/web/src/session-load-recovery.ts').read_text()
QR=(ROOT/'apps/web/src/session-qr-state.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()

class RC208SessionRecovery(unittest.TestCase):
 def test_owner_session_bootstraps_after_authentication(self):
  self.assertIn('if(!selected||!me){setSessionLoadState', WEB)
  self.assertIn('window.setTimeout(()=>controller.abort(),12000)', WEB)
  self.assertIn('window.setTimeout(()=>controller.abort(),10000)', WEB)
  self.assertIn('if(stopped||pending)return;', WEB)
  self.assertIn('setAuthRecheck(v=>v+1)', WEB)
  self.assertIn('useLive(me?selected||undefined:undefined', WEB)
  self.assertIn('isOwnerSessionSnapshot(s,selected)', WEB)
  self.assertIn('sessionSnapshotRequest(selected,controller.signal)', WEB)
  self.assertIn('if(!isOwnerSessionSnapshot(value,selected))', WEB)

 def test_transient_error_never_requires_cookie_deletion(self):
  self.assertIn("if(outcome==='expired')", WEB)
  self.assertIn("outcome==='unavailable'", WEB)
  self.assertIn("setSessionLoadState('retry')", WEB)
  self.assertIn('setSessionReload(v=>v+1)', WEB)
  self.assertIn('Torna alle sessioni', WEB)
  self.assertIn("sessionFailureForStatus(status:number|undefined)", RECOVERY)
  self.assertNotIn("document.cookie=''", WEB)

 def test_qr_timeout_and_no_stale_symbol(self):
  self.assertIn('window.setTimeout(()=>attempt.abort(),9000)', WEB)
  self.assertIn('window.clearTimeout(limit)', WEB)
  self.assertIn("controller.signal.addEventListener('abort',onStop", WEB)
  self.assertIn('updateQrTarget(old,sourceKey,null)', WEB)
  self.assertIn('const shown=visibleQrTarget(target,sourceKey)', WEB)
  self.assertIn('return state.sourceKey===sourceKey?state:null', QR)

 def test_recover_from_render_fault_without_dropping_auth(self):
  self.assertIn('class WorkspaceErrorBoundary', WEB)
  self.assertIn('componentDidCatch(){', WEB)
  self.assertIn("writeWorkspaceLocation({sessionId:'',section:'workspace',tab:'overview',pageId:''})", WEB)
  self.assertIn('window.location.assign(\'/\')', WEB)

 def test_ci_runs_early_before_dependencies(self):
  self.assertIn('test_rc208_session_recovery', CI)
  self.assertIn('apps/web/test/session-load-recovery.test.ts', CI)

if __name__=='__main__':unittest.main()
