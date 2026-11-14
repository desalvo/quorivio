# RC337 — Export PDF/PPTX: errore 500 e ripetizione senza autenticazione
## Italiano
**Causa verificata nel codice:** la RC335/336 interrogava `page_reactions` selezionando `widget_id`, che non esiste nello schema PostgreSQL. Poiché questa query veniva eseguita sempre, anche una sessione senza reazioni poteva fallire con HTTP 500 prima dell'avvio del converter.

**Fix:** il server riusa `snapshot(s.id).reactions`, che contiene conteggi aggregati per pagina ed emoji, e li collega soltanto agli ID delle widget `reactions` appartenenti a quella pagina. Nessun ID partecipante, voto individuale o segreto viene esportato. Restano invariati gli altri conteggi e la cattura Chromium isolata.

**Interfaccia:** i quattro pulsanti PDF/PPTX ora eseguono download `fetch` autenticati e validano MIME, dimensione e firma, evitando di sostituire la dashboard con un JSON d'errore. Il codice 401 usa il gestore di riautenticazione già esistente; un errore del convertitore restituisce HTTP 502, senza pubblicare dettagli sensibili. La risposta `authentication_required` indica una richiesta senza cookie valido; non è causata automaticamente dal precedente HTTP 500.

**Collaudo richiesto:** applicare entrambe le nuove immagini app/converter dello stesso commit, accedere nuovamente, provare PDF e PPTX in entrambe le viste su una sessione con pagine, su una con reazioni e su una con risultati/gauge; controllare che il filename corrisponda al nome della sessione più `presentatore`/`partecipante`. In caso di ulteriori errori verificare i log dell'app e del converter senza condividere token o cookie.

**Stato:** fix sottoposto a full CI e a pubblicazione Docker multiarch con gate fail-closed; accettazione indipendente invariata a 85,25%.

## English
The visual exporter incorrectly queried a nonexistent `page_reactions.widget_id` column, causing HTTP 500 even for otherwise valid sessions. The corrected export reuses privacy-safe activity-level reaction aggregates and maps them only to authored reaction widget IDs. All four downloads now use the authenticated fetch handler, stay inside the dashboard on error, verify resulting files and handle expired authentication normally. A failing converter produces sanitized HTTP 502. Full CI, native image publication and real deployment testing are separate prerequisites; independent acceptance remains 85.25%.
