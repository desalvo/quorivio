# Chromium editor con PostgreSQL reale — correzione del fixture di merge indipendente (25 ottobre 2026)

## Evidenza GitHub

- Run estesa **40220288310**, quality job **121250301296**: fallimento in `tools/ci_browser_editor_postgres.py:101` sull'attesa del messaggio `Nessun conflitto sui singoli campi`.
- Lo snapshot ARIA mostra invece un conflitto **reale** in `/widgets/pg-first/position/x`: valore locale **12**, remoto **10**, coordinata persistita prima del conflitto **11**.
- Il test inviava `draft('Remote collaborator')`: oltre all'etichetta, il fixture reimpostava `x` a **10**. Due autori modificavano quindi la stessa coordinata e il merge ha correttamente richiesto una scelta esplicita.
- Nella stessa CI sono avanzati i test Chromium editor mock, CAS HTTP PostgreSQL e Chromium partecipanti con PostgreSQL reale; container e pubblicazione sono stati saltati per il fallimento del quality gate.

## Correzione

- Nuovo helper puro `tools/ci_editor_collaboration_fixtures.py`: prepara l'aggiornamento remoto della **sola etichetta** partendo dall'ultima attività recuperata dal server, copiando senza mutazioni layout e risultati, con revisione CAS corrente.
- Il browser test recupera l'attività prima della scrittura remota, verifica la revisione 3 e le coordinate inalterate **[11, 41, 75]** dopo la revisione 4; quindi verifica il merge senza conflitti della coordinata locale x=12 con l'etichetta remota.
- Rimane intatto il successivo scenario di conflitto intenzionale sulla stessa etichetta, con scelta esplicita; nessuna protezione dell'editor è stata disattivata.
- Undici regressioni Python verificano mutazione di un solo campo, geometrie, dati risultati, copie indipendenti, revisione CAS, identificativi e casi non validi, e impediscono la reintroduzione del vecchio fixture.

## Accettazione / residui

- Verifiche locali: **644/644 test Python PASS**, **314/314 test Node PASS**, build TypeScript backend e TypeScript/Vite frontend PASS, Chromium isolato desktop/mobile PASS. Integrità ZIP verificata durante il confezionamento.
- L'end-to-end Chromium + PostgreSQL reale **resta da confermare** in una nuova GitHub CI `browser_test=true`. Il gate editor non è accettato prima del superamento. RC ponderata **45,5%** invariata.
- L'assistente non ha effettuato commit, push, tag, deploy o release.
