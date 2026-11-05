# RC188 — Avvio e routing delle proiezioni: correzione della CI

## Origine
La run GitHub Actions `42011405908` (job `127191083032`) fallisce prima di npm nel test storico `test_rc92_presenter_stage.py`: cerca il vecchio SQL `ORDER BY position,id LIMIT 1`, incompatibile con le pagine `presenterHidden` e `audiencePageId` introdotte in RC185.

## Contratto verificato
- La pagina iniziale del presentatore è la prima pagina non nascosta, nell'ordine salvato della sessione.
- La pagina pubblica può essere diversa e anche nascosta dalla navigazione del presentatore.
- L'avvio è un'operazione atomica con lock `FOR UPDATE`, chiusura delle vecchie pagine pubbliche e apertura di **una sola** pagina pubblica.
- Il puntatore del presentatore e quello del pubblico sono entrambi aggiornati nella transazione; i tentativi successivi non riavviano la presentazione né i timer.
- La scelta di una destinazione del pubblico mancante è respinta; nessun vecchio `LIMIT 1` deve tornare.

## Test
Aggiornato il test storico RC92; aggiunti `test_rc188_presenter_start_reconciliation.py` e un nuovo preflight CI prima di RC92/npm. Le prove negative disabilitano la selezione visibile, reintroducono il limite SQL o omettono l'aggiornamento del puntatore: devono fallire.

## Stato
Nessuna modifica runtime. Verifica locale riportata in `docs/validation/RC_CYCLE188_LOCAL_ACCEPTANCE_20261105.json`; build completa e CI sul nuovo commit ancora da confermare. **85,25% certificato**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
