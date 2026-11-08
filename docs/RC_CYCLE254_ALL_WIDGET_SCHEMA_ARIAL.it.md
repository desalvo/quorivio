# RC254 — Verifica integrale dei font nelle widget e negli schemi

## Full CI precedente

La full CI [42432817088](https://github.com/desalvo/quorivio/actions/runs/42432817088) della RC253, commit `93d029100ef09af4e3fe88119e83db38abc62960`, è **verde**: 14 job riusciti e 3 saltati secondo le regole del workflow.

## Audit e correzioni

`RichWidgetText` (RC252) omette già gli attributi assenti dal DOM. Tuttavia i percorsi di proiezione, opzioni di risposta, pulsanti di invio, risultati e numeri di pagina assumevano ancora che ogni stringa font fosse valida, anche quando i dati erano stati importati o recuperati da versioni precedenti.

RC254 introduce una singola allowlist (Arial, Georgia, Verdana, Tahoma, Trebuchet MS, monospace) per tutti i renderer di caratteri. I valori assenti, vuoti, sconosciuti o letterali `undefined`/`null` non vengono mai convertiti in nomi di font CSS. Le formattazioni esplicitamente scelte, i caratteri delle singole risposte e le modifiche per intervallo rimangono inalterate. La validazione API già respinge questi nomi invalidi in scrittura.

L'editor delle pagine e quello degli schemi condividono `WidgetCanvas`, `WidgetContentFit` e `RichWidgetText`. Verificate entrambe le viste senza inserire HTML persistente o normalizzare silenziosamente lo stile dei dati salvati.

## Regressioni e limiti

- Node: 20 tipi di widget, tutti i campi rich-text, opzioni e sottodomande; valori assenti, malformati e override espliciti.
- Chromium: 14 tipi di widget con testo, ciascuno in editor pagine e schemi, alle risoluzioni 390×844 e 1440×940. Isolati solo i WebSocket fittizi di test; errori console e React rimangono vincolanti.
- Per i widget immagine/video/logo/PDF, i controlli sui default coprono il font delle etichette, ma la presenza di un allegato reale è un tema distinto dai font.
- Il test locale non sostituisce la full CI GitHub e non prova che un deployment con vecchia immagine Docker sia aggiornato.

**Completamento**: 85,25% (43 accettati / 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag eseguito dall'assistente.
