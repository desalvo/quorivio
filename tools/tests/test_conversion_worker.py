"""Worker path and endpoint security checks without network services."""
import importlib.util
import pathlib
import tempfile
import sys
import unittest
from unittest.mock import patch

ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
spec=importlib.util.spec_from_file_location('conversion_worker',ROOT/'conversion_worker.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class WorkerTests(unittest.TestCase):
    def test_rejects_traversal(self):
        for job in ('../../etc/passwd','1/2','', 'z'*32, 'a'*31):
            with self.assertRaises(ValueError):module.execute_job(job)

    def test_rejects_missing_job(self):
        with tempfile.TemporaryDirectory() as d,patch.object(module,'ROOT',pathlib.Path(d)):
            with self.assertRaises(ValueError):module.execute_job('a'*32)

    def test_rejects_missing_source(self):
        with tempfile.TemporaryDirectory() as d,patch.object(module,'ROOT',pathlib.Path(d)):
            (pathlib.Path(d)/('a'*32)).mkdir()
            with self.assertRaises(ValueError):module.execute_job('a'*32)

    def test_deployment_has_private_worker_and_shared_directory(self):
        compose=(ROOT.parent/'compose.yaml').read_text()
        self.assertIn('Dockerfile.converter',compose)
        self.assertIn('conversion-tmp:/conversions',compose)
        self.assertIn('QUORIVIO_CONVERTER_WORKER_URL',compose)
        self.assertNotIn('8099:8099',compose)
        server=(ROOT.parent/'apps/api/src/server.ts').read_text()
        self.assertIn("fetch(`${workerUrl}/convert`",server)
        self.assertNotIn('const child=spawn(',server)

if __name__=='__main__':unittest.main()
