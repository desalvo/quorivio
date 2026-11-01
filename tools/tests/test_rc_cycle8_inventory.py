"""Cycle-8 grouped SHA256 inventory and historical baseline retention."""
import json
import re
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from verify_rc_cycle8_inventory import MANIFEST,load_inventory,decode_digest

class Cycle8Inventory(unittest.TestCase):
 def test_scanner_safe_and_complete(self):
  raw=(ROOT/MANIFEST).read_text(encoding='utf8')
  data=json.loads(raw)
  hashes=load_inventory()
  self.assertEqual(len(hashes),data['file_count_excluding_manifest'])
  self.assertEqual(data['source_files_preserved'],753)
  self.assertNotRegex(raw,r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])')
  self.assertEqual(len(set(hashes)),len(hashes))
  import hashlib
  self.assertEqual(hashes['LICENSE'],hashlib.sha256((ROOT/'LICENSE').read_bytes()).hexdigest())
 def test_digest_rejects_malformed(self):
  for x in ('bad',[],['ffffffff']*7,['ffffffff']*9,['ffffffff']*7+[42],['gggggggg']*8):
   with self.assertRaises(ValueError):decode_digest(x)
if __name__=='__main__':unittest.main()
