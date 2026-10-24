# Collaudo live HTTP con PostgreSQL 18

Il workflow `.github/workflows/ci.yml` avvia PostgreSQL 18 e un'istanza API usa-e-getta, cambia la password bootstrap con `tools/ci_portable_http.py`, quindi esegue `tools/ci_live_http.py`. Le credenziali di CI sono volutamente temporanee e non vanno riutilizzate su server reali.

Il test include 24 cookie jar indipendenti, concorrenza, doppio invio, privacy dei report, chiusura attività/sessione e quiz con scadenza di 5 secondi. Richiede solo Python standard library. Per eseguirlo manualmente occorre un'istanza **usa-e-getta** già inizializzata, con le variabili `QUORIVIO_CI_ADMIN_EMAIL`, `QUORIVIO_CI_NEW_PASSWORD` e, facoltativamente, `QUORIVIO_CI_BASE_URL`.

**Limiti:** questo test non verifica il bus WebSocket su più repliche, le interfacce browser, l'accuratezza del tempo percepita dai partecipanti, l'accessibilità o il carico di 500 utenti. Non autorizza la chiusura dei gate B1–B4 senza evidenze ulteriori.
