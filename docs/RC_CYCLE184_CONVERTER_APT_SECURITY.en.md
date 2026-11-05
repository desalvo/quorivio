# Quorivio 0.1.0-dev — RC184: Debian APT security upgrade in converter image

## CI evidence

GitHub Actions run [41988947593](https://github.com/desalvo/quorivio/actions/runs/41988947593) (commit `15fceb662007c86867d94461c77381fcbb746566`) passed the **Production quality gate**, ClamAV, Kubernetes, Podman, native Firefox/WebKit and AMD64/ARM64 OCI runtime checks. The RC campaign failed **solely** because the `Container build gate`, `Scan converter image` step, reported two HIGH findings in the Debian 13.7 converter: `apt` and `libapt-pkg7.0` 3.0.3, CVE-2026-109518, fixed by 3.0.4. The final summary correctly propagated the image scan failure.

Upstream evidence: Debian Security Advisory DSA-6607-1 (November 4, 2026), https://lists.debian.org/debian-security-announce/2026/msg00526.html and https://security-tracker.debian.org/tracker/CVE-2026-109518.

## RC184 change

- `Dockerfile.converter`: explicit `python:3.12-slim-trixie` base; `Acquire::Retries=0` during bootstrap to mitigate the vulnerable client; upgrade `apt` and `libapt-pkg7.0` **before** installing Poppler/LibreOffice; enforce `dpkg --compare-versions >= 3.0.4` for both; retain APT cache cleanup.
- No changes to converter user (`USER converter`), Python dependencies, worker, or Quorivio runtime.
- Add `tools/ci_converter_apt_security.py` and negative-mutation regression tests as an early preflight.
- Preserve a blocking Trivy converter image scan (`severity: CRITICAL,HIGH`, `exit-code: '1'`, `ignore-unfixed: true`), with no allowlisting or `continue-on-error`.
- Create a new RC184 inventory; historical inventories are immutable.

## Validation and limitations

Local checks include RC184 unit regressions, POSIX shell syntax and package inventory, when run. **No local Docker image build or actual Trivy image scan was possible** in this environment (Docker/Podman absent). The next GitHub CI must verify that both fixed APT packages are installed and that Trivy exits cleanly. If the security repository lacks the patch, the build fails closed rather than bypassing scanning.

**RC readiness:** 85.25% certified (43 accepted/17 partial) unless acceptance ledger changes; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag/release.
