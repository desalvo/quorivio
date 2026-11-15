"""Browser-launch home isolation: writable tmpfs paths and no worker credentials."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from visual_export import _browser_environment

class IsolatedBrowserEnvironment(unittest.TestCase):
    def test_browser_can_write_private_home_without_inheriting_token(self):
        with tempfile.TemporaryDirectory() as root, patch.dict(os.environ, {
            'QUORIVIO_WORKER_TOKEN': 'SENSITIVE_EPHEMERAL_WORKER_TOKEN',
            'QUORIVIO_CAPTURE_BASE_URL': 'http://example.invalid:8099',
            'DATABASE_URL': 'DO_NOT_INHERIT',
        }):
            result = _browser_environment(Path(root))
            self.assertEqual(set(result), {
                'HOME', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME',
                'XDG_RUNTIME_DIR', 'PATH', 'LANG',
            })
            for key in ('HOME', 'XDG_CONFIG_HOME', 'XDG_CACHE_HOME', 'XDG_RUNTIME_DIR'):
                folder = Path(result[key])
                self.assertTrue(folder.is_dir())
                self.assertTrue(os.access(folder, os.W_OK))
                self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
            self.assertNotIn('SENSITIVE_EPHEMERAL_WORKER_TOKEN', str(result))
            self.assertNotIn('DATABASE_URL', result)

if __name__ == '__main__':
    unittest.main()
