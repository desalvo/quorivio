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

    def test_one_click_campaign_cannot_publish_even_with_publish_consent(self):
        with tempfile.TemporaryDirectory() as temp:
            output=Path(temp)/'github-output'
            env={**os.environ,'GITHUB_EVENT_NAME':'workflow_dispatch',
                 'QUORIVIO_PUBLISH_IMAGE':'true','QUORIVIO_RC_ACCEPTANCE_SUITE':'true',
                 'GITHUB_REF':'refs/heads/main','GITHUB_SHA':SHA,
                 'QUORIVIO_PUBLISH_TAG':'','QUORIVIO_PUBLISH_LATEST':'false',
                 'GITHUB_REPOSITORY':'desalvo/quorivio','GITHUB_OUTPUT':str(output)}
            result=subprocess.run(['bash',str(SCRIPT)],env=env,capture_output=True,text=True,timeout=6)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('RC acceptance runs cannot publish',result.stderr)
            self.assertFalse(output.exists())

    def test_manual_publication_is_opt_in_and_never_implicit(self):
        import yaml
        jobs=yaml.safe_load(CI)['jobs']
        manual=jobs['publish']
        condition=manual['if']
        self.assertIn("github.event_name == 'workflow_dispatch'",condition)
        self.assertIn('inputs.publish_image == true',condition)
        self.assertIn('!inputs.rc_acceptance_suite',condition)
        self.assertNotIn("github.event_name == 'push'",condition)
        self.assertIn("needs.publish-platform.result == 'success'",condition)
        self.assertEqual(manual['needs'],['validate','image-build','publish-platform','publish-converter-platform'])
        self.assertIn('publish_image:\n        description:',CI)
        self.assertIn('publish_latest:\n        description:',CI)
        self.assertIn('default: false',CI)
        self.assertTrue(any('bash tools/resolve_image_tags.sh'==x.get('run') for x in manual['steps']))
        self.assertTrue(any('bash tools/publish_both_multiarch_manifest.sh'==x.get('run') for x in manual['steps']))
        self.assertIn('QUORIVIO_IMAGE_TAGS',str(manual['steps']))

    def test_native_build_and_both_publishers_have_read_only_github_permissions(self):
        import yaml
        jobs=yaml.safe_load(CI)['jobs']
        build=jobs['publish-platform']
        for key in ('publish-platform','publish','publish-on-commit'):
            self.assertEqual(jobs[key]['permissions'],{'contents':'read'})
            self.assertEqual(jobs[key]['environment'],'production')
        self.assertTrue(any(x.get('uses')=='docker/build-push-action@v6'
                            for x in build['steps']))
        self.assertEqual({x['arch']:x['platform'] for x in build['strategy']['matrix']['include']},
                         {'amd64':'linux/amd64','arm64':'linux/arm64'})
        for name in ('publish','publish-on-commit'):
            self.assertFalse(any(x.get('uses')=='docker/build-push-action@v6'
                                 for x in jobs[name]['steps']))
            self.assertTrue(any('bash tools/publish_multiarch_manifest.sh'==x.get('run')
                                for x in jobs[name]['steps']))
        commit=jobs['publish-on-commit']['if']
        self.assertIn("contains(github.event.head_commit.message, '[publish-docker]')",commit)
        self.assertIn("needs.rc-campaign-conclusion.result == 'success'",commit)
        self.assertIn("needs.publish-platform.result == 'success'",commit)

if __name__=='__main__': unittest.main()
