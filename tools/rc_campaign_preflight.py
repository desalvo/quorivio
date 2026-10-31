#!/usr/bin/env python3
"""Offline RC closure campaign: verify one-click CI is complete and non-publishing.

Do not promote gates based on a workflow run being green: only explicitly
verified individual job evidence can move a bounded automated subgate.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OPTIONS = (
 'browser_test', 'cross_browser_test', 'capacity_test', 'capacity_slo_test',
 'kubernetes_manifest_test', 'kubernetes_runtime_test',
 'kubernetes_multinode_test', 'kubernetes_haproxy_test',
 'live_idle_test', 'kubernetes_tls_test', 'clamav_runtime_test',
 'rootless_podman_test', 'runtime_arch_test',
)

def campaign_audit(root: Path = ROOT) -> dict:
 workflow = (root/'.github/workflows/ci.yml').read_text(encoding='utf-8')
 assert re.search(r'^      rc_acceptance_suite:\s*$', workflow, re.M), 'campaign input missing'
 # Every opt-in branch must be reachable with only the single campaign flag.
 for option in OPTIONS:
  active = [line.strip() for line in workflow.splitlines() if
            re.match(r'^\s*if:', line) and 'inputs.'+option in line]
  if not active or any(('inputs.'+option not in line or 'inputs.rc_acceptance_suite' not in line) for line in active):
   raise ValueError('uncovered RC campaign option: '+option)
 # The final job must inspect all 11 independently required jobs.
 from rc_campaign_result_gate import REQUIRED_JOBS
 for name in REQUIRED_JOBS:
  if not re.search(r'^      - '+re.escape(name)+r'\s*$',workflow,re.M):
   raise ValueError('missing mandatory RC campaign conclusion dependency: '+name)
 if not re.search(r'^  rc-campaign-conclusion:\s*$',workflow,re.M):
  raise ValueError('campaign conclusion job missing')
 # The campaign must not be able to activate publication or strict sign-off.
 # An RC campaign cannot trigger publishing or strict sign-off even if
 # GitHub persists a previously selected checkbox in workflow_dispatch.
 publish_guard = "if: github.event_name == 'workflow_dispatch' && inputs.publish_image == true && !inputs.rc_acceptance_suite &&"
 strict_guard = "if: github.event_name == 'workflow_dispatch' && inputs.rc_strict && !inputs.rc_acceptance_suite"
 if publish_guard not in workflow:
  raise ValueError('publishing guard must exclude the RC campaign')
 if strict_guard not in workflow:
  raise ValueError('strict release gate must exclude the RC campaign')
 if "RC_CAMPAIGN_PUBLISH: 'false'" not in workflow or "RC_CAMPAIGN_STRICT: 'false'" not in workflow:
  raise ValueError('RC admission must be isolated from other dispatch inputs')
 if "test \"$RC_CAMPAIGN_PUBLISH\" = 'false'" not in workflow or "test \"$RC_CAMPAIGN_STRICT\" = 'false'" not in workflow:
  raise ValueError('campaign admission checks missing')
 if 'QUORIVIO_RC_ACCEPTANCE_SUITE: ${{ inputs.rc_acceptance_suite }}' not in workflow:
  raise ValueError('publisher missing RC campaign safety flag')
 if 'QUORIVIO_RC_ACCEPTANCE_SUITE:-false' not in (root/'tools/resolve_image_tags.sh').read_text():
  raise ValueError('publisher script must explicitly deny RC campaigns')
 ledger = json.loads((root/'docs/RC_GATE_MATRIX.json').read_text())
 gates = ledger['gates']
 from rc_gate_audit import audit
 if round(sum(g['weight']*(1 if g['status']=='accepted' else .5 if g['status']=='partial' else 0) for g in gates), 2) != audit()['score']:
  raise ValueError('current certification score must come from RC matrix')
 pending = [{'id':g['id'],'area':g['area'],'weight':g['weight'],'remaining':g['remaining']}
            for g in gates if g['status']!='accepted']
 return {
  'version': ledger['version'],
  'certified_score':audit()['score'],
  'pending_gates':len(pending),
  'pending':pending,
  'dispatch':{'workflow':'.github/workflows/ci.yml',
              'rc_acceptance_suite':True,'rc_strict':False,'publish_image':False},
  'automatic_checks':list(OPTIONS),
  'external_signoff_required':True,
  'limits':['KIND TLS uses a disposable private certificate, not a public CA',
            'KIND RWX host-bind is not independent physical CSI/NFS storage',
            'Physical mobile/assistive-device, independent legal and security sign-offs are not CI-certifiable'],
 }

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--check-workflow',action='store_true')
 parser.add_argument('--output',type=Path)
 a=parser.parse_args()
 report=campaign_audit()
 if a.output:
  a.output.parent.mkdir(parents=True,exist_ok=True)
  a.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 if a.check_workflow:print('PASS non-publishing one-click RC campaign:',len(OPTIONS),'independent opt-in flags reachable; score not promoted')
 else:print(json.dumps(report,indent=2,ensure_ascii=False))
if __name__=='__main__':main()
