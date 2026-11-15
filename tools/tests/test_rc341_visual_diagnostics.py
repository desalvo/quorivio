"""RC341 bounded visual-render failure classifications and sanitized worker reply."""
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from visual_export import VisualExportFailure, _run_stage
import conversion_worker as worker
from tools.tests.test_converter_http_integration import HTTPWorkerIntegration

class Classification(unittest.TestCase):
    def test_visual_stage_wraps_internal_exception_without_revealing_private_content(self):
        def failure():
            raise RuntimeError("SECRET_PRIVATE_CAPTURE_URL")
        with self.assertRaises(VisualExportFailure) as ctx:
            _run_stage("package", failure)
        self.assertEqual(ctx.exception.stage, "package")
        self.assertNotIn("SECRET_PRIVATE_CAPTURE_URL", str(ctx.exception))
        self.assertIsInstance(ctx.exception.__cause__, RuntimeError)

    def test_visual_stage_is_not_overwritten(self):
        def failure():
            raise VisualExportFailure("navigate")
        with self.assertRaises(VisualExportFailure) as ctx:
            _run_stage("setup", failure)
        self.assertEqual(ctx.exception.stage, "navigate")

class WorkerStageHTTP(HTTPWorkerIntegration):
    def test_bounded_worker_phase_in_real_http_response(self):
        payload = json.dumps({"job": "f"*32}).encode()
        with patch.object(worker, "execute_portable_job",
                          side_effect=VisualExportFailure("render")):
            status, body = self.request("POST", "/visual-export", payload, self.token)
        self.assertEqual(status, 422)
        self.assertEqual(body, {"error": "conversion_failed", "phase": "render"})

    def test_invalid_phase_is_not_exposed(self):
        payload = json.dumps({"job": "e"*32}).encode()
        with patch.object(worker, "execute_portable_job",
                          side_effect=VisualExportFailure("SENSITIVE_PATH")):
            status, body = self.request("POST", "/visual-export", payload, self.token)
        self.assertEqual(status, 422)
        self.assertEqual(body, {"error": "conversion_failed"})

if __name__ == "__main__":
    unittest.main()
