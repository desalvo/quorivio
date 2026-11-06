# RC232 — Test conversione PDF/PPTX solo dopo installazione dipendenze CI

## Diagnosi

La run GitHub `42237834439` sul commit `86721afdd9ebed4ee9158d5770d7e4535c3b77a8` si è interrotta nel Production quality gate, passo `RC229 consolidated legacy UI and converter preflight before npm`: i test reali `tools.tests.test_rc_conversion_30_cycle` partivano prima dell'installazione di Poppler (`pdfinfo`, `pdftoppm`), ReportLab e LibreOffice. Il log mostra 6 errori e 3 fallimenti su 101 test. Si tratta di provisioning della CI, non di una prova di malfunzionamento del convertitore.

## Modifiche

- Conservati i test statici RC229 nel preflight iniziale senza npm.
- Spostato soltanto il modulo di conversione reale in uno step obbligatorio immediatamente successivo all'installazione OS/Python; resta inoltre incluso nella suite globale.
- Aggiunta verifica esplicita degli eseguibili e test RC232 contro regressioni dell'ordine dei passi, con casi negativi.
- Inventario RC231 storico preservato senza modifiche; RC232 unico inventario corrente.

Nessuna modifica all'app, ai permessi, GDPR, database o pubblicazione. Full CI GitHub RC232 ancora da eseguire. Completamento certificato 85,25% (43 gate accettati/17 parziali), invariato. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
