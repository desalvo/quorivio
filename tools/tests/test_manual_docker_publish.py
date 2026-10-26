"""Security regression: NO Docker Hub publication without explicit workflow_dispatch consent."""
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/resolve_image_tags.sh'
CI = (ROOT / '.github/workflows/ci.yml').read_text(encoding='utf-8')
SHA = 'a1b2c3d4' * 5

class ManualPublishPolicy(unittest.TestCase):
    def call(self, *, event='workflow_dispatch', consent='true', ref='refs/heads/main',
             tag='', latest='false', repo='desalvo/quorivio', sha=SHA):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'github-output'
            env={**os.environ,'GITHUB_EVENT_NAME':event,'QUORIVIO_PUBLISH_IMAGE':consent,
                 'GITHUB_REF':ref,'GITHUB_SHA':sha,'QUORIVIO_PUBLISH_TAG':tag,
                 'QUORIVIO_PUBLISH_LATEST':latest,'GITHUB_REPOSITORY':repo,'GITHUB_OUTPUT':str(output)}
            r=subprocess.run(['bash',str(SCRIPT)],env=env,check=False,capture_output=True,text=True,timeout=6)
            return r.returncode, output.read_text() if output.exists() else ''

    def test_default_manual_sha_tag_only(self):
        code,out=self.call();self.assertEqual(code,0);self.assertEqual(out.count('desalvo/quorivio:'),1)
        self.assertIn(f'desalvo/quorivio:sha-{SHA[:12]}',out);self.assertNotIn('quorivio:latest',out)

    def test_opt_in_latest_from_main(self):
        code,out=self.call(latest='true');self.assertEqual(code,0)
        self.assertIn('desalvo/quorivio:latest',out);self.assertEqual(out.count('desalvo/quorivio:'),2)

    def test_semver_git_tag_publish_without_latest(self):
        for tag in ('v0.1.0','v1.2.3-rc.1','v10.0.0'):
            with self.subTest(tag=tag):
                code,out=self.call(ref='refs/tags/'+tag);self.assertEqual(code,0);self.assertIn('quorivio:'+tag,out)
                self.assertNotIn('quorivio:latest',out)

    def test_custom_publish_tag_from_main(self):
        code,out=self.call(tag='rc-0.1.0');self.assertEqual(code,0);self.assertIn('quorivio:rc-0.1.0',out)

    def test_deny_automatic_and_unauthorized_actions(self):
        for event,consent in [('push','true'),('pull_request','true'),('workflow_dispatch','false'),('workflow_dispatch','')]:
            with self.subTest(event=event,consent=consent):
                code,out=self.call(event=event,consent=consent);self.assertNotEqual(code,0);self.assertEqual(out,'')

    def test_deny_publish_from_other_repositories_and_branches(self):
        for kwargs in ({'repo':'attacker/quorivio'},{'ref':'refs/heads/develop'},
                       {'ref':'refs/tags/v1.0.0evil'},{'ref':'refs/tags/test'},
                       {'ref':'refs/pull/5/merge'},{'sha':'not-a-git-sha'}):
            with self.subTest(**kwargs):
                code,out=self.call(**kwargs);self.assertNotEqual(code,0);self.assertEqual(out,'')

    def test_deny_latest_without_dedicated_checkbox(self):
        for kwargs in ({'tag':'latest'}, {'tag':'latest','latest':'true'},
                       {'latest':'true','ref':'refs/tags/v1.2.3'}, {'latest':'yes'}):
            with self.subTest(**kwargs):
                code,out=self.call(**kwargs);self.assertNotEqual(code,0);self.assertEqual(out,'')

    def test_deny_tag_injection(self):
        for tag in ('',):
            self.assertEqual(self.call(tag=tag)[0],0)
        for tag in ('bad tag','a\nb','evil:latest','-bad','a'*129,'a/other','$(touch /tmp/x)',
                    'x\rmore','x\tmore','\x00','*','..:latest'):
            with self.subTest(tag=repr(tag)):
                # OS process env cannot contain NUL; tests still cover all representable hostile input.
                if '\x00' in tag:continue
                code,out=self.call(tag=tag);self.assertNotEqual(code,0);self.assertEqual(out,'')

    def test_workflow_is_never_push_based(self):
        pub=CI.split('\n  publish:',1)[1]
        self.assertIn("github.event_name == 'workflow_dispatch'",pub.split('\n    needs:',1)[0])
        self.assertIn('inputs.publish_image == true',pub.split('\n    needs:',1)[0])
        self.assertNotIn("github.event_name == 'push'",pub.split('\n    needs:',1)[0])
        self.assertIn("publish_image:\n        description:",CI)
        self.assertIn("publish_latest:\n        description:",CI)
        self.assertIn('default: false',CI)
        self.assertIn('tags: ${{ steps.label.outputs.tags }}',pub)
        self.assertIn('needs: [validate, image-build]',pub)

    def test_publish_runner_has_no_write_permission(self):
        pub=CI.split('\n  publish:',1)[1]
        self.assertIn('permissions: {contents: read}',pub)
        self.assertIn('environment: production',pub)
        self.assertIn('docker/build-push-action@v6',pub)
        self.assertIn('platforms: linux/amd64,linux/arm64',pub)

if __name__=='__main__': unittest.main()
