# RC253 — Test Chromium deterministico senza WebSocket live per la verifica Arial

## Causa accertata nella full CI

La RC252 è stata committata con SHA `6af6db7e6ad812e20548fba8ce9c0451c26df2fe`. La full CI [42431610890](https://github.com/desalvo/quorivio/actions/runs/42431610890) è fallita nel job **Production quality gate**, allo step **Chromium editor UI acceptance (opt-in)**, nel nuovo `tools/ci_rc252_arial_rich_dom_chromium.py`. Le asserzioni sul font Arial del vero editor React compilato arrivavano fino al controllo finale, che intercettava un errore per una connessione fittizia `ws://live/?session=...` non risolvibile (`net::ERR_NAME_NOT_RESOLVED`). Il test carica il bundle Vite in una pagina offline, non in un'installazione con server live.

## Correzione circoscritta

- Nessuna modifica al codice React in produzione, alle correzioni font, alla creazione della widget o al controllo rigoroso degli errori.
- Solo nella pagina di test viene installato, prima del bundle, un WebSocket in memoria che accetta **esclusivamente** l'URL sintetico `ws://live/?session=<id-fixture>`; altri indirizzi generano un errore reale.
- La simulazione apre il socket in modo asincrono e lo chiude correttamente. Chromium verifica direttamente apertura, chiusura e rifiuto di host estranei.
- Restano attivi i controlli di errori JavaScript e console (`assert not errors`) senza filtri o esclusioni, nonché quelli sui font effettivi di titolo e risposte a 390×844 e 1440×940.

## Stato

Inventario storico RC252 immutato. RC253 include la correzione del test, l'annotazione CI, questa documentazione bilingue e un nuovo inventario SHA-256 del cumulativo. Build TypeScript/Vite e verifiche Chromium locali superate. La full CI RC253 deve ancora essere eseguita dopo il commit dell'utente. Nessun commit, push o Docker publish effettuati dall'assistente.

**Completamento: 85,25%** (43 accettati/17 parziali). `rc_strict=false`; `publish_image=false`; `publish_latest=false`.
