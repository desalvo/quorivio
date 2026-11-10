"""RC300: Docker archives must be built after scanning and never pushed by CI."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')
class PortableImages(unittest.TestCase):
 def test_images_are_exported_after_both_scans_only_on_explicit_full_ci(self):
  a=CI.index('      - name: Scan converter image')
  b=CI.index('      - name: Export scanned Docker images as portable archives [full-ci]')
  c=CI.index('      - name: Upload portable Docker images [full-ci]')
  self.assertLess(a,b);self.assertLess(b,c)
  subset=CI[b:CI.index('  kubernetes-api-manifests:',c)]
  guard="github.event_name == 'push' && github.ref == 'refs/heads/main' && contains(github.event.head_commit.message, '[full-ci]')"
  self.assertEqual(subset.count(guard),2)
  for marker in ('docker save "quorivio:sha-$short"','docker save "quorivio-converter:sha-$short"','sha256sum *.tar.gz > SHA256SUMS','gzip -t','actions/upload-artifact@v4','retention-days: 7'):
   with self.subTest(marker=marker): self.assertIn(marker,subset)
  for denied in ('push: true','docker push','docker/login-action'):
   self.assertNotIn(denied,subset)
 def test_extended_full_ci_still_includes_native_oci(self):
  self.assertIn("contains(github.event.head_commit.message, '[full-ci]')",CI)
  self.assertIn('name: Container build gate',CI)
  self.assertIn('name: Native OCI runtime on',CI)
  self.assertIn('name: Full automatic RC campaign acceptance summary',CI)
if __name__=='__main__':unittest.main()
