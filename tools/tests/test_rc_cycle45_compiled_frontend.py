"""Acceptance contract for GitHub run 41110214420 (empty React #root)."""
import ast
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


class CompiledFrontendCiRegression(unittest.TestCase):
    def test_preview_script_serves_the_already_compiled_application(self):
        package = json.loads((ROOT / 'apps/web/package.json').read_text())
        self.assertIn('vite preview', package['scripts']['preview'])
        self.assertIn('--port 5173', package['scripts']['preview'])
        self.assertIn('--strictPort', package['scripts']['preview'])
        self.assertNotIn('vite --host 0.0.0.0', package['scripts']['preview'])

    def test_full_editor_uses_production_assets_after_build(self):
        workflow = (ROOT / '.github/workflows/ci.yml').read_text()
        step = workflow[workflow.index('- name: Chromium editor UI acceptance (opt-in)'):workflow.index('- name: Upload Chromium failure diagnostics')]
        self.assertIn('npm run preview -w @quorivio/web', step)
        self.assertNotIn('npm run dev:web', step)
        self.assertLess(workflow.index('run: npm run build'), workflow.index('npm run preview -w @quorivio/web'))
        self.assertLess(step.index('python3 tools/ci_built_frontend_asset_probe.py'), step.index('python3 tools/ci_browser_editor.py'))
        self.assertIn('preview_pid=$!', step)
        self.assertIn('kill "$preview_pid"', step)

    def test_real_browser_asset_probe_detects_missing_bundle(self):
        src = (ROOT / 'tools/ci_built_frontend_asset_probe.py').read_text()
        ast.parse(src)
        for fragment in ("'/assets/'", "'/src/main.tsx'", "'/@vite/client'", "'JS'", "'#root .app'", "'pageerror'", "'requestfailed'"):
            self.assertIn(fragment, src)
        self.assertIn("urlsplit(BASE).hostname in ('127.0.0.1', 'localhost')", src)
        self.assertNotIn('page_error_details=', src)  # no private errors in logs

    def test_editor_waits_for_real_mount_and_not_an_optimizer_reload(self):
        src = (ROOT / 'tools/ci_browser_editor.py').read_text()
        ast.parse(src)
        self.assertIn("await page.locator('#root .app').wait_for(state='visible'", src)
        self.assertNotIn("await page.reload(wait_until='domcontentloaded')", src.split("async def await_frontend_mount",1)[1].split("async def main",1)[0])
        self.assertIn('asset_http=', src)
        self.assertLess(src.index('await await_frontend_mount(page,errors)'), src.index('await acknowledge_functional_cookie_notice(page)'))


if __name__ == '__main__':
    unittest.main()
