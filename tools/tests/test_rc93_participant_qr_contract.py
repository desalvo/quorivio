"""RC93 QR access contract: code and text resolve to one participation URL."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
WEB = (ROOT / 'apps/web/src/main.tsx').read_text()
API = (ROOT / 'apps/api/src/server.ts').read_text()
CSS = (ROOT / 'apps/web/src/style.css').read_text()


class ParticipantQrContract(unittest.TestCase):
    def test_default_label_and_subject(self):
        self.assertIn("kind==='qr'?'Accesso partecipanti'", WEB)
        self.assertIn('data-qr-target="participants"', WEB)
        self.assertIn('URL di accesso dei partecipanti', WEB)

    def test_url_is_supplied_by_server_not_guessed_from_code(self):
        self.assertIn("const endpoint=publicAccess?`${base}/qr-url`:`${base}/qr?format=json`", WEB)
        self.assertIn('setUrl(value.url)', WEB)
        self.assertNotIn('location.origin}/join/${joinCode}', WEB)

    def test_editor_rehearsal_presenter_and_participants_share_widget(self):
        self.assertIn("if(kind==='qr')return <ParticipantAccessQr", WEB)
        self.assertIn("w.kind==='qr'?<ParticipantAccessQr", WEB)
        self.assertIn('joinCode={snap.session.join_code} onUpload=', WEB)
        self.assertIn('joinCode={joinCode} widget=', WEB)
        self.assertIn('publicAccess widget={w}', WEB)
        self.assertIn('widget={w} activity={activity}', WEB)

    def test_owner_qr_json_and_svg_share_same_url(self):
        self.assertIn("req.query.format==='json'?'json'", API)
        self.assertIn("if(type==='json'){res.json({url});return}", API)
        self.assertIn("QRCode.toString(url,{type:'svg',margin:2})", API)
        self.assertIn("res.setHeader('Cache-Control','private, no-store')", API)

    def test_public_qr_json_and_svg_share_url_policy_and_active_gate(self):
        qr = API[API.index("app.get('/api/join/:code/qr.svg'"):API.index('// Read-only participation recovery:')]
        self.assertIn("app.get('/api/join/:code/qr-url'", qr)
        self.assertEqual(qr.count('await publicSession(req.params.code)'), 2)
        self.assertEqual(qr.count('${publicBase}/join/${s.join_secret}'), 2)
        self.assertIn("res.setHeader('Cache-Control','no-store')", qr)
        self.assertIn('QRCode.toString(url', qr)

    def test_display_under_scannable_image_with_wrapping(self):
        block = WEB[WEB.index('function ParticipantAccessQr('):WEB.index('function ProjectionWidgetContent(')]
        self.assertLess(block.index('<img src={imageSrc}'), block.index('className="participant-qr-url"'))
        self.assertIn('overflow-wrap:anywhere', CSS)
        self.assertIn('.participant-access-qr', CSS)
        self.assertIn('if(!controller.signal.aborted)', block)


if __name__ == '__main__':
    unittest.main()
