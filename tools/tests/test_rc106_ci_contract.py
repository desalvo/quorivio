"""RC106 regression: no stale inline context drawer and no ignored WS proxy errors."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
WEB = (ROOT/'apps/web/src/main.tsx').read_text(encoding='utf-8')
VITE = (ROOT/'apps/web/vite.config.ts').read_text(encoding='utf-8')
CI = (ROOT/'.github/workflows/ci.yml').read_text(encoding='utf-8')
from tools.ci_preview_proxy_guard import verify_preview_log

class RC106Gate(unittest.TestCase):
    def test_preview_proxy_is_offline_not_dev_proxy(self):
        self.assertIn("'/live': {target: 'ws://localhost:8080', ws: true}", VITE)
        self.assertIn('preview: {proxy: {}}', VITE)
        self.assertIn('npm run preview -w @quorivio/web', CI)

    def test_context_panel_remains_draggable_portalled_and_layout_independent(self):
        self.assertIn('pageContextOpen&&<EditorFloatingWindow portal placement="page" className="editor-context-drawer"', WEB)
        self.assertIn('return portal?createPortal(', WEB)
        self.assertIn('document.body):content', WEB)
        self.assertIn("closest('.palette-ribbon-head,.editor-drawer-heading')", WEB)
        self.assertNotIn('pageContextOpen&&<section className="editor-context-drawer"', WEB)

    def test_ws_refusal_is_fatal_even_if_browser_tests_pass(self):
        for error in ('AggregateError [ECONNREFUSED]', '[vite] ws proxy error:',
                      'proxy error: upstream missing', 'EHOSTUNREACH'):
            with self.subTest(error=error), self.assertRaises(RuntimeError):
                verify_preview_log('  ➜  Local: http://127.0.0.1:5173/\n'+error)

    def test_startup_must_be_evidenced_and_real_preview_can_pass(self):
        with self.assertRaises(RuntimeError):
            verify_preview_log('nothing started')
        self.assertGreater(verify_preview_log('  ➜  Local: http://127.0.0.1:5173/\nBrowser ready'),0)

    def test_guard_applies_even_when_chromium_step_exits_early(self):
        self.assertIn('trap cleanup_preview EXIT', CI)
        self.assertIn('python3 tools/ci_preview_proxy_guard.py /tmp/quorivio-ci-preview.log', CI)
        self.assertIn('rc=$?', CI)
        self.assertIn('exit "$rc"', CI)

if __name__=='__main__': unittest.main()
