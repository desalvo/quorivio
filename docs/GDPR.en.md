# GDPR privacy-by-design implementation register — 0.1.0-dev

**Status:** planning and technical safeguards only; **no claim of GDPR compliance**. Before production, the controller and processors must establish roles, lawful bases, Art. 13/14 notices, Art. 28 agreements, third-country-transfer assessments if relevant, applicable retention schedules and incident processes. Legal review and an assessment of whether an Art. 35 DPIA is necessary are outstanding.

## Personal data and purposes

- Presenter: login email, salted password hash, organisation membership; purpose: manage presentation sessions and authentication.
- Participant: randomly generated pseudonymous participant credential and selected option; linked to session, therefore may still be personal data. Anonymous UI does **not** guarantee legal anonymity.
- Runtime: access logs and network data depend on reverse proxy/operator; minimize retention, avoid logging credentials or participant tokens.
- External SSO: **not implemented**. Introduce only after provider-specific notices, data mapping and security review.

## Required safeguards / open implementation work

| Requirement | Current evidence | Outstanding |
| --- | --- | --- |
| Data minimisation and purpose limitation | poll participant pseudonym | formal record of purposes and lawful bases |
| Access control | owner checks in API prototype | full organisation boundary tests and security audit |
| Storage security | PostgreSQL persistence, secret references in wizard | encryption policy, TLS checks and backups |
| Storage limitation | none enforced | configurable expiry, deletion jobs, backup retention |
| Data subject rights | none implemented | access, export, correction and deletion workflow |
| Incident handling | documentation only | audit, incident register and operator procedures |
| Processor controls | self-hosting possible | DPA and subprocessor transparency |
| Privacy notices | not implemented | bilingual notices presented at collection |
| DPIA / risk assessment | pending | determination and, if required, documented DPIA |

Never advertise a session as strictly anonymous without proving unlinkability under the chosen deployment. Restrict access to PostgreSQL and avoid exposing it publicly. Treat the manual PDFs as guidance, not evidence of compliance.
