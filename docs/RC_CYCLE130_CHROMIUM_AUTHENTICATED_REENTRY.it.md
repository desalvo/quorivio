# RC130 — Rientro nell’editor Chromium autenticato e media picker

## Errore riscontrato

La run GitHub `41417000544`, job `125183202409` (commit `b6e3f2e0181478682beaa9b06e2831d9b4decaa3`) fallisce nel test reale PostgreSQL dello sfondo JPG e Logo, dopo che il test del reload browser è passato. `tools/ci_browser_media_picker_postgres.py` richiama `open_editor` dopo il caricamento del Logo; l'helper condiviso rientra in `/` e tenta di premere il vecchio pulsante della dashboard «Apri sessione». La miniatura dell'editor ripristinato intercetta correttamente il puntatore: il log non dimostra che i file JPG o Logo siano stati persistiti in modo errato.

## Correzione

L’helper condiviso controlla gli ID della sessione e della pagina della prova nella `sessionStorage` per scheda prima di usare la dashboard. Quando l’editor è ripristinato, verifica titolo e pagina mediante `GET /api/sessions/{sessionId}` autenticato, attende l'editor e richiede una sola miniatura attiva con `aria-current=page` e il canvas visibile. In caso di ID differenti la verifica fallisce esplicitamente. L’apertura iniziale conserva i clic reali e la gestione del dialogo cookie. Entrambi i test browser PostgreSQL passano gli ID al secondo ingresso.

## Evidenze e limiti

Cinque test Python eseguibili senza dipendenze esterne verificano ripristino corretto, rifiuto di sessione/pagina diverse e chiamate ai test. Restano attivi i contratti RC129/RC123 e le protezioni cookie/puntatore. Il solo timeout del sottoprocesso nel test fake-Docker RC125 passa da 5 a 15 secondi contro il carico locale, lasciando invariati script, digest e autorizzazioni della pubblicazione. Nessuna modifica al codice applicativo o alla pubblicazione Docker. La CI completa e la prova Chromium/PostgreSQL dal commit dovranno essere verificate su GitHub. Completamento certificato 85,25% (43 accettati, 17 parziali); RC rigorosa non approvata.

**Esito locale finale:** suite unittest completa: 1.674 eseguiti, 1.673 superati, 1 saltato, zero errori. Resta necessaria la CI GitHub con Chromium/PostgreSQL reale.
