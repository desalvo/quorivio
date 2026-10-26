"""Source-contract guardrails for durable asset/photo erasure and admin observability.
The live PostgreSQL / filesystem behavior is tested by ci_retention_postgres.mjs.
"""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[2]
SRC=(R/'apps/api/src/server.ts').read_text()
SCHEMA=(R/'apps/api/src/schema.sql').read_text()
WORKER=(R/'apps/api/src/asset-erasure.ts').read_text()
CI=(R/'tools/ci_retention_postgres.mjs').read_text()
class ErasureContracts(unittest.TestCase):
 def test_single_asset_delete_uses_atomic_outbox(self):
  route=SRC.split("app.delete('/api/sessions/:id/assets/:assetId'",1)[1].split("app.get('/api/sessions/:id/report.json'",1)[0]
  self.assertIn('ASSET_DELETE_WITH_CLEANUP_SQL',route)
  self.assertIn('drainAssetErasureJobs',route)
  self.assertNotIn('DELETE FROM session_assets WHERE',route)
 def test_linked_files_remain_protected(self):
  route=SRC.split("app.delete('/api/sessions/:id/assets/:assetId'",1)[1].split("app.get('/api/sessions/:id/report.json'",1)[0]
  self.assertIn('asset_in_use_by_widget',route)
  self.assertIn('asset_in_use_by_slide',route)
 def test_photo_update_is_transactional_with_erasure_intent(self):
  tx=SRC.split('async function replaceProfilePhoto',1)[1].split('async function cleanOldProfilePhoto',1)[0]
  self.assertIn("FOR UPDATE",tx)
  self.assertIn('PROFILE_ERASURE_ENQUEUE_SQL',tx)
  self.assertLess(tx.index('PROFILE_ERASURE_ENQUEUE_SQL'),tx.index("cx.query('COMMIT')"))
 def test_deleted_user_photo_enqueued_transactionally(self):
  route=SRC.split("app.delete('/api/admin/users/:id'",1)[1].split("app.get('/api/admin/privacy",1)[0]
  self.assertIn('PROFILE_ERASURE_ENQUEUE_SQL',route)
  self.assertLess(route.index('PROFILE_ERASURE_ENQUEUE_SQL'),route.index("cx.query('COMMIT')"))
  self.assertIn('primary_admin',route)
  self.assertIn('user_has_dependent_data',route)
 def test_admin_metrics_authenticated_without_personal_ids(self):
  route=SRC.split("app.get('/api/admin/privacy/erasure-status'",1)[1].split("app.get('/api/admin/settings'",1)[0]
  self.assertIn('requireAuth,requireAdmin',route)
  self.assertIn("Cache-Control','private, no-store",route)
  self.assertNotIn('SELECT *',route)
  self.assertNotIn('session_id AS',route)
  self.assertNotIn('photo_id AS',route)
 def test_schema_has_independent_persistent_non_fk_queues(self):
  self.assertIn('CREATE TABLE IF NOT EXISTS session_asset_file_cleanup_jobs(',SCHEMA)
  self.assertIn('CREATE TABLE IF NOT EXISTS profile_photo_cleanup_jobs(',SCHEMA)
  self.assertIn('PRIMARY KEY(session_id,asset_id)',SCHEMA)
  self.assertIn('photo_id uuid PRIMARY KEY',SCHEMA)
  self.assertIn('idx_asset_file_cleanup_due',SCHEMA)
  self.assertIn('idx_profile_photo_cleanup_due',SCHEMA)
 def test_workers_retry_on_fixed_max_hour(self):
  self.assertEqual(WORKER.count('LEAST(3600'),2)
  self.assertEqual(WORKER.count('FOR UPDATE SKIP LOCKED'),2)
 def test_workers_have_repeatable_minute_cadence(self):
  self.assertIn('setInterval(()=>drainAssetErasureJobs(db,assetRoot)',SRC)
  self.assertIn('setInterval(()=>drainProfileErasureJobs(db,assetRoot)',SRC)
 def test_db_ci_tests_unchanged_session_retention_and_new_file_erasure(self):
  self.assertIn('SESSION_RETENTION_PURGE_SQL',CI)
  self.assertIn('ASSET_DELETE_WITH_CLEANUP_SQL',CI)
  self.assertIn('drainAssetErasureJobs',CI)
  self.assertIn('drainProfileErasureJobs',CI)
  self.assertIn('cross-session deletion',CI)
 def test_no_reliance_on_public_profile_photo_endpoint(self):
  self.assertIn('publicPresenterProfiles',SRC)
  self.assertIn('profilePhotoId(url)',SRC)
if __name__=='__main__':unittest.main()
