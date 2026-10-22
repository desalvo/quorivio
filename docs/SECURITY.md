# Security requirements, threat model and verification (draft)

**AgID:** establish the precise current official guidance and scope with a dedicated review; current work makes no compliance or certification claim.

## Assets and trust boundaries

Presenter authenticated cookie; anonymous participant bearer cookie; session invitation secret; quiz answers; organization data; submitted choices. Boundaries: public browser → HTTP API, HTTP API → PostgreSQL, browser → WS upgrade, platform operator → server config.

## Threats and controls

| Threat | Existing control | Missing validation/mitigation |
|---|---|---|
| SQL injection | Parameterized SQL | Automated injection tests |
| Unauthorized presenter access | Owner ID checks | Multi-role permissions, E2E pen test |
| Quiz answer disclosure | Participant WebSocket redaction and public API omit correct answer | Automated integration tests |
| Duplicate votes | DB unique index and conflict handling | Concurrent load verification |
| Forged browser requests | SameSite strict cookies and Origin checks on unsafe verbs | Mandatory Origin/CSRF token enforcement, proxy-aware validation |
| Guessable sessions | Random join secrets and codes, rudimentary IP limit | Shared/Redis adaptive rate limits and brute-force audit |
| XSS | React auto-escaping | CSP enforcement and security scanning |
| Session theft | HttpOnly cookies | Login attempt lockout, key rotation, session revocation |
| Denial of service | Body size limit, request rate limit | WS handshake rate limit, Redis shared quotas |
| Data isolation | Owner constrained session routes | Organization permissions and cross-tenant tests |
| Backups | Documented manual pg_dump | Encrypted automated tested backup/restore |
| Upload exploitation | No file import in MVP | Sandbox conversion worker, MIME scanning and quotas |

## Before production

Required: official AgID reference review and traceability matrix, SAST/DAST/SCA, secrets audit, SBOM, independent security review, documented incident response, MFA/identity provider integration, authorized load and isolation tests, data lifecycle/GDPR analysis, TLS ingress validation, immutable logs with PII minimization, backup restore drills, versioned migrations, revocable/rotatable session credentials. Do not expose this prototype as a production-ready public service.
