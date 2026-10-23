
## 2026-10-23 — Verifica editor con Chromium: blocco di accesso al server locale
- Chromium 144 e Python Playwright disponibili e avviabili; il browser gestito dall'ambiente blocca le navigazioni verso il server Vite su 127.0.0.1 (`ERR_BLOCKED_BY_ADMINISTRATOR`). Non è stato eseguito alcun E2E browser né PostgreSQL (server non disponibile).
- Correzione: i campi input dentro i widget non avviano più trascinamenti accidentali; la perdita della cattura del puntatore annulla il gesto e ripristina la geometria precedente. Aggiornati i test di regressione.
- Build backend/frontend superate; Node 107/107, Python 104/104. I gate RC rimangono al 37,5% secondo matrice, senza promuovere test sorgente ad accettazione browser.

### Collaudi in sospeso
- Drag/resize/rotazione con mouse e touch su browser reali.
- Salvataggio e riapertura con PostgreSQL 18.
- Tastiera e screen reader; confronto viewport mobile/tablet.
