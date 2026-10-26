# Q&A: esaurimento pool connessioni PostgreSQL — CI 40366108461

## 26/10/2026 — CI GitHub 40366108461: correzione stallo nel pool PostgreSQL Q&A (non committato)
- **Baseline committata:** commit `1d4f0e957da2a568c188279e8d8e4fa76cb6dd33`; quality gate FAILED in `tools/ci_audience_moderation_postgres.py:73` durante 12 richieste parallele, timeout HTTP di 25 secondi. Test Node 442/442 e compilazione frontend/backend PASS; pubblicazione SKIPPED. Test moderazione PostgreSQL reale non terminato.
- **Causa:** gli endpoint domande, parole e voti riservavano connessioni dal pool PostgreSQL da 10 *prima* di eseguire `audienceIdentity()`, funzione che fa ulteriori query con lo stesso pool. Con 12 richieste si esaurivano tutte le connessioni: le verifiche dell'identità non potevano procedere. Il fixture riutilizzava inoltre impropriamente un unico opener/cookie jar su più thread.
- **Correzione applicativa:** acquisizione PostgreSQL soltanto dopo la verifica dell'identità, su tutti e tre gli endpoint; lock transazionali `FOR UPDATE` / `FOR SHARE`, limite tre domande per partecipante, privacy e rate limiting mantenuti. Rilascio immediato dopo COMMIT e prima di `notifyAudience()`, che richiede nuove query; rollback/rilascio difensivi in caso di errore.
- **Accettazione:** 12 client HTTP distinti, cookie copiati della stessa identità, controllano esattamente tre richieste accolte e nove limitate. Aggiunti tre test Python di regressione che impediscono di riaprire la condizione di stallo; il test PostgreSQL resta obbligatorio in CI.
- **Verifiche locali:** **442/442 Node PASS**, **51/51 Python mirati PASS** (e suite specifica moderazione 18/18), sintassi TypeScript e compilazione Python PASS. Suite Python complessiva non conclusa per timeout nei test HTTP di conversione documenti dell'ambiente locale. Nuova CI PostgreSQL/TypeScript/container **DA VERIFICARE**.
- **RC:** **48,0% invariato**; B3 ancora partial fino al collaudo reale PostgreSQL/Chromium. La CI corrente è fallita, la precedente baseline verde resta evidenza storica. Nessun commit, push, tag o release dell'assistente.

## Verifiche

- [x] Nessun checkout PostgreSQL prima della verifica identità sul pool condiviso.
- [x] Rilascio connessione dopo COMMIT e prima del broadcast.
- [x] Rate limit, lock, privacy e vincoli di sessione invariati.
- [x] Dodici client HTTP indipendenti della stessa identità, tre richieste accettate.
- [x] Test locali Node, Python mirati e sintassi.
- [ ] Nuova CI PostgreSQL concorrente PASS.
- [ ] CI build/container PASS e pubblicazione SKIPPED.
- [ ] Browser Chromium opzionale e accettazione accessibilità indipendente.
