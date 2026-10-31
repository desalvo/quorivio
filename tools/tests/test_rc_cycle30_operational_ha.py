"""Cycle 30: actual Kubernetes API evidence, negative HA cases and wizard CLI parity."""
from __future__ import annotations

import copy
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import k8s_operational_gate as gate
import k8s_wizard as wizard


def fixture() -> dict:
    labels = {'app':'quorivio'}
    dep={'metadata':{'generation':4}, 'spec':{
        'replicas':2, 'selector':{'matchLabels':labels},
        'strategy':{'type':'RollingUpdate','rollingUpdate':{'maxUnavailable':0}},
        'template':{'spec':{'terminationGracePeriodSeconds':45,
            'topologySpreadConstraints':[{'topologyKey':'kubernetes.io/hostname',
                'whenUnsatisfiable':'DoNotSchedule','minDomains':2}],
            'volumes':[{'name':'assets','persistentVolumeClaim':{'claimName':'quorivio-assets'}}]}}},
        'status':{'observedGeneration':4,'readyReplicas':2,'availableReplicas':2}}
    def pod(name,node):
        return {'metadata':{'name':name},'spec':{'nodeName':node},
                'status':{'conditions':[{'type':'Ready','status':'True'}]}}
    return {'deployment':dep,'pods':{'items':[pod('app-a','node-a'),pod('app-b','node-b')]},
        'pvc':{'metadata':{'name':'quorivio-assets'},
               'spec':{'volumeName':'pv-rwx','accessModes':['ReadWriteMany']},
               'status':{'phase':'Bound'}},
        'pv':{'metadata':{'name':'pv-rwx'},
              'spec':{'accessModes':['ReadWriteMany'],'csi':{'driver':'cephfs.csi.ceph.com'}}},
        'pdb':{'metadata':{'name':'quorivio-availability'},
               'spec':{'selector':{'matchLabels':labels}},
               'status':{'currentHealthy':2,'disruptionsAllowed':1}},
        'service':{'spec':{'selector':labels}},
        'endpoints':{'items':[{'metadata':{'labels':{'kubernetes.io/service-name':'quorivio'}},
                   'endpoints':[{'nodeName':'node-a','conditions':{'ready':True}},
                                {'nodeName':'node-b','conditions':{'ready':True}}]}]},
        'ingress':{'spec':{'ingressClassName':'nginx',
                   'rules':[{'host':'quorivio.example.org','http':{'paths':[
                       {'path':'/','pathType':'Prefix',
                        'backend':{'service':{'name':'quorivio'}}}]}}],
                   'tls':[{'hosts':['quorivio.example.org'],'secretName':'quorivio-tls'}]}}}


def check(data):
    return gate.check(data, app='quorivio', service='quorivio',
                      ingress='quorivio', host='quorivio.example.org',
                      ingress_class='nginx', replicas=2, require_tls=True,
                      pdb='quorivio-availability')


