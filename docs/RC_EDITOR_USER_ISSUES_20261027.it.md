# Batch problemi editor grafico — 27 ottobre 2026

Baseline: commit confermato `551396cdaafb8765140355557eae8f8ceb59c8d4`, archivio precedente `quorivio-0.1.0-dev-rc-53-dynamic-gate-score-ci-hotfix-cumulative.zip`.

## Correzioni

- Canvas centrale responsivo 16:9, esteso a tutta la colonna centrale.
- Menu miniature rialzati sopra il canvas e non ritagliati dalla tessera; fallback per viewport mobile.
- Tooltip unico sui tasti a icona: rimossi i tooltip nativi duplicati, conservando descrizioni ARIA e tooltip su hover/focus/touch.
- Menu pagina e strumenti di allineamento reciprocamente esclusivi, con nuova voce «Strumenti di selezione e allineamento».
- Maniglie di ridimensionamento su tutti gli otto lati/angoli e maniglia rotazione con priorità di puntamento.
- Doppio clic sulle widget di domanda/quiz per aprire le proprietà; anteprima delle opzioni di risposta nel canvas.
- Geometria percentuale esplicita al momento dell'inserimento, condivisa con la proiezione.
- **Causa reale del salvataggio non riuscito**: il backend impone ID widget <=48 caratteri; gli ID prefissati `topic-question-<UUID>`, `results-button-<UUID>` e `participant-count-<UUID>` erano lunghi 51/51/54. Creazione, trascinamento, copia e duplicazione ora usano UUID di 36 caratteri.
- Blocco del salvataggio con widget multimediali non configurati; messaggio di errore leggibile dentro l'editor; rilettura del server e controllo revisione/contenuto prima di dichiarare salvato il layout.

## Verifiche e limiti

- 824/824 test Python e 447/447 Node passati localmente.
- Smoke reale del validatore API su sei tipi widget con UUID: passato.
- Parsing TypeScript/TSX superato; build completa impossibile da certificare con gli stub delle dipendenze contenuti nell'archivio.
- **Da verificare nella prossima Full CI e sul server reale:** salvataggio e riapertura PostgreSQL, rotazione e resize con mouse/touch, resa identica tra editor e pubblico, menu in viewport multipli, compatibilità browser.

**Percentuale RC invariata: 53,0%; release_candidate_ready=false.** Non promuovere i gate A1/A2/A3 senza prove end-to-end e revisione visiva operativa.
