"""Cycle 46: assert real quality-gate fixes remain semantically scoped."""
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]

class Cycle46QualityGate(unittest.TestCase):
    def test_compiled_browser_is_still_required_after_python_suite(self):
        source=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertIn('python3 tools/verify_rc_cycle45_inventory.py --historical', source)
        self.assertIn('python3 tools/verify_rc_cycle46_inventory.py', source)
        self.assertLess(source.index('python3 tools/verify_rc_cycle46_inventory.py'), source.index('Detect credential leaks'))
        self.assertIn('python3 tools/ci_built_frontend_asset_probe.py', source)
        self.assertIn('python3 tools/ci_browser_editor.py', source)

    def test_current_canvas_has_both_media_sources_and_upload_callbacks(self):
        source=(ROOT/'apps/web/src/main.tsx').read_text()
        self.assertRegex(source,r'<WidgetCanvas\b[\s\S]*?assets=\{assets\}\s+backgrounds=\{backgrounds\}\s+sessionId=\{selected\}\s+onUpload=\{uploadWidgetMedia\}\s+assetBusy=\{assetBusy\}')
        self.assertIn('onBackgroundSelect=', source)
        self.assertIn('onBackgroundUpload=', source)

    def test_historical_evidence_and_current_failure_are_not_confused(self):
        proof=json.loads((ROOT/'docs/validation/RC_CYCLE35_GITHUB_VERIFIED_20261030.json').read_text())
        failure=json.loads((ROOT/'docs/validation/RC_CYCLE46_CI_FAILURE_20261030.json').read_text())
        self.assertEqual(proof['committed_sha'],'f5ccf9a7545e7c17b4323d067db66aff5eca9b41')
        self.assertEqual(failure['source_run'],41114355433)
        self.assertEqual(len(failure['python_failures']),2)
        self.assertFalse(failure['browser_compiled_frontend_evaluated_in_source_run'])
        self.assertFalse(failure['new_changes_github_verified'])

if __name__=='__main__': unittest.main()