class OperationalGateTests(unittest.TestCase):
    def test_valid_multi_node_csi_and_ingress(self):
        evidence = check(fixture())
        self.assertEqual((evidence['status'],evidence['distinct_ready_nodes'],evidence['rwx_backend_type']),
                         ('API_CONTRACT_PASS',2,'csi'))
        self.assertTrue(evidence['limitations'])

    def test_nfs_and_cephfs_are_known_protocols(self):
        for key in ('nfs','cephfs'):
            with self.subTest(storage=key):
                f=fixture(); f['pv']['spec']={'accessModes':['ReadWriteMany'],key:{'server':'example'}}
                self.assertEqual(check(f)['rwx_backend_type'],key)

    def test_refuse_unready_or_stale_deployment(self):
        for action in (
            lambda x:x['deployment']['status'].update(availableReplicas=1),
            lambda x:x['deployment']['status'].update(observedGeneration=2),
            lambda x:x['deployment']['spec']['strategy']['rollingUpdate'].update(maxUnavailable=1),
        ):
            f=fixture();action(f)
            with self.assertRaises(gate.EvidenceFailure):check(f)

    def test_refuse_collocation_unready_and_terminating_pods(self):
        for action in (
            lambda x:x['pods']['items'][1]['spec'].update(nodeName='node-a'),
            lambda x:x['pods']['items'][1]['status']['conditions'][0].update(status='False'),
            lambda x:x['pods']['items'][1]['metadata'].update(deletionTimestamp='2026-10-30T00:00:00Z'),
        ):
            f=fixture();action(f)
            with self.assertRaises(gate.EvidenceFailure):check(f)

    def test_refuse_non_strict_spread(self):
        f=fixture();f['deployment']['spec']['template']['spec']['topologySpreadConstraints'][0]['whenUnsatisfiable']='ScheduleAnyway'
        with self.assertRaisesRegex(gate.EvidenceFailure,'Strict'):check(f)

    def test_refuse_rwo_unbound_and_mismatched_claims(self):
        for action in (
            lambda x:x['pvc']['spec'].update(accessModes=['ReadWriteOnce']),
            lambda x:x['pvc']['status'].update(phase='Pending'),
            lambda x:x['pvc']['spec'].update(volumeName='different-pv'),
        ):
            f=fixture();action(f)
            with self.assertRaises(gate.EvidenceFailure):check(f)

    def test_hostpath_and_local_are_rejected_even_with_rwx_label(self):
        for backend in ('hostPath','local'):
            f=fixture();f['pv']['spec'][backend]={'path':'/var/local'}
            with self.assertRaisesRegex(gate.EvidenceFailure,'HostPath/local'):
                check(f)

    def test_unknown_pv_driver_is_not_an_accepted_proof(self):
        f=fixture();f['pv']['spec'].pop('csi')
        with self.assertRaisesRegex(gate.EvidenceFailure,'Unknown storage'):check(f)

    def test_refuse_pdb_without_available_disruption(self):
        f=fixture();f['pdb']['status']['disruptionsAllowed']=0
        with self.assertRaisesRegex(gate.EvidenceFailure,'PDB'):check(f)

    def test_refuse_pdb_wrong_selector(self):
        f=fixture();f['pdb']['spec']['selector']['matchLabels']={'app':'other'}
        with self.assertRaisesRegex(gate.EvidenceFailure,'PDB'):check(f)

    def test_refuse_service_without_distinct_ready_endpoints(self):
        f=fixture();f['endpoints']['items'][0]['endpoints'][1]['conditions']['ready']=False
        with self.assertRaisesRegex(gate.EvidenceFailure,'endpoints'):check(f)

    def test_ingress_host_tls_and_service_must_match(self):
        for action in (
            lambda x:x['ingress']['spec'].update(ingressClassName='haproxy'),
            lambda x:x['ingress']['spec']['rules'][0].update(host='wrong.example.org'),
            lambda x:x['ingress']['spec']['rules'][0]['http']['paths'][0]['backend']['service'].update(name='not-quorivio'),
            lambda x:x['ingress']['spec'].update(tls=[]),
        ):
            f=fixture();action(f)
            with self.assertRaises(gate.EvidenceFailure):check(f)

    def test_query_errors_redact_sensitive_stdout_and_stderr(self):
        from subprocess import CompletedProcess
        with patch.object(gate.subprocess,'run',return_value=CompletedProcess([],1,'raw secret','private error')):
            with self.assertRaises(gate.EvidenceFailure) as e:gate.kubectl('get','secrets')
        self.assertNotIn('raw secret',str(e.exception));self.assertNotIn('private error',str(e.exception))

    def test_public_probe_tls_with_hostname_validation(self):
        response=unittest.mock.MagicMock()
        response.status=200
        response.read.return_value=b'{"status":"ready"}'
        response.__enter__.return_value=response
        handler=unittest.mock.MagicMock()
        handler.open.return_value=response
        with patch.object(gate.urllib.request,'build_opener',return_value=handler) as mock_open:
            result=gate.probe_public_ingress('quorivio.example.org',require_tls=True)
        self.assertEqual(result['public_ingress_readiness'],'HTTP_200')
        self.assertTrue(result['certificate_hostname_validation'])
        self.assertIn('https://quorivio.example.org/api/health/ready',handler.open.call_args.args[0].full_url)
        self.assertTrue(mock_open.called)

    def test_public_probe_rejects_nonready_and_redacts_errors(self):
        response=unittest.mock.MagicMock()
        response.status=503
        response.read.return_value=b'No database'
        response.__enter__.return_value=response
        handler=unittest.mock.MagicMock();handler.open.return_value=response
        with patch.object(gate.urllib.request,'build_opener',return_value=handler):
            with self.assertRaises(gate.EvidenceFailure):
                gate.probe_public_ingress('quorivio.example.org',require_tls=True)
        handler.open.side_effect=OSError('secret private address')
        with patch.object(gate.urllib.request,'build_opener',return_value=handler):
            with self.assertRaises(gate.EvidenceFailure) as error:
                gate.probe_public_ingress('quorivio.example.org',require_tls=True)
        self.assertNotIn('secret private address',str(error.exception))

    def test_fail_closed_context_and_invalid_names(self):
        with self.assertRaisesRegex(gate.EvidenceFailure,'resource name invalid'):
            gate.collect(namespace='valid',app='../../bad',service='service',ingress='ing',
                         host='quorivio.example.org',ingress_class='nginx',pdb='pdb',replicas=2,require_tls=True,context='k')
        with patch.object(gate,'kubectl',return_value={'contexts':[{'name':'production'}]}):
            with self.assertRaisesRegex(gate.EvidenceFailure,'unexpected Kubernetes context'):
                gate.collect(namespace='valid',app='app',service='service',ingress='ing',
                             host='quorivio.example.org',ingress_class='nginx',pdb='pdb',replicas=2,require_tls=True,context='staging')

    def test_read_only_commands_cannot_mutate_k8s(self):
        seen=[]
        f=fixture()
        def api(*args,**kwargs):
            seen.append(args)
            if args[:2]==('config','view'):
                return {'contexts':[{'name':'test-kind'}]}
            if args[0]=='get':return f['pv']
            kind=args[3] if len(args)>4 else ''
            if kind=='deployment':return f['deployment']
            if kind=='pods':return f['pods']
            if kind=='pvc':return f['pvc']
            if kind=='pdb':return f['pdb']
            if kind=='ingress':return f['ingress']
            if kind=='service':return f['service']
            if kind=='endpointslices':return f['endpoints']
            raise AssertionError(args)
        with patch.object(gate,'kubectl',side_effect=api):
            receipt=gate.collect(namespace='quorivio',app='quorivio',service='quorivio',ingress='quorivio',
                                 host='quorivio.example.org',ingress_class='nginx',pdb='quorivio-availability',
                                 replicas=2,require_tls=True,context='test-kind')
        self.assertEqual(receipt['status'],'API_CONTRACT_PASS')
        self.assertTrue(all(a[0] in ('config','-n','get') for a in seen))


