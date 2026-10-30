"""Fail-closed local shell/CI contract checks for the opt-in rootless Podman job.

Actual Podman image-build and PostgreSQL runtime acceptance is GitHub-only.
The static tests are intentionally NOT counted as operational acceptance.
"""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/ci_rootless_podman_smoke.sh'
WORKFLOW = ROOT / '.github/workflows/ci.yml'


class RootlessPodmanSmoke(unittest.TestCase):
    def test_bash_syntax(self):
        result = subprocess.run(['bash', '-n', str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_arguments_are_rejected_before_engine_is_called(self):
        for args in ((), ('x', 'arm64'), ('oops;rm -rf',), ('',)):
            with self.subTest(args=args):
                result = subprocess.run(['bash', str(SCRIPT), *args], capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stderr)

    def test_missing_engine_fails_without_claiming_acceptance(self):
        with tempfile.TemporaryDirectory() as temporary:
            # bash remains available via absolute path; PATH has no Podman.
            result = subprocess.run(['/bin/bash', str(SCRIPT), 'quorivio:ci-rootless'],
                                    env={'PATH': temporary}, capture_output=True, text=True)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertIn('rootless Podman binary missing', result.stderr)
        self.assertNotIn('PASS', result.stdout)

    def test_rootful_engine_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            fake = Path(temporary) / 'podman'
            fake.write_text('#!/bin/sh\nif [ "$1" = info ]; then echo false; exit 0; fi\nexit 79\n')
            fake.chmod(0o755)
            result = subprocess.run(['/bin/bash', str(SCRIPT), 'quorivio:ci-rootless'],
                                    env={**os.environ, 'PATH': temporary + ':' + os.environ.get('PATH', '')},
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn('rootless Podman is required', result.stderr)

    def test_remote_socket_environment_is_rejected(self):
        if os.getuid() == 0:
            self.skipTest('rootful check takes precedence when tests run as root')
        with tempfile.TemporaryDirectory() as temporary:
            fake = Path(temporary) / 'podman'
            fake.write_text('#!/bin/sh\nif [ "$1" = info ]; then echo true; exit 0; fi\nexit 79\n')
            fake.chmod(0o755)
            result = subprocess.run(['/bin/bash', str(SCRIPT), 'quorivio:ci-rootless'],
                                    env={**os.environ, 'PATH': temporary + ':' + os.environ.get('PATH', ''),
                                         'CONTAINER_HOST': 'tcp://example.invalid:123'},
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 4, result.stderr)
        self.assertIn('remote container engine', result.stderr)

    def test_application_and_nonroot_guards_are_mandatory(self):
        source = SCRIPT.read_text()
        for required in ('set -Eeuo pipefail', 'podman info --format', 'id -u',
                         'CONTAINER_HOST', 'DOCKER_HOST', 'PODMAN_HOST',
                         'podman network create --internal', 'postgres:18-alpine',
                         'process.getuid()===0', '/app/apps/api/dist/server.js',
                         '/app/apps/web/dist/index.html', '/usr/local/bin/npm',
                         '/api/health/ready', '/api/health/live', 'trap cleanup EXIT',
                         'podman rm -f', 'podman network rm'):
            self.assertIn(required, source)
        self.assertNotIn('podman push', source)
        self.assertNotIn('--privileged', source)
        self.assertNotIn('--network host', source)

    def test_tmpfs_uses_podman_compatible_owner_mapping_and_fail_closed_probe(self):
        source = SCRIPT.read_text()
        # The upstream Ubuntu Podman rejects Docker-specific uid/gid tmpfs
        # options. U=true maps ownership to the image's non-root USER.
        self.assertNotIn('uid=1000', source)
        self.assertNotIn('gid=1000', source)
        self.assertIn('type=tmpfs,destination=/app/assets,', source)
        self.assertIn('tmpfs-size=268435456', source)
        self.assertIn('tmpfs-mode=0700,U=true', source)
        self.assertEqual(source.count('\"$asset_mount\"'), 2)
        self.assertIn('fs.writeFileSync(p, "ok"', source)
        self.assertIn('fs.unlinkSync(p)', source)
        self.assertIn('unprivileged assets tmpfs is not writable', source)
        self.assertLess(source.index('fs.writeFileSync'), source.index('podman run -d --name "$service"'))
        self.assertNotIn('--user 0', source)
        self.assertNotIn('--userns=host', source)

    def test_ci_is_explicitly_opt_in_and_cannot_publish(self):
        workflow = WORKFLOW.read_text()
        self.assertIn('rootless_podman_test:', workflow)
        block = workflow.split('  runtime-podman-rootless:\n', 1)[1].split('\n  publish:', 1)[0]
        self.assertIn("github.event_name == 'workflow_dispatch' && inputs.rootless_podman_test", block)
        self.assertIn('needs: validate', block)
        self.assertIn('runs-on: ubuntu-24.04', block)
        self.assertIn('podman build --format docker --pull=always', block)
        self.assertIn('bash tools/ci_rootless_podman_smoke.sh', block)
        self.assertNotIn('docker/login-action', block)
        self.assertNotIn('push:', block)


if __name__ == '__main__':
    unittest.main()
