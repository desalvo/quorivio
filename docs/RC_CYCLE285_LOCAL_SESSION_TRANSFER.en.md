# RC285 — Portable local sessions in the sidebar

## Presenter workflow

1. Open a session. Select **Export locally (.quo)** in the **Current session** sidebar group. Browser downloads a validated session archive, not an error JSON payload.
2. Use **Import locally (.quo)** in the sidebar, even when no session is open, and select a previously exported file.
3. The server checks archive safety, quotas, SHA-256/media signatures and antivirus before creating a **separate draft session** with fresh page, asset and access IDs.
4. Verify slides, master schemes, media and linked results. The original session remains untouched.

## Privacy and completeness

Every presenter-owned private library file is included, even if unused by widgets. Participant-uploaded media, participant identities, answers, votes, statistics, original joining credentials and secrets remain excluded. This is not a full instance backup or data-analytics export. Limits: 300 media files, 80 MiB total media, 100 MiB ZIP. Administrator disaster-recovery backups remain separate. No persistent browser storage is used.

**CI:** early Node regression and a real PostgreSQL HTTP roundtrip including a media file not referenced on any page, with fresh IDs on repeat imports. The existing ZIP security checks remain in place.
