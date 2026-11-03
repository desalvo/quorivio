# RC153 — Prova reale di 500 risposte e risoluzione del conflitto editor

## Correzione CI 41711064819

La build TypeScript/Vite, gli 825 test Node e i controlli browser preliminari erano verdi; il job `Production quality gate` si è interrotto in `tools/ci_browser_editor_postgres.py` perché la finestra flottante «Formattazione rapida widget selezionato» intercettava il clic sul pulsante «Confronta e riconcilia le modifiche» visibile e abilitato. L'editor nasconde temporaneamente la sola finestra di formattazione durante un conflitto di revisione (`suspendFormattingRibbon={pageConflict}`), mantenendo disponibili le funzioni di recupero e salvaguardando la bozza locale. La ripetizione del test autenticato/PostgreSQL in GitHub CI è indispensabile per la certificazione.

## Presentazione di prova privata, disponibile in tutti gli account

La presentazione `Quorivio · Prova tecnica 500 partecipanti` è **distinta dal tutorial preesistente**. Contiene una pagina introduttiva, la domanda a scelta singola **«Prova 500 risposte: quale funzionalità vuoi esplorare?»** con le opzioni `live`, `quiz`, `questions`, e un widget Risultati collegato alla domanda e una pagina di istruzioni per i risultati. È privata, in stato `draft`, e **non viene avviata automaticamente**. Solo il proprietario può attivarla/pubblicarla. Non contiene risultati o partecipanti reali.

La migrazione additive `sessions.demo_template_key` e l'indice unico parziale `(owner_id,demo_template_key)` impediscono duplicati, anche in caso di richieste simultanee o repliche. Per i nuovi utenti la creazione è inclusa nella transazione di registrazione/amministrazione/bootstrap. Per gli utenti esistenti viene creata idempotentemente alla prima richiesta autenticata di profilo (`/api/auth/me`) o dell'elenco sessioni (`/api/sessions`). Quando viene cancellata esplicitamente, le relative risposte sono eliminate dal normale processo di cancellazione GDPR e **viene creata una presentazione nuova, vuota**; non si recuperano dati cancellati. Gli account senza privilegi di presentazione la ricevono comunque, ma non possono pubblicarla finché non sono autorizzati.

## Esecuzione CLI controllata, sul server dell'operatore

Prerequisiti: Python 3 con `aiohttp` (`python3 -m pip install aiohttp`), account presentatore approvato, sessione di prova nello stesso account, cookie `q_auth` valido recuperato dagli strumenti sviluppatore/autenticazione, HTTPS configurato, capacità e autorizzazione a generare carico. Non inserire cookie, QR segreti e token nei log, chat, shell history o comandi CLI. Nessuna chiamata viene eseguita dal package durante l'installazione.

```bash
export QUORIVIO_LOAD_PRESENTER_COOKIE='q_auth=INSERISCI_IL_COOKIE_REALE'
python3 tools/live_500_answers.py \
  --base-url https://quorivio.example.org \
  --confirm-host quorivio.example.org \
  --confirm-run --open-test-question \
  --users 500 --concurrency 30 --ramp-seconds 900 \
  --option-id live --json-out ./quorivio-load-500-summary.json
```

`--open-test-question` attiva **soltanto** la sessione di test dell'account e seleziona la sua domanda predefinita; ometterlo per avviare la pagina manualmente dall'interfaccia del presentatore. Il test rifiuta altre presentazioni, un URL differente, un target non confermato, cookie mancanti e una domanda cambiata. Il report è solo aggregato: nuove identità, conferme HTTP, delta di risposte valide letto dal PostgreSQL tramite `/api/sessions/{id}/report.json`, errori raggruppati e latenza p50/p95/p99. Esito positivo soltanto con 500 conferme *e* +500 nuove risposte del widget confermate lato server. Le risposte legacy del sondaggio non sono conteggiate come risposte al widget.

Il limite normale dell'API è **100 richieste/minuto/IP**: ogni partecipante richiede almeno due POST. Il ramp di 900 secondi è prudente per un singolo IP, ma non sostituisce una pianificazione del carico né garantisce l'assenza di limiti di ingress, proxy o WAF. In ambiente **staging non di produzione**, impostando un `LOAD_TEST_TOKEN` forte nel server e la stessa stringa in `QUORIVIO_LOAD_TEST_TOKEN` nel client, si può ridurre la durata (es. `--ramp-seconds 60 --concurrency 80`). Il bypass rate-limit lato server è disabilitato per `NODE_ENV=production`, anche quando è presente il token. Non disabilitare le protezioni della produzione per eseguire lo stress test. Coordinare finestre di manutenzione e monitorare CPU, RAM, PostgreSQL, connessioni, risorse TLS, rate-limit e code.

**Limiti della certificazione locale:** il simulatore delle risposte non mantiene 500 WebSocket contemporanei. Per la prova di presenza simultanea è già disponibile `tools/load_500.py`, da eseguire separatamente. Lo script non è stato eseguito su alcun server reale e il test completo di PostgreSQL/Chromium e del carico da 500 risposte deve essere autorizzato/eseguito nell'ambiente di destinazione.
