# Sessioni collaborative, import/export e upload — 0.1.0-dev

## Implementato (API, non ancora verificato end-to-end)

- Nome e data di riferimento della sessione (`reference_date`, ISO 8601).
- Invito/rimozione co-presentatori della stessa organizzazione, approvati dall'amministratore. Il proprietario della sessione gestisce i collaboratori.
- `GET /api/sessions/:id/export.json` esporta solo definizioni, template e attività, non i dati personali o le risposte. `POST /api/sessions/import` importa una definizione validata; `POST /api/sessions/:id/duplicate` crea una copia in bozza con nuovi link e senza risposte.
- Modifica in diretta del testo e delle opzioni conservando gli identificativi storici; opzioni con risposte non possono essere rimosse. Modificare la risposta corretta di quiz già votati richiede prima invalidazione.
- `POST /api/sessions/:id/activities/:aid/invalidate` contrassegna le risposte come invalidate mantenendole per audit. Vengono escluse dai risultati live e CSV, senza cancellazione silenziosa. Non consente ancora votare di nuovo dopo invalidazione (vincolo unicità da evolvere).
- Limite upload configurabile nelle impostazioni: `max_upload_mb` (1–1024, predefinito 100). Il wizard genera il limite Ingress corrispondente. Non sono ancora presenti pipeline di upload file, scansione malware, memorizzazione, quota utenti o conversioni.

## Da implementare prima della produzione

- Backup **completo** administrator: includere dump PostgreSQL coerente, oggetti S3/media, manifest, checksum, cifratura, restore atomico di prova e controllo versioni. Nessun endpoint pubblico per import DB arbitrari deve essere attivato senza processi isolati e convalida.
- Import/export della sessione comprensivo di risultati e allegati con protezione GDPR e verifiche di ownership; oggi l'export JSON è **solo definizione**.
- Pannelli UI completi per collaboratori, duplicazione/import/export e editing live.
- Ingress HAProxy community: verificare l'annotazione appropriata per la precisa distribuzione; l'impostazione `haproxy.org/max-body-size` si applica alla variante HAProxy Technologies.
- Test PostgreSQL, WebSocket multi-presentatore, permessi e migrazioni su dati esistenti.
