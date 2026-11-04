# Quorivio 0.1.0-dev — RC169 — Fedeltà del gradimento e tipografia smartphone

## Base verificata e difetti corretti

La RC168 mantiene un solo modello di impaginazione smartphone, ma il contenuto del widget **Gradimento** aveva implementazioni distinte tra editor, anteprima e partecipazione reale: legenda e descrizione non coincidevano, la dimensione dei pulsanti configurata veniva ignorata dalla pagina reale e l’editor montava anche una seconda anteprima del commento. Inoltre la tipografia smartphone del titolo poteva usare 16 px anziché la dimensione del titolo ereditata dallo schema.

## Implementazione

1. `RatingStageContent` è l’unica definizione di titolo, descrizione con formattazione, campo commento facoltativo, scala 0–9 e dimensione dei pulsanti. Viene utilizzata da editor, presentatore in sola lettura, anteprime interattive e URL partecipante. Il campo commento ha sfondo bianco e testo scuro, indipendentemente dal tema.
2. Rimossa la precedente seconda istanza del commento nel canvas dell’editor. Le anteprime non inviano risposte al server.
3. `stageWidgetTypography` risolve la configurazione del titolo ereditato dallo schema *prima* di applicare il font smartphone. La stessa funzione viene chiamata dalle viste partecipante reali e di prova, senza modificare il progetto salvato.
4. Nella prova smartphone del presentatore, i contenuti con altezza eccedente usano lo stesso scorrimento interno del widget della URL reale.
5. La fixture Chromium/PostgreSQL registra anche un widget Gradimento con descrizione e dimensione pulsanti personalizzate. Le sue verifiche controllano presenza di un solo commento, dieci voti, leggibilità, scelta dello stile e altezza documento smartphone di 1.174 pixel logici senza spazi riservati ai widget del presentatore.

## Evidenze e criteri

- Contratti Node RC169 di ereditarietà titolo, override font e condivisione del gradimento; regressioni negative contro il ripristino di commenti duplicati e dimensioni ignorate.
- Preflight Python RC169 prima di npm e verifica Chromium CSS/DOM su viewport 390/1440 px; il collaudo Chromium autenticato di una sessione PostgreSQL effettiva è predisposto nella CI.
- Conservazione integrale dei certificati storici e nuovo manifesto cumulativo con SHA-256, validazione Git e contenuto ZIP.

**Da confermare in GitHub Actions:** build TypeScript/Vite completa, collaudo autenticato Chromium/PostgreSQL e campagne hardware e funzionali indipendenti. I test CSS/DOM locali da soli non sono una certificazione pixel-per-pixel dei dispositivi fisici. Completamento conservativo **85,25% (43 gate accettati, 17 parziali)**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag/deploy da parte dell’assistente.
