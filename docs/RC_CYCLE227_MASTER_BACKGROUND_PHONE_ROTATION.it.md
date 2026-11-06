# RC227 — Libreria sfondi e modalità partecipante adattativa

## Funzioni implementate

- Nell'editor degli schemi il gruppo **Sfondo globale delle pagine** ospita un comando **Sfondi** con icona sopra, nome sotto e tooltip; rimangono i comandi Carica immagine e Rimuovi.
- La libreria si apre in un dialogo con miniature e nomi originali, aria-modal, etichette per screen reader, intrappolamento Tab/Shift+Tab, Escape, clic sul backdrop e ritorno del focus al pulsante di apertura. Le miniature usano aria-pressed per distinguere lo sfondo scelto.
- La libreria non determina più la larghezza della barra degli schemi. Su schermi 320–1440px il dialogo è interamente contenuto nella finestra e la sua griglia interna può scorrere.
- Vista partecipanti: prima della selezione esplicita, la modalità smartphone segue variazioni della larghezza e del puntatore (anche rotazione dispositivo); dopo aver scelto manualmente Diapositiva 16:9, Layout smartphone o Lettura accessibile, la preferenza non viene sovrascritta dagli eventi di resize o pointer change.
- Confermati nome originale degli allegati, styling di widget, autorizzazioni, numero massimo delle widget, persistenza e visibilità delle proiezioni esistenti. Nessun cambiamento a endpoint/database.

## Test e blocchi

- Frontend Node **398/398** inclusi nuovi test RC227 e riconciliazione del test storico RC173. Python mirati RC222–227 **34/34**. Sintassi TSX analizzata con TypeScript 5.8.3: zero errori di parsing.
- Chromium reale con CSS di produzione e DOM rappresentativo, **320×568, 390×844, 760×920, 1440×900**: dialogo contenuto nel viewport, miniature scorrevoli, mantenimento delle prove RC226.
- **Non** sono state eseguite build Vite/React o prove con app React compilata e PostgreSQL: `npm ci` non è riuscito per risoluzione DNS (`EAI_AGAIN` verso registry.npmjs.org), non a causa di una build fallita. La GitHub full CI RC227 è da eseguire dopo il commit dell'utente.
- Percentuale certificata invariata: **85,25%** (43 gate accettati, 17 parziali). Ultima full verde RC219 `42197607753`. Versione `0.1.0-dev`; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o pubblicazione Docker eseguito.

- La suite globale Python non è stata completata entro il limite temporale di 45 secondi; nessun esito globale viene dichiarato.