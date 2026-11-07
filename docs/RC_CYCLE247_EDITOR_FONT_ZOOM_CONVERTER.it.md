# RC247 — Parità tipografica dei widget, spazio canvas e tag converter

## Problemi riprodotti

Dalle schermate dell'installazione RC246: nell'editor il font dei risultati con stile indipendente risultava sproporzionato rispetto alle anteprime; alcuni titoli/opzioni apparivano non Arial; la selezione testuale prevaleva sull'ambito «Widget intero»; lo zoom dell'elemento HTML restringeva un overlay `fixed` lasciando la dashboard sottostante esposta. Lo spazio guadagnato deve essere restituito al canvas, non diventare bande vuote.

## Correzioni RC247

- La tipografia indipendente dei risultati usa unità `cqw` basate sul canvas logico da 1280px invece dei pixel dello schermo; mantiene i colori, caratteri e pesi salvati per le singole opzioni.
- Il comando **Widget intero** prevale sulla selezione residua e aggiorna font di titoli, opzioni, pulsanti e sottodomande, incluse le marcature rich-text già esistenti. I formati selezionati esplicitamente restano supportati quando si sceglie un ambito specifico.
- Il font predefinito editor pagina e schemi è Arial per tutti i discendenti testuali dei 20 tipi di widget; i font scelti dall'utente rimangono autorevoli. Test in Chromium senza font di default iniettati nella fixture.
- L'interfaccia globale è più compatta: **100% visualizzato equivale all'80% precedente**, con nuova chiave di persistenza zoom `v2`. Le finestre `fixed` sono compensate rispetto al viewport fisico; l'editor rimane a schermo intero, il canvas 16:9 sfrutta lo spazio disponibile e la dashboard si estende in larghezza.
- Il workflow manuale `converter-image.yml` pubblica **`desalvo/quorivio-converter:latest` da `main`** oppure **`desalvo/quorivio-converter:<nome-tag-git>`** quando eseguito sul riferimento tag. Nessuna pubblicazione automatica da push. Il wizard non distruttivo accetta `latest`, un tag di release o digest verificabile e continua a usare una patch revisionata.

## Prove e limiti

Regressioni Node frontend/API, controlli pre-npm, test browser Chromium 390/760/1440px a zoom 80/100/120 e verifica degli inventari. La full CI RC247 (inclusi typecheck React e Postgres) va ancora verificata sul commit prodotto dal manutentore. Non sono state eseguite modifiche nel cluster, pubblicazioni Docker, commit o tag. Punteggio certificato **85,25%** (43 gate accettati/17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
