# Quorivio RC166 — GitGuardian incident triage and disposable CI credentials

GitHub run `41802327982` passed, including the production quality gate and full RC campaign. The independent GitGuardian "Generic Password" incident has not been retrieved: verify its **file, line, commit, validity and source** in GitGuardian without disclosing the literal credential.

The repository previously used fixed test-only credentials in the primary CI job. RC166 generates run-scoped PostgreSQL values using the ephemeral GitHub run context and random, masked administrator/change-password and application authentication credentials; the bootstrap, timed-widget and SSO fixtures no longer use the same fixed passwords. This is preventive hardening; it **does not prove the reported alert originated there** or remove historical occurrences from Git history.

If the incident references a real active credential, revoke/rotate it and check usage immediately. If it refers solely to an isolated CI fixture, investigate and document it as a test false positive only after confirming the exact incident. Do not disable the scanner or introduce broad exemptions. Any Git history rewrite must be separately authorized and coordinated.

Version remains `0.1.0-dev`, release readiness remains 85.25% pending external acceptance. No commit/push/deploy performed. Full GitHub CI must revalidate generated credentials.
