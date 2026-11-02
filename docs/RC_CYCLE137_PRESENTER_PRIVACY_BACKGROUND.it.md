# RC137 — Risposte private del pubblico e caricamento sfondo canvas (2 novembre 2026)

**Base cumulativa RC136** (commit non confermato) e ultima CI completa verde RC135: commit `6c1118e93076c5d2eb8d60e96a43f8c663178053`, run `41437489546`. Nessun commit, push, pubblicazione Docker o approvazione ufficiale della RC.

## Correzioni funzionali

- Sullo schermo reale del presentatore i campi delle domande, dei quiz e delle risposte rimangono **vuoti e disabilitati**, senza riflettere le risposte inviate dal pubblico.
- La widget collegata a «Risultati» sul canvas del presentatore è un **pulsante esplicito**, non un grafico aggiornato automaticamente. Conteggi, grafici, classifiche e domande moderate vengono caricati e mostrati **solo nel pannello Risultati** quando il presentatore lo apre. Cambiando pagina il pannello si chiude.
- Nell'anteprima affiancata i campi del presentatore non leggono bozze, spunte o indicatori delle risposte simulate del partecipante. Le statistiche simulate si mostrano soltanto quando il presentatore le richiede, in una regione distinta. Il partecipante mantiene i propri controlli attivi; la prova non invia dati al server.
- Il caricamento dello sfondo dal menu contestuale mostra ora i motivi reali dei rifiuti HTTP e non un messaggio generico: dimensioni, formato, permessi, sessione chiusa e problemi del servizio antivirus/server. L'interfaccia non stampa HTML grezzo o dettagli sensibili. JPEG con MIME segnalato come `image/jpg`, `image/pjpeg` e `application/x-jpeg` viene normalizzato; `text/html` rimane vietato. Il server mantiene scanner e verifica dei byte obbligatori.

## Verifiche e limitazioni

- Nuovo preflight RC137 per separazione dei dati e caricamenti; test Node per MIME/errori; contratti storici aggiornati senza disabilitare controlli.
- I test Chromium/PostgreSQL reali già presenti per libreria e persistenza sfondi saranno rieseguiti sulla prossima CI. Se l'installazione reale continua a rifiutare il file, il nuovo messaggio permetterà di distinguere un errore di configurazione (antivirus, cartella asset, limite) da un problema del browser; non viene dichiarato risolto un problema server non riprodotto.
- **Avanzamento certificato 85,25% (43 gate accettati/17 parziali)**; restano necessarie le evidenze indipendenti esterne. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Hotfix CI RC137 (run 41473679963)

La compilazione TypeScript del frontend è fallita (TS2307) perché `background-upload-error.test.ts`, che importa `node:assert/strict` e `node:test`, si trovava nella cartella browser `apps/web/src/`. Il test è stato spostato in `apps/web/test/`, già eseguita dal comando CI `node --experimental-strip-types --test apps/web/test/*.test.ts`, e il percorso dell'import è stato aggiornato. Il compilatore browser non include più questo test. Nessuna modifica al runtime applicativo, alla sicurezza, ai gate RC o alla pubblicazione Docker. La correzione richiede un nuovo commit e una nuova CI.

**Verifiche locali hotfix:** suite Python completa 1.709 test (1.708 superati, 1 saltato, nessun fallimento); frontend Node 210/210, compreso il test trasferito; quattro intestazioni di rilascio e 124 verificatori storici/correnti validati; controlli SHA-256 di sorgenti e ZIP superati. Build npm/Vite e browser GitHub da confermare con una nuova CI.
