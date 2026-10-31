# Quorivio 0.1.0-dev — RC62 — correzione della CI standard 41186895267

**Data:** 31 ottobre 2026. **Ultimo commit confermato dal manutentore:** `5a088fc300037b5a6a98a533de36ac6700b3b765`, con CI standard fallita [run 41186895267, job 124495541784](https://github.com/desalvo/quorivio/actions/runs/41186895267/job/124495541784). Il ciclo RC62 è successivo a tale commit e NON è stato committato dall'assistente.

## Diagnosi riprodotta dal codice e confermata dal log

Il job `validate` ha completato installazione, **546/546 unit API**, **99/99 unit frontend**, build frontend/backend, bootstrap PostgreSQL, prove federated link/revocation, gestione identità federate e `ci_portable_http.py`. È poi fallito in `ci_background_library_postgres.py`, alla seconda richiesta `GET /api/sessions/<id>/backgrounds` dell'utente collaboratore: `HTTP 429`, atteso `200`.

`apps/api/src/server.ts` applica `throttle` a tutta `/api` con una finestra fissa di 100 richieste/minuto per hash dell'IP. I test integrati sullo stesso runner GitHub condividono `127.0.0.1` e consumano il medesimo budget. Il backend prevede già un token temporaneo, abilitato **esclusivamente quando `NODE_ENV !== production`**, confrontato con `timingSafeEqual` e generato dalla CI con `openssl rand -hex 32`. Il workflow non passava il token alle suite HTTP portable/background, prima che il budget fosse esaurito. Non è un bug del permesso sugli sfondi; il middleware ha respinto la richiesta prima della route.

## Correzione

- `tools/ci_http_isolation.py`: la richiesta deve utilizzare un URL `http://localhost:<porta>` o `http://127.0.0.1:<porta>` senza userinfo, path aggiuntivi, query o frammenti e deve avere un token ASCII temporaneo di 32–256 caratteri. La validazione avviene *prima* dell'invio: il token non può essere trasmesso a host esterni.
- `tools/ci_portable_http.py` e `tools/ci_background_library_postgres.py`: token allegato per ogni metodo HTTP, inclusi GET/POST/PATCH/DELETE, con cookie jar e richieste negative invariate. Assenza token => fail-closed prima della rete, nessun retry 429 che mascheri le regressioni.
- `.github/workflows/ci.yml`: le due suite ricevono `QUORIVIO_CI_LOAD_TOKEN` dalla stessa variabile effimera del server e delle prove successive. Nessuna modifica a `apps/api/src/server.ts`, al database, al limite per i client normali, alle immagini o al deployment.
- `tools/tests/test_rc_cycle62_ci_rate_isolation.py`: regressioni sul passaggio token, rifiuto di host esterni, mancanza token, verifica configurazione e limitatore production.

## Validazione e impatto RC

Le unit Python dei due client e i contratti CI sono verificabili senza database. La nuova CI GitHub resta necessaria per confermare l'esito end-to-end PostgreSQL. La prova relativa a background/SSO (che era già passata fino al 429) deve terminare con `PASS` prima di attribuire nuovi punti.

**Punteggio certificato invariato 81,75%: 38 gate accepted, 17 partial su 55.** La CI fallita non abilita `rc_strict`; `rc_strict=false`, `publish_image=false`. I gate fisici/esterni rimangono aperti. Non eseguire commit, push, tag o pubblicazioni automatiche.
