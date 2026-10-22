# Upload allegati per partecipanti — Quorivio 0.1.0-dev

Un partecipante anonimo già entrato nella sessione può caricare un allegato dalla domanda-widget di tipo `file`. Formati ammessi: PNG, JPEG, GIF, WebP, PDF, MP4, WebM; la dimensione massima deriva dalle impostazioni amministrative (default 100 MB) e dal limite dell’Ingress. Il backend richiede che sessione e pagina siano attive, un cookie partecipante valido, una domanda-widget di tipo file e una firma binaria compatibile con il MIME dichiarato.

Il partecipante carica il file dalla pagina e poi conferma la risposta; le due operazioni sono distinte. Il caricamento restituisce un asset_id che viene inserito automaticamente nel modulo. Gli asset sono memorizzati in uno storage privato, con checksum SHA-256 e il partecipante proprietario; altri partecipanti non possono usare l’asset nella loro risposta. Il presentatore autorizzato può inventariare e scaricare gli asset.

## Limiti e rischi ancora aperti

L'implementazione usa buffer in memoria, non esegue scansione antivirus e non elimina ancora con una coda affidabile gli upload rimasti senza risposta. Il massimo è 10 asset per partecipante per sessione; i controlli non costituiscono una quota transazionale resistente a richieste concorrenti. Prima della produzione sono richiesti streaming verso storage condiviso, scansione malware, controllo quote e test PostgreSQL/browser.

## Verifiche

I test unitari Node e Python non sostituiscono test end-to-end di cookie, identità, storage, migrazioni e autorizzazioni. La migrazione `session_assets.participant_id` richiede collaudo reale.
