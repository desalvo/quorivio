# RC229 — Riconciliazione test Python globali e diagnostica upload

## Origine

L'utente ha committato RC227 (`ec9de12e8f7e39cbc90d573bc2758b7fdf034ce2`); la run `42226572219` ha fallito al vecchio test RC225 della galleria sfondi. Il cumulativo RC228 risolve questo blocco. Il successivo test Python globale sullo ZIP estratto (2168 casi) ha evidenziato altri 9 fallimenti e 20 errori; gli errori di inventario e due fallimenti di invocazione dipendono dalla mancanza della directory `.git` nello ZIP e non costituiscono automaticamente problemi su GitHub.

## Correzioni

- Conservata RC228, inclusi i controlli di mutazione per la nuova finestra degli sfondi.
- Aggiornate le verifiche storiche per import JSON della pagina (ora con `aria-label`), URL QR come link accessibile invece di testo statico, ridimensionamento font smartphone, caricamento sfondi tramite helper nominato, persistenza del dialogo in caso di errore.
- Ripristinati i messaggi di errore HTTP utili e sanitizzati per gli sfondi nella funzione comune `uploadNamedFile`, mediante `backgroundUploadError()`; conferma dei file duplicati e blocchi di sicurezza invariati.
- Corretta la prova di dimensione massima nel convertitore PDF/PPTX: ora il mock non fallisce anticipatamente per l'archivio PPTX volutamente fittizio e verifica realmente il limite di 2 MiB per la struttura JSON.
- Nuovo passo anticipato GitHub Actions RC229 per 101 test, prima delle dipendenze npm.

## Certificazione

- Preflight locale RC229: 101/101 test Python superati; altri test mirati, API e frontend nel report finale. La full CI integrata dopo il nuovo commit resta da verificare. Ultima CI pienamente verde RC219 `42197607753`; completamento certificato **85,25%**, 43 gate accettati e 17 parziali.
- `rc_strict=false`, `publish_image=false`, `publish_latest=false`; nessun commit/push/tag o pubblicazione dell'assistente. Messaggio di commit successivo solo RC228–229, visto che l'utente ha già committato RC227.
