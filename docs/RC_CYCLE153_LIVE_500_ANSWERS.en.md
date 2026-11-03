# RC153 — Real 500-answer CLI trial and editor conflict click fix

GitHub Actions run `41711064819` passed TypeScript/Vite, 825 Node tests and preliminary Chromium checks but failed when the selected-widget floating formatting ribbon covered the enabled, visible **Compare and reconcile changes** button in the authenticated PostgreSQL editor test. The app now suspends only that ribbon while a revision conflict is being resolved; local drafts and recovery actions are preserved. The full authenticated CI run must still verify this change.

Every new user receives the additional private **Quorivio · Prova tecnica 500 partecipanti** template, separate from the existing tutorial. Its three pages comprise an introduction, one fixed single-choice poll widget (`live`, `quiz`, `questions`) with a linked presenter results widget and result instructions. It is initially unpublished and never activates itself. A partial unique `(owner_id,demo_template_key)` index provides concurrency-safe idempotence across API replicas. Existing accounts are lazily populated on the next authenticated `/api/auth/me` or `/api/sessions` call. Deleting this official template deletes its responses through the ordinary GDPR deletion path, then provisions a fresh empty replacement. A user without presenter privileges cannot publish it.

The opt-in CLI `tools/live_500_answers.py` requires the exact server hostname, an authenticated presenter cookie via environment variable, and `--confirm-run`. It selects only the official owner demo and the unmodified target poll; `--open-test-question` optionally activates that test page. For every simulated participant the CLI creates a separate cookie jar, joins anonymously, submits one real question-widget answer using the same endpoint as the participant UI, measures latency and checks the authorized `/api/sessions/{id}/widget-answers` aggregate before/after. A success requires exactly 500 new responses confirmed by the database, not merely HTTP attempts. Outputs omit secrets and personal data. The normal production limit is 100 API calls/minute/IP, so a 900-second ramp is the conservative default; staging-only load tokens are never honored in production. No script automatically runs on any deployment. It does not replace the existing simultaneous-WebSocket tool `tools/load_500.py`.

Example (replace hostname and set `QUORIVIO_LOAD_PRESENTER_COOKIE='q_auth=...'` securely in the environment):

```bash
python3 tools/live_500_answers.py --base-url https://quorivio.example.org \
  --confirm-host quorivio.example.org --confirm-run --open-test-question \
  --users 500 --concurrency 30 --ramp-seconds 900 \
  --json-out ./quorivio-load-500-summary.json
```

A fresh authorized deployment, the real 500-response run and Chromium/PostgreSQL re-acceptance are pending; no load has been sent to any user's server.
