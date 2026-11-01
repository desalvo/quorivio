import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
class ReplicationInfrastructure(unittest.TestCase):
 def test_helm_persistent_assets(self):
  deployment=(ROOT/'helm/quorivio/templates/deployment.yaml').read_text()
  pvc=(ROOT/'helm/quorivio/templates/assets-pvc.yaml').read_text()
  self.assertIn('mountPath: /app/assets',deployment)
  self.assertIn('persistentVolumeClaim:',deployment)
  self.assertIn('ReadWriteOnce',(ROOT/'helm/quorivio/values.yaml').read_text())
  self.assertIn('existingClaim',pvc)
 def test_database_bus_wired(self):
  server=(ROOT/'apps/api/src/server.ts').read_text()
  self.assertIn('startSessionBus(',server)
  self.assertIn('pg_notify($1,$2)',server)
  self.assertIn('broadcastLocal(',server)
