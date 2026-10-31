# Quorivio 0.1.0-dev — Ciclo RC 54: recupero live WebSocket (30 ottobre 2026)

**Baseline committata:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`. **Cumulativo ancora non committato:** cicli 49–54. **RC certificata 81,25%**, 53 gate (36 accettati, 17 parziali). Nessun punto aggiunto senza collaudo indipendente.

**Sviluppo funzionale:** il nuovo client live WebSocket evita che messaggi/errori di connessioni sostituite sovrascrivano lo stato corrente. Alla perdita di rete cancella timer e chiude il vecchio socket; al ritorno online apre una sola connessione. Gestisce handshake che non terminano entro 15 secondi, retry esponenziali con jitter individuale e limite di 30 secondi, terminazione per codici 4003/1008 senza reconnessione non autorizzata, messaggio dedicato per accesso revocato e callback React aggiornati. Presenter e partecipanti usano la stessa logica. Il protocollo server/PostgreSQL rimane invariato.

**Evidenze e limiti:** nove test deterministici e controllo TypeScript stretto; le prove di carico/resilienza su browser reale e la CI GitHub rimangono necessarie. Test infrastrutturali HTTPS, SLO 500 partecipanti e CSP dei cicli 49–53 non ancora confermati su GitHub. Nessuna pubblicazione/commit dell'assistente.
