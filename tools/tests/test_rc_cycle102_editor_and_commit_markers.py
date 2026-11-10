"""RC102: no fixed-header obscuring and explicit gated commit-trigger publication."""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
CI=(ROOT/'.github/workflows/ci.yml').read_text()
WEB=(ROOT/'apps/web/src/main.tsx').read_text()
CSS=(ROOT/'apps/web/src/style.css').read_text()
SCRIPT=ROOT/'tools/resolve_commit_image_tags.sh'
SHA='b0c1d2e3'*5

class RC102Contracts(unittest.TestCase):
    def test_background_menu_portalled_and_dismissible(self):
        self.assertIn('backgroundMenu&&onBackgroundSelect&&createPortal(<div className="canvas-background-context canvas-background-context-floating"',WEB)
        self.assertIn('</div>,document.body)}{widgets.map(',WEB)
        self.assertIn(".closest?.('.canvas-background-context-floating')",WEB)
        self.assertIn("if(event.key==='Escape')setBackgroundMenu(false)",WEB)
        self.assertIn('.canvas-background-context-floating{',CSS)
        self.assertIn('z-index:10030!important',CSS)
        self.assertIn('position:fixed!important',CSS)
        self.assertIn('ci_background_context_portal_chromium.py',CI)

    def test_ci_marker_paths_include_all_extended_gates(self):
        # Validate each explicit per-job branch; no external YAML package in preflight.
        marker="contains(github.event.head_commit.message, '[full-ci]')"
        publish_marker="contains(github.event.head_commit.message, '[publish-docker]')"
        for job in ('cross-browser','kubernetes-api-manifests','kubernetes-runtime',
                    'kubernetes-multinode-ingress','kubernetes-https-ingress',
                    'kubernetes-haproxy-ingress','runtime-architecture',
                    'runtime-podman-rootless','clamav-runtime','rc-campaign-conclusion'):
            with self.subTest(job=job):
                section=CI.split('  '+job+':',1)[1][:650]
                self.assertIn(marker,section)
                self.assertIn(publish_marker,section)
        for name in ('Chromium editor UI acceptance (opt-in)',
                     'Chromium participant UI and PostgreSQL lifecycle (opt-in)',
                     'Chromium editor PostgreSQL persistence and conflict acceptance (opt-in)',
                     'Chromium presenter profile upload and anonymous avatar acceptance (opt-in)',
                     'PostgreSQL two-replica quiet live snapshot freshness (opt-in)',
                     'Optional 500-participant PostgreSQL/WebSocket acceptance',
                     'Optional sustained 500-participant global-latency SLO acceptance'):
            section=CI.split('      - name: '+name,1)[1].split('      - name:',1)[0]
            self.assertIn(marker,section)
            self.assertIn(publish_marker,section)

    def test_commit_publish_cannot_skip_complete_qa(self):
        publish=CI.split('  publish-on-commit:',1)[1]
        condition=publish.split('    needs:',1)[0]
        self.assertIn("github.event_name == 'push'",condition)
        self.assertIn("github.ref == 'refs/heads/main'",condition)
        self.assertIn('needs: [validate, image-build, rc-campaign-conclusion, publish-platform, publish-converter-platform]',publish)
        for gate in ('validate','image-build','rc-campaign-conclusion'):
            self.assertIn("needs."+gate+".result == 'success'",condition)
        self.assertIn('environment: production',publish)
        self.assertIn('permissions: {contents: read}',publish)
        self.assertIn("needs.publish-platform.result == 'success'",condition)
        self.assertIn("needs.publish-converter-platform.result == 'success'",condition)
        self.assertIn('bash tools/publish_both_multiarch_manifest.sh',publish)
        platform=CI.split('  publish-platform:',1)[1].split('  publish:',1)[0]
        self.assertIn('push=true',platform)
        self.assertIn('ubuntu-24.04-arm',platform)
        converter=CI.split('  publish-converter-platform:',1)[1].split('  publish:',1)[0]
        self.assertIn('file: Dockerfile.converter',converter)
        self.assertIn('ubuntu-24.04-arm',converter)
        self.assertIn("needs.rc-campaign-conclusion.result == 'success'",converter)
        self.assertIn("needs.rc-campaign-conclusion.result == 'success'",platform)
        self.assertIn('docker/setup-buildx-action@v3',publish)
        self.assertIn('secrets.DOCKERHUB_TOKEN',publish)
        # Preserve independent manual publishing; RC workflow_dispatch cannot publish.
        manual=CI.split('  publish:',1)[1].split('  publish-on-commit:',1)[0]
        self.assertIn("github.event_name == 'workflow_dispatch'",manual)
        self.assertIn('!inputs.rc_acceptance_suite',manual)

    def run_publisher(self, **values):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'github_output'
            env={**os.environ,'GITHUB_EVENT_NAME':'push','GITHUB_REF':'refs/heads/main',
                 'GITHUB_REPOSITORY':'desalvo/quorivio','GITHUB_SHA':SHA,
                 'QUORIVIO_CAMPAIGN_CONCLUSION':'success',
                 'QUORIVIO_COMMIT_MESSAGE':'Refine editor [publish-docker]',
                 'GITHUB_OUTPUT':str(out),**values}
            result=subprocess.run(['bash',str(SCRIPT)],env=env,text=True,capture_output=True,timeout=8)
            return result.returncode,(out.read_text() if out.exists() else ''),result.stderr

    def test_commit_publisher_outputs_versioned_sha_and_latest_only_after_success(self):
        code,out,err=self.run_publisher()
        self.assertEqual(code,0,err)
        self.assertIn('desalvo/quorivio:sha-'+SHA[:12],out)
        self.assertIn('desalvo/quorivio:latest',out)
        self.assertEqual(out.count('desalvo/quorivio:'),2)

    def test_commit_publisher_rejects_untrusted_or_unverified_events(self):
        for overrides in (
            {'GITHUB_EVENT_NAME':'pull_request'},
            {'GITHUB_EVENT_NAME':'workflow_dispatch'},
            {'GITHUB_REF':'refs/heads/experimental'},
            {'GITHUB_REF':'refs/tags/v0.1.0'},
            {'GITHUB_REPOSITORY':'fork/quorivio'},
            {'QUORIVIO_CAMPAIGN_CONCLUSION':'failure'},
            {'QUORIVIO_CAMPAIGN_CONCLUSION':'skipped'},
            {'QUORIVIO_CAMPAIGN_CONCLUSION':''},
            {'QUORIVIO_COMMIT_MESSAGE':'Refine editor [full-ci]'},
            {'QUORIVIO_COMMIT_MESSAGE':'Refine editor'},
            {'GITHUB_SHA':'abc'},
        ):
            with self.subTest(overrides=overrides):
                code,out,_=self.run_publisher(**overrides)
                self.assertNotEqual(code,0)
                self.assertEqual(out,'')

if __name__=='__main__':unittest.main()
