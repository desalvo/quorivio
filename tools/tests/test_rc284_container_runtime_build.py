"""RC284: ensure the production image RUN layer is a real shell continuation.

Docker / Podman / KIND depend on this shared Dockerfile; a literal escaped
newline previously turned into the nonexistent Alpine package 'n'.
"""
from __future__ import annotations
import shlex
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCKERFILE = ROOT / 'Dockerfile'


def assert_runtime_install_contract(source: str) -> None:
    expected = 'RUN apk add --no-cache postgresql18-client tar \\\n    && npm install --omit=dev --no-audit --no-fund \\'
    assert expected in source, 'Runtime package install must use a real Dockerfile line continuation'
    runtime = source.split('FROM node:22-alpine3.23\n', 1)[-1]
    assert 'USER node' in runtime, 'Production runtime must remain nonroot'
    assert 'test ! -e /usr/local/bin/npm' in runtime, 'Runtime npm removal must remain enabled'
    command = source[source.index('RUN apk add --no-cache postgresql18-client tar '):].split('\nCOPY --from=build', 1)[0]
    shell = command[len('RUN '):].replace('\\\n', ' ')
    # Read the apk portion as shell tokens, not raw substring matching. A
    # mistaken escaped newline appears here as an extra 'n' package argument.
    apk = shlex.split(shell.split('&&', 1)[0])
    assert apk == ['apk', 'add', '--no-cache', 'postgresql18-client', 'tar'], apk
    check = subprocess.run(['/bin/sh', '-n'], input=shell, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           check=False)
    assert check.returncode == 0, f'Runtime RUN shell syntax invalid: {check.stderr}'


class RC284ContainerBuild(unittest.TestCase):
    def test_production_runtime_run_has_valid_shell_continuation(self):
        assert_runtime_install_contract(DOCKERFILE.read_text(encoding='utf8'))

    def test_literal_backslash_n_would_restore_ci_failure(self):
        original = DOCKERFILE.read_text(encoding='utf8')
        expected = 'tar \\\n    && npm install'
        self.assertIn(expected, original)
        broken = original.replace(expected, r'tar \n    && npm install', 1)
        with self.assertRaises(AssertionError):
            assert_runtime_install_contract(broken)

    def test_runtime_hardening_must_not_be_removed(self):
        original = DOCKERFILE.read_text(encoding='utf8')
        for old, new in (('USER node', 'USER root'),
                         ('test ! -e /usr/local/bin/npm', 'true')):
            self.assertIn(old, original)
            with self.subTest(changed=old), self.assertRaises(AssertionError):
                assert_runtime_install_contract(original.replace(old, new, 1))

    def test_build_stage_and_runtime_are_present(self):
        source = DOCKERFILE.read_text(encoding='utf8')
        self.assertIn('FROM node:22-alpine3.23 AS build', source)
        self.assertIn('RUN npm run build', source)
        self.assertIn('COPY --from=build /app/apps/api/dist apps/api/dist', source)
        self.assertIn('COPY --from=build /app/apps/web/dist apps/web/dist', source)


if __name__ == '__main__':
    unittest.main()
