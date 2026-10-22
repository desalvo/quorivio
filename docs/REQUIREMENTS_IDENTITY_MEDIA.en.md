# Identity and rich media — Quorivio 0.1.0-dev

Implemented in source: local registration pending admin approval; admin approval and role updates; mandatory first-login password change; pseudonym-based anonymous entry and technical cookie; anonymous participation per session; JSON-based page designs with logos, backgrounds and HTTPS media assets; configurable public URL; default 60-day configurable retention for closed sessions.

Demo admin@example.com / 000000 bootstrap is permitted only with ALLOW_INSECURE_DEV_BOOTSTRAP=true outside NODE_ENV=production, requiring a password change. **Never expose publicly**. Existing installations are not reset.

Incomplete: SSO, TOTP/email MFA, SMTP/SMTPS and test email, safe upload/storage, visual template editor, live results customization, authenticated participation, self-registration UI, full admin user CRUD UI, XLSX, comprehensive cookie consent, GDPR and security audit. An HTTPS media URL is not evidence that the content or provider is trusted. Not production-ready.

Update: local registration UI, admin create/edit/delete account UI, anonymous access toggle and optional publication of live results are implemented in source; CI and integration testing remain outstanding.
