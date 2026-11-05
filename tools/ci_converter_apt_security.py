#!/usr/bin/env python3
"""RC184 fast, fail-closed converter APT security contract.

This is a source-level preflight, not a substitute for image build and Trivy.
Dockerfile.converter enforces installed-package versions during the image build.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify_converter_security(dockerfile: str, workflow: str) -> None:
    expected = (
        "FROM python:3.12-slim-trixie",
        "apt-get -o Acquire::Retries=0 update",
        "--only-upgrade apt libapt-pkg7.0",
        "for package in apt libapt-pkg7.0",
        'dpkg-query -W -f=\'${Version}\' "$package"',
        'dpkg --compare-versions "$version" ge 3.0.4',
        "exit 1",
        "libreoffice-impress fonts-dejavu-core",
        "USER converter",
    )
    for token in expected:
        if token not in dockerfile:
            raise ValueError("Missing converter APT security contract: " + token)
    start = dockerfile.index("apt-get -o Acquire::Retries=0 update")
    upgrade = dockerfile.index("--only-upgrade apt libapt-pkg7.0")
    compare = dockerfile.index('dpkg --compare-versions "$version" ge 3.0.4')
    application_packages = dockerfile.index("libreoffice-impress fonts-dejavu-core")
    if not start < upgrade < compare < application_packages:
        raise ValueError("Patch both APT packages before other Debian package installs")
    if "apt-get upgrade -y || true" in dockerfile or "|| true" in dockerfile:
        raise ValueError("Converter security upgrade must fail closed")

    scanner = workflow.split("- name: Scan converter image", 1)
    if len(scanner) != 2:
        raise ValueError("Missing converter image Trivy gate")
    scan = scanner[1].split("\n      - name:", 1)[0]
    for token in (
        "image-ref: quorivio-converter:gate",
        "severity: CRITICAL,HIGH",
        "exit-code: '1'",
    ):
        if token not in scan:
            raise ValueError("Converter image scan was weakened: " + token)


if __name__ == "__main__":
    verify_converter_security(
        (ROOT / "Dockerfile.converter").read_text(encoding="utf-8"),
        (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8"),
    )
    print("RC184 converter APT baseline and blocking Trivy gate VALID")
