# GitHub / Docker Hub setup
Repository: `https://github.com/desalvo/quorivio`. Docker Hub target: `desalvo/quorivio`.

1. Create and verify the Docker Hub repository `desalvo/quorivio`; create a **scoped access token** with read/write permissions (not a password).
2. In GitHub repository **Settings > Environments**, create **production**. Set environment variable `DOCKERHUB_USERNAME=desalvo`, and environment secret `DOCKERHUB_TOKEN` to your Docker Hub access token.
3. Restrict the production environment to trusted `main` and release tag patterns. If GitHub plan / repository visibility permits, require independent reviewers. A single self-approving reviewer is not an independent release gate.
4. Under **Settings > Actions > General** allow the required GitHub and Docker actions. Enable GitHub Actions. Under **Settings > Branches / Rulesets** protect `main`, require status checks `Production quality gate` and `Container build gate`, disallow direct unreviewed pushes and force pushes, restrict tag creation.
5. Ensure GitHub secret scanning, Dependabot alerts, and security advisories are enabled where supported. Review CI failures prior to release. For a stricter supply-chain guarantee, pin third-party actions by full commit SHA and require digest/provenance verification by deployers.
6. **Every push, PR and tag runs validation only; Docker Hub publication is not automatic.** Use Actions → Quorivio CI and Docker Hub → Run workflow, select main (or semver release tag), and explicitly check `publish_image=true`. With `publish_tag` empty, main publishes `sha-<first 12 commit chars>` and release tag runs publish that version. `publish_latest=true` is a **separate** checkbox permitted on main only; it remains false by default. Do not assume any mutable tag is a signed RC. Deploy by digest where possible.
7. Leave `publish_image=false` for routine or full-browser CI. `rc_strict=true` opts into a separate fail-closed RC gate (all 18 gates must be independently accepted), and defaults to false. See `docs/RC_MANUAL_PUBLICATION_MFA_BATCH.en.md`.

The workflow does not deploy to servers. Its publication step only runs with explicit opt-in after the gates and any environment protections. A public GitHub repository may be required for reviewer gates on some GitHub plans.
