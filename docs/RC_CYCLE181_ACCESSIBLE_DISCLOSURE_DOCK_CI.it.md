# Quorivio 0.1.0-dev — RC181: riconciliazione CI dei controlli accessibili

## Diagnosi della run GitHub

Run [41931287829](https://github.com/desalvo/quorivio/actions/runs/41931287829), commit `8eccbfb48a214e584c3e685c2877bede0bbbcf94`: installazione, unit test, compilazione e controlli Chromium RC180 superati. Il test `tools/ci_accessible_disclosure_chromium.py` fallisce alla riga 54 perché impone ancora la *sovrapposizione* tra toolbar e riepilogo accessibile in una fixture smartphone a 390px (`assert overlap`). La RC180 aveva correttamente eliminato tale difetto spostando i pannelli in flusso. Il riepilogo della campagna RC fallisce di conseguenza, mentre ClamAV è verde.

## Correzione

Aggiornato il test Chromium per richiedere **assenza di sovrapposizione** con il CSS reale dell'app. Conservati click e tap nativi (senza `force=True`) su `<summary>`, checkbox, toolbar contestuale e comando livello; l'apertura dell'alternativa accessibile chiude correttamente gli strumenti. Verificati 390px touch e 1440px desktop. Il test storico `tools/tests/test_ci_mobile_disclosure_overlap.py` ora protegge il comportamento corretto invece di pretendere il difetto eliminato. Un nuovo controllo anticipato `test_rc181_disclosure_dock.py` impedisce che tornino l'asserzione obsoleta e la perdita del reale hit-test.

Nessuna modifica al runtime o ai dati applicativi. Cataloghi SHA-256 storici immutati; nuovo inventario RC181 derivato dalla RC180. In CI il vecchio verificatore RC180 passa in modalità storica.

## Stato

Controlli Chromium locali (390px touch, 1440px desktop) e regressione Python mirata superati. CI GitHub completa, browser autenticato React/PostgreSQL e validazione assistiva su dispositivi reali ancora aperti. **Completamento certificato 85,25% (43 gate accettati / 17 parziali)**, `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o deploy dell'assistente.
