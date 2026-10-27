# Quorivio 0.1.0-dev — Editor conforme alla struttura mock, autosalvataggio e JSON per pagina (27/10/2026)

Baseline: ultimo commit dichiarato dall'utente `551396cdaafb8765140355557eae8f8ceb59c8d4`. Package cumulativo comprensivo del precedente intervento all'editor **non ancora committato**. Nessun commit o rilascio effettuato.

## Implementato

- Editor a piena finestra: un'unica intestazione Quorivio, colonna miniature, canvas 16:9 responsivo e palette di widget a icone; **Esci** è l'unico comando permanente. Inclusi logo SVG locale e atmosfera fotografica alpina. La prova strutturale non equivale a una verifica visiva pixel-per-pixel.
- **Autosalvataggio ritardato di 850 ms**, con controllo di revisione PostgreSQL e rilettura dal server: soltanto una conferma coerente marca la bozza come sincronizzata. Su errore o conflitto le modifiche restano locali, senza sovrascrittura silenziosa. Rimossi i comandi Salva sotto il canvas; **Salva ora** rimane nel menu contestuale.
- Menu contestuale canvas con clic destro o pressione prolungata touch (580 ms), senza pulsante permanente. Export/import JSON nel menu contestuale della miniatura della singola pagina.
- Le 17 tipologie di widget dispongono di icone distinte e tooltip per focus/touch, senza duplicato nativo.
- Aggiornati i collaudi Chromium che cercavano il vecchio pulsante Salva: le prove simulate e con PostgreSQL ora richiedono autosalvataggio, persistenza dopo riapertura, conflitti e riconciliazione. Nuovo preflight dell'intestazione con stato e pulsante Esci.

## Verifiche

- Suite Node: **447/447 PASS**.
- Suite completa Python: **832/832 PASS** prima dell'ultima regressione del percorso di successo; regressione mirata PASS. Ripetere suite completa prima del commit.
- Parsing React/TSX PASS. Build Vite/React integrale **non verificata localmente**: dipendenze npm incomplete nell'ambiente isolato.
- Chromium isolato reale desktop/mobile: menu CSS, comandi di autosalvataggio, controllo clic su Esci, impaginazione a tre colonne: **PASS**.
- **Ancora da collaudare:** rendering del frontend reale rispetto al mock di riferimento, build React, browser contro PostgreSQL reale, rotazione/ridimensionamento fisico e corrispondenza visiva 1:1 con la proiezione finale.

## Gate RC

A2 e A4 restano **partial**. Il punteggio RC resta **53,0%**, senza incrementi non giustificati dai test locali; `release_candidate_ready=false`. Dopo il commit eseguire Full CI con `browser_test=true`, `publish_image=false`, `publish_latest=false` e verificare i collaudi dell'editor con database reale.
