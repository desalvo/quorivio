"""RC263 CI: pure synthetic Poppler stubs and exact PostgreSQL drift semantics."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class EarlyGate(unittest.TestCase):
 def test_mock_pdf_tests_stub_availability_not_real_poppler(self):
  contents=(ROOT/'tools/tests/test_rc261_conversion_mount_and_zlib.py').read_text()
  self.assertIn("patch.object(converter.shutil,'which',side_effect=_fake_tools)",contents)
  self.assertEqual(contents.count("patch.object(converter.shutil,'which',side_effect=_fake_tools)"),2)
 def test_statefulset_sync_only_tolerates_exact_api_defaults(self):
  src=(ROOT/'tools/k8s_disk_monitor_upgrade.py').read_text()
  self.assertIn("'terminationMessagePath':'/dev/termination-log'",src)
  self.assertIn("'terminationMessagePolicy':'File'",src)
  self.assertIn('if actual!=expected:',src)
  self.assertNotIn('if probes[0]!=expected:',src)
 def test_standalone_disk_probe_mirror_matches_module(self):
  import sys
  sys.path.insert(0,str(ROOT/'tools'))
  import k8s_wizard, k8s_disk_monitor_upgrade
  self.assertEqual(k8s_wizard._standalone_component('k8s_disk_monitor_upgrade')._API_CONTAINER_DEFAULTS,
                   k8s_disk_monitor_upgrade._API_CONTAINER_DEFAULTS)
if __name__=='__main__':unittest.main()
