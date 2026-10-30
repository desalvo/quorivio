#!/usr/bin/env python3
"""Fail early if a workflow-referenced source checksum inventory is missing.

The CI must not reach expensive PostgreSQL/Chromium/ClamAV acceptance before
confirming that every historical checksum receipt is present *in Git*. The
original historical bytes are not regenerated or revised by this guard.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = '.github/workflows/ci.yml'
COMMAND = re.compile(r'^\s*python3 tools/(verify_rc_cycle\d+_inventory\.py)(?:\s+(--historical))?\s*$', re.M)
MANIFEST = re.compile(r"^MANIFEST\s*=\s*'([^']+)'", re.M)
# Byte-for-byte originals recovered from the previous cumulative archives.
RECOVERED_RECEIPTS = {
    'docs/validation/RC_CYCLE42_PACKAGE_INVENTORY_20261030.json':
        ''.join(('dcb77af5', '59e66a61', 'd950ce37', '77aabcc4', '2a4de61f', '5db1af18', '1d9b9c44', '07a78950')),
    'docs/validation/RC_CYCLE43_PACKAGE_INVENTORY_20261030.json':
        ''.join(('109cfa85', '3e83d2e8', '32fbf975', '495ff6f6', '97a36d2e', 'f7e89d71', '6579a6ef', '4b4030a3')),
}


def verify_references(root: Path = ROOT, workflow: str | None = None,
                      enforce_git: bool = True) -> int:
    if workflow is None:
        workflow = (root / WORKFLOW).read_text(encoding='utf-8')
    commands = COMMAND.findall(workflow)
    if not commands:
        raise ValueError('no historical inventory verification commands found in CI')
    tracked: set[str] | None = None
    if enforce_git and (root / '.git').exists():
        output = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--cached', '-z'])
        tracked = set(output.decode('utf-8').strip('\x00').split('\x00'))
    for script, historic in commands:
        script_path = 'tools/' + script
        source = root / script_path
        if not source.is_file() or source.is_symlink():
            raise ValueError('workflow referenced missing inventory verifier: ' + script_path)
        match = MANIFEST.search(source.read_text(encoding='utf-8'))
        if match is None:
            # Legacy verifier scripts can use a different constant format.
            continue
        name = match.group(1)
        if not name.startswith('docs/validation/') or '..' in Path(name).parts:
            raise ValueError('unsafe inventory path: ' + name)
        manifest = root / name
        if not manifest.is_file() or manifest.is_symlink():
            raise ValueError('workflow referenced missing inventory manifest: ' + name)
        if tracked is not None and (name not in tracked or script_path not in tracked):
            raise ValueError('inventory evidence not present in git index: ' + name)
        data = json.loads(manifest.read_text(encoding='utf-8'))
        counts = data.get('files_sha256_hex_groups')
        if not isinstance(counts, dict) or not counts or data.get('file_count_excluding_manifest') != len(counts) or data.get('version') != '0.1.0-dev':
            raise ValueError('inconsistent workflow inventory manifest: ' + name)
        frozen = RECOVERED_RECEIPTS.get(name)
        if frozen and hashlib.sha256(manifest.read_bytes()).hexdigest() != frozen:
            raise ValueError('historical inventory has changed from its original cumulative ZIP: ' + name)
        if not historic and script != commands[-1][0] and script not in ('verify_rc_cycle8_inventory.py', 'verify_rc_cycle10_inventory.py'):
            raise ValueError('only the current inventory can require latest-source comparison: ' + script)
    for name in RECOVERED_RECEIPTS:
        if name not in {(MANIFEST.search((root / 'tools' / script).read_text(encoding='utf-8')).group(1)) for script, _ in commands if MANIFEST.search((root / 'tools' / script).read_text(encoding='utf-8'))}:
            raise ValueError('missing pinned historical receipt from workflow: ' + name)
    return len(commands)


if __name__ == '__main__':
    count = verify_references()
    print(f'PASS historical/current workflow inventory prerequisites: {count} verifiers, original cycle 42/43 bytes verified')
