# Quorivio RC72 — Live access, dashboard, and widget visuals (31 October 2026)

**RC readiness unchanged at 84.75%** (42 accepted and 17 partial of 59 weighted gates, total 100). No new standard or extended GitHub CI has validated RC72 yet; strict RC remains blocked and publishing disabled. Last user-confirmed Git commit `487c960f09b3c9adb996d489f44b52d059da12b2`; RC66–RC72 remain a cumulative, not-yet-confirmed-committed package; the assistant does not commit/push/tag.

Active-session transition or publishing a page now extends audience-link expiry for at least 24 hours; the displayed participant URL follows the actual browser origin. Authenticated QR GET uses a checked same-origin browser Referer/Host/Sec-Fetch-Site when available, with configured canonical origin fallback. Live WebSocket accepts the application's exact same-host browser Origin only (with existing authorization/revocation) rather than requiring an outdated server setting. Authenticated HTTP polling refreshes dashboard snapshots every 12s during WebSocket outage and labels the fallback honestly.

Dashboard Settings contains monitoring; there is no third Monitoring tab. The one-column layout has no empty grid cells. Timer restart explicitly chooses whether to preserve existing responses/attachments or erase them transactionally; the option is required. Widgets are transparent and square by default, with rounded forms explicit and presentation effects consistently applied across editor, rehearsal, and live surfaces. Connected-participant palette icon uses a gauge. Motion-reduction preferences remain honored.

**Local evidence:** 558 Node API tests and 118 web tests green, TypeScript transpile syntax clean, nine targeted Python RC71 tests green, SHA-256 archive/source validation. Full Python suite timed out locally; full bundle build and live PostgreSQL/browser tests remain CI-pending. No automatic CI gate promotion.

---
