"""Cycle 49 accepted GitHub HAProxy evidence + fail-closed real-cluster RWX probe."""
from __future__ import annotations

import copy
import json
import sys
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools'))
import k8s_rwx_cross_node_probe as rwx
from rc_gate_audit import audit
from rc_release_preflight import preflight


def fixture():
    selector={'app':'quorivio'}
    mount={'name':'assets','mountPath':'/app/assets'}
    vol={'name':'assets','persistentVolumeClaim':{'claimName':'quorivio-assets'}}
    def pod(name,node):
        return {'metadata':{'name':name,'labels':selector},
                'spec':{'nodeName':node,'volumes':[copy.deepcopy(vol)],
                        'containers':[{'name':'api','volumeMounts':[copy.deepcopy(mount)]}]},
                'status':{'conditions':[{'type':'Ready','status':'True'}],
                          'containerStatuses':[{'name':'api','ready':True}]}}
    dep={'metadata':{'generation':1},'spec':{'replicas':2,'selector':{'matchLabels':selector},
         'template':{'spec':{'volumes':[copy.deepcopy(vol)],
                             'containers':[{'name':'api','volumeMounts':[copy.deepcopy(mount)]}]}}},
         'status':{'observedGeneration':1,'readyReplicas':2}}
    pvc={'metadata':{'name':'quorivio-assets'},'spec':{'accessModes':['ReadWriteMany'],'volumeName':'pv-rwx'},
         'status':{'phase':'Bound'}}
    pv={'metadata':{'name':'pv-rwx'},'spec':{'accessModes':['ReadWriteMany'],'csi':{'driver':'cephfs.csi.ceph.com'}}}
    return dep,{'items':[pod('api-a','node-a'),pod('api-b','node-b')]},pvc,pv


class EvidenceReconciliation(unittest.TestCase):
    def test_verified_haproxy_split_is_not_double_counted(self):
        matrix=json.loads((ROOT/'docs/RC_GATE_MATRIX.json').read_text())
        b4={x['id']:x for x in matrix['gates'] if x['id'].startswith('B4')}
        self.assertEqual(set(b4),{'B4','B4-LOAD','B4-KIND-INGRESS-RECOVERY','B4-HAProxyTECH-KIND','B4-500-GLOBAL-SLO'})
        self.assertEqual((b4['B4']['status'],b4['B4']['weight']),('partial',0.5))
        self.assertEqual((b4['B4-HAProxyTECH-KIND']['status'],b4['B4-HAProxyTECH-KIND']['weight']),('accepted',1))
        self.assertEqual(b4['B4-HAProxyTECH-KIND']['verified_job_id'],124297991439)
        self.assertEqual(b4['B4-HAProxyTECH-KIND']['verified_commit_sha'],
                         '64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c')
        self.assertEqual(sum(x['weight'] for x in b4.values()),5)
        self.assertEqual(audit()['score'],81.75)
        self.assertEqual((preflight()['accepted_gates'],len(preflight()['unaccepted_gates'])),(38,17))


