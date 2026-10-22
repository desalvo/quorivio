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

class WorkerRegressionTests(unittest.TestCase):
    def test_existing_output_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as root, patch.object(module, 'ROOT', pathlib.Path(root)):
            job='c'*32
            work=pathlib.Path(root)/job
            work.mkdir()
            (work/'source.pdf').write_bytes(b'%PDF-1.4 test')
            (work/'pages').symlink_to(pathlib.Path(root))
            with self.assertRaisesRegex(ValueError,'output already exists'):
                module.execute_job(job)

    def test_duplicate_job_protected_and_released_after_failure(self):
        with tempfile.TemporaryDirectory() as root, patch.object(module, 'ROOT', pathlib.Path(root)):
            job='d'*32
            work=pathlib.Path(root)/job
            work.mkdir()
            (work/'source.pdf').write_bytes(b'%PDF-1.4 test')
            def overlap(source, dest):
                with self.assertRaisesRegex(ValueError,'job already running'):
                    module.execute_job(job)
                raise RuntimeError('conversion failure')
            with patch.object(module,'convert',side_effect=overlap):
                with self.assertRaisesRegex(RuntimeError,'conversion failure'):
                    module.execute_job(job)
            self.assertNotIn(job,module._ACTIVE_JOBS)
            with patch.object(module,'convert',return_value={'page_count':2}):
                self.assertEqual(module.execute_job(job),{'page_count':2})

    def test_converter_image_scanned_in_ci(self):
        ci=(ROOT.parent/'.github/workflows/ci.yml').read_text()
        self.assertIn('image-ref: quorivio-converter:gate',ci)
        self.assertIn('severity: CRITICAL,HIGH',ci)

class DistributedWorkerReservationTests(unittest.TestCase):
    def test_existing_shared_reservation_rejected(self):
        with tempfile.TemporaryDirectory() as root, patch.object(module,'ROOT',pathlib.Path(root)):
            job='e'*32
            work=pathlib.Path(root)/job
            work.mkdir()
            (work/'source.pdf').write_bytes(b'%PDF-1.4 test')
            (work/'.conversion-lock').mkdir()
            with self.assertRaisesRegex(ValueError,'job already running'):
                module.execute_job(job)
            self.assertTrue((work/'.conversion-lock').is_dir())
            self.assertNotIn(job,module._ACTIVE_JOBS)

    def test_shared_reservation_exists_during_conversion_and_is_released(self):
        with tempfile.TemporaryDirectory() as root, patch.object(module,'ROOT',pathlib.Path(root)):
            job='f'*32
            work=pathlib.Path(root)/job
            work.mkdir()
            (work/'source.pdf').write_bytes(b'%PDF-1.4 test')
            def converted(source,dest):
                self.assertTrue((work/'.conversion-lock').is_dir())
                return {'page_count':1}
            with patch.object(module,'convert',side_effect=converted):
                self.assertEqual(module.execute_job(job),{'page_count':1})
            self.assertFalse((work/'.conversion-lock').exists())

    def test_reservation_cleanup_when_converter_raises(self):
        with tempfile.TemporaryDirectory() as root, patch.object(module,'ROOT',pathlib.Path(root)):
            job='1'*32
            work=pathlib.Path(root)/job
            work.mkdir()
            (work/'source.pdf').write_bytes(b'%PDF-1.4 test')
            with patch.object(module,'convert',side_effect=RuntimeError('failed')):
                with self.assertRaises(RuntimeError):module.execute_job(job)
            self.assertFalse((work/'.conversion-lock').exists())

class AdditionalWorkerSafetyTests(unittest.TestCase):
    def test_duplicate_sources_rejected_before_lock(self):
        with tempfile.TemporaryDirectory() as root, patch.object(module, 'ROOT', pathlib.Path(root)):
            job = 'b'*32
            work = pathlib.Path(root)/job
            work.mkdir()
            (work/'source.pdf').write_bytes(b'%PDF-1.4 test')
            (work/'source.pptx').write_bytes(b'PK dummy')
            with self.assertRaisesRegex(ValueError, 'exactly one source'):
                module.execute_job(job)
            self.assertFalse((work/'.conversion-lock').exists())

    def test_publish_manifest_before_pages(self):
        content = (ROOT/'import_presentation.py').read_text()
        self.assertIn("(images/'manifest.json').write_text", content)
        self.assertIn('images.rename(output)', content)
        self.assertNotIn("(output/'manifest.json').write_text", content)
