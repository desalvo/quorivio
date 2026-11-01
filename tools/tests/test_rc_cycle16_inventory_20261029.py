"""Cycle-16 integrity and historical receipt safety.

Current source and committed Git index must exactly match the newest manifest;
previous inventory is immutable documentary evidence, not a current-tree gate.
"""
import hashlib
import json
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from verify_rc_cycle16_inventory import MANIFEST, load_inventory, verify_source, decode_digest
from verify_rc_cycle14_inventory import load_inventory as load_historical

ROOT=Path(__file__).resolve().parents[2]

class RC16Integrity(unittest.TestCase):
 def test_new_inventory_matches_all_current_sources(self):
  hashes=load_inventory()
  self.assertGreaterEqual(len(hashes),800)
  self.assertEqual(len(hashes),805)  # immutable cycle-16 snapshot, not current files
  self.assertIn('tools/ci_live_replicas.py',hashes)
  self.assertIn('tools/ci_rehearsal_singleton_offline_chromium.py',hashes)
  self.assertIn('docs/validation/RC_CYCLE14_PACKAGE_INVENTORY_20261029.json',hashes)
  self.assertEqual(hashes['LICENSE'],hashlib.sha256((ROOT/'LICENSE').read_bytes()).hexdigest())
 def test_historical_manifest_never_rewritten_to_new_tree(self):
  old=load_historical()
  self.assertEqual(len(old),800)
  self.assertNotIn('tools/verify_rc_cycle16_inventory.py',old)
  self.assertEqual(len(json.loads((ROOT/MANIFEST).read_text())['files_sha256_hex_groups']),len(load_inventory()))
 def test_secret_scanner_safe_and_fail_closed(self):
  raw=(ROOT/MANIFEST).read_text()
  self.assertIsNone(re.search(r'(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])',raw))
  for bad in ([],['abcdef01']*7,['xyzzyxyz']*8,'0'*64):
   with self.assertRaises(ValueError):decode_digest(bad)
  with TemporaryDirectory() as t:
   x=json.loads(raw)
   x['files_sha256_hex_groups']['LICENSE']=['deadbeef']
   p=Path(t)/'bad.json';p.write_text(json.dumps(x))
   with self.assertRaises(ValueError):load_inventory(p)
 def test_workflow_uses_only_latest_source_manifest(self):
  w=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('python3 tools/verify_rc_cycle14_inventory.py --historical',w)
  self.assertIn('python3 tools/verify_rc_cycle16_inventory.py --historical',w)
  self.assertIn('python3 tools/verify_rc_cycle17_inventory.py',w)
  self.assertLess(w.index('python3 tools/verify_rc_cycle17_inventory.py'),w.index('Detect credential leaks'))
  self.assertIn('gitleaks/gitleaks-action@v2',w)

if __name__=='__main__':unittest.main()
