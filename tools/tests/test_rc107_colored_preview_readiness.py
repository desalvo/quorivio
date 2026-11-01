"""RC107: actual ANSI-styled Vite preview banner must not trigger false failure.

The CI 111954785384 logs contained a green startup with SGR sequences
around Local, the colon and the URL; all Chromium tests passed while the
RC106 readiness regex incorrectly failed. Keep error detection fail-closed.
"""
from __future__ import annotations

import unittest
from tools.ci_preview_proxy_guard import verify_preview_log

# Reconstructed from the exact styled preview banner of the failed CI run.
VITE_BANNER = (
    "> @quorivio/web@0.1.0-dev preview\n"
    "> vite preview --host 127.0.0.1 --port 5173 --strictPort\n"
    "  \x1b[32m➜\x1b[39m  \x1b[1mLocal\x1b[22m:   "
    "\x1b[36mhttp://127.0.0.1:\x1b[1m5173\x1b[22m/\x1b[39m\n"
)

class StyledVitePreview(unittest.TestCase):
    def test_real_colored_banner_passes(self):
        self.assertGreater(verify_preview_log(VITE_BANNER), 0)

    def test_uncolored_banner_passes(self):
        self.assertGreater(verify_preview_log('  ➜ Local: http://127.0.0.1:5173/\n'), 0)

    def test_plain_missing_or_wrong_host_port_fails(self):
        for value in ('', 'vite preview started',
                      '  ➜ Local: http://127.0.0.1:5174/\n',
                      '  ➜ Local: http://0.0.0.0:5173/\n'):
            with self.subTest(value=value), self.assertRaises(RuntimeError):
                verify_preview_log(value)

    def test_colored_real_socket_refusal_stays_fatal(self):
        with self.assertRaisesRegex(RuntimeError, 'failure log lines'):
            verify_preview_log(VITE_BANNER + '\x1b[31mAggregateError [ECONNREFUSED]\x1b[0m\n')

    def test_colored_proxy_error_stays_fatal(self):
        with self.assertRaises(RuntimeError):
            verify_preview_log(VITE_BANNER + '\x1b[31m[vite]\x1b[0m ws proxy error: missing upstream\n')

    def test_vite_banner_alone_has_no_false_socket_error(self):
        self.assertEqual(verify_preview_log(VITE_BANNER), 3)

if __name__ == '__main__':
    unittest.main()