class CrossNodeRWXContract(unittest.TestCase):
    def check(self,data=None):
        return rwx.assess(*(data or fixture()),mount='/app/assets')

    def test_two_ready_nodes_bound_network_pvc(self):
        actual=self.check()
        self.assertEqual((actual['status'],actual['backend'],actual['distinct_nodes']),
                         ('API_CONTRACT_PASS','csi',2))
        self.assertEqual(actual['pod_pair'],['api-a','api-b'])

    def test_refuse_hostpath_local_rwo_unknown_and_unbound(self):
        for change in (
            lambda d: d[3]['spec'].update(hostPath={'path':'/host'}),
            lambda d: d[3]['spec'].update(local={'path':'/local'}),
            lambda d: d[2]['spec'].update(accessModes=['ReadWriteOnce']),
            lambda d: d[3]['spec'].pop('csi'),
            lambda d: d[2]['status'].update(phase='Pending'),
            lambda d: d[2]['spec'].update(volumeName='other-pv'),
        ):
            case=list(copy.deepcopy(fixture()))
            change(case)
            with self.subTest(change=change),self.assertRaises(rwx.ProbeError):self.check(case)

    def test_refuse_non_disjoint_nodes_and_unready_or_mislabelled_pods(self):
        for change in (
            lambda d: d[1]['items'][1]['spec'].update(nodeName='node-a'),
            lambda d: d[1]['items'][1]['status']['conditions'][0].update(status='False'),
            lambda d: d[1]['items'][1]['status']['containerStatuses'][0].update(ready=False),
            lambda d: d[1]['items'][1]['metadata'].update(labels={'app':'other'}),
            lambda d: d[1]['items'][1]['metadata'].update(deletionTimestamp='2026-10-30T00:00:00Z'),
            lambda d: d[1]['items'][1]['spec'].update(volumes=[]),
            lambda d: d[1]['items'][1]['spec']['containers'][0].update(volumeMounts=[]),
        ):
            case=list(copy.deepcopy(fixture()));change(case)
            with self.subTest(change=change),self.assertRaises(rwx.ProbeError):self.check(case)

    def test_refuse_unsafe_mount_and_readonly_or_subpath(self):
        for path in ('/','/app','app/assets','/app/assets/../admin','/app/assets/','/app/../../tmp'):
            with self.subTest(path=path),self.assertRaises(rwx.ProbeError):rwx.validate_mount(path)
        for change in (
            lambda d:d[0]['spec']['template']['spec']['containers'][0]['volumeMounts'][0].update(readOnly=True),
            lambda d:d[0]['spec']['template']['spec']['containers'][0]['volumeMounts'][0].update(subPath='mixed'),
            lambda d:d[1]['items'][0]['spec']['containers'][0]['volumeMounts'][0].update(readOnly=True),
        ):
            case=list(copy.deepcopy(fixture()));change(case)
            with self.subTest(change=change),self.assertRaises(rwx.ProbeError):self.check(case)

    def test_opt_in_exchange_success_and_cleanup_both_pods(self):
        calls=[]
        def fake(command,**kwargs):
            calls.append((command,kwargs))
            return 'RWX_OK'
        result=rwx.exchange(context='production',namespace='quorivio',evidence=self.check(),runner=fake)
        self.assertEqual(result['status'],'CROSS_NODE_RW_EXCHANGE_PASS')
        self.assertEqual([c[0][-1] for c in calls],['write-a','read-a','write-b','read-b','clean','clean'])
        self.assertEqual([c[0][7] for c in calls],['api-a','api-b','api-b','api-a','api-a','api-b'])
        self.assertTrue(all(c[0][0]=='kubectl' and c[0][1:5]==['--context','production','-n','quorivio'] for c in calls))
        self.assertEqual(len({c[0][-2] for c in calls}),1)
        self.assertEqual(len({c[1]['stdin'] for c in calls[:4]}),1)

    def test_write_error_still_cleans_both_pods(self):
        calls=[]
        def fake(command,**kwargs):
            action=command[-1];calls.append(action)
            if action=='read-a':raise rwx.ProbeError('synthetic I/O failure')
            return 'RWX_OK'
        with self.assertRaisesRegex(rwx.ProbeError,'synthetic I/O failure'):
            rwx.exchange(context='production',namespace='quorivio',evidence=self.check(),runner=fake)
        self.assertEqual(calls,['write-a','read-a','clean','clean'])

    def test_wrong_context_fails_before_reading_cluster(self):
        calls=[]
        def fake(command,**kwargs):
            calls.append(command)
            return 'wrong-cluster'
        with self.assertRaisesRegex(rwx.ProbeError,'different from the expected'):
            rwx.collect(context='production',namespace='quorivio',deployment='api',
                        mount='/app/assets',confirm_write=True,runner=fake)
        self.assertEqual(calls,[['kubectl','config','current-context']])

    def test_read_only_by_default_and_real_opt_in(self):
        dep,pods,pvc,pv=fixture()
        response=[dep,pods,pvc,pv]
        calls=[]
        def fake(command,**kwargs):
            calls.append(command)
            if command[-2:] == ['current-context'] or command==['kubectl','config','current-context']:
                return 'production'
            if 'exec' in command:
                return 'RWX_OK'
            return json.dumps(response.pop(0))
        result=rwx.collect(context='production',namespace='quorivio',deployment='api',
                           mount='/app/assets',confirm_write=False,runner=fake)
        self.assertEqual(result['status'],'API_CONTRACT_ONLY_NO_IO')
        self.assertFalse(any('exec' in c for c in calls))
        response[:]=[dep,pods,pvc,pv];calls.clear()
        result=rwx.collect(context='production',namespace='quorivio',deployment='api',
                           mount='/app/assets',confirm_write=True,runner=fake)
        self.assertEqual(result['status'],'CROSS_NODE_RW_EXCHANGE_PASS')
        self.assertEqual(sum('exec' in c for c in calls),6)

    def test_real_node_file_exchange_and_cleanup_without_kubernetes(self):
        if not shutil.which('node'):
            self.skipTest('Node runtime unavailable')
        with tempfile.TemporaryDirectory() as directory:
            token='abcdef'*8
            identity='a'*32
            for action in ('write-a','read-a','write-b','read-b','clean'):
                result=subprocess.run(['node','-e',rwx.NODE_PROBE,directory,identity,action],
                                      input='' if action=='clean' else token, text=True,
                                      capture_output=True,timeout=10,check=False)
                self.assertEqual((result.returncode,result.stdout),(0,'RWX_OK'),
                                 action+': '+result.stderr[:180])
            self.assertFalse((Path(directory)/('.quorivio-rwx-probe-'+identity)).exists())

    def test_no_shell_commands_token_and_sensitive_output(self):
        self.assertNotIn('shell=True',(ROOT/'tools/k8s_rwx_cross_node_probe.py').read_text())
        self.assertIn('O_NOFOLLOW',rwx.NODE_PROBE)
        self.assertNotIn('secret',rwx.NODE_PROBE.lower())
        self.assertNotIn('kubectl cp',rwx.NODE_PROBE)


if __name__=='__main__':unittest.main()
