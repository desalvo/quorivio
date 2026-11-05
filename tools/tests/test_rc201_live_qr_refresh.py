"""RC201: live participant URLs and scannable QR symbols must rotate without reload.

These source preflights are paired with executable TypeScript state tests and the
existing disposable PostgreSQL RC71 lifecycle integration test.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = (ROOT / 'apps/web/src/main.tsx').read_text()
STATE = (ROOT / 'apps/web/src/session-qr-state.ts').read_text()
API = (ROOT / 'apps/api/src/server.ts').read_text()
CI = (ROOT / '.github/workflows/ci.yml').read_text()


class LiveQrRefresh(unittest.TestCase):
    def test_session_change_invalidates_old_pixels_before_next_response(self):
        self.assertIn("const sourceKey=accessKey?`${publicAccess?'public':'owner'}:${base}:${joinCode||''}`:''", WEB)
        self.assertIn('const shown=visibleQrTarget(target,sourceKey)', WEB)
        self.assertIn('return state.sourceKey===sourceKey?state:null', STATE)
        self.assertIn("return {...current,url:'',revision:current.url?current.revision+1:current.revision,failed:true}", STATE)
        self.assertIn('updateQrTarget(old,sourceKey,null)', WEB)

    def test_canonical_url_is_refreshed_on_event_and_timer_without_reload(self):
        self.assertIn('useSynchronizedParticipantQr(sessionId:string|undefined,joinCode:string|undefined,publicAccess=false)', WEB)
        self.assertIn('cache:\'no-store\'', WEB)
        self.assertIn('const timer=window.setInterval(()=>void refresh(),12000)', WEB)
        for action in ["window.addEventListener('focus',focus)", "window.addEventListener('online',online)", "document.addEventListener('visibilitychange',visible)"]:
            self.assertIn(action, WEB)
        self.assertIn('controller.abort()', WEB)

    def test_dashboard_and_widget_share_authoritative_qr_and_invalidate_image_cache(self):
        self.assertIn('const sessionQr=useSynchronizedParticipantQr(me?selected:undefined', WEB)
        self.assertIn('const {url,revision,failed,imageSrc}=useSynchronizedParticipantQr(sessionId,joinCode,publicAccess)', WEB)
        self.assertIn('<img key={revision} src={imageSrc}', WEB)
        self.assertIn('className="qr" src={sessionQr.url?', WEB)
        self.assertIn('className="session-presenter-qr" src={sessionQr.url?', WEB)
        self.assertIn('src={sessionQr.url?`/api/sessions/${selected}/qr?format=svg&revision=${sessionQr.revision}`:undefined}', WEB)
        self.assertIn('href={sessionQr.url}', WEB)
        self.assertNotIn('href={snap.session.join_url}', WEB)

    def test_owner_websockets_stay_open_on_reset_while_participants_are_invalidated(self):
        reset = API.split("app.post('/api/sessions/:id/reset-to-ready'", 1)[1].split("app.post('/api/sessions/:id/activities/:aid/close'", 1)[0]
        self.assertIn("join_code=$2,join_secret=$3", reset)
        self.assertIn("if((ws as any).view!=='owner')ws.close(1008,'session reset')", reset)
        self.assertIn('await broadcast(req.params.id)', reset)
        self.assertLess(reset.index('await cx.query(\'COMMIT\')'), reset.index('await broadcast(req.params.id)'))
        self.assertIn('DELETE FROM participants WHERE session_id=$1', reset)
        self.assertNotIn("for(const ws of sockets.get(req.params.id)||[])ws.close(1008,'session reset')", reset)

    def test_all_qr_origins_are_read_from_shared_settings_for_replicas(self):
        self.assertIn("SELECT value FROM platform_settings WHERE key='public_base_url'", API)
        self.assertIn('qrBrowserOrigin(await configuredQrPublicBase()', API)
        self.assertIn('${await configuredQrPublicBase()}/join/${s.join_secret}', API)
        self.assertIn("res.setHeader('Cache-Control','private, no-store')", API)
        self.assertIn("res.setHeader('Cache-Control','no-store')", API)

    def test_early_ci_checks_executable_qr_state_and_source_contracts(self):
        self.assertIn('test_rc201_live_qr_refresh', CI)
        self.assertIn('apps/web/test/session-qr-state.test.ts', CI)


if __name__ == '__main__':
    unittest.main()
