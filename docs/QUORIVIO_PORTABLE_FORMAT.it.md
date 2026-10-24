# Archivio portabile Quorivio (v1)

Un file `.quorivio` è un archivio ZIP con `manifest.json` e file `media/<UUID>`. Il manifest contiene la definizione della sessione v1 e, per ogni allegato, MIME, dimensione e digest SHA-256. L'esportazione include soltanto gli asset appartenenti alla sessione e realmente referenziati da widget, sfondi o tema. Non include partecipanti, risposte, token, vecchi codici di accesso, password né segreti MFA. L'importazione crea una nuova sessione in bozza, con credenziali di accesso nuove.

API autenticate: `GET /api/sessions/:id/export.quorivio` e `POST /api/sessions/import.quorivio`, Content-Type `application/vnd.quorivio.session+zip`. L'interfaccia le affianca a JSON legacy e PPTX. Sono supportati PNG, JPEG, GIF, WebP, PDF, MP4 e WebM, con limiti di 300 file / 80 MiB di media decompressi / 100 MiB per archivio. Sono respinti percorsi non consentiti, duplicati, cifratura, compressioni incompatibili, checksum errati e file troppo grandi. Il backend verifica proprietà e digest prima dell'esportazione; l'importazione crea i nuovi record degli asset nella stessa transazione della nuova sessione.

Il vecchio JSON resta disponibile per la sola definizione, **senza allegati**. Gli URL esterni non sono incorporati e possono non funzionare offline; gli allegati caricati ma non referenziati non sono inclusi. L'archivio non è un backup completo del server. Sono necessari collaudi con database e browser reali, import/export tra due istanze e verifica di immagini, video, PDF e sfondi.

## Rafforzamento ottobre 2026: importazioni ripetute e duplicazione sicura

Ogni asset importato riceve un **nuovo UUID globale del database**, anche importando più volte lo stesso `.quorivio`. I riferimenti condivisi in tema, widget, sfondi pagina e risultati vengono aggiornati in modo coerente. `POST /api/sessions/:id/duplicate` copia i file effettivi nella nuova sessione invece di mantenere collegamenti ai file originali. Entrambi i percorsi verificano lunghezza, hash, firma del contenuto e politica antivirus configurata. In duplicazione, le dimensioni PostgreSQL `BIGINT` vengono convertite in numeri sicuri prima della convalida.

Il nuovo step CI `PostgreSQL-backed portable and profile lifecycle E2E` prova importazioni ripetute, assenza di collisioni, riferimenti condivisi, duplicazione di media e rifiuto di uno ZIP alterato. **Lo step è stato scritto ma non eseguito contro PostgreSQL in questo ambiente.** Per la RC servono ancora trasferimenti reali tra istanze distinte e verifiche con tutte le tipologie di media.
