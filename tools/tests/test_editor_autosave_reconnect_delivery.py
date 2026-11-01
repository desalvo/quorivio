"""Guard the difference between real-DB acceptance and isolated retry semantics.

The ordinary PostgreSQL browser fixture remains unmocked. Real retry recovery
logic is also covered by the mandatory Node web-unit step and browser E2E.
"""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
MAIN=(ROOT/'apps/web/src/main.tsx').read_text()
CORE=(ROOT/'apps/web/src/page-autosave.ts').read_text()
GEOMETRY=(ROOT/'apps/web/src/widget-geometry.ts').read_text()
CI=(ROOT/'.github/workflows/ci.yml').read_text()
DB=(ROOT/'tools/ci_browser_editor_postgres.py').read_text()

class EditorResilienceContracts(unittest.TestCase):
 def test_server_readback_must_precede_retries(self):
  self.assertIn('autosaveRecoveryDecision(remote,requestedDraft,expectedRevision,confirmedPatchRevision)',MAIN)
  self.assertIn('confirmedPatchRevision=saved.design_revision',MAIN)
  self.assertIn("verdict==='unchanged'&&recoverableAutosaveTransportError(e)",MAIN)
  self.assertIn("if(verdict==='persisted' && remote)",MAIN)
  self.assertIn('attempts<3',MAIN)
  self.assertIn('setPageConflict(true)',MAIN)
 def test_write_identity_scopes_retries_to_page(self):
  self.assertIn("savePageId+':'+savedSignature",MAIN)
  self.assertIn("designActivity+':'+latestPageDraft.current",MAIN)
  self.assertIn('retryAutosaveDelay(attempts)',MAIN)
  self.assertIn('setAutoSaveBlockedSignature(savedSignature)',MAIN)
 def test_ambiguous_outcomes_do_not_blindly_retry(self):
  self.assertIn("return 'conflict'",CORE)
  self.assertIn("return 'unverifiable'",CORE)
  self.assertIn("revision===expectedRevision+1",CORE)
  self.assertIn('Failed to fetch',CORE)
  self.assertIn('HTTP (502|503|504)',CORE)
 def test_editor_audience_presenter_use_one_layout_calculator(self):
  self.assertGreaterEqual(MAIN.count('widgetGeometryStyle(w.position)'),2)
  self.assertIn('widgetGeometryStyle(pos)',MAIN)
  self.assertIn("height:(p.height??24)+'%'",GEOMETRY)
 def test_browser_with_postgresql_is_still_unmocked(self):
  self.assertNotIn('.route(',DB)
  self.assertIn('await await_revision(context,sid,aid,3)',DB)
  self.assertIn("remote_design['widgets'][0]['label']='Remote second edit'",DB)
 def test_new_web_unit_step_is_mandatory(self):
  self.assertIn('Editor autosave recovery and shared geometry unit tests',CI)
  self.assertIn('node --experimental-strip-types --test apps/web/test/*.test.ts',CI)
  self.assertIn('npm run build',CI)
