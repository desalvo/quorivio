# RC123 — Caricamento media dei presentatori e pubblicazione Docker con timeout

Data: 2 novembre 2026. Ambito: Quorivio `0.1.0-dev`, successivo alla RC122 committata.

## Baseline verificata

La run GitHub Actions `41350047731`, commit `a97b80b8d09ebd1a6054111bf88326581e2cc80f`, ha completato con successo **11/11 job obbligatori** della campagna RC. Lo stato finale della run è però `cancelled`, per la cancellazione forzata del job Docker `publish-on-commit` rimasto in esecuzione. I test automatici sono dunque verificati, **non è certificata la pubblicazione Docker**. Restano parziali le approvazioni indipendenti GDPR/AGID, la fedeltà Office e i test su dispositivi fisici.

## Media dell'editor

Una sola politica `mediaUploadMime` gestisce tipo MIME e fallback dall'estensione nota per cinque percorsi: file della sessione, Logo/Immagine/Video/PDF, riempimento del widget, background privato della pagina e importazione di immagini convertite. Quando il selettore macOS/Desktop produce un JPEG con `type` vuoto o `application/octet-stream`, un'estensione `.jpg/.jpeg` riconosciuta determina solo l'header HTTP; il server continua a convalidare firma binaria, MIME, dimensione, autorizzazione, scanner antivirus e salvataggio. SVG ed eseguibili non sono accettati.

Il test preesistente per la libreria privata verifica proprietario, collaboratori e protezione degli accessi. Il nuovo `tools/ci_browser_media_picker_postgres.py` verifica con Chromium vero + PostgreSQL temporaneo i selettori file per sfondo e Logo, la libreria, gli asset indipendenti, l'autosalvataggio e la riapertura. Nessuna simulazione degli endpoint HTTP. **La prova browser RC123 deve ancora essere eseguita su GitHub.**

## Pubblicazione Docker

Il job Docker su commit `[publish-docker]` mantiene tutte e tre le condizioni obbligatorie di successo e l'autenticazione Docker Hub; ha ora un limite di **45 minuti**. Una pubblicazione bloccata deve terminare come errore o timeout, non trascinare indefinitamente la run. Il commit `[full-ci]` esegue la campagna estesa senza pubblicare. Eventuali retry Docker rimangono un'azione esplicita del manutentore.

## Stato

Sono richiesti test API/frontend, contratti mirati e inventario sullo ZIP definitivo. Build TypeScript, browser con backend reale e comportamento del timeout saranno verificati su GitHub. Nessuna modifica a server pubblici, credenziali, dati utenti o tag. Nessun commit/push dall'assistente. Completamento certificato invariato: **85,25%** (43 accettati, 17 parziali su 60; `rc_strict=false`, `publish_image=false`, `publish_latest=false`).
