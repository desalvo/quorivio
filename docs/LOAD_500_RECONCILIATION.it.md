# Carico di 500 partecipanti — riconciliazione degli shard (24 ottobre 2026)

**Non costituisce un rapporto di collaudo eseguito.** Utilizzare soltanto endpoint di staging autorizzati. Non lanciare test di carico sulla produzione senza una finestra concordata. Il simulatore `tools/load_500.py` esegue partecipazioni anonime separate e genera un JSON per shard. Tutti gli shard devono utilizzare la *stessa* sessione. Su cinque generatori/processi impostare `--users 500 --shards 5 --shard-index N --json-out shard-N.json`; un solo shard deve effettuare l'osservazione autenticata del presenter. Gli indici dei partecipanti sono ripartiti senza duplicazione fra shard.

Dopo aver completato i processi, riunire i JSON ed eseguire:

```bash
python tools/aggregate_load_500.py shard-0.json shard-1.json shard-2.json shard-3.json shard-4.json --expected 500 --json-out 500-review.json
```

L'aggregatore restituisce codice 2 se mancano partecipazioni o WebSocket completati, esistono errori, manca l'osservatore presenter oppure il picco rilevato è inferiore al 95% (475). Rifiuta report mancanti, duplicati o incoerenti. Non somma i picchi di osservatori differenti perché ciò sovrastimerebbe la concorrenza. Anche un risultato PASS **non dimostra** la contemporaneità effettiva di 500 identità distinte, la correttezza dei quiz, la consistenza PostgreSQL, la modalità multi-replica, il rispetto degli SLO di latenza o l'accettazione RC. Verificare date/orari, metriche server, carico di CPU/memoria, connessioni DB e garanzie privacy. Il gate D4 resta aperto fino ai collaudi indipendenti.
