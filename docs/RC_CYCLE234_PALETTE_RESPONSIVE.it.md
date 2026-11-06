# RC234 — Correzione overflow della palette nell'editor smartphone

## Causa verificata

La full CI GitHub `42245983528`, commit `d744de0eac508c5e6196e97315c09aa388c55985` (RC233), si è fermata nella verifica Chromium `ci_rc171_editor_palette_chromium.py` a **620 px**: larghezza di scorrimento **1198 px**, larghezza disponibile **608 px**. A 1440 e 960 px il test passava. Una regola RC226 per l'editor a colonna unica, con selettore CSS più specifico, imponeva `flex-wrap:nowrap` e `overflow-x:auto`, sovrascrivendo la palette RC171 progettata per andare a capo e scorrere in verticale.

## Correzione e prove

- Editor smartphone a una colonna invariato; la palette resta entro il viewport con `min-width:0`, `max-width:100%` e `box-sizing:border-box`, altezza limitata a `min(30dvh,198px)` e scorrimento verticale. Nessuno scorrimento orizzontale della palette.
- Tutti i 19 strumenti della fixture, incluse linee e forme, restano compatti e raggiungibili. Nessuna variazione a dati, API, privacy, database o layout desktop.
- Test Chromium RC171 mantenuto. Nuovo Chromium RC234 con risoluzioni **320, 390, 440, 620, 740, 760, 761, 960 e 1440 px**, verifica dei 19 strumenti, dell'assenza di overflow orizzontale e della raggiungibilità dell'ultimo pulsante dopo lo scroll.
- Nuovo test Python con tre verifiche di regressione e mutazioni negative delle regole CSS; controlli obbligatori nel workflow.
- Inventario RC234 promosso come corrente e inventario RC233 conservato come storico; intestazioni aggiornate in quattro documenti.

Le prove Chromium e Python mirate passano localmente; **full CI RC234 ancora da certificare**. Completamento invariato **85,25%** (43 gate accettati, 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Versione invariata `0.1.0-dev`, senza commit/push/tag dell'assistente.
