# Matrice di accettazione RC — 7 novembre 2026

**RC245: full CI [42382296263](https://github.com/desalvo/quorivio/actions/runs/42382296263) verde, commit c108694705d2bd0d8d8444f7840a944b5913e25d; 11/11 obbligatori e 14 riusciti. App Docker Hub amd64/arm64 pubblicata con [42385404670](https://github.com/desalvo/quorivio/actions/runs/42385404670), non l’immagine worker separata. **85,25/100**, 17 gate parziali, RC formale non approvata.**

Receipt: `docs/validation/RC245_FULL_CI_DOCKER_20261107.json`. Previous RC239 proof remains in history. RC246 full CI pending. Never commit private operator evidence.

---

# Matrice di accettazione RC — 7 novembre 2026

**0.1.0-dev; ultima full CI verde verificata: RC239, run GitHub 42284582481, commit `0594b72806a7b6bf27de07a5fb2856747c8fd68d`. Passati 11/11 job obbligatori e tutti i 14 job attivi. Punteggio 85,25/100; 17 gate esterni parziali. Release candidate formale NON approvata.**

Convenzione: accepted=100%, partial=50%, open/blocked=0%; non rappresenta copertura software né certificazione legale o di accessibilità. I job di pubblicazione sono stati saltati intenzionalmente. `docs/validation/RC239_FULL_CI_ACCEPTANCE_20261107.json` contiene l'elenco dei job; la precedente CI rimane archiviata. Servono ancora le approvazioni indipendenti; le prove private non vanno committate nel repository.

---

## Storico delle verifiche (ottobre 2026)

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
