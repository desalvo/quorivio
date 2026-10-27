# GitHub Chromium boot without apt: CI 40395950707

## Evidence and root cause

- Committed baseline: `a6ecaf1105a78893bbecdb4229677fefe072972e`.
- Manual GitHub run `40395950707`, quality job `121829112173`, failed when the **Chromium editor acceptance step timed out after eight minutes**. The step was downloading operating-system dependencies using `python3 -m playwright install --with-deps chromium`, and the apt/Ubuntu mirror stalled. **No editor browser test ran**, and no new editor UI failure was observed in that run. Container build and Docker publication were SKIPPED (publication remains explicit opt-in).
- The GitHub-hosted Ubuntu 24.04 runner image already ships with Chromium and Google Chrome. Browser installation via apt inside every opt-in run was both unnecessary and an external mirror dependency.

## Changes

1. Pin the quality job to the documented Ubuntu 24.04 runner, rather than a moving `ubuntu-latest` label; the container/publisher jobs keep their existing settings.
2. Retain the lightweight Python Playwright package install, but **remove browser download and apt/system-dependency installation** from the Chromium editor step.
3. Add `tools/ci_browser_bootstrap.py` to select an already installed Chrome/Chromium, check executable/version within eight seconds, run a real headless Playwright smoke, and export `QUORIVIO_CHROMIUM_PATH` to `GITHUB_ENV` only after success. If absent or unusable, fail quickly and clearly; never silently skip UI tests or fetch dependencies.
4. Explicitly export the selected path within the same step so the CSS preflight and editor browser smoke also use it. Subsequent browser jobs read the persistent `GITHUB_ENV` path. All six existing browser acceptance scripts already support this variable.
5. Add standard-library Python regression tests for the runner workflow, option/opt-in preservation, browser search and smoke/export order, and failure mode. The standalone actual CSS Chromium test is exercised locally using the same browser path.

## Verification and remaining gate

- Preinstalled `/usr/bin/chromium` (local Chromium 144): real Playwright headless smoke PASS, no apt/no downloads.
- `ci_nested_context_css_chromium.py`: real desktop and mobile CSS pointer acceptance PASS with the preinstalled browser.
- `test_ci_browser_bootstrap.py`: 7/7 PASS; workflow YAML parses; other related tests documented separately in delivery notes.
- GitHub-hosted Ubuntu 24.04 compatibility and the **full Chromium and PostgreSQL CI must still be confirmed by the maintainer on a new run**. No release candidate gate promoted and weighted readiness remains 48.0%. This change neither fixes nor asserts any browser UI behavior beyond the local isolated preflight.

## Maintenance

GitHub runner image documentation: https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md
Use GitHub Actions `workflow_dispatch`, `browser_test=true`, `publish_image=false`, `publish_latest=false`; review full gate results, not only the bootstrap step. Never publish Docker on pushes.
