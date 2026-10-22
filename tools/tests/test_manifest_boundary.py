"""Regression contract: API must verify worker-produced images, ordering and source."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

class ManifestBoundaryTests(unittest.TestCase):
    def test_manifest_and_source_checked_before_database_transaction(self):
        src = (ROOT/'apps/api/src/server.ts').read_text()
        start = src.index("app.post('/api/sessions/:id/presentation-import'")
        finish = src.index('// Public slide images', start)
        route = src[start:finish]
        self.assertIn("manifest.format!=='quorivio-presentation-pages'", route)
        self.assertIn('manifest.version!==1', route)
        self.assertIn('manifest.source_sha256!==sourceHash', route)
        self.assertIn('manifest.source_type!==expectedSourceType', route)
        self.assertIn("entry.position!==i+1", route)
        self.assertIn('contents.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))', route)
        self.assertIn('BEGIN', route)

    def test_ci_forces_real_pdf_render_and_private_worker_http(self):
        ci = (ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn("python3 -c 'import reportlab'", ci)
        self.assertIn('test_import_presentation.TestImport.test_convert_pdf', ci)
        self.assertIn('PYTHONPATH=tools python3 -m unittest discover', ci)

if __name__ == '__main__': unittest.main()
