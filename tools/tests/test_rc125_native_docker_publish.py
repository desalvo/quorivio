"""RC125: fail-closed native publication, digest-based manifest and no QEMU."""
from pathlib import Path
import os
import json
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'tools/publish_multiarch_manifest.sh'

class NativePublisherAcceptance(unittest.TestCase):
    def test_workflow_has_explicit_gates_native_matrix_and_no_qemu(self):
        import yaml
        jobs=yaml.safe_load((ROOT/'.github/workflows/ci.yml').read_text())['jobs']
        build=jobs['publish-platform']
        self.assertEqual(set(build['needs']), {'validate','image-build','rc-campaign-conclusion'})
        runners={case['arch']:(case['runner'],case['platform']) for case in build['strategy']['matrix']['include']}
        self.assertEqual(runners, {'amd64':('ubuntu-24.04','linux/amd64'), 'arm64':('ubuntu-24.04-arm','linux/arm64')})
        self.assertNotIn('setup-qemu-action',str(build))
        self.assertTrue(0 < build['timeout-minutes'] <= 40)
        self.assertEqual(build['environment'],'production')
        buildstep=next(x for x in build['steps'] if x.get('id')=='native-build')
        self.assertEqual(buildstep['with']['sbom'],True)
        self.assertEqual(buildstep['with']['provenance'],'mode=max')
        self.assertIn('push-by-digest=true',buildstep['with']['outputs'])
        self.assertNotIn('tags',buildstep['with'])
        for job in ('publish','publish-on-commit'):
            obj=jobs[job]
            self.assertIn('publish-platform',obj['needs'])
            self.assertIn('publish-converter-platform',obj['needs'])
            self.assertIn("needs.publish-platform.result == 'success'",obj['if'])
            self.assertTrue(obj['timeout-minutes']<=10)
            self.assertEqual(obj['environment'],'production')
            self.assertTrue(any('bash tools/publish_both_multiarch_manifest.sh'==x.get('run') for x in obj['steps']))
            self.assertFalse(any('docker/build-push-action' in x.get('uses','') for x in obj['steps']))
        self.assertIn('!inputs.rc_acceptance_suite',jobs['publish-platform']['if'])
        self.assertIn("needs.rc-campaign-conclusion.result == 'success'",jobs['publish-platform']['if'])

    def run_fake(self, *,digests=True,arch_map=None,tags='desalvo/quorivio:sha-abcdef123456',bad_arch=None):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); (p/'digests').mkdir(); (p/'bin').mkdir()
            amd='sha256:'+'a'*64; arm='sha256:'+'b'*64
            if digests:
                (p/'digests/amd64.digest').write_text(amd+'\n')
                (p/'digests/arm64.digest').write_text((bad_arch or arm)+'\n')
            fake=p/'bin/docker';fake.write_text('''#!/usr/bin/env python3
import json,os,sys
args=sys.argv[1:]; f=os.environ['FAKE_DOCKER_CALLS']
with open(f,'a') as out: out.write(json.dumps(args)+'\\n')
if args[:3]==['buildx','imagetools','inspect']:
  ref=args[-1]
  if ref.endswith('a'*64): arch='amd64'
  elif ref.endswith('b'*64): arch=os.environ.get('FAKE_ARM_ARCH','arm64')
  else: arch='multi'
  platforms=[{'os':'linux','architecture':v} for v in (['amd64','arm64'] if arch=='multi' else [arch])]
  print(json.dumps({'manifests':[{'platform':p} for p in platforms]}))
elif args[:3]==['buildx','imagetools','create']: pass
else: sys.exit(1)
''');fake.chmod(0o755)
            env={**os.environ,'PATH':str(p/'bin')+os.pathsep+os.environ['PATH'],
                 'GITHUB_REPOSITORY':'desalvo/quorivio','GITHUB_EVENT_NAME':'push',
                 'QUORIVIO_IMAGE_TAGS':tags,'QUORIVIO_DIGEST_DIR':str(p/'digests'),
                 'FAKE_DOCKER_CALLS':str(p/'calls'),'FAKE_ARM_ARCH':arch_map or 'arm64'}
            completed=subprocess.run(['bash',str(SCRIPT)],env=env,capture_output=True,text=True,timeout=15)
            calls=[json.loads(x) for x in (p/'calls').read_text().splitlines()] if (p/'calls').exists() else []
            return completed,calls

    def test_publishes_both_digests_only_after_prechecking_both_architectures(self):
        finished,calls=self.run_fake(tags='desalvo/quorivio:sha-abcdef123456\ndesalvo/quorivio:latest')
        self.assertEqual(finished.returncode,0,finished.stderr)
        self.assertEqual([x[2] for x in calls],['inspect','inspect','create','inspect','inspect'])
        create=calls[2]
        self.assertEqual(create.count('--tag'),2)
        self.assertTrue(any('sha256:'+'a'*64 in x for x in create))
        self.assertTrue(any('sha256:'+'b'*64 in x for x in create))
    def test_wrong_architecture_fails_before_mutable_tags(self):
        finished,calls=self.run_fake(arch_map='amd64')
        self.assertNotEqual(finished.returncode,0)
        self.assertFalse(any('create' in x for x in calls))
    def test_missing_digest_fails_closed(self):
        finished,calls=self.run_fake(digests=False)
        self.assertNotEqual(finished.returncode,0)
        self.assertEqual(calls,[])
    def test_untrusted_digests_and_tags_are_rejected(self):
        for opts in ({'bad_arch':'not-a-digest'},
                     {'tags':'desalvo/quorivio:good\nevildomain/image:latest'},
                     {'tags':'desalvo/quorivio:latest\ndesalvo/quorivio:latest'}):
            with self.subTest(opts=opts):
                finished,calls=self.run_fake(**opts)
                self.assertNotEqual(finished.returncode,0)
                self.assertFalse(any('create' in x for x in calls))

if __name__=='__main__': unittest.main()
