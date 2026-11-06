# RC211 — Riconciliazione della numerazione presentatore/partecipanti nei test CI

## Evidenza e causa
Full CI della RC210: run `42139200296`, job `127634916707`. Il preflight RC195 (`tools.tests.test_rc195_master_typography_ci`) falliva in due test perché pretendeva `viewPageNumber=slidePageNumber(activities,viewActivity.id)`; la RC206 utilizza giustamente `slidePageNumber(activities,activity.id)`. La numerazione del footer deve seguire la pagina corrente del presentatore, **escludendo le pagine saltate** anche quando il partecipante guarda una pagina indipendente. Identificata anche l'asserzione storica RC91 con lo stesso errore, da eseguire successivamente.

## Correzione e protezioni
- Riconciliati entrambi i test storici RC91 e RC195 alla semantica approvata nella RC206, mantenendo i controlli tipografici e dei widget.
- Aggiunti tre test negativi RC211 che falliscono se il footer usa la pagina del partecipante, un indice assoluto o perde il routing indipendente delle pagine.
- Aggiunto preflight RC211 in GitHub Actions e test Node del conteggio delle sole pagine visibili; ricevute inventario storiche immutate.
- Nessuna modifica al runtime dell'applicazione né allo schema DB; versione `0.1.0-dev`; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Verifiche e certificazione
Il preflight che ha fallito in GitHub, i test di pagina RC91/RC195 e la regressione RC211 passano localmente. Full CI RC211 da eseguire, ultima full CI completamente verde RC203 `42110429701`. Completamento certificato 85,25% (43 gate accettati, 17 parziali). Nessun commit, push, tag o release eseguiti.
