# Quorivio 0.1.0-dev — RC111 — Anteprime visibili, testi risultati a capo, editor schemi accessibile (1 novembre 2026)

**Baseline:** RC107 full CI GitHub `41309042012` verde e immagine Docker Hub pubblicata, commit `99a801ab7623347ba776b8214d054aa872ddb5c6`. Le modifiche cumulative RC108–RC111 non sono ancora certificate da GitHub. Versione `0.1.0-dev` invariata. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Anteprime Presentatore, Partecipante, Affiancate:** Il problema non era nel click: il fullscreen editor aveva `z-index:9000`, il dialog delle anteprime solo 5000. Le anteprime si aprivano sotto l'editor, pur mostrando il pulsante selezionato. Il portale montato su `document.body` ora usa livello 15000, sopra editor e finestre proprietà/formattazione (12000), mantenendo focus trap, chiusura e anteprima dei dati non salvati. Il test Chromium verifica il livello che riceve davvero i clic su desktop/mobile; in CI il test React compilato viene rafforzato con controllo di hit-test, non soltanto di presenza nel DOM.

**Risultati:** il CSS troncava domanda e risposte lunghe con `white-space:nowrap` ed ellissi. Ora i testi vanno a capo rispetto alla larghezza effettiva del widget, anche in modalità nuvola, con spezzatura sicura delle parole lunghe e scroll interno se l'autore ha assegnato un'altezza troppo piccola. Non viene modificata la logica dei conteggi. Prova Chromium reale su 1440×900 e 390×844.

**Schemi:** conservato l'editor globale Titolo/Footer e il salvataggio con controllo concorrenza. Aggiunto accesso `Editor degli schemi` nella navigazione della dashboard quando una sessione è aperta, e bottone `▤ Schemi` nell'intestazione dell'editor delle pagine. Rimane il comando `Modifica schemi` sulle miniature. Il passaggio dall'editor è bloccato durante autosalvataggi incompleti.

**Verifiche e limiti:** test Node API 565/565, web 157/157, regressioni RC111 e prove Chromium CSS locali verdi. Installazione npm offline incompleta: build React completa e end-to-end vanno confermati dalla full CI GitHub. Completamento certificato invariato **85,25%** (43 gate accettati, 17 parziali su 60). Nessun commit/push/tag/pubblicazione effettuato.

**Commit cumulativo suggerito da RC107:** `Export grouped question PPTX, improve response inputs and footers, fix JPG backgrounds, word clouds and floating previews, and expose slide schemes [full-ci]`.
