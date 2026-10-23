# Ricalcolo di accettazione RC — 23 ottobre 2026

**Versione:** 0.1.0-dev. **Avanzamento ponderato verificabile: 37,5 punti su 100.** Sostituisce la vecchia stima ripetuta del 67%, non derivata da una matrice di accettazione mantenuta. **Non significa che sia stato scritto il 37,5% del codice** e non è una misura statistica della qualità.

La fonte riproducibile è `docs/RC_GATE_MATRIX.json`. Eseguire `python3 tools/rc_gate_audit.py`. Ogni gate possiede peso, stato, evidenza e condizione residua; i pesi sommano a 100. `accepted` vale il 100% del peso, `partial` il 50%, `open`/`blocked` zero. Si tratta di una convenzione prudenziale **di project management**, non di percentuale di copertura dei test. Stati e pesi richiedono verifica umana delle prove reali.

| Area | Punti acquisiti / totali | Accettazione |
| --- | ---: | ---: |
| A: editor grafico | 9 / 24 | 37,5% |
| B: sessioni e risultati | 11,5 / 23 | 50,0% |
| C: amministrazione, MFA e SSO | 8,5 / 22 | 38,6% |
| D: validazione release | 8,5 / 31 | 27,4% |
| **Totale** | **37,5 / 100** | **37,5%** |

I sorgenti comprendono già editor, API di sincronizzazione delle sessioni, quiz a tempo indipendenti, risultati per il presentatore, TOTP e revoca delle sessioni. Non sono accettati end-to-end senza PostgreSQL, browser simultanei e, quando pertinente, repliche multiple. Le ultime build frontend/backend riuscite, 95 test Node e 93 Python sono evidenze del package precedente, non certificazioni di deployment.

**Collaudi esterni indispensabili:** PostgreSQL 18 e migrazioni, simultaneità e latenza presentatore/partecipanti, accessibilità desktop/tablet/smartphone, SMTP e provider OAuth/OIDC reali, conversione PDF/PPTX e antivirus, container AMD64/ARM64, Podman rootless, Kubernetes multi-replica, disaster recovery, GDPR e revisione di sicurezza/licenze. Il secondo fattore email è ancora mancante: il supporto SMTP non equivale a email MFA.

**Regola di aggiornamento:** modificare gli stati soltanto in presenza di test effettivamente eseguiti e conservare gli esiti negativi. La CI verde valida i gate configurati nella CI, non l'intera RC. Il punteggio può crescere raccogliendo evidenza senza modificare i sorgenti. Non dichiarare la RC raggiunta fino all'accettazione di tutti i gate obbligatori.
