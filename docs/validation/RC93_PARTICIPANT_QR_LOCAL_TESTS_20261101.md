# RC93 — participant QR local validation

- API Node: `node --experimental-strip-types --test apps/api/test/*.test.ts` — **565/565 PASS**.
- Web Node: `node --experimental-strip-types --test apps/web/test/*.test.ts` — **139/139 PASS**.
- QR source/security contracts: `python3 -m unittest tools.tests.test_rc93_participant_qr_contract` — **6/6 PASS**.
- TypeScript TSX/TS source parser: **0 syntax errors** (main.tsx, server.ts).
- No full TypeScript compile, browser E2E, PostgreSQL or GitHub CI claim. Native PPTX QR rendering is not included; the exporter currently handles only its established widget subset.
- Endpoint auth boundaries: presenter metadata requires owner/co-presenter authentication; public metadata requires `publicSession`, which permits active and nonexpired sessions only.
- Both endpoint variants generate the **same URL as their paired QR SVG**. The frontend does not synthesize a URL from the join code or include a presenter route.
- Verified only at source and unit/contract level; verify against a live deployment with reverse proxy and real devices.
