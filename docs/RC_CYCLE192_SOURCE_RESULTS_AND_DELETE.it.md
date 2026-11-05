# Quorivio 0.1.0-dev — RC192: domanda sorgente nei risultati ed eliminazione pagine

**Baseline:** cumulativo RC191; ultima campagna GitHub completamente verde: RC190 `42027634427`, publish Docker Hub multiarch `42032833536`, commit `bb80a3ce`. Versione invariata `0.1.0-dev`.

## Interventi

1. **Titolo e opzioni sorgente facoltativi nella widget Risultati.** La casella «Mostra titolo e risposte della domanda sorgente» (`showSourceQuestion`) inserisce sopra le statistiche una copia non interattiva della domanda originale: titolo, descrizione e tutte le possibili risposte, conservando font, marcatori di formattazione nel testo e stile delle opzioni. Funziona anche per sorgente in altra pagina o sottodomanda indipendente (`targetQuestionId`). Per gradimento e reazioni visualizza la scala 0–9 o le icone. Predefinita disattivata. «Solo risultati» e questa opzione sono reciprocamente esclusive. Non mostra chiavi di correzione; i risultati live rimangono privati del presentatore. Il difetto dei dati risultati precedente, come chiarito dall'utente, riguardava **le sole anteprime**, non i conteggi live.
2. **Elimina pagina ora esegue la cancellazione confermata.** L'API prima rispondeva 409 `page_referenced_by_session` se la pagina era destinazione del pubblico o sorgente di risultati. Dopo la conferma, la cancellazione ora mantiene il lock di sessione, blocca le altre pagine, scollega i riferimenti di proiezione e statistiche (`audiencePageId`, `targetActivityId`, `targetWidgetId`, `targetQuestionId`), incrementa la revisione dei layout interessati e cancella pagina e risposte nella stessa transazione. Riordina le posizioni residue, aggiorna lo snapshot nell'editor e segnala quante pagine avevano collegamenti rimossi. Annullare non cancella nulla; bozze non salvate restano protette.

## Verifica e collaudi richiesti

- **603/603 test Node API**, **329/329 frontend** e **18 test Python mirati** superati, insieme al controllo TypeScript strict dei moduli source/result/domain e ai test storici sulla doppia proiezione. Controllo sintattico TSX e inventario SHA-256 cumulativo.
- Compilazione npm React/Vite/backend completa e verifica browser/PostgreSQL della cancellazione **da confermare con la prossima CI**. Non vanno dichiarate già certificate.
- Nuovo preflight anticipato RC192 nel workflow; inventari precedenti conservati.
- Completamento certificato **85,25%** (43 gate accettati, 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag/publish dell'assistente.

## Prova funzionale guidata

Nella pagina A creare una domanda a scelta multipla, con titolo e opzioni formattati e una sottodomanda indipendente. Nella pagina B creare una widget Risultati collegata ad A, abilitare `showSourceQuestion`: anteprima affiancata e proiezione del presentatore devono mostrare titolo e opzioni sopra al grafico. Disattivare e verificare il layout precedente, senza rivelare chiavi vero/falso. Assegnare poi A come pagina per il pubblico di B; eliminare A confermando e verificare che A scompaia, B rimanga, la configurazione della destinazione del pubblico sia ripristinata al valore predefinito (pagina corrente) e il collegamento risultati non rimanga orfano. Ripetere con editor multipli per i conflitti di revisione.
