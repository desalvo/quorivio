# 27 ottobre 2026 — Hotfix compilazione e consolidamento widget (dopo 6395b0b)

## Origine e CI
Package cumulativo allegato, basato sul commit confermato `6395b0b9982bbcd898d921eab836d3ee63b305eb`. Versione 0.1.0-dev e licenza EUPL-1.2 invariate. La run GitHub `40574076999` è fallita in compilazione frontend per tre TS2339 su `fillMode` e `fillImageAssetId` (riga 939); la successiva verifica CI GitHub richiede il commit dell'utente. Nessuna nuova CI verde dichiarata.

## Correzioni effettive
1. Lo storico widget dell'editor usa il tipo `WidgetTextStyle` esportato dal backend; l'helper grafico condivide lo stesso contratto per forma, trasparenza, gradiente, bordi e asset privati. Nessun nuovo `any` o `@ts-ignore` usato per eliminare gli errori.
2. Aggiunto contratto di compilazione con controllo di parità per `fillMode`, `fillImageAssetId`, forma e opacità; conversioni esplicite alle union per allineamenti e animazioni.
3. Corretto il tipo `PageDesign` per il widget `participant-count`, già ammesso dal validatore runtime; tipizzate durata del quiz, risposte corrette e vista risultati; validazione stretta delle viste risultati.
4. Aggiunta conferma cancellazione dal pannello proprietà, come negli altri percorsi di rimozione. Uno sfondo impostato su trasparente non visualizza più un'immagine di riempimento rimasta selezionata.
5. Duplicazione di sessioni terminate e rimappatura degli asset mantenute, con regressioni locali verdi; restano da verificare sul database PostgreSQL effettivo e tramite browser autenticato.

## Evidenze locali
- Archivio dipendenze già fornito dall'utente recuperato dalla Libreria per aggirare il DNS del registry npm; `node_modules` non sarà incluso nel package.
- `npm run build`: **PASS** (backend TypeScript; `tsc --noEmit` frontend; Vite production build).
- `npm test`: **450/450 PASS**; test frontend Node **23/23 PASS**; test Node mirati dopo la modifica **26/26 PASS**.
- Test Python specifici duplicazione/editor/autosalvataggio **26/26 PASS**.
- **7/7** script Chromium isolati verdi su viewport desktop/mobile, ma NON equivalgono a una prova applicativa end-to-end con PostgreSQL 18.
- Suite Python globale e discovery RC: **timeout locale**, non dichiarate verdi.

## RC e prossimi passi
- Matrice RC: nessun gate promosso, A1/A2/A3/A4 ancora parziali. Percentuale globale **53,0%**, RC non pronta.
- Dopo commit eseguito dall'utente: CI standard senza pubblicare immagini Docker; poi workflow manuale `browser_test=true`, senza `publish_image` né `publish_latest`, con PostgreSQL 18 e controlli su persistenza delle proprietà dei widget, isolamento delle copie di sessioni terminate, autosave dopo perdita di rete e confronto editor/anteprima/proiezione.
- Necessari verifiche cross-browser, accessibilità con screen reader, touch reale, verifiche visive indipendenti e firma RC. Nessun commit, push, tag, release o pubblicazione Docker eseguito qui.
