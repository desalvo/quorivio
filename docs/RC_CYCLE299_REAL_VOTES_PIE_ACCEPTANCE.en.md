# RC299 — Real participant votes, live pie and privacy

**Baseline:** RC298 merged at 9df7c1ce48e1; its post-merge [full CI 42874569129](https://github.com/desalvo/quorivio/actions/runs/42874569129) is green.

## Implemented on the RC299 development branch

- Actual source-label and vote-count SVG tooltips for pie slices, including correct singular/plural and a percentage only when the author enabled percentages. No change to the pie sizing or R grading geometry.
- Mandatory end-to-end Chromium + PostgreSQL acceptance uses the production-compiled frontend and a disposable authenticated session. Three independent desktop/mobile participants enter through the real join flow and submit the real radio choice through React: alpha, beta, alpha.
- Authenticated PostgreSQL reporting must record three submissions. The **separate live presenter screen** must show 2/1/0 distribution with original labels, 67% / 33% and the right count grammar. This replaces no real service with simulated rehearsal responses.
- The public participant interface must not render a presenter-only result widget, and aggregate report calls must fail with HTTP 401. JavaScript exceptions fail the gate.
- Mandatory Python compile/source preflight runs before npm; browser acceptance runs after PostgreSQL/Chromium bootstrap and before screenshot/manual publishing.

## Acceptance boundaries

RC299's branch CI must be green before merge. The formal weighted score remains **85.25% (43 accepted, 17 partial)** while external physical A4/B3 acceptance is absent. No release tag, publishing, or strict RC flag is authorized. NVDA, VoiceOver, TalkBack, keyboard and physical participant evidence are still required; CI does not replace real operator sign-off. Version remains 0.1.0-dev.

**Suggested merge title:** `test: verify real participant votes in live PostgreSQL result pies`
