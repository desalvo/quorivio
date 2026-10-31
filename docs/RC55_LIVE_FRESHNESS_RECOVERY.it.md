# Quorivio 0.1.0-dev — Ciclo RC 55: freschezza snapshot WebSocket e visibilità dei dati obsoleti (30 ottobre 2026)

**Ultima baseline committata:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`; **cicli 49–55 cumulativi non ancora committati**. **RC certificata invariata: 81,25% (53 gate: 36 accettati, 17 parziali)**. Non attribuire punti ai test locali prima dei collaudi su GitHub e senza confondere l'implementazione con una certificazione di disponibilità.

**Sviluppo reale:** `apps/web/src/live-connection.ts` sorveglia la freschezza degli snapshot dopo l'apertura di ogni WebSocket (65 secondi predefiniti rispetto a snapshot server periodici ~20 secondi). Solo gli snapshot validi e della sessione giusta riarmano il watchdog; uno stream bloccato viene dismesso in modo atomico, il vecchio socket non può più aggiornare dati o stato, e un nuovo tentativo usa il backoff esistente. Anche `onerror` senza `onclose` forza un recupero delimitato. Timer annullati su offline, dispose, close e revoca.

**Interfaccia:** avviso accessibile per statistiche presenter e schermo pubblico con connessione persa o revocata; il contenuto precedente rimane visibile ma è dichiarato potenzialmente obsoleto. Nessuna modifica alle risposte o ai dati di sessione nel database.

**Evidenze locali:** 505 test backend e 99 frontend Node PASS; 1.347 Python PASS (1 saltato) in 8 gruppi, oltre al controllo TypeScript del transport; nuovi test Node deterministici su timeout senza snapshot, reset su snapshot validi, rifiuto di quelli di altra sessione, perdita rete, errori senza evento di close e annullamento timer; contratti Python e inventario. **Non dimostrato:** vera perdita di rete su due nodi indipendenti, 500 client sostenuti, tempi di recovery rappresentativi; CI standard ed estesa da eseguire dopo il commit. Gli input `kubernetes_tls_test` e `capacity_slo_test` dei cicli 50–52 restano opzionali e non ancora eseguiti sul nuovo cumulativo.

---

