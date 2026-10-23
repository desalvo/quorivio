# Calendario, paginazione e ciclo di vita delle sessioni

## API
- `GET /api/sessions?page=1&page_size=10&search=...&role=all|owner|collaborator`: risposta `{items,total,page,page_size}`. In assenza di `page` resta disponibile la risposta array precedente.
- `GET /api/admin/users?page=1&page_size=10&search=...&approval=all|approved|pending`: risposta paginata, riservata agli amministratori.
- `GET /api/calendar?from=YYYY-MM-DD&to=YYYY-MM-DD`: eventi dell'utente (owner e collaboratore) ordinati per giorno e orario.
- `GET /api/sessions/:id/appointments`, `PUT /api/sessions/:id/appointments`: appuntamenti con `date`, `start_time` (HH:MM), `duration_minutes` (5–1440), `time_zone` (IANA). La modifica è riservata al proprietario.
- `POST /api/sessions/:id/status` con `status: "paused"` e successiva `status: "active"` per riprendere.

## Note di collaudo
La data e l'orario sono memorizzati nel fuso esplicitato: verificare il comportamento durante i cambi dell'ora legale. Il calendario è una prima vista mensile, non è ancora un clone funzionale di Google Calendar. Testare CI, migrazione su backup PostgreSQL e browser ARM64 prima di deploy in produzione.
