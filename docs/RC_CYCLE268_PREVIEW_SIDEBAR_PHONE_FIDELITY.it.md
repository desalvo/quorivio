# Quorivio 0.1.0-dev RC268 — Anteprima, miniature e fedeltà smartphone

## Obiettivo

Interventi cumulativi successivi alla RC267, validata dal maintainer con full CI verde
[42516844646](https://github.com/desalvo/quorivio/actions/runs/42516844646)
e pubblicazione multiarch manuale verde
[42518673212](https://github.com/desalvo/quorivio/actions/runs/42518673212).

## Funzioni implementate

- Anteprima in fullscreen nativo: l'area del canvas 1280×720 è scalata secondo
  larghezza **e altezza** del viewport, con barre nascoste; lo zoom globale
  dello studio è temporaneamente sospeso e ripristinato all'uscita.
- Frecce sinistra/destra e PagSu/PagGiù avanzano/arretrano le pagine in anteprima.
  Non intercettano i tasti mentre si scrive in campi, controlli editabili o
  con modificatori di tastiera.
- Menu della pagina apribile anche facendo clic in una zona vuota della sidebar;
  trascinamento delle miniature anche negli slot prima, fra e dopo le pagine,
  senza sovrascrivere altre miniature. Salvataggio dell'ordine secondo il flusso
  transazionale già usato dall'editor.
- Layout smartphone automatico: ridotte le altezze eccessive per domande e
  risultati con poche risposte; dimensione QR bounded; le righe dei risultati
  possono andare a capo senza ereditare limiti desktop non compatibili.
- **Regola per singola pagina proiettata:** una pagina importata da PDF/PPTX come
  immagine full-canvas, oppure una pagina `slide` senza widget modificabili
  nella pagina stessa, viene resa automaticamente come **diapositiva 16:9**
  sullo smartphone del partecipante. La regola cambia con la pagina corrente,
  senza modificare `page_design.mobile` o il modo della sessione; quando
  segue una pagina con widget interattivi torna l'impaginazione smartphone.
  Un utente che seleziona esplicitamente un layout manuale mantiene la scelta.
  La modalità di lettura accessibile rimane autonoma. L'anteprima partecipante
  smartphone usa lo stesso criterio pagina-per-pagina.

## Verifiche

- `node --experimental-strip-types --test apps/web/test/rc268-preview-sidebar-mobile.test.ts`
  include geometrie, navigazione, slot sidebar, altezza QR/risultati, pagine
  statiche/PDF, transizioni statico→interattivo→statico e selezione manuale.
- Il preflight CI esegue questo test prima delle dipendenze npm.
- Test frontend, API, build TypeScript/Vite e Python completi eseguiti localmente;
  risultati registrati nella consegna. Il collaudo funzionale sul cluster e
  la full CI GitHub RC268 sono ancora richiesti.

## Confini e sicurezza

Nessun cambiamento a DB, exporter, conversione PDF/PPTX, wizard Kubernetes,
segreti, PVC o immagini Docker. Nessun commit/push/tag/release è eseguito in
questa consegna. `rc_strict=false`, `publish_image=false`,
`publish_latest=false`. Il completamento complessivo resta **85,25%**.
