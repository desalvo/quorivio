# Quorivio — architettura di riferimento per 1 presentatore e 500 partecipanti anonimi

**Stato: dimensionamento iniziale, non benchmark certificato.** Versione `0.1.0-dev`. Nessuna modifica al cluster è necessaria per leggere o eseguire localmente lo scenario.

## Flusso

```
500 browser mobili -- HTTPS /join/<token QR> --> LB/TLS --> Ingress NGINX o HAProxy
                                                      | WebSocket /live
                                               Service ClusterIP
                                                 /    |    \
                                            3 pod Quorivio
                                   [API + converter + ClamAV] per pod
                                                 |    |
                                PostgreSQL 18 condiviso   PVC RWX per asset
                                                 |
                            tabella live_connections (presenza distribuita)
```

La connessione WebSocket resta associata al pod che l'ha accettata. Il contatore dei presenti è calcolato da PostgreSQL per partecipante distinto; l'heartbeat è ogni 20 secondi e l'assenza viene rilevata dopo circa 50 secondi. **Verificare il fan-out cross-pod degli eventi**: la presenza condivisa NON dimostra che un broadcast eseguito da un pod raggiunga i WebSocket degli altri pod. Prima di certificare il multi-pod occorre un bus Redis Pub/Sub, PostgreSQL LISTEN/NOTIFY con recupero su riconnessione, o un meccanismo equivalente misurato. In alternativa un solo pod può mantenere tutti i WebSocket, ma questa scelta riduce la resilienza e va verificata sotto carico.

## Stima iniziale risorse

| Componente | Quantità | CPU request / limit | RAM request / limit | Note |
|---|---:|---|---|---|
| Quorivio API | 3 pod | 0,5 / 2 vCPU ciascuno | 512 MiB / 1 GiB ciascuno | circa 167 socket/pod a distribuzione uniforme |
| Converter | 1 sidecar per pod | 0,25 / 2 vCPU | 512 MiB / 2 GiB | isolare i job pesanti durante le sessioni live |
| ClamAV | 1 sidecar per pod | 0,2 / 2 vCPU | 768 MiB / 2 GiB | costo di memoria rilevante |
| PostgreSQL 18 | 1 primario + backup, HA opzionale | 2–4 vCPU riservate | 4–8 GiB | pool applicativo limitato, SSD e metriche lock/IO |
| Ingress | 2 repliche consigliate | 0,5–1 vCPU ciascuna | 256–512 MiB ciascuna | almeno 2 nodi per disponibilità |
| Storage asset | RWX | — | ≥20 GiB iniziali | verificare latenza e IOPS |

**Budget cluster:** richieste pod applicativi ~2,85 vCPU / ~5,25 GiB, esclusi ingress, database, sistema e margine. Prevedere almeno 3 nodi worker con ~4 vCPU e 8–16 GiB disponibili ciascuno, e margine del 30% o più; considerare la collocazione dei sidecar e failover di un nodo. I limiti sono massimi teorici, non capacità garantita. Separare DB e load generator dai worker applicativi quando possibile.

## Traffico e sincronizzazione

500 socket WebSocket aperti richiedono relativamente poca banda *a riposo*. La variabile dominante è la dimensione e frequenza degli snapshot e i download media. Ad esempio, 500 client × 10 KiB × 1 aggiornamento/s = ~4,9 MiB/s (~41 Mbit/s) di payload in uscita, senza overhead TLS/rete; con 100 KiB il requisito sale a ~410 Mbit/s. Raccomandare collegamento disponibile **≥1 Gbit/s** sulla rete ingress/worker e verificare l'egress internet reale. Limitare snapshot, usare delta events/payload versionati e distribuire media statici con cache autenticata appropriata; non inviare asset binari nelle notifiche WebSocket.

Ingress TLS termination: timeout di lettura/invio WebSocket ≥3600 s; supporto `Upgrade`/`Connection`, TLS e inoltro dell'host/origin, keepalive appropriati, rate limiting degli anonimi senza penalizzare 500 utenti dietro NAT condiviso. NGINX supportato tramite `values-500-staging.yaml`; per HAProxy configurare timeout tunnel/client/server equivalenti secondo la versione del controller e preservare le annotazioni legacy già richieste dal deployment esistente. Non copiare annotazioni NGINX su HAProxy.

Distribuire i pod su nodi diversi (topology spread / anti-affinity), impostare PDB minAvailable=2, readiness/liveness, graceful drain dei socket durante rollout; HPA CPU 60–70%, minimo 3 massimo 6, solo dopo misure e **con fan-out multi-pod confermato**. Scelta prudente: pre-scalare prima dell'evento anziché fare affidamento esclusivo su HPA mentre entrano 500 partecipanti.

## Test anonimi via QR

La prova simula il percorso `GET /join/<token>` → GET delle informazioni di sessione → POST anonimo `/api/join/<token>` con pseudonimo e cookie indipendente → WebSocket `/live?session=<uuid>`. Non crea account. Il QR deve risolvere all'URL completo passato come `--join-url`. Solo su staging autorizzato usare il bypass rate limit con `LOAD_TEST_TOKEN` (disabilitato in produzione).

```bash
python -m pip install aiohttp
python tools/load_500.py --join-url 'https://staging.example/join/TOKEN' --session-id UUID --users 500 --ramp-seconds 120 --hold-seconds 300 --presenter-cookie 'q_auth=...' --load-token "$LOAD_TEST_TOKEN" --json-out result.json
```

Per distribuire 500 utenti su **5 generatori realmente distinti** (100 per host), usare su ogni host gli stessi `--users 500 --shards 5`, variando `--shard-index` da 0 a 4. Solo un generatore include `--presenter-cookie`; la metrica di picco così osservata deve essere confrontata con 500. La distribuzione IP reale dipende dalla rete/egress, non dall'identificatore del partecipante. `--source-ips 192.0.2.10,192.0.2.11` funziona **solo** per indirizzi effettivamente assegnati al generatore: non produce IP pubblici fittizi e non elude limiti del server. Non usare proxy aperti o sorgenti di terzi.

## Gate minimi di accettazione proposti

1. 1 presentatore + **500 partecipanti distinti** collegati nello stesso intervallo per 5 minuti, senza crash o OOM.
2. ≥99% ingressi riusciti; errori 5xx inferiori allo 0,5%; tempo ingresso p95 <3 s su rete di prova controllata.
3. Cambio pagina/pause e rilascio quiz osservati da ≥99% dei client in <2 s (p95), inclusi client su pod differenti.
4. Contatore convergente al valore osservato entro 5 s dopo l'ingresso completo, e diminuzione entro 60 s dopo disconnessione improvvisa.
5. Testare un pod terminato durante la prova, riconnessioni, 2 ingress diversi, risposte simultanee, CPU/RAM, DB pool/lock, latenza e banda.

Lo script attuale misura join, primo snapshot e presenza vista dal presentatore; **non misura ancora automaticamente tutti i gate sopra riportati** (per esempio la latenza degli eventi multi-pod): usare browser/probe e metriche Kubernetes/Prometheus aggiuntivi. Non dichiarare il requisito certificato prima della prova reale.


## Event bus recovery / Ripristino del bus

Le API usano già PostgreSQL LISTEN/NOTIFY per distribuire gli eventi tra pod. Ogni replica mantiene un listener dedicato e ricarica gli snapshot dal database quando riceve notifiche. Dopo una riconnessione, risincronizza le sessioni con client WebSocket locali, recuperando gli eventi persi. Occorre collaudare interruzioni e ripristino con più repliche; non equivale a una certificazione dei 500 partecipanti.
