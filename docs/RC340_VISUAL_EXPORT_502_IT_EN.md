# RC340 — Esportazione PDF/PPTX: converter, ingress e immagini coerenti

## Italiano

Il 502 segnalato su `quorivio.apps.desalvo.eu` NON è stato riprodotto direttamente: non abbiamo accesso ai log del deployment. Il percorso di esportazione utilizza un converter isolato con Chromium/Playwright e, per PDF, LibreOffice. Gli errori possono nascere nel worker o nel proxy prima che la risposta HTTP raggiunga l'interfaccia.

**Verifica schema:** una prima ipotesi riguardava `page_ratings.widget_id`, apparentemente assente nella definizione iniziale di PostgreSQL. Il nuovo test CI sul database reale ha dimostrato che la colonna esiste grazie alla successiva istruzione `ALTER TABLE page_ratings ADD COLUMN IF NOT EXISTS widget_id`. La query originale era valida. La modifica SQL ipotizzata è stata annullata: i voti restano distinti per widget, senza perdita di dati né cambiamenti di schema.

**Correzioni effettive:**
- Il worker ora intercetta anche eccezioni inattese di Chromium/Playwright e restituisce `422 conversion_failed` anziché chiudere la connessione, senza pubblicare dettagli sensibili. Il server mantiene il proprio errore `502 visual_export_renderer_failed` quando il converter fallisce.
- Helm ora usa di default `desalvo/quorivio:latest` e `desalvo/quorivio-converter:latest`, entrambe con `imagePullPolicy: Always`; la versione precedente puntava il converter a `0.1.0-dev` e riutilizzava potenzialmente immagini app obsolete.
- Docker Compose può scaricare direttamente entrambe le immagini pubblicate e conserva la possibilità di build locale.
- Helm imposta timeout ingress di 900 secondi per NGINX (`proxy-read-timeout`, `proxy-send-timeout`) e HAProxy Technologies (`haproxy.org/timeout-server`), mantenendo le annotazioni personalizzate prevalenti. I timeout precedenti predefiniti possono interrompere conversioni lente.
- Regression test: errore HTTP imprevisto del converter, coerenza immagini e timeout ingress. La suite RC339 di export su un ambiente reale è ancora opt-in e non è stata eseguita sul sito dell'utente.

**Deploy e accettazione:** pubblicare prima app e converter dallo stesso SHA dopo la full CI; usare preferibilmente tag immutabili corrispondenti `sha-<SHA12>` per entrambi. Aggiornare Helm o Compose: Docker Hub da solo non aggiorna container/pod già in esecuzione. Verificare quattro esportazioni (PDF e PPTX, presentatore e partecipante), includendo reazioni, risultati e QR. Se compare ancora un 502, raccogliere solo i log tecnici, evitando segreti:

    kubectl -n <namespace> get pods -o wide
    kubectl -n <namespace> describe pod <nome-pod>
    kubectl -n <namespace> logs <nome-pod> -c quorivio --since=20m
    kubectl -n <namespace> logs <nome-pod> -c converter --since=20m

Controllare gli eventi di `OOMKilled` e timeout ingress. In Compose usare `docker compose ps` e `docker compose logs --since=20m app converter`. Per distinguere il 502 prodotto dall'applicazione da quello del proxy controllare `Content-Type` e corpo della risposta senza copiare cookie o token.

**Stato:** senza una prova end-to-end sul deployment non è corretto dichiarare risolto il 502 di produzione; avanzamento RC esterno invariato 85,25% (43 gate accettati, 17 parziali).

## English

The reported production 502 is not directly reproducible without access to the deployment logs. The original `page_ratings.widget_id` query is valid: a later SQL migration adds that column, as the real PostgreSQL CI gate proved. The proposed page-level aggregation was reverted. RC340 instead prevents unexpected Playwright exceptions from dropping the converter HTTP connection, aligns published app/converter image defaults in Helm and Compose, and adds overrideable 900-second NGINX/HAProxy ingress timeouts. Production resolution still requires matched-image rollout, worker and ingress logs, and real four-view PDF/PPTX acceptance. External RC readiness remains 85.25%.
