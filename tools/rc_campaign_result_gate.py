#!/usr/bin/env python3
"""Require every requested automatic RC campaign job to succeed, not merely end.

This job is always evaluated after all campaign dependencies. It never upgrades
independent/manual RC ledger gates, and does not publish anything.
"""
from __future__ import annotations
import json
import os
from pathlib import Path

REQUIRED_JOBS = (
 'validate', 'cross-browser', 'image-build', 'kubernetes-api-manifests',
 'kubernetes-runtime', 'kubernetes-multinode-ingress',
 'kubernetes-https-ingress', 'kubernetes-haproxy-ingress',
 'runtime-architecture', 'runtime-podman-rootless', 'clamav-runtime',
)

def evaluate_results(needs: object) -> dict:
 if not isinstance(needs, dict):
  raise ValueError('invalid campaign job results')
 names = set(needs)
 if names != set(REQUIRED_JOBS):
  raise ValueError('campaign dependencies changed or missing: ' + ','.join(sorted(set(REQUIRED_JOBS)-names)))
 results = {}
 for job in REQUIRED_JOBS:
  item = needs[job]
  if not isinstance(item, dict) or item.get('result') not in ('success','failure','cancelled','skipped'):
   raise ValueError('invalid campaign job result: '+job)
  results[job]=item['result']
 return {'ok':all(result == 'success' for result in results.values()),
         'results':results,
         'completed':sum(result=='success' for result in results.values()),
         'required':len(REQUIRED_JOBS)}

def main()->int:
 value=os.environ.get('RC_CAMPAIGN_NEEDS_JSON')
 if not value:raise ValueError('GitHub campaign job results missing')
 report=evaluate_results(json.loads(value))
 rows=['## Quorivio automatic RC campaign',
       f"{report['completed']}/{report['required']} required jobs succeeded.",
       '', '| Automated job | Result |','|---|---|',
       *(f"| `{name}` | {status} |" for name,status in report['results'].items()),
       '', 'Independent GDPR/AGID/security, physical devices, public TLS and CSI/NFS RWX are NOT certified by this campaign.',
       'Do not promote RC gates without individual logged evidence and explicit reconciliation.']
 text='\n'.join(rows)+'\n'
 print(text)
 if os.environ.get('GITHUB_STEP_SUMMARY'):
  with Path(os.environ['GITHUB_STEP_SUMMARY']).open('a',encoding='utf-8') as f:f.write(text)
 return 0 if report['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
