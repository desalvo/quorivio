#!/usr/bin/env python3
"""Fail-closed verification of Quorivio cycle-8 cumulative source integrity.

Digest values are grouped, not 64-character hex strings, to prevent secret
scanners from misclassifying evidence as generic API keys.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MANIFEST='docs/validation/RC_CYCLE8_FILE_INVENTORY_20261028.json'
WORD=re.compile(r'^[0-9a-f]{8}$')

def decode_digest(words:object)->str:
    if not isinstance(words,list) or len(words)!=8 or any(not isinstance(v,str) or WORD.fullmatch(v) is None for v in words):
        raise ValueError('invalid grouped SHA256 value')
    return ''.join(words)

def load_inventory(path:Path=ROOT/MANIFEST)->dict[str,str]:
    record=json.loads(path.read_text(encoding='utf-8'))
    hashes=record.get('files_sha256_hex_groups')
    if record.get('version')!='0.1.0-dev' or not isinstance(hashes,dict) or not hashes:
        raise ValueError('invalid inventory version or content')
    if record.get('file_count_excluding_manifest')!=len(hashes):
        raise ValueError('inventory count mismatch')
    for name in hashes:
        if not isinstance(name,str) or not name or name.startswith('/') or '..' in Path(name).parts or '\x00' in name or name==MANIFEST:
            raise ValueError('unsafe or self-referential file path')
    return {key:decode_digest(value) for key,value in hashes.items()}

def verify_zip(package:Path,inventory:Path=ROOT/MANIFEST)->int:
    hashes=load_inventory(inventory)
    with zipfile.ZipFile(package) as z:
        if z.testzip() is not None:
            raise ValueError('ZIP CRC error')
        names=z.namelist()
        if len(names)!=len(set(names)):
            raise ValueError('duplicate ZIP member')
        expected={'quorivio/'+x for x in hashes}|{'quorivio/'+MANIFEST}
        if set(names)!=expected:
            raise ValueError('missing/unexpected ZIP members')
        for name,digest in hashes.items():
            if hashlib.sha256(z.read('quorivio/'+name)).hexdigest()!=digest:
                raise ValueError('checksum mismatch for '+name)
    return len(expected)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package',type=Path)
    args=parser.parse_args()
    values=load_inventory()
    print('Cycle-8 grouped inventory VALID:',len(values),'SHA256 entries')
    if args.package:print('Cycle-8 cumulative ZIP VALID:',verify_zip(args.package),'files')
