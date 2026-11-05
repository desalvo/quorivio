# RC189 — Tipizzazione import pagine e compilazione TypeScript anticipata nella CI

## Errore GitHub

La run `42021367453`, job `127224676741` (commit `d1540d215638ee893e480fdad152dd116135be8a`) supera il preflight storico RC92 e i test unitari, ma si ferma alla compilazione API con due errori `TS2345` in `apps/api/src/server.ts:982`. La mappa inferita come `Map<unknown,unknown>` non rispetta il parametro `ReadonlyMap<string,string>` richiesto dalla funzione di rimappatura.

## Correzione

`createFromPortable()` costruisce una `Map<string,string>` esplicita e inserisce soltanto ID sorgente verificati come stringhe. Gli archivi portabili legacy senza ID di pagina rimangono compatibili e non introducono chiavi `undefined`. Restano invariati i collegamenti delle pagine pubbliche e delle widget risultati fra pagine. Nessuna modifica alle autorizzazioni o alle revisioni.

## Regressioni e CI

`tools/tests/test_rc189_portable_map_types.py` prova il frammento reale con Node 22 e, se `tsc` autonomo è presente, compila il codice con TypeScript strict e verifica che la vecchia espressione produca ancora `TS2345`. Il preflight viene prima di npm; subito dopo npm parte **la compilazione TypeScript rigorosa dell'API**, senza aspettare PostgreSQL e Chromium. Rimane obbligatoria la build completa successiva.

## Stato

Verifiche locali: Python, TypeScript isolato, 599/599 test API e 321/321 frontend. Build integrale e campagna CI sul commit RC189 **da confermare**. Percentuale certificata invariata 85,25% (43 gate accettati, 17 parziali). Nessuna pubblicazione né commit/push/tag dell'assistente.
