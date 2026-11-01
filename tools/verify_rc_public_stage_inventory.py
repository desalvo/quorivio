#!/usr/bin/env python3
"""Validate preserved historical SHA-256 inventory without scanner-ambiguous digests."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / 'docs/validation/RC_PUBLIC_STAGE_FILE_INVENTORY_20261028.json'
WORD = re.compile(r'^[0-9a-f]{8}$')


def decode_groups(value: object) -> str:
    if not isinstance(value,list) or len(value)!=8 or any(not isinstance(word,str) or WORD.fullmatch(word) is None for word in value):
        raise ValueError('expected exactly eight lower-case eight-hex-character words')
    return ''.join(value)


def validate(path: Path=INVENTORY) -> dict[str,str]:
    report=json.loads(path.read_text(encoding='utf-8'))
    if 'files_sha256' in report or 'source_archive_sha256' in report:
        raise ValueError('unsafe legacy SHA-256 inventory serialization')
    if report.get('version')!='0.1.0-dev':
        raise ValueError('unexpected software version')
    hashes=report.get('files_sha256_hex_groups')
    if not isinstance(hashes,dict) or not hashes or report.get('legacy_inventory_file_count')!=len(hashes):
        raise ValueError('missing or inconsistent historical checksum inventory')
    archive_hash=decode_groups(report['source_archive_sha256_hex_groups'])
    if len(archive_hash)!=64: raise ValueError('invalid archived package hash')
    if any(not isinstance(name,str) or not name or name.startswith('/') or '..' in Path(name).parts or '\x00' in name for name in hashes):
        raise ValueError('unsafe archive member path')
    return {name:decode_groups(words) for name,words in hashes.items()}


def validate_source_archive(inventory: Path, archive: Path) -> int:
    """Verify the *input baseline* archive; its files precede public-stage edits."""
    report=json.loads(inventory.read_text(encoding='utf-8'))
    expected_archive=decode_groups(report['source_archive_sha256_hex_groups'])
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected_archive:
        raise ValueError('original baseline ZIP SHA-256 mismatch')
    with zipfile.ZipFile(archive) as z:
        files=[name for name in z.namelist() if name.startswith('quorivio/') and not name.endswith('/')]
        if len(files)!=report['baseline_files_preserved'] or z.testzip() is not None:
            raise ValueError('original baseline ZIP file count/integrity mismatch')
        return len(files)


def validate_package(inventory: Path, package: Path) -> int:
    """Verify captured public-stage outputs; they are not the input baseline."""
    expected=validate(inventory)
    with zipfile.ZipFile(package) as z:
        file_names={name.removeprefix('quorivio/') for name in z.namelist() if name.startswith('quorivio/') and not name.endswith('/')}
        if not set(expected).issubset(file_names):
            raise ValueError('stage package missing recorded member')
        for name,digest in expected.items():
            if hashlib.sha256(z.read('quorivio/'+name)).hexdigest()!=digest:
                raise ValueError('stage package checksum mismatch: '+name)
    return len(expected)


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory',type=Path,default=INVENTORY)
    parser.add_argument('--source-archive',type=Path,help='optional exact original source archive ZIP')
    parser.add_argument('--stage-package',type=Path,help='optional already-built public-stage ZIP whose file digests are recorded')
    args=parser.parse_args()
    count=len(validate(args.inventory))
    if args.source_archive:
        print(f'Original baseline archive VALID: {validate_source_archive(args.inventory,args.source_archive)} files')
    if args.stage_package:
        print(f'Historical stage package VALID: {validate_package(args.inventory,args.stage_package)} checksums')
    print(f'Public-stage integrity inventory VALID: {count} grouped SHA-256 entries')
    return 0

if __name__=='__main__':
    sys.exit(main())
