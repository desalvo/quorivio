"""RC77: one-click RC must be observational even with extra checked inputs."""
from __future__ import annotations
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
WORKFLOW=ROOT/'.github/workflows/ci.yml'
SCRIPT=ROOT/'tools/resolve_image_tags.sh'

class CampaignDispatchIsolation(unittest.TestCase):
 def test_campaign_admission_does_not_consume_any_publish_or_strict_inputs(self):
  text=WORKFLOW.read_text()
  chunk=text.split('      - name: Validate RC campaign is non-publishing and non-strict',1)[1].split('      - name:',1)[0]
  self.assertIn('inputs.rc_acceptance_suite',chunk)
  self.assertIn("RC_CAMPAIGN_PUBLISH: 'false'",chunk)
  self.assertIn("RC_CAMPAIGN_STRICT: 'false'",chunk)
  self.assertNotIn('RC_CAMPAIGN_PUBLISH: ${{ inputs.publish_image }}',chunk)
  self.assertNotIn('RC_CAMPAIGN_STRICT: ${{ inputs.rc_strict }}',chunk)
  self.assertIn('python3 tools/rc_campaign_preflight.py --check-workflow',chunk)

 def test_publish_and_strict_jobs_explicitly_reject_campaign_mode(self):
  text=WORKFLOW.read_text()
  pub=text.split('\n  publish:',1)[1].split('\n    needs:',1)[0]
  self.assertIn('inputs.publish_image == true',pub)
  self.assertIn('!inputs.rc_acceptance_suite',pub)
  self.assertIn("github.event_name == 'workflow_dispatch'",pub)
  strict=text.split('      - name: Strict release-candidate gate (manual opt-in)',1)[1].split('      - name:',1)[0]
  self.assertIn('inputs.rc_strict && !inputs.rc_acceptance_suite',strict)
  self.assertIn('environment: production',text.split('\n  publish:',1)[1])

 def test_publisher_shell_denies_campaign_even_with_explicit_publish_consent(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'out'
   env={**os.environ,'GITHUB_EVENT_NAME':'workflow_dispatch',
        'GITHUB_REPOSITORY':'desalvo/quorivio','GITHUB_REF':'refs/heads/main',
        'GITHUB_SHA':'abcd'*10,'GITHUB_OUTPUT':str(out),
        'QUORIVIO_PUBLISH_IMAGE':'true','QUORIVIO_PUBLISH_LATEST':'false',
        'QUORIVIO_RC_ACCEPTANCE_SUITE':'true'}
   blocked=subprocess.run(['bash',str(SCRIPT)],env=env,capture_output=True,text=True,timeout=8)
   self.assertNotEqual(blocked.returncode,0)
   self.assertIn('RC acceptance runs cannot publish',blocked.stderr)
   self.assertFalse(out.exists())
   env['QUORIVIO_RC_ACCEPTANCE_SUITE']='false'
   allowed=subprocess.run(['bash',str(SCRIPT)],env=env,capture_output=True,text=True,timeout=8)
   self.assertEqual(allowed.returncode,0,allowed.stderr)
   self.assertIn('desalvo/quorivio:sha-',out.read_text())

 def test_campaign_preflight_verifies_all_safety_layers(self):
  import sys
  sys.path.insert(0,str(ROOT/'tools'))
  from rc_campaign_preflight import campaign_audit
  audit=campaign_audit()
  self.assertFalse(audit['dispatch']['publish_image'])
  self.assertFalse(audit['dispatch']['rc_strict'])
  self.assertTrue(audit['dispatch']['rc_acceptance_suite'])

if __name__=='__main__':unittest.main()
