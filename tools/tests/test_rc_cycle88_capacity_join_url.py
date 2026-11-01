"""RC88: API path-only QR links must become safe absolute loopback simulator URLs."""
import os
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from ci_capacity_500 import normalize_disposable_join_url

UUID = '123e4567-e89b-12d3-a456-426614174000'
TOKEN = 'EXAMPLE_QR_TOKEN_1234'  # harmless fake, never production credentials


class CapacityJoinUrlRC88(unittest.TestCase):
    def test_root_relative_api_link_is_normalized_to_loopback(self):
        self.assertEqual(normalize_disposable_join_url('http://127.0.0.1:8080',
                         '/join/' + TOKEN), 'http://127.0.0.1:8080/join/' + TOKEN)
        self.assertEqual(normalize_disposable_join_url('http://localhost:8081/',
                         '/join/' + TOKEN), 'http://localhost:8081/join/' + TOKEN)

    def test_same_origin_absolute_link_is_allowed_but_never_redirected(self):
        target = 'http://127.0.0.1:8080/join/' + TOKEN
        self.assertEqual(normalize_disposable_join_url('http://127.0.0.1:8080', target), target)
        with self.assertRaisesRegex(RuntimeError, 'unsafe'):
            normalize_disposable_join_url('http://127.0.0.1:8080',
                                           'http://127.0.0.1:8081/join/' + TOKEN)

    def test_external_or_tricky_origins_are_rejected(self):
        bad = ('http://external.example:8080', 'https://127.0.0.1:8080',
               'http://localhost:8080@evil.example:8080',
               'http://127.0.0.1:8080.evil.example:8080',
               'http://127.0.0.1:8080/admin', 'http://127.0.0.1:0')
        for base in bad:
            with self.subTest(base=base), self.assertRaises(RuntimeError):
                normalize_disposable_join_url(base, '/join/' + TOKEN)

    def test_cross_origin_and_invalid_join_paths_are_rejected(self):
        bad = ('//evil.example/join/' + TOKEN, 'https://evil.example/join/' + TOKEN,
               '/join/' + TOKEN + '?data=1', '/join/' + TOKEN + '#fragment',
               '/api/sessions', '/join/QR%2FSECRET', '/join/a',
               '/join/' + TOKEN + '/extra', 'join/' + TOKEN)
        for target in bad:
            with self.subTest(target=target), self.assertRaises(RuntimeError):
                normalize_disposable_join_url('http://127.0.0.1:8080', target)

    def test_real_load_cli_accepts_canonical_url_but_rejects_relative(self):
        script = ROOT / 'tools/load_500.py'
        argv = ['--session-id', UUID, '--join-url', '/join/' + TOKEN,
                '--users', '0']
        # CLI rejects the URL itself even if all other parameters are valid.
        invalid = subprocess.run([sys.executable, str(script), '--session-id', UUID,
                                  '--join-url', '/join/' + TOKEN],
                                 capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertIn('join-url must be an absolute', invalid.stderr)
        canonical = subprocess.run([sys.executable, str(script), '--session-id', UUID,
                         '--join-url', normalize_disposable_join_url('http://127.0.0.1:8080', '/join/' + TOKEN),
                         '--users', '0'], capture_output=True, text=True)
        self.assertEqual(canonical.returncode, 2)
        self.assertIn('users must be 1..500', canonical.stderr)
        self.assertNotIn('join-url must be', canonical.stderr)

    def test_capacity_runner_passes_canonical_url_not_raw_path(self):
        source = (ROOT/'tools/ci_capacity_500.py').read_text()
        self.assertIn("join_url=normalize_disposable_join_url(base, session['join_url'])", source)
        self.assertIn("'--join-url',join_url", source)
        self.assertIn('stderr=subprocess.PIPE', source)

    def test_ci_preflight_checks_this_contract_before_expensive_gates(self):
        workflow = (ROOT/'.github/workflows/ci.yml').read_text()
        marker = 'python3 -m unittest tools.tests.test_rc_cycle88_capacity_join_url -q'
        self.assertIn(marker, workflow)
        self.assertLess(workflow.index(marker), workflow.index('Install reproducibly'))


if __name__ == '__main__':
    unittest.main()
