#!/usr/bin/env python3
"""Fail-closed grouped SHA-256 source/ZIP verification for RC cycle 55.

Hashes are eight 8-character lowercase words to reduce false-positive generic
API-key secret scanner hits. Reassembling them yields the original SHA-256.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = 'docs/validation/RC_CYCLE55_PACKAGE_INVENTORY_20261030.json'
WORD = re.compile(r'^[0-9a-f]{8}$')


def decode_digest(words: object) -> str:
    if not isinstance(words, list) or len(words) != 8 or any(
        not isinstance(word, str) or WORD.fullmatch(word) is None for word in words
    ):
        raise ValueError('SHA-256 requires exactly eight lowercase hex words')
    return ''.join(words)


def load_inventory(path: Path = ROOT / MANIFEST) -> dict[str, str]:
    document = json.loads(path.read_text(encoding='utf8'))
    values = document.get('files_sha256_hex_groups')
    if document.get('version') != '0.1.0-dev' or not isinstance(values, dict) or not values:
        raise ValueError('missing inventory or wrong version')
    if document.get('file_count_excluding_manifest') != len(values):
        raise ValueError('inventory entry count mismatch')
    for name in values:
        posix = Path(name)
        if (not name or not isinstance(name, str) or name.startswith('/') or
            '..' in posix.parts or '\x00' in name or name == MANIFEST or '\\' in name):
            raise ValueError('unsafe or self-referential inventory path')
    hashes = {name: decode_digest(words) for name, words in values.items()}
    if len(set(hashes.values())) < 1:
        raise ValueError('empty integrity evidence')
    return hashes


def verify_source(root: Path = ROOT, inventory: Path = ROOT / MANIFEST) -> int:
    hashes = load_inventory(inventory)
    for name, digest in hashes.items():
        p = root / name
        if not p.is_file() or p.is_symlink():
            raise ValueError(f'file missing or symlinked: {name}')
        if hashlib.sha256(p.read_bytes()).hexdigest() != digest:
            raise ValueError(f'source checksum mismatch: {name}')
    # A packaged log must also be present in the Git checkout, not just
    # in a locally created ZIP. Compare committed/staged filenames with the
    # manifest when a Git worktree is available. This catches gitignored
    # evidence files before they cause failures in GitHub Actions.
    if (root / '.git').exists():
        tracked = subprocess.check_output(
            ['git', '-C', str(root), 'ls-files', '--cached', '-z']
        ).decode('utf-8').split('\0')
        tracked_names = set(filter(None, tracked))
        expected = set(hashes) | {MANIFEST}
        if tracked_names != expected:
            missing = sorted(expected - tracked_names)
            extra = sorted(tracked_names - expected)
            raise ValueError(f'Git index / manifest mismatch: missing={missing[:8]} extra={extra[:8]}')
    return len(hashes)


def verify_zip(archive: Path, inventory: Path = ROOT / MANIFEST) -> int:
    hashes = load_inventory(inventory)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError('ZIP CRC mismatch')
        members = z.namelist()
        if len(members) != len(set(members)):
            raise ValueError('duplicate ZIP member')
        expected = {'quorivio/' + name for name in hashes} | {'quorivio/' + MANIFEST}
        if set(members) != expected:
            raise ValueError('ZIP members do not match inventory')
        for name, digest in hashes.items():
            if hashlib.sha256(z.read('quorivio/' + name)).hexdigest() != digest:
                raise ValueError('ZIP SHA-256 mismatch for ' + name)
        if z.read('quorivio/' + MANIFEST) != inventory.read_bytes():
            raise ValueError('ZIP manifest differs from verified source')
    return len(expected)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, help='optional historical cycle-55 ZIP')
    parser.add_argument('--historical', action='store_true', help='validate immutable cycle-55 checksum catalog without comparing later source edits')
    args = parser.parse_args()
    if args.historical:
        print('Cycle 55 historical checksum catalog VALID:', len(load_inventory()), 'digests')
    else:
        print('Cycle 55 current-source checksums VALID:', verify_source(), 'files')
    if args.package:
        print('Cycle 55 cumulative ZIP VALID:', verify_zip(args.package), 'files')
