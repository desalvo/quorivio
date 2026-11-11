"""RC127: native OCI runtime per-architecture CI and truthful external RC plan."""
from pathlib import Path
import json
import subprocess
import unittest
import yaml
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from rc_operator_acceptance import make_plan, PLAN
from rc_gate_audit import audit


class NativeRuntimeAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.jobs = yaml.safe_load((ROOT/'.github/workflows/ci.yml').read_text())['jobs']

    def test_architecture_mapped_to_genuine_native_runner(self):
        job = self.jobs['runtime-architecture']
        self.assertEqual(job['runs-on'], '${{ matrix.runner }}')
        self.assertFalse(job['strategy']['fail-fast'])
        matrix = {case['arch']: (case['platform'], case['runner']) for case in job['strategy']['matrix']['include']}
        self.assertEqual(matrix, {'amd64': ('linux/amd64', 'ubuntu-24.04'),
                                  'arm64': ('linux/arm64', 'ubuntu-24.04-arm')})
        self.assertNotIn('setup-qemu-action', str(job))
        self.assertEqual(job['permissions'], {'contents': 'read'})
        self.assertEqual(job['needs'], 'validate')
        self.assertLessEqual(job['timeout-minutes'], 30)

    def test_native_os_identity_is_checked_before_build(self):
        steps = self.jobs['runtime-architecture']['steps']
        guard = next(i for i, step in enumerate(steps) if 'Verify actual native runner architecture' in step.get('name',''))
        builder = next(i for i, step in enumerate(steps) if step.get('uses') in ('docker/build-push-action@v6', 'docker/build-push-action@v7'))
        self.assertLess(guard, builder)
        self.assertIn('uname -m', steps[guard]['run'])
        self.assertIn('aarch64', steps[guard]['run'])
        self.assertIn('x86_64', steps[guard]['run'])
        self.assertEqual(steps[builder]['with']['platforms'], '${{ matrix.platform }}')
        self.assertEqual(steps[builder]['with']['tags'], 'quorivio:ci-oci-${{ matrix.arch }}')
        self.assertFalse(steps[builder]['with']['push'])
        self.assertTrue(steps[builder]['with']['load'])
        self.assertFalse(any('docker/login' in s.get('uses','') or 'upload-artifact' in s.get('uses','') for s in steps))

    def test_runtime_executes_postgres_health_non_root_and_headers(self):
        steps = self.jobs['runtime-architecture']['steps']
        self.assertTrue(any('ci_oci_runtime_smoke.sh' in x.get('run','') for x in steps))
        script = (ROOT/'tools/ci_oci_runtime_smoke.sh').read_text()
        for needle in ('postgres:18-alpine', 'process.arch', 'process.getuid()===0',
                       '/api/health/ready', '/api/health/live', 'content-security-policy',
                       'permissions-policy', 'trap cleanup EXIT', 'docker network create --internal'):
            self.assertIn(needle, script)
        self.assertNotIn('setup-qemu', str(steps))
        self.assertNotIn('docker push',script)
        self.assertEqual(subprocess.run(['bash','-n',str(ROOT/'tools/ci_oci_runtime_smoke.sh')],
                        capture_output=True).returncode, 0)

    def test_native_smoke_remains_mandatory_for_full_campaign(self):
        campaign = self.jobs['rc-campaign-conclusion']
        self.assertIn('runtime-architecture', campaign['needs'])
        runtime = self.jobs['runtime-architecture']['if']
        self.assertIn('inputs.runtime_arch_test',runtime)
        self.assertIn('inputs.rc_acceptance_suite',runtime)
        self.assertIn("'[full-ci]'",runtime)
        self.assertIn("'[publish-docker]'",runtime)

    def test_external_operator_plan_is_not_automatic_acceptance(self):
        plan = make_plan()
        self.assertEqual(plan['schema'], 'quorivio-rc-external-acceptance-plan-v1')
        self.assertFalse(plan['ready_for_rc'])
        self.assertEqual(plan['external_reviews_completed'], 0)
        self.assertEqual(plan['unaccepted_count'], 17)
        self.assertEqual(len(plan['items']), 17)
        for item in plan['items']:
            self.assertEqual(item['review_status'], 'not_submitted')
            self.assertIsNone(item['evidence_uri'])
            self.assertFalse(item['operator_approval'])
            self.assertTrue(item['evidence_to_collect'])
        self.assertEqual(json.loads(PLAN.read_text()), plan)
        self.assertEqual(audit()['score'], 85.25)


if __name__ == '__main__':
    unittest.main()
