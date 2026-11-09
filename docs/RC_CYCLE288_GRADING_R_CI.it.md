# RC288 — Correzione CI: risultati e pulsante R

La full CI [42662034657](https://github.com/desalvo/quorivio/actions/runs/42662034657) si è fermata nel controllo storico RC221, che pretendeva il riquadro «Evidenzia le risposte vere sotto la widget risultati». Il riquadro era stato **rimosso intenzionalmente nella RC287**, perché invadeva il footer dell’editor. Il comportamento corretto usa il pulsante circolare **R** nel widget risultati e lo switch di configurazione nella finestra «Formato widget».

## Intervento

- Il controllo RC221 conserva la verifica della conversione PDF editabile, della riservatezza delle chiavi e delle formattazioni dei risultati; verifica ora la UI attuale anziché imporre il ritorno della barra difettosa.
- Nuovi test RC288, inclusi test negativi su assenza del pulsante R, attivazione senza chiave, rimozione dei campi riservati e reintroduzione dell’overlay.
- Nuovo gate prima del controllo RC221 nella CI; lo script dei controlli inventario mantiene la RC287 storica e promuove RC288.
- Sei manuali bilingui rigenerati con build RC288, senza attribuire le vecchie schermate della RC283 al nuovo build.

**Limiti di verifica:** nessuna modifica al codice runtime; nuove CI PostgreSQL/Chromium e campagne container da confermare dopo commit dell'utente. Baseline **85,25%** (43 gate accettati, 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o tag eseguito.
