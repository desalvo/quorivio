# RC248 — Canvas interamente visibile dopo lo zoom della RC247

## Errore confermato in GitHub

RC247 è stata committata come `6a7f8e5eae6a972a218fca4b45348067ef58307d`. La full CI [42401914583](https://github.com/desalvo/quorivio/actions/runs/42401914583), quality gate `128491331054`, ha superato il controllo TypeScript e i controlli Chromium precedenti, ma è fallita in `tools/ci_editor_mock_layout_chromium.py` a **1440×900**. Il canvas 16:9 terminava a y=914,92, mentre la zona editor terminava a y=900. ClamAV verde; il resto della campagna è stato saltato in conseguenza del fallimento.

## Correzione RC248

Il massimo della larghezza del canvas RC247 dipendeva dall'intera altezza finestra (`100dvh`), ignorando lo spazio occupato da intestazione e palette. Ora la zona canvas desktop è un *CSS size container*: `100cqh` rappresenta l'altezza effettivamente rimasta. Nel limite si sottraggono l'altezza del righello superiore e un piccolo margine di sicurezza, compensando anche i 28px del righello verticale. Il canvas continua a sfruttare quasi tutto lo spazio disponibile, mantenendo il rapporto 16:9, senza bande inutili e senza tagli. Il layout smartphone intenzionalmente scorrevole rimane immutato.

Nuovo controllo statico negativo prima di npm, più test Chromium a 1440×900, 1200×900, 960×760, 760×820 e 390×844 con scale UI 0,64/0,80/0,96. Verificati dimensioni viewport, contenimento, proporzioni e assenza di scorrimento verticale involontario sul desktop. Il test storico RC178 rimane obbligatorio e invariato. Nessuna modifica API, database, Helm, Kubernetes, worker o publisher Docker.

## Stato e limiti

RC247 resta storica e immutata. Full CI RC248 **da eseguire**. Un test Chromium locale non equivale alla certificazione della full CI. Completamento **85,25%** (43 accettati, 17 parziali): `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o pubblicazione effettuati dall'assistente.
