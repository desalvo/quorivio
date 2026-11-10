"""RC302: dual Docker Hub publishing must be explicit, cross-arch and fail-closed."""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'tools/publish_converter_multiarch_manifest.sh'
CI=ROOT/'.github/workflows/ci.yml'

class PairedImagePublication(unittest.TestCase):
    def run_fake(self, *,missing=False,badarch=False,event='push',
                 marker='release [publish-docker]',campaign='success',
                 authorized='true',suite='false',repo='desalvo/quorivio',
                 tags='desalvo/quorivio:sha-abcdef123456\n'
                      'desalvo/quorivio:latest',mode='--publish'):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); (root/'digests').mkdir(); (root/'bin').mkdir()
            if not missing:
                (root/'digests/converter-amd64.digest').write_text('sha256:'+'a'*64+'\n')
                (root/'digests/converter-arm64.digest').write_text('sha256:'+'b'*64+'\n')
            fake=root/'bin/docker'
            fake.write_text('''#!/usr/bin/env python3
import json,os,sys
args=sys.argv[1:]
with open(os.environ['FAKE_LOG'],'a') as f:f.write(json.dumps(args)+'\\n')
if args[:3]==['buildx','imagetools','inspect']:
    path=args[-1]
    if path.endswith('a'*64): arch=['amd64']
    elif path.endswith('b'*64): arch=['amd64'] if os.environ.get('BADARCH')=='1' else ['arm64']
    else:arch=['amd64','arm64']
    print(json.dumps({'manifests':[{'platform':{'os':'linux','architecture':a}} for a in arch]}))
elif args[:3]==['buildx','imagetools','create']:pass
else:sys.exit(1)
''')
            fake.chmod(0o755)
            env={**os.environ,
                'PATH':str(root/'bin')+os.pathsep+os.environ['PATH'],
                'FAKE_LOG':str(root/'calls'),'BADARCH':str(int(badarch)),
                'GITHUB_REPOSITORY':repo,'GITHUB_REF':'refs/heads/main',
                'GITHUB_SHA':'a'*40,'GITHUB_EVENT_NAME':event,
                'QUORIVIO_COMMIT_MESSAGE':marker,
                'QUORIVIO_CAMPAIGN_CONCLUSION':campaign,
                'QUORIVIO_PUBLISH_IMAGE':authorized,
                'QUORIVIO_RC_ACCEPTANCE_SUITE':suite,
                'QUORIVIO_IMAGE_TAGS':tags,
                'QUORIVIO_DIGEST_DIR':str(root/'digests')}
            p=subprocess.run(['bash',str(SCRIPT),mode],env=env,text=True,
                             capture_output=True,timeout=15)
            calls=[json.loads(x) for x in (root/'calls').read_text().splitlines()] if (root/'calls').exists() else []
            return p,calls

    def test_native_verified_tags_are_matched_and_published(self):
        p,calls=self.run_fake()
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual([x[2] for x in calls],['inspect','inspect','create','inspect','inspect'])
        self.assertIn('desalvo/quorivio-converter:sha-abcdef123456',calls[2])
        self.assertIn('desalvo/quorivio-converter:latest',calls[2])
        self.assertEqual(calls[2].count('--tag'),2)

    def test_verify_only_is_read_only(self):
        p,calls=self.run_fake(mode='--verify-only')
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual([x[2] for x in calls],['inspect','inspect'])

    def test_bad_evidence_cannot_update_tag(self):
        for kwargs in (
            {'missing':True},{'badarch':True},
            {'repo':'not-the-owner/quorivio'},
            {'marker':'no authorization'},{'campaign':'failure'},
            {'event':'pull_request'},
            {'event':'workflow_dispatch','authorized':'false'},
            {'event':'workflow_dispatch','suite':'true'},
            {'tags':'desalvo/quorivio:latest\nattacker/repo:latest'},
            {'tags':'desalvo/quorivio:latest\ndesalvo/quorivio:latest'},
        ):
            with self.subTest(kwargs=kwargs):
                p,calls=self.run_fake(**kwargs)
                self.assertNotEqual(p.returncode,0,p.stderr)
                self.assertNotIn('create',[x[2] for x in calls])

    def test_workflow_builds_two_native_images_before_tagging(self):
        import yaml
        jobs=yaml.safe_load(CI.read_text(encoding='utf8'))['jobs']
        build=jobs['publish-platform']
        builds=[s for s in build['steps'] if s.get('uses')=='docker/build-push-action@v6']
        self.assertEqual(len(builds),2)
        self.assertEqual({s['id'] for s in builds},
                         {'native-build','converter-native-build'})
        converter=next(s for s in builds if s['id']=='converter-native-build')
        self.assertEqual(converter['with']['file'],'Dockerfile.converter')
        self.assertIn('push-by-digest=true',converter['with']['outputs'])
        self.assertIn('name=desalvo/quorivio-converter',converter['with']['outputs'])
        self.assertIs(converter['with']['sbom'],True)
        self.assertEqual(converter['with']['provenance'],'mode=max')
        transfer=next(s for s in build['steps'] if s.get('uses')=='actions/upload-artifact@v4')
        self.assertIn('converter-${{ matrix.arch }}.digest',transfer['with']['path'])
        self.assertEqual(build['environment'],'production')
        for name in ('publish','publish-on-commit'):
            job=jobs[name]
            commands=[s.get('run','') for s in job['steps']]
            self.assertIn('bash tools/publish_converter_multiarch_manifest.sh --verify-only',commands)
            self.assertIn('bash tools/publish_multiarch_manifest.sh',commands)
            self.assertIn('bash tools/publish_converter_multiarch_manifest.sh',commands)
            self.assertLess(commands.index('bash tools/publish_converter_multiarch_manifest.sh --verify-only'),
                            commands.index('bash tools/publish_multiarch_manifest.sh'))
            self.assertLess(commands.index('bash tools/publish_multiarch_manifest.sh'),
                            commands.index('bash tools/publish_converter_multiarch_manifest.sh'))
            self.assertEqual(job['environment'],'production')
            for step in job['steps']:
                if step.get('run','').startswith('bash tools/publish_converter_multiarch_manifest.sh'):
                    for key in ('QUORIVIO_IMAGE_TAGS','QUORIVIO_COMMIT_MESSAGE',
                                'QUORIVIO_CAMPAIGN_CONCLUSION','QUORIVIO_PUBLISH_IMAGE'):
                        self.assertIn(key,step['env'])
        self.assertIn("contains(github.event.head_commit.message, '[publish-docker]')",
                      jobs['publish-on-commit']['if'])
        self.assertIn("needs.rc-campaign-conclusion.result == 'success'",
                      jobs['publish-on-commit']['if'])
        self.assertIn('inputs.publish_image == true',jobs['publish']['if'])

if __name__=='__main__':
    unittest.main()
