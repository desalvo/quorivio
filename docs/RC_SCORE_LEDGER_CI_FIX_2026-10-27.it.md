# Correzione CI del punteggio RC — 27/10/2026

## Incidente

- Ultimo commit confermato dal maintainer: `551396cdaafb8765140355557eae8f8ceb59c8d4`.
- Run GitHub Actions push `40522786396`, job qualità `122254095095`: **FAILED** al passo `Kubernetes wizard and worker integration tests` (esegue la suite Python generale).
- Un solo test su 817 fallisce: `test_rc_gate_audit.RcGateAuditTests.test_weighted_ledger_is_normalized` confronta il punteggio RC corretto **53,0** con una costante obsoleta **48,0**. Gli altri 816 test sono passati. Build container successiva saltata e pubblicazione ordinaria disabilitata.

## Correzione

- Il test dell'audit ricalcola ora il valore atteso dai pesi e dagli stati effettivi dei gate; verifica i 100 punti, i subtotali per macroarea e i gate non ancora accettati. Casi sintetici verificano l'aumento lecito del punteggio e il rifiuto di stati/pesi non validi.
- Il test di preflight di rilascio non blocca più l'avanzamento sulla costante 53,0.
- Il test di milestone conserva come soglia minima le evidenze del 53,0 e i riferimenti storici, ma permette ai gate di essere promossi dopo verifica indipendente, fino all'eventuale completamento al 100%. Restano obbligatorie le evidenze documentali.
- Nessuna modifica a software di produzione, schema PostgreSQL, Docker o policy di pubblicazione manuale.

## Verifiche e limiti

- Suite Python completa locale **819/819 PASS** (due test aggiuntivi nell'audit).
- Suite RC mirata **310/310 PASS**, prima dell'aggiornamento dei controlli di milestone; questi ultimi hanno successivamente superato i test mirati.
- `python tools/rc_gate_audit.py`: **53,0**; `python tools/rc_release_preflight.py`: **release_candidate_ready=false** e nessun file obbligatorio mancante.
- La nuova CI GitHub di questo hotfix è **ancora da eseguire**. Nessuna promozione artificiale dei gate.

## Passaggio successivo

Commit del solo hotfix ai test ed esecuzione della CI standard su push. Non serve pubblicare nuove immagini Docker.
