# GitHub / Docker Hub setup
Repository: `https://github.com/desalvo/quorivio`. Docker Hub target: `desalvo/quorivio`.

1. Create and verify the Docker Hub repository `desalvo/quorivio`; create a **scoped access token** with read/write permissions (not a password).
2. In GitHub repository **Settings > Environments**, create **production**. Set environment variable `DOCKERHUB_USERNAME=desalvo`, and environment secret `DOCKERHUB_TOKEN` to your Docker Hub access token.
3. Restrict the production environment to trusted `main` and release tag patterns. If GitHub plan / repository visibility permits, require independent reviewers. A single self-approving reviewer is not an independent release gate.
4. Under **Settings > Actions > General** allow the required GitHub and Docker actions. Enable GitHub Actions. Under **Settings > Branches / Rulesets** protect `main`, require status checks `Production quality gate` and `Container build gate`, disallow direct unreviewed pushes and force pushes, restrict tag creation.
5. Ensure GitHub secret scanning, Dependabot alerts, and security advisories are enabled where supported. Review CI failures prior to release. For a stricter supply-chain guarantee, pin third-party actions by full commit SHA and require digest/provenance verification by deployers.
6. `main` creates Docker tag `latest`; pushing a tag matching `v*` or `0.*`/`1.*`/`2.*` creates **exactly that tag**. Do not assume `latest` is semantically released or suitable for immutable deployments; deploy by SHA digest or version tag.

The workflow does not deploy to servers. It only publishes the container after the gates and any environment protections. A public GitHub repository may be required for reviewer gates on some GitHub plans.
