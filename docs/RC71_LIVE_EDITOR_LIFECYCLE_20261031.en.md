# RC71 — Provisional session and timer lifecycle acceptance

The first live opening of a page starts its countdown. Returning to it never resets the deadline. Authorized manual restart requires confirmation and clears prior responses and linked participant files. Owner-only reset returns a session to ready, permanently deletes participant data and preserves authored settings.

These flows require fresh PostgreSQL integration and browser acceptance in GitHub CI. No external GDPR/AGID approval is implied, and presenter QR entry still requires authentication.
