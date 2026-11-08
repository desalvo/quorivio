# Quorivio 0.1.0-dev RC265 — Importazione PDF/PPTX a pieno canvas

## Correzione operativa
La full CI RC264 è verde: [GitHub Actions 42498365156](https://github.com/desalvo/quorivio/actions/runs/42498365156). La pubblicazione manuale della applicazione e del converter è riuscita: run 42500277043 e 42500299374. L'operatore ha verificato il converter sul cluster reale e ha risolto il conflitto Multi-Attach del PVC RWO adottando `Recreate` (cambiamento operativo, non modificato in questo pacchetto).

**RC265:** l'importazione PDF/PPTX come immagini offre tre modalità per ogni pagina: **Riempi canvas** (default, `cover`: proporzioni conservate con ritaglio), **Adatta interamente** (`contain`: nessun ritaglio, bande bianche se necessarie), **Espansione forzata** (`fill`: 100%×100%, possibile deformazione). L'opzione «Nascondi schema, titoli, footer e numero pagina» è attiva di default e può essere disabilitata. Il backend valida gli header prima della conversione, salva un asset interno come `backgroundAssetId` locale della pagina e conserva `importedImageFit` e `suppressMaster` nel `page_design`. Non inserisce widget/titoli sovrapposti sulle pagine importate.

La scelta viene rispettata da editor, presentatore, anteprima, partecipanti desktop e smartphone. Nessuna immagine master traspare sotto un'immagine pieno canvas. Le miniature mostrano la reale immagine di background, non segnaposto testuali; anche i comuni widget immagine ora sono rappresentati con la miniatura effettiva.

L'immagine proviene solo da un asset privato della sessione. `validPageDesign` accetta soltanto `cover`, `contain` o `fill`, con UUID di asset; non accetta URL arbitrari per questa modalità. Importazioni già eseguite prima della RC265 mantengono il layout precedente: **reimportare il PDF** per applicare la nuova modalità full bleed; le immagini-widget esistenti avranno comunque miniature reali.

## Validazione e limiti
Test mirati del comportamento di background, ereditarietà, route headers e miniature; suite API/frontend, build TS/Vite, inventario SHA-256. La full CI RC265 e la prova manuale di import su Kubernetes sono ancora da effettuare. Nessun nuovo migration schema SQL, nessun cambiamento al wizard Kubernetes o alle immagini del converter. Le opzioni riguardano l'importazione *come immagini*; la conversione modificabile resta invariata.

**Stato prodotto:** 85,25% (43 gate accettati, 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Non eseguire commit/push/tag senza autorizzazione.
