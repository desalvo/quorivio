"""Cycle 32: production upload AV and managed Kubernetes scanner parity."""
from __future__ import annotations
import tempfile
import unittest
import sys
from pathlib import Path
import yaml

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
from k8s_wizard import DEFAULTS,validate,generate


class AntivirusKubernetesCycle32(unittest.TestCase):
    def test_managed_scanner_is_private_and_mandatory(self):
        with tempfile.TemporaryDirectory() as tmp:
            generated=Path(tmp)
            files=generate(validate(dict(DEFAULTS)),generated)
            cm=yaml.safe_load((generated/'10-configmap.yaml').read_text())
            self.assertEqual(cm['data']['QUORIVIO_AV_REQUIRED'],'true')
            self.assertEqual(cm['data']['CLAMAV_HOST'],'quorivio-clamav')
            self.assertIn('13-clamav-deployment.yaml', files)
            self.assertIn('14-clamav-service.yaml', files)
            deployment=yaml.safe_load((generated/'13-clamav-deployment.yaml').read_text())
            container=deployment['spec']['template']['spec']['containers'][0]
            self.assertEqual(container['name'],'clamav')
            self.assertEqual(container['ports'][0]['containerPort'],3310)
            self.assertEqual(container['resources']['limits']['memory'],'4Gi')
            self.assertFalse(deployment['spec']['template']['spec']['automountServiceAccountToken'])
            svc=yaml.safe_load((generated/'14-clamav-service.yaml').read_text())
            self.assertEqual(svc['spec']['type'],'ClusterIP')
            self.assertNotIn('externalIPs',svc['spec'])
            self.assertNotIn('nodePort',svc['spec']['ports'][0])
            ingress=yaml.safe_load((generated/'40-ingress.yaml').read_text())
            self.assertNotIn('clamav',str(ingress))
            policy=yaml.safe_load((generated/'16-clamav-networkpolicy.yaml').read_text())
            self.assertEqual(policy['spec']['ingress'][0]['from'][0]['podSelector']['matchLabels'],{'app':'quorivio'})
            manifest=(generated/'kustomization.yaml').read_text()
            for resource in ('13-clamav-deployment.yaml','14-clamav-service.yaml','16-clamav-networkpolicy.yaml'):
                self.assertIn('  - '+resource,manifest)

    def test_external_av_mode_cannot_silently_disable_scanning(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg={**DEFAULTS,'antivirus_mode':'external','antivirus_host':'clamav.example.internal'}
            generated=Path(tmp)
            generate(validate(cfg),generated)
            cm=yaml.safe_load((generated/'10-configmap.yaml').read_text())
            self.assertEqual(cm['data']['QUORIVIO_AV_REQUIRED'],'true')
            self.assertEqual(cm['data']['CLAMAV_HOST'],'clamav.example.internal')
            self.assertFalse((generated/'13-clamav-deployment.yaml').exists())
            self.assertFalse((generated/'14-clamav-service.yaml').exists())
            self.assertNotIn('13-clamav-deployment.yaml',(generated/'kustomization.yaml').read_text())
            # Switching deployment mode removes orphan resources, not only references.
            generate(validate(dict(DEFAULTS)),generated)
            self.assertTrue((generated/'13-clamav-deployment.yaml').exists())
            generate(validate(cfg),generated)
            self.assertFalse((generated/'13-clamav-deployment.yaml').exists())
            self.assertFalse((generated/'16-clamav-networkpolicy.yaml').exists())

    def test_antivirus_mode_and_host_fail_closed(self):
        for changes in ({'antivirus_mode':'none'},
                        {'antivirus_mode':'external'},
                        {'antivirus_mode':'external','antivirus_host':'http://localhost:3310'},
                        {'antivirus_mode':'external','antivirus_host':'a..b'},
                        {'antivirus_mode':'managed','antivirus_host':'someone.example'},
                        {'antivirus_image':'invalid image'}):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):validate({**DEFAULTS,**changes})

    def test_latest_integrity_gate_is_before_gitleaks(self):
        wf=(ROOT/'.github/workflows/ci.yml').read_text()
        self.assertLess(wf.index('verify_rc_cycle31_inventory.py --historical'),
                        wf.index('verify_rc_cycle33_inventory.py'))
        self.assertLess(wf.index('verify_rc_cycle33_inventory.py'),wf.index('Detect credential leaks'))

    def test_actual_clamd_acceptance_is_opt_in_and_no_registry_publish(self):
        wf=yaml.safe_load((ROOT/'.github/workflows/ci.yml').read_text())
        job=wf['jobs']['clamav-runtime']
        self.assertIn('inputs.clamav_runtime_test',job['if'])
        self.assertIn('quorivio-ci-clamav',str(job))
        self.assertNotIn('docker push',str(job))
        self.assertIn('127.0.0.1:23310:3310',str(job))
        source=(ROOT/'tools/ci_clamav_real.mjs').read_text()
        self.assertIn('eicar_not_detected',source)
        self.assertIn('malware_detected',source)
        self.assertIn('await scan(clean,env)',source)

    def test_production_no_missing_scanner_bypass_contract(self):
        src=(ROOT/'apps/api/src/malware-scan.ts').read_text()
        self.assertIn("env.NODE_ENV==='production'||env.QUORIVIO_AV_REQUIRED==='true'",src)
        self.assertIn('antivirus_premature_response',src)
        self.assertIn('antivirus_response_too_large',src)
        self.assertIn('antivirus_timeout',src)

if __name__=='__main__': unittest.main()
