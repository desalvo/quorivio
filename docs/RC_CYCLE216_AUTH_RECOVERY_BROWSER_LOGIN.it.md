# RC216 — Recupero Chromium: test di login dopo scadenza credenziali

## Diagnosi della run
La run GitHub `42145939288` (job di produzione `127657299986`) ha superato i preflight e lo strict typecheck, ma è fallita in `tools/ci_browser_editor.py` alla riga 402. Dopo la simulazione di un `401` su `/api/auth/me`, Chromium mostrava correttamente la schermata iniziale anonima con titolo «Accedi come presentatore», email/nickname, password e tasto «Accedi». Il test cercava invece il contenitore CSS storico `main.narrow`, rimosso dal layout attuale. ClamAV superato, campagna completa fallita e dipendenze saltate; nessuna pubblicazione Docker Hub.

## Correzione
La prova browser verifica tramite ruoli accessibili l'intestazione del login, i due campi e il pulsante; conferma anche che il precedente editor protetto non sia più renderizzato. L'intera seconda metà dello scenario rimane obbligatoria: ripristinata l'autenticazione simulata, il browser ricarica e deve ritrovare l'editor della stessa sessione. Nessuna cancellazione dei cookie, nessuna modifica al runtime, agli endpoint, alla persistenza o alla UI. Nuovo controllo fail-closed `tools/tests/test_rc216_expired_auth_browser_contract.py` con mutazioni negative (selettore obsoleto, form incompleto, mancato ripristino, eliminazione cookie) eseguito prima di `npm install`.

## Validazione e consegna
I test Python mirati sono verdi. La verifica completa della prova Chromium integrata richiede la full CI GitHub RC216. Conservati gli inventari storici, versione `0.1.0-dev`, completamento certificato **85,25%** (43 gate accettati / 17 parziali), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o tag dall'assistente.
