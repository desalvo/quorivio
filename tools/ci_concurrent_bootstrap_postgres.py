#!/usr/bin/env python3
"""Acceptance: TWO simultaneous Quorivio processes on one fresh PostgreSQL 18 DB.

Run only inside disposable GitHub CI. Creates a named temporary database owned by
CI and drops it afterwards; leaves the normal integration database untouched.
No secrets or raw application/PostgreSQL logs are printed.
"""
from __future__ import annotations
import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

DB = 'quorivio_bootstrap_ci'
PORTS = (19081, 19082)
BASE = 'postgresql://quorivio:ci-only-secret@127.0.0.1:5432/'

def psql(statement: str, database: str = 'postgres') -> str:
    env = {**os.environ, 'PGPASSWORD': 'ci-only-secret', 'PGCONNECT_TIMEOUT': '5'}
    try:
        proc = subprocess.run(['psql', '-X', '-v', 'ON_ERROR_STOP=1', '-h', '127.0.0.1',
                               '-U', 'quorivio', '-d', database, '-A', '-t', '-c', statement],
                              env=env, text=True, capture_output=True, timeout=25)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError('Disposable PostgreSQL command unavailable') from exc
    if proc.returncode:
        raise RuntimeError('Disposable PostgreSQL command failed (output redacted)')
    return proc.stdout.strip()


def ready(port: int) -> bool:
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/health/ready',timeout=2) as response:
            return response.status == 200 and b'"ok"' in response.read(256)
    except (OSError, urllib.error.HTTPError):
        return False


def execute() -> None:
    # The fixed DB identifier is intentionally not configurable by untrusted CI input.
    processes: list[subprocess.Popen] = []
    logs = []
    created = False
    try:
        psql(f'DROP DATABASE IF EXISTS {DB} WITH (FORCE)')
        psql(f'CREATE DATABASE {DB}')
        created = True
        with tempfile.TemporaryDirectory(prefix='quorivio-ci-startup-') as tmp:
            for port in PORTS:
                path = Path(tmp) / f'{port}.log'
                logfile = path.open('w+', encoding='utf8')
                logs.append(logfile)
                env = {**os.environ,
                    'DATABASE_URL': BASE + DB, 'NODE_ENV': 'production',
                    'PORT': str(port), 'PUBLIC_BASE_URL': f'http://127.0.0.1:{port}',
                    'AUTH_SECRET': 'ci-only-bootstrap-lock-secret-long-enough-2026',
                    'ADMIN_EMAIL': 'bootstrap-ci@example.invalid',
                    'ADMIN_PASSWORD': 'bootstrap-ci-admin-password-long-123',
                    'QUORIVIO_ASSET_DIR': str(Path(tmp)/'assets'),
                    'QUORIVIO_CONVERSION_DIR': str(Path(tmp)/'conversions')}
                processes.append(subprocess.Popen(['node', 'apps/api/dist/server.js'],
                      cwd=Path(__file__).resolve().parents[1], env=env,
                      stdout=logfile, stderr=subprocess.STDOUT))
            deadline = time.monotonic() + 150
            while time.monotonic() < deadline:
                if all(ready(port) for port in PORTS):
                    break
                if any(p.poll() is not None for p in processes):
                    raise RuntimeError('Concurrent server bootstrap process exited before readiness')
                time.sleep(.5)
            else:
                raise RuntimeError('Concurrent bootstrap did not reach readiness')
            # Partial provisioning or one duplicate administrator must FAIL.
            query = "SELECT (SELECT count(*) FROM users WHERE role='platform_admin' AND is_primary_admin=true)::text || ':' || (SELECT count(*) FROM organizations)::text || ':' || (SELECT count(*) FROM users)::text"
            if psql(query, DB) != '1:1:1':
                raise RuntimeError('Concurrent bootstrap produced missing or duplicate default identities')
            # Ensure that both processes are independently serving after the lock releases.
            if not all(p.poll() is None and ready(port) for p, port in zip(processes, PORTS)):
                raise RuntimeError('Concurrent bootstrap lost API readiness after provisioning')
            print('PASS PostgreSQL 18: simultaneous fresh-schema API bootstrap, one atomic admin, two ready replicas')
    finally:
        for p in processes:
            if p.poll() is None:
                p.send_signal(signal.SIGTERM)
        for p in processes:
            try:
                p.wait(timeout=20)
            except subprocess.TimeoutExpired:
                p.kill()
                p.wait(timeout=10)
        for stream in logs:
            stream.close()
        if created:
            psql(f'DROP DATABASE IF EXISTS {DB} WITH (FORCE)')


if __name__ == '__main__':
    try:
        execute()
    except RuntimeError as exc:
        print('FAIL CI concurrent bootstrap: ' + str(exc),file=sys.stderr)
        sys.exit(1)
