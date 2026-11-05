"""RC184 regression: Debian APT security update must fail closed before converter builds."""
from pathlib import Path
import subprocess
import unittest

from tools.ci_converter_apt_security import verify_converter_security

ROOT = Path(__file__).resolve().parents[2]
DOCKER = (ROOT / "Dockerfile.converter").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")


class RC184ConverterAptSecurity(unittest.TestCase):
    def test_real_converter_build_installs_security_fix_before_other_packages(self):
        verify_converter_security(DOCKER, WORKFLOW)

    def test_old_unpatched_converter_is_rejected(self):
        stale = DOCKER.replace("--only-upgrade apt libapt-pkg7.0", "apt")
        with self.assertRaises(ValueError):
            verify_converter_security(stale, WORKFLOW)

    def test_version_floor_is_enforced(self):
        stale = DOCKER.replace('ge 3.0.4', 'ge 3.0.3')
        with self.assertRaises(ValueError):
            verify_converter_security(stale, WORKFLOW)

    def test_upgrade_cannot_be_moved_after_libreoffice(self):
        # A regression that installs LibreOffice before patching the APT client
        # must fail even if the security upgrade still appears later.
        stale = DOCKER.replace(
            'apt-get -o Acquire::Retries=0 update;',
            'apt-get -o Acquire::Retries=0 update; \\\n'
            '    apt-get -o Acquire::Retries=0 install -y --no-install-recommends '
            'poppler-utils libreoffice-impress fonts-dejavu-core;',
        )
        self.assertNotEqual(stale, DOCKER)
        with self.assertRaises(ValueError):
            verify_converter_security(stale, WORKFLOW)

    def test_trivy_high_severity_must_remain_blocking(self):
        start = WORKFLOW.index("- name: Scan converter image")
        weakened = (
            WORKFLOW[:start]
            + WORKFLOW[start:].replace("severity: CRITICAL,HIGH", "severity: LOW", 1)
        )
        self.assertNotEqual(weakened, WORKFLOW)
        with self.assertRaises(ValueError):
            verify_converter_security(DOCKER, weakened)

    def test_converter_shell_syntax(self):
        # Dockerfile RUN layers use /bin/sh; syntax check only, no network calls.
        lines = DOCKER.splitlines()
        start = next(i for i, line in enumerate(lines) if line.startswith("RUN set -eux"))
        command = []
        for line in lines[start:]:
            if not command and not line.startswith("RUN "):
                continue
            command.append(line.removeprefix("RUN ").rstrip(" \\"))
            if not line.rstrip().endswith("\\"):
                break
        result = subprocess.run(["sh", "-n", "-c", "\\n".join(command)],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
