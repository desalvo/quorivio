# Quorivio RC87 — phase-independent idle live acceptance

**Evidence:** `logs_111783956906.zip`, RC86 extended CI. `ci_live_idle_snapshots.py` failed after the 70-second observation for the presenter. The Chromium palette acceptance and PostgreSQL cross-replica WebSocket E2E had passed.

The server's 20-second broadcast timer is aligned to server startup, not socket connection. A healthy observed sequence at elapsed 0/14/34/54 seconds was rejected by absolute 35/55-second cutoffs despite every delivery gap being under 25 seconds. RC87 adds reproducible simulated receiver tests for this boundary.

The corrected 70-second acceptance still requires 3 or more authoritative session snapshots, at least one within the final 40 seconds and another within the final 20 seconds. Each receive retains a 25-second timeout. Cross-session snapshots, invalid frames, closed sockets, and participant-only privacy violations still fail. Failures report only relative delivery times and never session IDs, cookies, responses, or URLs. The real HTTP/WebSocket test is not mocked or skipped.

Opt-in workflow runs the synthetic receiver regression after aiohttp installation, before the real 70-second test. Earlier SHA manifests remain immutable. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Certified completion unchanged: 84.75%** (42 accepted / 17 partial gates); independent sign-offs and physical infrastructure certification remain open.
