#!/usr/bin/env python3
"""Build future cumulative RC ZIPs without silently dropping earlier receipts.

Usage (from repository root, after editing source and the CI inventory lines):
  python3 tools/package_rc_cumulative.py --cycle 80 --previous 79 \
     --add tools/tests/test_new_feature.py --output /tmp/quorivio-rc80.zip

The previous manifest itself and every historical receipt referenced by CI are
included automatically. The newly generated inventory must match the exact
ZIP members; a separate source check is performed before creating the ZIP.
No Git operations or release publication are performed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
import zipfile
from pathlib import Path

from rc_inventory_closure import (
    check_inventory_closure, is_ephemeral_source_path, required_inventory_files,
)

ROOT = Path(__file__).resolve().parents[1]


def manifest_path(cycle: int, day: str) -> str:
    return f'docs/validation/RC_CYCLE{cycle}_PACKAGE_INVENTORY_{day}.json'


def assemble_paths(root: Path, previous: str, current: str, extra: list[str]) -> list[str]:
    old = json.loads((root / previous).read_text(encoding='utf8'))
    entries = old['files_sha256_hex_groups']
    paths = set(entries) | {previous, 'tools/package_rc_cumulative.py', 'tools/rc_inventory_closure.py'} | set(extra)
    # Include historical receipts even if an earlier release's inventory list
    # forgot to enumerate that release's own manifest (the original RC78 bug).
    paths |= {str(f.relative_to(root)) for f in (root / 'docs/validation').glob('RC_CYCLE*_PACKAGE_INVENTORY_*.json') if str(f.relative_to(root)) != current}
    deps = required_inventory_files(lambda name: (root / name).read_text(encoding='utf8'))
    paths |= deps - {current}
    paths.discard(current)
    # A historical inventory can contain an ignored local bytecode artifact;
    # do not carry it forward or let its existence influence source closure.
    paths = {name for name in paths if not is_ephemeral_source_path(name)}
    for name in paths:
        p = root / name
        if p.is_symlink() or not p.is_file() or p.resolve().is_relative_to(root.resolve()) is False:
            raise ValueError('missing/unsafe source for package: ' + name)
    check_inventory_closure(paths | {current}, lambda name: (root / name).read_text(encoding='utf8'))
    return sorted(paths)


def build(cycle: int, previous_cycle: int, day: str, output: Path, extra: list[str], root: Path = ROOT, previous_day: str | None = None) -> tuple[int, str]:
    prev = manifest_path(previous_cycle, previous_day or day)
    cur = manifest_path(cycle, day)
    if (root / cur).exists():
        # Prevent silent mutation of an existing acceptance receipt.
        raise ValueError('current receipt already exists; do not overwrite: ' + cur)
    names = assemble_paths(root, prev, cur, extra)
    if any(is_ephemeral_source_path(name) for name in names):
        raise ValueError('ephemeral generated file in package list')
    digests = {}
    for name in names:
        value = hashlib.sha256((root / name).read_bytes()).hexdigest()
        digests[name] = [value[i:i + 8] for i in range(0, 64, 8)]
    (root / cur).write_text(json.dumps({'version': '0.1.0-dev', 'cycle': cycle,
                                        'file_count_excluding_manifest': len(digests),
                                        'files_sha256_hex_groups': digests},
                                       ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    module = importlib.import_module(f'verify_rc_cycle{cycle}_inventory')
    module.verify_source(root=root, inventory=root / cur)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name in names + [cur]:
            archive.write(root / name, arcname='quorivio/' + name)
    count = module.verify_zip(output, inventory=root / cur)
    return count, hashlib.sha256(output.read_bytes()).hexdigest()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cycle', type=int, required=True)
    parser.add_argument('--previous', type=int, required=True)
    parser.add_argument('--day', default='20261031')
    parser.add_argument('--previous-day', default=None, help='date of previous immutable inventory, when crossing midnight')
    parser.add_argument('--add', action='append', default=[])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    count, digest = build(args.cycle, args.previous, args.day, args.output, args.add, previous_day=args.previous_day)
    print(f'PASS cumulative archive: {count} files, sha256={digest}')
