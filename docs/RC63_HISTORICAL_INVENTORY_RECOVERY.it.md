# RC63 — Correzione manifest storici della CI standard (31 ottobre 2026)

**Baseline dell'ultimo commit utente:** `8e7d2df0f3badb39136f9901cd91acf2897ca453` (include RC62). La CI standard `41187779633`, job `124498103225`, ha superato la precedente anomalia HTTP 429, test Node, build, collaudi PostgreSQL, vulnerability gate. Si è arrestata in `tools/ci_inventory_reference_guard.py` con `ValueError: workflow referenced missing inventory manifest: docs/validation/RC_CYCLE59_PACKAGE_INVENTORY_20261031.json` durante i test Kubernetes/Python.

**Causa:** RC61 aveva escluso dal package cumulativo due ricevute storiche RC59 e RC60, pur conservando gli script e i riferimenti nella CI; RC62 non le aveva ripristinate. Non era una regressione del backend o della sicurezza SSO.

**Correzione:** ripristinate dai pacchetti originari, senza rigenerazione né modifica, le due ricevute `RC_CYCLE59_PACKAGE_INVENTORY_20261031.json` (SHA-256 `1b8249a51936669090377ca1d170576ad9fc01a0c94197e18a14ce4324f69121`) e `RC_CYCLE60_PACKAGE_INVENTORY_20261031.json` (SHA-256 `0fb86a1049a8c84512d4b5991c05f939ac2473621a014be2ffe83e6055732e5d`). Guard con ricevute immutable pin-nate, regressioni automatiche per presenza e assenza, verificatore RC63 in CI e inventario cumulativo RC63 da verificare prima del commit.

**Consegna:** RC63 cumulativo 0.1.0-dev, nessun commit/push/tag dal modello. CI standard deve essere rieseguita sul commit manuale successivo. La percentuale RC certificata resta **81,75%**, 38 gate accettati e 17 parziali su 55, RC strict bloccata. `publish_image=false`, `rc_strict=false`, `publish_latest=false`.
