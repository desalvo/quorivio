"""RC92 presenter projection: guarded server navigation, real view and privacy."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
API=(ROOT/'apps/api/src/server.ts').read_text()
UI=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()

class PresenterStageContract(unittest.TestCase):
 def test_first_page_is_atomically_started_without_rewinding(self):
  self.assertIn("'/api/sessions/:id/presentation/ensure-first-page'",API)
  route=API.split("app.post('/api/sessions/:id/presentation/ensure-first-page'")[1].split("app.post('/api/sessions/:id/activities/:aid/open'")[0]
  self.assertIn('FOR UPDATE',route)
  self.assertIn('if(session.current_activity_id)',route)
  # RC185+: the first *presenter-visible* page may not be the first
  # activity, while the audience may remain on a hidden question page.
  self.assertIn('SELECT id,page_design FROM activities WHERE session_id=$1 ORDER BY position,id',route)
  self.assertIn('const presenter=firstPresenterPage(pages)',route)
  self.assertIn('const audience=audienceForPresenter(pages,presenter)',route)
  self.assertIn('presenter_activity_id=$3',route)
  self.assertNotIn('ORDER BY position,id LIMIT 1',route)
  self.assertIn("status='active'",route)
  self.assertIn('opened_at=COALESCE(opened_at,now())',route)
  self.assertIn('await broadcast(req.params.id)',route)
 def test_concurrent_arrows_guard_against_stale_page(self):
  self.assertIn('expected_current_activity_id',API)
  self.assertIn('page_changed_by_another_presenter',API)
  self.assertIn('pending.current=true',UI)
  self.assertIn('pending.current=false',UI)
 def test_controls_are_presenter_only_and_update_server(self):
  self.assertIn('function PresenterLiveScreen(',UI)
  self.assertIn('setVerified(true)',UI)
  self.assertIn("request<Snapshot>(`/sessions/${encodeURIComponent(sessionId)}`)",UI)
  self.assertIn('verified&&<>',UI)
  self.assertIn('presenter-slide-navigation',UI)
  self.assertIn('Pagina precedente',UI)
  self.assertIn('Pagina successiva',UI)
  self.assertIn('changePage(-1)',UI)
  self.assertIn('changePage(1)',UI)
  self.assertIn('/activities/${encodeURIComponent(target.id)}/open',UI)
  self.assertIn('joinPath?<main',UI)
  self.assertNotIn('presenter-slide-navigation',UI.split('joinPath?<main')[1].split('publicPath?<PresenterLiveScreen')[0])
 def test_fullscreen_and_tactile_mobile(self):
  self.assertIn('stageRef.current?.requestFullscreen()',UI)
  self.assertIn('document.exitFullscreen()',UI)
  self.assertIn("document.addEventListener('fullscreenchange'",UI)
  self.assertIn('presenterKeyboardDirection(event)',UI)
  self.assertIn("(hover:none),(pointer:coarse)",CSS)
  self.assertIn('.presenter-nav-zone:hover .presenter-nav-arrow',CSS)
  self.assertIn('.presenter-stage:fullscreen',CSS)

if __name__=='__main__':unittest.main()
