# RC212 — Proiezione pubblica e numerazione del presentatore: riconciliazione CI

## Evidenza
La full CI RC211 [42140039942](https://github.com/desalvo/quorivio/actions/runs/42140039942) si è interrotta al controllo `test_rc185_cross_page_projection`: il vecchio test vietava **anche l'uso interno** di `presenter_activity_id` nel generatore dello snapshot pubblico. Dalla RC206 questo valore viene usato per calcolare il numero del footer del presentatore, che deve essere condiviso dai partecipanti senza buchi dovuti a pagine saltate.

## Intervento
Il codice applicativo resta invariato. Nel controllo storico RC185 l'estrazione della funzione si ferma al suo vero confine (il precedente delimitatore per parentesi graffe su riga separata includeva erroneamente funzioni successive). Il test ammette l'uso interno dell'ID, ma ne verifica **l'assenza nella risposta pubblica**. La risposta mantiene `presenter_page_number` e pubblica esclusivamente la pagina audience aperta e le sue statistiche quando autorizzate.

Un nuovo test Python RC212 pre-npm aggiunge mutazioni negative contro fughe dell'ID privato, ampliamento delle pagine o cambiamento della pagina pubblicata. Quattro test Node eseguono la **funzione reale** di proiezione estratta da `server.ts` usando stub minimi, verificando numerazione coerente, nessun ID o segreto privato, dati solo della pagina audience, pagine chiuse non pubblicabili e statistiche nascoste se disabilitate.

## Stato
Versione `0.1.0-dev` invariata, `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessuna modifica runtime, database o policy di autorizzazione. Full CI RC212 da verificare; ultima full CI verde RC203 `42110429701`. Completamento funzionale certificato **85,25%** (43 accettati, 17 parziali). Nessun commit, push o tag.
