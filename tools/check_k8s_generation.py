#!/usr/bin/env python3
"""CI acceptance of Kubernetes credential persistence without secret disclosure."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
WIZARD = ROOT / 'tools' / 'k8s_wizard.py'


def render(out: Path) -> None:
    run = subprocess.run([sys.executable, str(WIZARD), '--unattended', '--output', str(out), '--set', 'host=quorivio.example.org'], cwd=ROOT, capture_output=True, text=True)
    if run.returncode:
        raise RuntimeError('Kubernetes wizard failed (output suppressed to protect secrets)')


def fingerprints(out: Path) -> dict:
    return {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in out.rglob('*') if p.is_file()}


def main() -> int:
    with tempfile.TemporaryDirectory(prefix='quorivio-ci-k8s-') as temporary:
        a, b = Path(temporary) / 'first', Path(temporary) / 'independent'
        render(a)
        initial = fingerprints(a)
        overrides = a / 'quorivio-overrides.json'
        secrets = a / '05-app-secret.yaml'
        if not overrides.is_file() or not secrets.is_file():
            raise AssertionError('Generated credentials or Kubernetes Secret missing')
        if os.name == 'posix' and ((overrides.stat().st_mode | secrets.stat().st_mode) & 0o077):
            raise AssertionError('Generated credential files must not be group/world readable')
        render(a)
        if fingerprints(a) != initial:
            raise AssertionError('A repeat invocation changed the Kubernetes configuration or credentials')
        render(b)
        first = json.loads(overrides.read_text())
        second = json.loads((b / 'quorivio-overrides.json').read_text())
        for key in ('auth_secret', 'admin_password', 'postgres_password'):
            if not first.get(key) or not second.get(key) or first[key] == second[key]:
                raise AssertionError(f'Independent installations must receive distinct {key}')
    print('PASS: repeat generation is stable, fresh installs use unique credentials, and secrets remain private')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (AssertionError, RuntimeError) as e:
        print(f'FAIL: {e}', file=sys.stderr)
        raise SystemExit(1)
