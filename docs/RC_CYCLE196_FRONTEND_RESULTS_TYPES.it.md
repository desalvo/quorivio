# RC196 — Compilazione React e tipizzazione risultati fra pagine

## Provenienza del blocco

La run GitHub Actions [#296](https://github.com/desalvo/quorivio/actions/runs/42081815639), commit `b8d689a139d50b24724fbeb37da3d50c23e84fd1`, ha superato i controlli preliminari RC195, i 345 test Node frontend e i test dell’API, ma il gate di produzione si è arrestato al passo **Compile frontend and backend**. La compilazione rigorosa React (`tsc --noEmit && vite build`) ha trovato tre errori in `apps/web/src/main.tsx`: `TS2552` per il simbolo `linkedResultQuestion` non importato e due `TS2339` per `showSourceQuestion` assente dal tipo editabile.

## Correzione

- Import esplicito di `linkedResultQuestion` dal modulo sorgente `widget-results.js`. La copia della domanda sopra il grafico torna a usare la funzione reale e non un identificatore indefinito.
- Aggiunta di `showSourceQuestion` al tipo `EditorWidgetPermissionFields`, derivato dalla definizione validata di `PageDesign.widgets` per impedire divergenze fra editor, schema persistito e risultato.
- Nuovo preflight RC196 **prima di npm**, con mutazioni negative per import mancante, proprietà non tipizzata e scollegamento della renderizzazione; test Node esistenti invariati.
- Subito dopo `npm install`, prima dei collaudi lenti, controllo rigoroso separato `tsc --noEmit -p apps/web/tsconfig.json`, oltre a quello API già presente.
- Conservazione degli inventari storici e nuova ricevuta SHA-256 cumulativa indipendente.

## Validazione

Locale: 345/345 test Node frontend e 603/603 test Node API; Python mirati RC192/RC195/RC196; compilazione strict isolata dei tipi **reali** del widget e della funzione `linkedResultQuestion`. La build Vite/React completa non è stata eseguita: `npm ci --offline` segnala una dipendenza non presente nella cache locale, mentre la modalità online è scaduta nell’ambiente. Per la prova integrale servono la prossima CI GitHub e le sue dipendenze npm complete. Nessun commit, push, tag o pubblicazione effettuato.

**Versione** `0.1.0-dev` invariata. **Baseline CI e pubblicazione**: RC190, run `42027634427` e `42032833536`. **Completamento certificato**: 85,25%, 43 gate accettati e 17 parziali; nessuna promozione automatica. Per la nuova RC le opzioni `rc_strict`, `publish_image` e `publish_latest` restano disattivate salvo scelta esplicita.
