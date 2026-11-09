"""RC280: before network-based npm ci, verify workspace and LDAP lock integrity.

These tests prevent the exact EUSAGE failure of GitHub Actions run 42605580476,
without replacing the authoritative npm ci install or disabling lockfile hashes.
"""
from __future__ import annotations
import base64
import copy
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCK = json.loads((ROOT / 'package-lock.json').read_text(encoding='utf8'))
API = json.loads((ROOT / 'apps/api/package.json').read_text(encoding='utf8'))
WORKFLOW = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf8')
EXPECTED = {
 'ldapts': ('9.2.0', '5mDg3OT5fDP9DUXga9dCLW8cMW24OTOKT4pv/Qj+f2zCV3qxb+gkZLCzMAqzVTOANoycidKkYpPvkclUQU2aXw=='),
 'strict-event-emitter-types': ('2.0.0', 'Nk/brWYpD85WlOgzw5h173aci0Teyv8YdIAEtV+N88nDB0dLlazZyJMIsN6eo1/AR61l+p6CJTG1JIyFaoNEEA=='),
}

def verify_lock(lock=LOCK, api=API):
 if lock.get('lockfileVersion') != 2 or not isinstance(lock.get('packages'), dict) or not isinstance(lock.get('dependencies'), dict):
  raise AssertionError('expected npm v2 workspace lockfile with packages and dependencies')
 direct=api.get('dependencies', {})
 workspace=lock['packages']['apps/api']['dependencies']
 legacy=lock['dependencies']['@quorivio/api']['requires']
 for dep, spec in direct.items():
  if workspace.get(dep) != spec or legacy.get(dep) != spec:
   raise AssertionError(f'API workspace out of sync: {dep}')
  if 'node_modules/'+dep not in lock['packages']:
   raise AssertionError(f'missing direct dependency in packages: {dep}')
 if direct.get('ldapts') != '^9.2.0':
  raise AssertionError('unexpected LDAP client constraint')
 for name, (version, expected_digest) in EXPECTED.items():
  loc='node_modules/'+name
  entry=lock['packages'].get(loc)
  legacy_entry=lock['dependencies'].get(name)
  if not entry or not legacy_entry:
   raise AssertionError(f'missing LDAP lockfile entry: {name}')
  if any(value.get('version') != version for value in (entry, legacy_entry)):
   raise AssertionError(f'version mismatch: {name}')
  uri=f'https://registry.npmjs.org/{name}/-/{name}-{version}.tgz'
  if any(value.get('resolved') != uri for value in (entry, legacy_entry)):
   raise AssertionError(f'registry origin mismatch: {name}')
  integrity='sha512-'+expected_digest
  if any(value.get('integrity') != integrity for value in (entry, legacy_entry)):
   raise AssertionError(f'lock SRI mismatch: {name}')
  if len(base64.b64decode(expected_digest,validate=True)) != 64:
   raise AssertionError(f'bad SHA512 data: {name}')
  if name=='ldapts' and (entry.get('dependencies',{}).get('strict-event-emitter-types') != '2.0.0' or legacy_entry.get('requires',{}).get('strict-event-emitter-types') != '2.0.0'):
   raise AssertionError('missing transitive LDAP dependency')
 return len(EXPECTED)

class RC280LockfileContract(unittest.TestCase):
 def test_consistent_lockfile_and_integrity(self):
  self.assertEqual(verify_lock(),2)
 def test_missing_ldapts_is_rejected(self):
  altered=copy.deepcopy(LOCK)
  del altered['packages']['node_modules/ldapts']
  with self.assertRaisesRegex(AssertionError,'missing LDAP lockfile entry|missing direct dependency'):
   verify_lock(altered)
 def test_missing_transitive_dependency_is_rejected(self):
  altered=copy.deepcopy(LOCK)
  del altered['packages']['node_modules/strict-event-emitter-types']
  with self.assertRaisesRegex(AssertionError,'missing LDAP lockfile entry'):
   verify_lock(altered)
 def test_invalid_sri_is_rejected(self):
  altered=copy.deepcopy(LOCK)
  altered['packages']['node_modules/ldapts']['integrity']='sha512-invalid'
  with self.assertRaisesRegex(AssertionError,'SRI mismatch'):
   verify_lock(altered)
 def test_workspace_drift_is_rejected(self):
  altered=copy.deepcopy(LOCK)
  altered['dependencies']['@quorivio/api']['requires'].pop('ldapts')
  with self.assertRaisesRegex(AssertionError,'workspace out of sync'):
   verify_lock(altered)
 def test_ci_tests_before_npm_ci_in_both_jobs(self):
  gate='python3 -m unittest tools.tests.test_rc280_npm_lock -q'
  install='run: npm ci --ignore-scripts --no-audit --no-fund'
  self.assertEqual(WORKFLOW.count(gate),2)
  self.assertEqual(WORKFLOW.count(install),2)
  for match in re.finditer(re.escape(install),WORKFLOW):
   self.assertIn(gate,WORKFLOW[max(0,match.start()-250):match.start()])
  self.assertNotIn('run: npm install --ignore-scripts --no-audit --no-fund',WORKFLOW)

if __name__ == '__main__':unittest.main()
