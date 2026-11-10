"""RC302: fail-closed paired Docker Hub publication for application and converter."""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
BOTH=ROOT/'tools/publish_both_multiarch_manifest.sh'
CI=(ROOT/'.github/workflows/ci.yml').read_text(encoding='utf8')

class DualPublisher(unittest.TestCase):
    def test_workflow_guarded_one_consent_both_native_architectures(self):
        for marker in (
            'publish-converter-platform:',
            'name: Native converter OCI image',
            'file: Dockerfile.converter',
            'name=desalvo/quorivio-converter,push-by-digest=true',
            'name: Verified Quorivio + Converter multiarch publication (manual)',
            'name: Verified Quorivio + Converter multiarch publication (explicit commit)',
            'needs.publish-converter-platform.result',
            'needs.rc-campaign-conclusion.result',
            'run: bash tools/publish_both_multiarch_manifest.sh',
            'QUORIVIO_CONVERTER_DIGEST_DIR: converter-digests',
            'inputs.publish_image == true',
            'python3 -m unittest tools.tests.test_rc302_dual_docker_publish -q',
        ):
            with self.subTest(marker=marker):
                self.assertIn(marker,CI)
        dual=BOTH.read_text(encoding='utf8')
        self.assertIn('converter_tags+=("desalvo/quorivio-converter:$label")',dual)
        self.assertIn('for kind in app converter',dual)
        self.assertIn('QUORIVIO_IMAGE_REPOSITORY=desalvo/quorivio-converter',dual)
        one=(ROOT/'tools/publish_multiarch_manifest.sh').read_text(encoding='utf8')
        self.assertIn('image_repo=',one)
        self.assertIn('"$image_repo@$amd64"',one)
        self.assertIn('"$image_repo@$arm64"',one)

    def fake(self, **options):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)
            for kind,values in (('app',('a','b')),('converter',('c','d'))):
                (p/kind).mkdir()
                for arch,char in zip(('amd64','arm64'),values):
                    if options.get('missing') and kind=='converter' and arch=='arm64':
                        continue
                    digest='sha256:'+char*64
                    if options.get('bad') and kind=='converter' and arch=='arm64':
                        digest='bad-digest'
                    (p/kind/(arch+'.digest')).write_text(digest+'\n',encoding='utf8')
            (p/'bin').mkdir()
            fake=p/'bin/docker'
            fake.write_text("""#!/usr/bin/env python3
import json,os,sys
args=sys.argv[1:]
with open(os.environ['FAKE_CALLS'],'a') as f:
    f.write(json.dumps(args)+'\\n')
if args[:3]==['buildx','imagetools','inspect']:
    target=args[-1]
    if '@sha256:' in target:
        ch=target[-1]
        arch='amd64' if ch in 'ac' else 'arm64'
        if os.environ.get('WRONG_ARM')=='1' and ch=='d':
            arch='amd64'
        if ch not in 'abcd':
            sys.exit(3)
        arches=[arch]
    else:
        arches=['amd64','arm64']
    print(json.dumps({'manifests':[{'platform':{'os':'linux','architecture':a}} for a in arches]}))
elif args[:3]==['buildx','imagetools','create']:
    sys.exit(0)
else:
    sys.exit(4)
""",encoding='utf8')
            fake.chmod(0o755)
            log=p/'calls'
            env={**os.environ,
                'PATH':str(p/'bin')+os.pathsep+os.environ['PATH'],
                'GITHUB_REPOSITORY':options.get('repo','desalvo/quorivio'),
                'GITHUB_EVENT_NAME':'push',
                'FAKE_CALLS':str(log),
                'WRONG_ARM':'1' if options.get('wrong_arm') else '0',
                'QUORIVIO_IMAGE_TAGS':options.get('tags','desalvo/quorivio:sha-abcdef123456\ndesalvo/quorivio:latest'),
                'QUORIVIO_DIGEST_DIR':str(p/'app'),
                'QUORIVIO_CONVERTER_DIGEST_DIR':str(p/'converter'),
            }
            response=subprocess.run(['bash',str(BOTH)],env=env,cwd=ROOT,
                                     capture_output=True,text=True,timeout=20)
            calls=[json.loads(s) for s in log.read_text().splitlines()] if log.exists() else []
            return response,calls

    def test_pair_publishes_only_matching_labels(self):
        result,calls=self.fake()
        self.assertEqual(result.returncode,0,result.stderr)
        create=[c for c in calls if c[:3]==['buildx','imagetools','create']]
        self.assertEqual(len(create),2,calls)
        for suffix in ('sha-abcdef123456','latest'):
            self.assertIn('desalvo/quorivio:'+suffix,create[0])
            self.assertIn('desalvo/quorivio-converter:'+suffix,create[1])

    def test_converter_failure_blocks_both_mutable_tags(self):
        for condition in (
            {'missing':True},{'bad':True},{'wrong_arm':True},
            {'repo':'somebody/else'},
            {'tags':'desalvo/quorivio:good\nuntrusted/repo:evil'},
        ):
            with self.subTest(condition=condition):
                result,calls=self.fake(**condition)
                self.assertNotEqual(result.returncode,0)
                self.assertFalse(any(c[:3]==['buildx','imagetools','create'] for c in calls))

if __name__=='__main__':
    unittest.main()