class WizardAndCIContracts(unittest.TestCase):
    def test_cli_strict_spread_true_can_be_enabled(self):
        with tempfile.TemporaryDirectory() as td:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(wizard.main(['--unattended','--output',td,
                    '--set','replicas=2','--set','asset_access_mode=ReadWriteMany',
                    '--set','enforce_node_diversity=true']),0)
            deploy=(Path(td)/'20-deployment.yaml').read_text()
            self.assertIn('whenUnsatisfiable: DoNotSchedule',deploy)
            self.assertIn('minDomains: 2',deploy)

    def test_cli_false_is_boolean_and_invalid_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with redirect_stdout(io.StringIO()):
                self.assertEqual(wizard.main(['--unattended','--output',td,'--set','enforce_node_diversity=false']),0)
            with redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
                wizard.main(['--unattended','--output',td,'--set','enforce_node_diversity=yes'])

    def test_ingress_ready_label_and_no_auto_publish(self):
        kind=(ROOT/'tools/ci_kind_multinode.yaml').read_text()
        self.assertIn('ingress-ready: "true"',kind)
        workflow=(ROOT/'.github/workflows/ci.yml').read_text()
        job=workflow[workflow.index('  kubernetes-multinode-ingress:'):workflow.index('  runtime-architecture:')]
        self.assertNotIn('docker push',job)
        self.assertIn('python3 tools/ci_k8s_multinode_ingress_smoke.py',job)

    def test_helm_does_not_automount_service_account(self):
        deploy=(ROOT/'helm/quorivio/templates/deployment.yaml').read_text()
        self.assertIn('automountServiceAccountToken: false',deploy)

    def test_rc_score_unchanged_without_ci_and_independent_review(self):
        from rc_gate_audit import audit
        from rc_release_preflight import preflight
        self.assertEqual(audit()['score'],81.75)
        self.assertFalse(preflight()['release_candidate_ready'])


if __name__=='__main__':unittest.main()
