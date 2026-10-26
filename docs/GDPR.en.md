# GDPR privacy-by-design implementation register — 0.1.0-dev

**Status:** planning and technical safeguards only; **no claim of GDPR compliance**. Before production, the controller and processors must establish roles, lawful bases, Art. 13/14 notices, Art. 28 agreements, third-country-transfer assessments if relevant, applicable retention schedules and incident processes. Legal review and an assessment of whether an Art. 35 DPIA is necessary are outstanding.

## Personal data and purposes

- Presenter: login email, salted password hash, organisation membership; purpose: manage presentation sessions and authentication.
- Participant: randomly generated pseudonymous participant credential and selected option; linked to session, therefore may still be personal data. Anonymous UI does **not** guarantee legal anonymity.
- Runtime: access logs and network data depend on reverse proxy/operator; minimize retention, avoid logging credentials or participant tokens.
- External SSO: GitHub/Facebook OAuth2 and OIDC provider flows are present in source, but not yet validated against real providers; provider-specific notices, data mapping and security review are required before activation.

## Required safeguards / open implementation work

| Requirement | Current evidence | Outstanding |
| --- | --- | --- |
| Data minimisation and purpose limitation | poll participant pseudonym | formal record of purposes and lawful bases |
| Access control | owner checks in API prototype | full organisation boundary tests and security audit |
| Storage security | PostgreSQL persistence, secret references in wizard | encryption policy, TLS checks and backups |
| Storage limitation | session-specific retention purge; durable session, file and profile erasure jobs added | real shared-volume acceptance, backup retention and operator oversight |
| Data subject rights | limited owner-directed session deletion and admin account deletion; portable/report exports do not replace a rights response | verified access, correction, portability and erasure request workflows |
| Incident handling | documentation only | audit, incident register and operator procedures |
| Processor controls | self-hosting possible | DPA and subprocessor transparency |
| Privacy notices | not implemented | bilingual notices presented at collection |
| DPIA / risk assessment | pending | determination and, if required, documented DPIA |

Never advertise a session as strictly anonymous without proving unlinkability under the chosen deployment. Restrict access to PostgreSQL and avoid exposing it publicly. Treat the manual PDFs as guidance, not evidence of compliance.

## Development cycle: added operational controls
- `PATCH /api/sessions/:id/retention` allows the owner to choose retention between 1 and 3650 days (default 60). The retention interval starts at closure or expiry, not at creation. Existing sessions keep their own retention value when the administrator changes the default for new sessions.
- `POST /api/sessions/:id/revoke` closes a session, expires public access, rotates join credentials and disconnects WebSocket subscribers.
- `DELETE /api/sessions/:id` erases a session and associated activities, responses and participants via PostgreSQL `ON DELETE CASCADE`. Previously downloaded exports and backup copies are not covered; backup expiry must be documented before release.
- CSV export neutralizes potentially executable spreadsheet formulas.
- A participant rejoining with a valid cookie retains their technical participant identity and submitted responses.

**Limitations:** real PostgreSQL integration tests, backup lifecycle verification, legal-basis decisions, GDPR rights-request workflows and legal review remain outstanding. These controls do not establish GDPR compliance certification.

## 2026-10-24 privacy/security addendum

During this cycle, account avatar images remain authenticated and are deleted from local storage after replacement/removal; the underlying PostgreSQL user row is locked during updates to prevent concurrent stale paths. Portable session imports receive independent asset identifiers and never transfer prior participants or answers. Email MFA enrollment requires proof of mailbox control with an expiring, attempt-limited code; disabled/enabled changes revoke old sessions, while TOTP remains separate. A new CI PostgreSQL API smoke is pending execution.

**These controls are not evidence of GDPR compliance.** Verify filesystem and backup retention, private asset paths in shared volumes, email provider data processing, revocation across replicas and organizational deletion requests. Existing GDPR obligations listed above remain open.


## 2026-10-26 addendum — Enforced session retention and media cleanup

The purge now uses each session's own retention value, measured from closure or expiry; the global administrator setting defaults new sessions only. Only the session owner can change it. Session deletion atomically queues filesystem media erasure in PostgreSQL, with retry after lease expiration. Backup copies and operational multi-replica erasure remain independently governed and unverified; these changes are not a claim of GDPR compliance.

## 2026-10-26 post-commit addendum — atomic individual media and avatar erasure

Session attachment metadata removal and the filesystem erasure intent now commit together in a PostgreSQL CTE; nonexistent/cross-session assets cannot create a cleanup job. Previously, an unlink error after metadata deletion could strand a private file with no retry record. Profile-photo replacement/removal and administrator user deletion now queue the prior avatar within the same locked DB transaction, before losing the reference. New independent leased/retryable queues and a one-minute worker cadence cover session directories, individual files and user avatars. An admin-only, no-store HTTP endpoint exposes aggregated backlogs, not user IDs or file paths. Full inventory and limits: `docs/RC_ERASURE_RECOVERY_BATCH.en.md`.

These new flows have local file and SQL contract tests only; **real PostgreSQL acceptance is pending**. Backup/export copies, object-store snapshots, historical proxy logs and third-party providers are unaffected. GDPR Art. 17 rights-request fulfillment is **not** established until a controller-approved end-to-end process, backup retention and independent operational checks are verified.
