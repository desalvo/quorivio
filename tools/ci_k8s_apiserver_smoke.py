#!/usr/bin/env python3
"""Validate real Kustomize manifests against a disposable Kubernetes API server.

The KIND runner must supply kubectl, cluster API and a pre-existing `default`
namespace. This is API-schema validation, never runtime, ingress, RWX or HA.
No generated credentials or manifest values are printed or uploaded.
"""
import subprocess
import sys
import tempfile
from pathlib import Path

from k8s_wizard import DEFAULTS,generate,validate

VARIANTS=(
    ('nginx-internal',{}),
    ('nginx-multi-internal',{'replicas':2,'asset_access_mode':'ReadWriteMany',
                             'tls_secret':'tls-test','app_node_selector':'kubernetes.io/arch=amd64'}),
    ('haproxy-community',{'replicas':3,'asset_access_mode':'ReadWriteMany',
                           'ingress_controller':'haproxy','postgres_mode':'external',
                           'postgres_host':'pg.example.invalid',
                           'postgres_password':'ci-disposable-db-password-only'}),
    ('haproxytech-external',{'replicas':2,'asset_access_mode':'ReadWriteMany',
                              'ingress_controller':'haproxy','haproxy_variant':'haproxytech',
                              'postgres_mode':'external','postgres_host':'pg.example.invalid',
                              'postgres_password':'ci-disposable-db-password-only',
                              'tls_secret':'test-tls-secret'})
)


def run(argv):
    result=subprocess.run(argv,capture_output=True,text=True,timeout=90)
    if result.returncode:
        raise RuntimeError(f'Kubernetes API/schema rejected manifest (code {result.returncode}; secrets and detailed output suppressed)')


def main():
    run(['kubectl','cluster-info'])
    with tempfile.TemporaryDirectory(prefix='quorivio-disposable-k8s-') as tmp:
        for name,values in VARIANTS:
            output=Path(tmp)/name
            cfg=validate({**DEFAULTS,**values,'namespace':'default',
                          'name':'quorivio-'+name})
            generate(cfg,output)
            run(['kubectl','kustomize',str(output)])
            run(['kubectl','apply','--dry-run=server','-k',str(output)])
            print('PASS Kubernetes API server-side dry-run:',name)
    print('PASS Kubernetes API manifest validation only; real workload, RWX, HAProxy/NGINX runtime and hardware remain pending')


if __name__=='__main__':
    try: main()
    except (RuntimeError,subprocess.TimeoutExpired) as e:
        print('FAIL:',str(e),file=sys.stderr)
        sys.exit(1)
