# Quorivio — collaudo 500 partecipanti

Obiettivo: **1 presentatore + 500 partecipanti contemporanei** su ambiente di staging autorizzato. Il requisito non è ancora certificato: eseguire il test su cluster reale e registrare p50/p95/p99, errori, CPU, RAM, database e latenza degli aggiornamenti.

## Preparazione

1. Creare una sessione di prova, abilitarne la partecipazione anonima e avviarla. Recuperare `session_id` e **join_secret** dall'URL di invito (non il codice corto mostrato dalla UI).
2. Autenticarsi come presentatore ed estrarre il cookie `q_auth` in modo sicuro.
3. Sullo staging soltanto, impostare `NODE_ENV=development` e `LOAD_TEST_TOKEN` casuale di almeno 32 caratteri. Questa opzione permette alle richieste di test autenticate dal segreto di oltrepassare il rate limit generale; in produzione è sempre disabilitata. Proteggere il token come una password.
4. Installare `aiohttp` nell'ambiente del generatore di carico, separato dal server.

```bash
python -m pip install aiohttp
python tools/load_500.py --url https://quorivio-staging.example --session-id UUID --join-code JOIN_SECRET --presenter-cookie 'q_auth=...' --load-token "$LOAD_TEST_TOKEN" --users 500 --ramp-seconds 60 --hold-seconds 120
```

Lo script apre una connessione WebSocket del presentatore, registra fino a 500 partecipanti con cookie distinti e mantiene le relative connessioni. Stampa JSON con latenza dei join, errori e massimo di partecipanti distinti rilevati. Una prova può fallire per limiti sul generatore stesso: aumentare i file descriptor ed eseguire da un host separato. Nessun benchmark è stato eseguito su un cluster reale in questo ciclo.

Il conteggio in `live_connections` è distinto per partecipante su tutte le repliche e aggiornato a intervalli di 20 secondi; i record stale non contano dopo 50 secondi, perciò una perdita improvvisa di rete può lasciare temporaneamente la presenza visibile. I record vengono eliminati alla disconnessione normale. Valutare retention e purging periodico dei record stale.

> **Aggiornamento:** lo scenario precedente basato su `--url` e `--join-code` è stato sostituito dal flusso QR anonimo `--join-url`. Per topologia, risorse, più generatori e criteri di accettazione fare riferimento a `docs/ARCHITECTURE_500.it.md`.
