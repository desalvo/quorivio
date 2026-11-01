"""Regression contract for production CSP and real OCI/Podman runtime checks."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class SecurityHeadersCycle53(unittest.TestCase):
    def test_production_server_uses_enforcing_policy(self):
        src = (ROOT / 'apps/api/src/server.ts').read_text()
        self.assertIn("import {productionCspDirectives,quorivioPermissionsPolicy}", src)
        self.assertIn("process.env.NODE_ENV==='production'", src)
        self.assertIn('directives:productionCspDirectives(base)', src)
        self.assertIn("res.setHeader('Permissions-Policy',quorivioPermissionsPolicy)",src)

    def test_script_policy_never_opens_inline_or_eval(self):
        code = (ROOT / 'apps/api/src/security-headers.ts').read_text()
        self.assertIn('scriptSrc:["\'self\'"]', code)
        self.assertIn('scriptSrcAttr:["\'none\'"]', code)
        self.assertNotIn("'unsafe-eval'", code)
        self.assertNotIn('scriptSrc:["\'self\'","\'unsafe-inline\'"]',code)

    def test_real_production_smokes_require_csp(self):
        for name in ('ci_oci_runtime_smoke.sh','ci_rootless_podman_smoke.sh'):
            with self.subTest(name=name):
                path=ROOT / 'tools' / name
                text=path.read_text()
                for term in ('content-security-policy','permissions-policy','script-src',
                             'connect-src','frame-ancestors','object-src','unsafe-eval'):
                    self.assertIn(term,text)
                subprocess.run(['bash','-n',str(path)],check=True)

    def test_no_product_media_breakage(self):
        policy = (ROOT / 'apps/api/src/security-headers.ts').read_text()
        for term in ('frameAncestors:["\'self\'"]', 'styleSrc:["\'self\'","\'unsafe-inline\'"]',
                     "'data:'", "'blob:'", "'https:'",'socketOrigin'):
            self.assertIn(term,policy)


if __name__ == '__main__': unittest.main()
