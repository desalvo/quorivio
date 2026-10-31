"""RC69 conservative filmstrip subgate and source-level recovery contracts."""
from __future__ import annotations
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from rc_gate_audit import audit
from rc_release_preflight import preflight
from rc_campaign_preflight import campaign_audit

class ThumbnailReorderCycle69(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
  cls.gates={x['id']:x for x in cls.matrix['gates']}
  cls.receipt=json.loads((ROOT/'docs/validation/RC_CYCLE69_GITHUB_THUMBNAIL_EXPORT_VERIFIED_20261031.json').read_text())

 def test_verified_download_is_distinct_from_prior_thumbnails_and_autosave(self):
  g=self.gates
  self.assertEqual((g['A2']['weight'],g['A2']['status']),(3,'partial'))
  self.assertEqual((g['A2-PAGE-JSON']['weight'],g['A2-PAGE-JSON']['status']),(1,'accepted'))
  self.assertEqual(g['A2-ORDER']['weight'],2)
  self.assertEqual(g['A2-PAGE-JSON']['verified_run_id'],41191751069)
  self.assertEqual(g['A2-PAGE-JSON']['verified_job_id'],124509777927)
  self.assertEqual(g['A2-PAGE-JSON']['verified_commit_sha'],self.receipt['source']['commit_sha'])
  self.assertIn('pixel-accurate',g['A2']['remaining'])
  self.assertIn('Firefox/WebKit',g['A2']['remaining'])
  self.assertIn('not merely a visible menu',g['A2-PAGE-JSON']['scope'])
  self.assertNotEqual(g['A2-PAGE-JSON']['scope'],g['A2-ORDER']['scope'])

 def test_real_chromium_download_receipt_not_only_menu_presence(self):
  script=(ROOT/'tools/ci_browser_editor.py').read_text()
  self.assertIn('async with page.expect_download() as info:',script)
  self.assertIn("name='Esporta layout JSON'",script)
  self.assertIn('assert Path(await backup.path()).exists()',script)
  w=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('python3 tools/ci_browser_editor.py',w)
  self.assertEqual(self.receipt['source']['extended_run_id'],41191751069)
  self.assertEqual(self.receipt['source']['quality_job_id'],124509777927)

 def test_new_reorder_handles_ambiguous_http_write_without_invented_rollback(self):
  module=(ROOT/'apps/web/src/page-order-recovery.ts').read_text()
  ui=(ROOT/'apps/web/src/main.tsx').read_text()
  case=(ROOT/'apps/web/test/page-order-recovery.test.ts').read_text()
  for s in ('await write()','await read()','recovered','concurrent','rejected','Page collection changed'):
   self.assertIn(s,module)
  self.assertIn('commitAndReconcilePageOrder(',ui)
  self.assertIn('Esito del riordino non verificabile',ui)
  self.assertIn('lost write response after COMMIT',case)
  self.assertNotIn('ordine precedente conservato',ui)

 def test_native_cross_browser_acceptance_proves_real_drag_and_readback_when_ci_runs(self):
  script=(ROOT/'tools/ci_page_thumbnail_native.py').read_text()
  workflow=(ROOT/'.github/workflows/ci.yml').read_text()
  self.assertIn('.drag_to(',script)
  self.assertIn('commitThenLose',script)
  self.assertIn('rejectNext',script)
  self.assertIn("Alt+ArrowUp",script)
  self.assertIn('await page.add_script_tag(content=js,type=\'module\')',script)
  self.assertIn('python3 tools/ci_page_thumbnail_native.py --engines chromium',workflow)
  self.assertIn('python3 tools/ci_page_thumbnail_native.py --engines firefox webkit',workflow)
  self.assertIn('Native Firefox and WebKit page thumbnail reorder',workflow)
  self.assertFalse(self.matrix['rc_cycle69_thumbnail_export_reconciliation_20261031']['native_dnd_promoted'])

 def test_conservative_progress_and_publication_guard(self):
  p=preflight();self.assertEqual((audit()['score'],p['score'],campaign_audit()['certified_score']),(84.75,)*3)
  self.assertEqual((p['gate_count'],p['accepted_gates'],len(p['unaccepted_gates'])),(59,42,17))
  self.assertEqual(sum(x['weight'] for x in self.matrix['gates']),100)
  self.assertFalse(p['release_candidate_ready'])
  self.assertEqual(self.receipt['accounting']['delta_points'],0.5)
  self.assertTrue(campaign_audit()['external_signoff_required'])
  self.assertFalse(self.receipt['publish_image'])
  self.assertFalse(self.receipt['rc_strict'])
  self.assertIn('A2',{x['id'] for x in p['unaccepted_gates']})

if __name__=='__main__':unittest.main()
