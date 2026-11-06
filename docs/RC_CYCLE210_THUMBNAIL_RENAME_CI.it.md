# RC210 — Riconciliazione test storici con rinomina multipla delle miniature

## Evidenza e causa
La full CI RC209 `42138018546`, job qualità `127630992928`, fallisce nel gruppo Python RC197 perché il test storico `tools.tests.test_page_rename_preview_contract_20261027` pretende la stringa `void renameCanvasPage(a)`. Dalla RC206 il menu delle miniature usa correttamente `void renameSelectedPages(a.id)`: questo percorso ordina le pagine selezionate con Ctrl/Cmd+clic o con la scorciatoia **R**, quindi chiama `await renameCanvasPage(page)` per la rinomina autorizzata di ciascuna. Il menu contestuale del canvas conserva la rinomina della singola pagina.

## Correzione
- Aggiornato il contratto storico ai percorsi attuali, senza rimuovere i controlli su endpoint proprietario, rinomina singola, ordine delle pagine e aggiornamento dello snapshot locale.
- Aggiunti tre test RC210, inclusa una mutazione negativa che verifica il fallimento del test se la rinomina multipla perde la delega al percorso autorizzato.
- Nuovo preflight anticipato in CI prima di npm/browser/Kubernetes; ricevute inventari storici conservate.
- Nessuna modifica al runtime applicativo o allo schema DB; `0.1.0-dev`, `rc_strict=false`, `publish_image=false`, `publish_latest=false` invariati.

## Verifiche e stato
Il comando aggregato di sette moduli che falliva su GitHub supera ora **35 test Python** in locale. Il nuovo controllo RC210 supera **3 test** (8 insieme al test storico della rinomina). Non è ancora una certificazione della full CI: TypeScript, Chromium, PostgreSQL, Kubernetes e pubblicazione dipendono dalla successiva esecuzione GitHub. Riepilogo RC209 fallito come conseguenza, ulteriori job saltati. Ultima full CI verde indipendente: RC203 `42110429701`. Completamento certificato invariato **85,25%** (43 gate accettati, 17 parziali). Nessun commit, push, tag o pubblicazione automatica.
