# Quorivio RC276 — Correzione contratto presenter cross-page e toggle R

- Sorgente: cumulativo RC275, full CI 42565597725, job 128991308978.
- Errore esatto: `rc191-cross-page-preview.test.ts`, test "live projection uses the same cross-page resolver with the source activity id". Richiedeva `LinkedResultChart widget={{...widget,showCorrectAnswers:showCorrectLive}}`, `resultHasAnswerKey` e `setShowCorrectLive` dentro `PresenterLinkedResult`, dove non sono più presenti.
- Comportamento esistente: `PresenterLinkedResult` risolve `linkedStatisticContext` e passa i `sourceWidgets` alla stessa `LinkedResultChart` usata da editor/anteprima. La chart crea `truthVisible`, abilita R soltanto quando `resultHasAnswerKey(source,targetQuestionId)`, applica `showCorrectAnswers:hasKey&&truthVisible` e mostra ✓/✕ tramite `answerTruthVerdict`.
- Correzione: sostituite le asserzioni RC191 obsolete con controlli dei flussi correnti; cinque test RC276 coprono il percorso positivo e mutazioni negative (sorgente errata, toggle scollegato, copia sorgente non aggiornata, chiave assente). Gate anticipato pre-npm; nessun codice runtime modificato.
- Integrità: mantenere immutabile l'inventario RC275, verificare RC276 come sorgente corrente. La CI completa e le prove browser rimangono obbligatorie.
- Stato: 85,25% certificato invariato, non pubblicare immagini Docker senza autorizzazione, no commit/push/tag da assistant.
