# RC228 — Correzione CI del contratto storico della galleria sfondi

## Diagnosi verificata

- Commit RC227 dell'utente: `ec9de12e8f7e39cbc90d573bc2758b7fdf034ce2`, run GitHub [42226572219](https://github.com/desalvo/quorivio/actions/runs/42226572219) del 6 novembre 2026.
- Job `Production quality gate` (`127921466008`): al passo `RC225 asset filenames, delete recovery and schema background before npm`, il test `test_gallery_covers_all_background_flows` richiedeva l'attributo inline `label="Immagine sfondo dello schema"` ora obsoleto.
- La RC227 ha spostato la libreria in una finestra di dialogo; il codice effettivamente committato usa `label="Scegli lo sfondo globale"` all'interno di `SchemaBackgroundTool`. Il job riassuntivo è fallito per effetto del quality gate; gli altri job dipendenti sono stati saltati. La run non dimostra un errore funzionale della libreria sfondi.

## Intervento

- Il test RC225 conserva le verifiche delle altre quattro gallerie e controlla per gli schemi il dialogo accessibile, la galleria, l'immagine selezionata e la chiusura dopo la selezione.
- Nuovo test RC228: verifica che il contratto funzioni anche nella forma esatta committata e che la rimozione del dialogo o della chiusura causi un fallimento. Nuovo passo CI anticipato prima di npm.
- Nessuna modifica a login, dati personali, API, database o pubblicazione immagini.

## Certificazione

- Suite mirate locali verificate (vedi handoff). Full CI GitHub successiva da convalidare; ultima verde RC219 `42197607753`. Avanzamento certificato **85,25%** (43 accettati, 17 parziali), invariato.
- `rc_strict=false`, `publish_image=false`, `publish_latest=false`; nessun commit/push/tag eseguito dall'assistente. Il nuovo messaggio di commit riguarderà soltanto RC228.
