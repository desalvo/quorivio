# GitHub Actions 40379416187 — correzione BIGINT nel test delle classifiche (26/10/2026)

**SHA committato:** `5369f4384358face1822d4ada8a2df20425e32c2` (quiz temporizzati e nuovo editor).
**Errore:** test PostgreSQL obbligatorio `tools/ci_timed_widgets_postgres.py:79`: `TypeError`, confronto stringa `duration_ms` con intero. Prima del blocco sono passati 447 test Node, compilazione frontend/backend e moderazione reale PostgreSQL. Container saltato e Docker SKIPPED per policy opt-in.

## Causa

Entrambe le query delle classifiche proiettano `elapsed_ms` PostgreSQL `BIGINT`. Il driver `pg` di Node.js restituisce il tipo int8 come **stringa** per non perdere precisione oltre i 53 bit JavaScript. La UI già usa `Number(duration_ms)` solo per visualizzare i tempi. Il test Python introduceva un'aspettativa erronea sul formato.

## Correzioni

- Parser `duration_milliseconds()` nel test CI: valida stringa decimale ASCII nel range BIGINT positivo o zero, restituisce un intero Python senza perdita di precisione; utilizzato per le classifiche widget e legacy, compresi i pari merito.
- Quattro nuovi test regressivi verificano il range completo, rifiuto di altri tipi/formati, proiezioni SQL e uso del parser nell'accettazione HTTP.
- Stato sviluppo IT/EN e matrice RC aggiornati. API, DB e sicurezza di produzione invariati.

## Da validare

Eseguire dopo commit la CI standard e verificare test PostgreSQL delle classifiche, quality e container SUCCESS, Docker publication SKIPPED. Poi eseguire la CI Chromium manuale, con pubblicazione disabilitata, e controllare la resa effettiva dell'editor sui dispositivi. Punteggio RC 48,0% invariato.
