"""Cycle 36: two-worker HAProxy Technologies runtime contract (CI proof pending)."""
from __future__ import annotations
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import yaml
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import ci_k8s_multinode_ingress_smoke as smoke
from k8s_wizard import DEFAULTS,generate,validate
from rc_gate_audit import audit

class HAProxyRuntimeAcceptance(unittest.TestCase):
    def test_workflow_requires_explicit_optin_and_never_publishes(self):
        workflow=yaml.safe_load((ROOT/'.github/workflows/ci.yml').read_text())
        input_cfg=workflow['on']['workflow_dispatch']['inputs'] if 'on' in workflow else workflow[True]['workflow_dispatch']['inputs']
        self.assertFalse(input_cfg['kubernetes_haproxy_test']['default'])
        job=workflow['jobs']['kubernetes-haproxy-ingress']
        self.assertIn('workflow_dispatch',job['if'])
        self.assertIn('inputs.kubernetes_haproxy_test',job['if'])
        self.assertEqual(job['permissions'],{'contents':'read'})
        self.assertEqual(job['needs'],'validate')
        self.assertNotIn('publish_image',str(job))
        self.assertNotIn('docker push',str(job))
        self.assertNotIn('kubectl get secrets',str(job))
        self.assertIn('--controller haproxytech',str(job))
        self.assertIn('if: always()', (ROOT/'.github/workflows/ci.yml').read_text())
        self.assertEqual(job['steps'][-1]['if'],'always()')

    def test_haproxytech_generated_ingress_has_class_and_legacy_annotation(self):
        with tempfile.TemporaryDirectory() as td:
            cfg=validate({**DEFAULTS,'name':smoke.APP,'namespace':smoke.NS,
                          'ingress_controller':'haproxy','haproxy_variant':'haproxytech',
                          'tls_termination':False,'replicas':2,
                          'enforce_node_diversity':True,'asset_access_mode':'ReadWriteMany'})
            generate(cfg,Path(td))
            manifests=[]
            for f in Path(td).glob('*.yaml'):
                for resource in yaml.safe_load_all(f.read_text()):
                    if isinstance(resource,dict) and resource.get('kind')=='Ingress':
                        manifests.append(resource)
            self.assertEqual(len(manifests),1)
            ing=manifests[0]
            self.assertEqual(ing['spec']['ingressClassName'],'haproxy')
            self.assertEqual(ing['metadata']['annotations']['haproxy.org/ingress.class'],'haproxy')
            self.assertEqual(ing['spec']['rules'][0]['host'],cfg['host'])
            self.assertNotIn('tls',ing['spec'])

    def test_haproxy_service_discovery_requires_unique_private_http_port(self):
        def fetch(*args,**kwargs):
            self.assertIn('quorivio-ci-haproxy',args)
            return json.dumps({'items':[{'metadata':{'name':'ingress-svc'},
                 'spec':{'type':'ClusterIP','clusterIP':'10.0.0.4',
                         'ports':[{'port':80,'protocol':'TCP'},{'port':443}]}}]})
        with patch.object(smoke,'run',fetch):
            self.assertEqual(smoke.haproxy_ingress_service(),
                'ingress-svc.quorivio-ci-haproxy.svc.cluster.local:80')
        for services in ([],[{'metadata':{'name':'only-443'},'spec':{'type':'ClusterIP',
                'clusterIP':'10.0.0.4','ports':[{'port':443}]}}],
                [{'metadata':{'name':n},'spec':{'type':'ClusterIP','clusterIP':'10.0.0.4',
                    'ports':[{'port':80}]}} for n in ('x','y')]):
            with patch.object(smoke,'run',return_value=json.dumps({'items':services})):
                with self.assertRaisesRegex(RuntimeError,'exactly one'):
                    smoke.haproxy_ingress_service()

    def test_official_version_pinned_no_unintended_public_endpoint(self):
        captured=[]
        def fake(*args,**kwargs):
            captured.append(args)
            if args[:3]==('kubectl','get','ingressclass'):
                return json.dumps({'metadata':{'name':'haproxy'}})
            if 'services' in args: return json.dumps({'items':[{'metadata':{'name':'haproxy'},'spec':{
                'type':'ClusterIP','clusterIP':'10.0.0.1','ports':[{'port':80}]}}]})
            return ''
        with patch.object(smoke,'run',fake):
            uri=smoke.install_ingress('haproxytech')
        self.assertEqual(uri,'haproxy.quorivio-ci-haproxy.svc.cluster.local:80')
        helm=next(a for a in captured if a[0]=='helm')
        self.assertIn('oci://ghcr.io/haproxytech/helm-charts/kubernetes-ingress',helm)
        self.assertEqual(helm[helm.index('--version')+1],smoke.HAPROXY_CHART_VERSION)
        self.assertIn('controller.service.type=ClusterIP',helm)
        self.assertIn('controller.ingressClass=haproxy',helm)
        self.assertNotIn('LoadBalancer',helm)
        with self.assertRaisesRegex(ValueError,'Unsupported'):
            smoke.install_ingress('public-unknown')

    def test_nginx_path_untouched_and_new_mode_has_distinct_evidence(self):
        self.assertIn('ingress-nginx-controller',smoke.NGINX_INGRESS)
        self.assertIn('controller-v1.12.1',smoke.NGINX_MANIFEST)
        self.assertEqual(smoke.ingress_http_source().count('http.request'),1)
        self.assertEqual(audit()['score'],80.75)

if __name__=='__main__':unittest.main()
