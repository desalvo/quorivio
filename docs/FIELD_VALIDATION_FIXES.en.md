# Field validation follow-up — phases 1 and 2

ARM64 Compose now defaults to `clamav/clamav:stable-debian`. Administrator has a stable `admin` nickname, immutable privileges, editable email and protected identity. Other users can have unique nicknames; login accepts nickname or email. Password change now sends the UI back to login. Main content pages separate users, server settings, SSO, MFA, presenter profile and workspace. Approval switches between green and red. SMTPS credentials are encrypted in PostgreSQL and editable in Server Settings; MFA enrollment requires SMTP and shows otpauth URI and protected QR. Sessions may have zero or multiple calendar dates.

**Still pending:** CI, real migration and deployment testing, actual SMTP delivery, an optional email MFA factor, administrative enrollment provisioning, full SSO management UI and richer calendar. This is not yet an accepted release candidate.
