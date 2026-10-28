# Matrice di accettazione RC — 25 ottobre 2026

**Versione 0.1.0-dev. Punteggio ponderato verificabile: 45,5/100. NON è una release candidate.**

Il punteggio è una convenzione prudenziale di gestione dei gate, non una misura del codice scritto, della copertura dei test o uno SLA. `accepted` vale 100% del peso, `partial` 50%, `open`/`blocked` zero. Fonte: `docs/RC_GATE_MATRIX.json`; ricalcolo: `python3 tools/rc_gate_audit.py`.

| Area | Punti / totale | Percentuale |
| --- | ---: | ---: |
| A-editor | 9 / 24 | 37.5% |
| B-sessions | 11.5 / 23 | 50.0% |
| C-admin | 11 / 22 | 50.0% |
| D-validation | 14 / 31 | 45.2% |
| **Totale** | **45.5 / 100** | **45.5%** |

**CI verde confermata:** workflow GitHub Actions `40141894130` (quality e container), Chromium opt-in PASS, 500 partecipanti indipendenti PASS (picco presentatore >=475, zero errori), WebSocket su due repliche PostgreSQL 18 PASS e DR PostgreSQL 18 PASS. D4 passa da aperto a parziale: 43,0 -> 45,5 punti.

**Nuovo sviluppo editor:** lotto di 20 interventi con 205 test Node e 277 Python PASS, build API/web PASS; il browser test ampliato non è ancora stato eseguito in CI. La fixture di salvataggio/reload non è una prova PostgreSQL reale.

**Ancora aperti:** dispositivi/screen reader reali, corpus PPTX, latenza/fairness live, DR staging e RPO/RTO, ARM64/Podman rootless, Kubernetes HA, provider SMTP/SSO, antivirus/pentest, GDPR/licenze.


## 2026-10-28 — Full CI 40638652838 audited subgate reconciliation

Full CI conferma migrazione storica multi-domanda, editor Chromium reale, fairness temporale e prova limitata a 500 partecipanti. I sottogate A3-AUTO, B2-DB, B4-LOAD sono accettati con peso complessivo 6, trasferito dai rispettivi gate parziali; formula invariata, punteggio 53,0 -> 56,0. I restanti controlli indipendenti restano aperti, RC non pronta e nuove statistiche del tema ancora senza punti.
