# Runtime widgets and portable session definitions — 0.1.0-dev

## Live countdown
In the presenter workspace open **Page layout**, insert `timer`, save and start a timed quiz. The participant view shows remaining minutes and seconds using server-supplied `opened_at` and `duration_seconds`. The displayed countdown is informational: **the server remains authoritative** for answer deadlines. A full live time-sync mechanism and accessible countdown-end announcements are pending.

## Session QR widget
Insert `qr` from the palette. During an active session the participant page renders an application-generated SVG QR containing **only the public participant URL**. It does not grant presenter rights. Expired or inactive sessions have no accessible public QR endpoint. The generic API request rate limiter applies.

## Portable quiz definitions
The session definition JSON now preserves `answer_mode`, `answer_required`, `correct_option_ids`, duration, and page designs. Import creates a new set of IDs; **it does not restore responses, identities, assets or access codes**. Use the separate offline administrator backup for an instance-level restore. Legacy imports still require actual PostgreSQL compatibility tests.

## Verification limits
Rating, reactions, text, divider, countdown and QR now have participant-side rendering and the editor can reorder them. Arbitrary widgets on every page type remain incomplete. End-to-end browser, accessibility, real database and load tests are still outstanding.
