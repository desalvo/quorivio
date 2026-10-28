# Quorivio 0.1.0-dev — topic statistics and audited RC gates

**Baseline:** confirmed commit `a32ef78902a656262d346a0fa622604a4deda405`; successful GitHub Full CI `40638652838`, publication skipped.

**Results** widgets may now target a **topic-question** widget on the same page. The new owner-authenticated `GET /api/sessions/:id/activities/:aid/topic-widgets/:wid/stats` is count-only: it never transfers question texts, pseudonyms or participant identifiers. Real PostgreSQL CI includes 10 questions, participant-denied and unknown-widget cases.

The side-by-side rehearsal accepts 5–2000-character local topic questions, up to 10 per widget and page, and updates the presenter and connected result counters. **No rehearsal POST**; Restart clears all temporary counts.

**Local checks:** TypeScript/Vite build PASS, Node API 468/468, Node Web 50/50 and Python 917/917 PASS, offline Chromium 1440px/390px canvas/tooltip smoke PASS. New authenticated/PostgreSQL Full CI and independent browser/hardware review remain required.

**RC score 53 → 56%:** unchanged accepted 100% / partial 50% weighting; subdivided A3/B2/B4 into three previously GitHub-verified 2-point automated subgates and still-partial independent residual gates. 21 total, 4 accepted, 17 partial. **NOT RC READY**. No credit for unverified new topic functionality.

No commit, push, tag, release or image publishing was performed.
