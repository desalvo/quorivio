# RC202 — Test PowerPoint dopo installazione delle dipendenze

## Causa del fallimento

Nella GitHub Actions `42105427044`, job Production quality gate `127518865236`, lo step `Validate active RC release headers against the current inventory` fallisce nonostante intestazioni e inventari corretti: due test PowerPoint di `tools.tests.test_rc200_editor_portability` importano `pptx` e `PIL` prima che siano installati. Il workflow installa appositamente le librerie di conversione in una fase successiva.

## Correzione

- I quattro test di solo codice, API e UI RC200 restano nel preflight come classe `RC200EditorPortability`.
- I due test reali immagine/PPTX vengono eseguiti nella nuova classe `RC200NativePowerPointPortability`, obbligatoria dopo l’installazione e verifica esplicita di `pptx`, `PIL` e `aiohttp`, oltre che nella suite integrale `unittest discover`.
- Aggiunto `tools.tests.test_rc202_dependency_staging` per impedire che le dipendenze native finiscano nuovamente nella fase priva di pacchetti.
- Conservati il controllo storico RC97 e gli inventari precedenti byte per byte.

Nessuna modifica a runtime applicativo, schema, autenticazione, aggiornamenti URL/QRCode RC201 o pubblicazione Docker. Restano `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o tag effettuato.

## Validazioni e handoff

Superati localmente i test RC200 preflight, i test PPTX reali e i controlli RC97/RC202. La full CI di RC202 dovrà confermare tutto il percorso. Ultima full CI verde: RC199, `42096705867`. Completamento certificato 85,25% (43 gate accettati, 17 parziali), invariato.
