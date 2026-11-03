# Quorivio 0.1.0-dev — RC149 — Correzione CI del contratto sfondi desktop/smartphone

RC149 dopo il commit RC148: GitHub Actions `41690976927` si è fermata nel controllo storico RC110 perché cercava il vecchio binding desktop non condizionale e la funzione upload con due parametri. L’editor attuale instrada correttamente selezione e caricamento del background smartphone in un layout indipendente; il test RC110 ora verifica entrambe le modalità e la regressione RC149 include casi negativi. Nessuna modifica al runtime dell’editor. L’inventario RC148 rimane storico e immutabile; CI completa, browser e accettazioni esterne ancora da confermare. **Completamento certificato 85,25%** (43 accettati / 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/rilascio dell’assistente.

## Verifica

- Verifiche RC110 esistenti su API, upload, nuvole e risposte conservate.
- Selezione e caricamento degli sfondi distinti tra desktop e smartphone.
- I test negativi rifiutano il ritorno allo sfondo desktop incondizionato.
- Inventari storici conservati con hash; ZIP e sorgenti chiusi e verificati.
