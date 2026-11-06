# RC218 — Riconciliazione selettore di rinomina nel test Chromium/PostgreSQL reale

## Errore GitHub e causa
La full CI della RC217 (run GitHub Actions `42191917542`, job di produzione `127805753403`) è fallita nella fase **Chromium editor PostgreSQL persistence and conflict acceptance**, in `tools/ci_browser_editor_postgres.py:151`. Il browser attendeva per 12 secondi `get_by_role('button', name='Rinomina pagina', exact=True)` dopo aver aperto il menu della prima miniatura. Dalla RC206 l'etichetta accessibile è **`Rinomina pagina (R)`** (o **`Rinomina pagine selezionate (R)`** nella selezione multipla). Il selettore a corrispondenza esatta era quindi obsoleto. ClamAV e i controlli precedenti sono passati; i job successivi sono stati saltati a causa del gate fallito.

## Intervento
Il test PostgreSQL reale individua ora il gruppo **portaled** `Azioni pagina 1` e riconosce esclusivamente `Rinomina pagina (R)` o `Rinomina pagine selezionate (R)` tramite espressione regolare ancorata. Verifica un singolo pulsante visibile e lo attiva, senza confonderlo con `Rinomina pagina` nel menu contestuale del canvas. Rimangono i controlli reali PostgreSQL: nuovo titolo persistito, revisione del design invariata, opzioni e geometria dei widget preservate, oltre ai controlli successivi su conflitti, riconciliazione ed export JSON.

Aggiunto il test preventivo `tools/tests/test_rc218_browser_postgres_thumbnail_rename.py` prima di npm, con mutazioni negative sui selettori, sull'ambito del menu, sul clic, sui controlli DB e sulla delega della rinomina. Smoke test dell'accessibilità Chromium superato con etichette singola e plurale. Le modifiche interessano solo test browser, preflight CI, documentazione e inventario; nessuna modifica al runtime, database, CSS o permessi.

## Verifiche e vincoli
Test Python mirati e controllo Chromium del selettore superati; la prova Chromium/PostgreSQL integrata e la full CI GitHub **restano da eseguire**. Versione `0.1.0-dev`, ultima full CI interamente verde RC203 (`42110429701`). Completamento certificato **85,25%** (43 gate accettati, 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o release eseguiti dall'assistente.
