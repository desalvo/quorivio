# Ciclo 52 — Accettazione carico e SLO di latenza globale

## Scopo
La CI standard non deve effettuare carichi sostenuti. La CI estesa con `capacity_slo_test=true` crea una **sessione temporanea** sul PostgreSQL effimero del runner. Il processo avvia 500 partecipanti con cookie separati e un solo osservatore presentatore, con 40 secondi di rampa e 90 secondi di mantenimento.

## Evidenze
`tools/load_500.py --latency-samples` genera solo array numerici `join_latency_samples_ms` e `first_snapshot_samples_ms`, senza ID, token o contenuti delle risposte. `tools/aggregate_load_500.py --strict-slo` aggrega tutti i campioni prima di calcolare il p95 globale. Il controllo rifiuta errori, dati mancanti, campioni invalidi e incoerenze fra i percentili riportati e i campioni originali.

**Limiti di default del nuovo test:** p95 join <= 5000 ms, p95 prima snapshot <= 8000 ms; 500/500 partecipanti, osservatore unico con picco >= 95%, zero errori, almeno 60 secondi di hold. La CI esercita un hold di 90 secondi.

**Uso:** dopo aver effettuato il commit, nella workflow dispatch selezionare `capacity_slo_test=true` e `publish_image=false`, `rc_strict=false`. Può essere unito a `kubernetes_tls_test=true`. Non usare il test su produzione. Per report su più generatori: `python3 tools/aggregate_load_500.py shard*.json --strict-slo`. Exit code 2 indica mancata accettazione SLO; dati invalidi producono un errore e non vengono accreditati.

## Da certificare esternamente
La prova non misura CPU/memoria dei server, SLO sotto guasti reali, latenza rete WAN, macchine fisiche indipendenti, ricampionamenti temporali o partecipanti con dispositivi reali. B4 resta parziale e il credito rimane subordinato al successo del job Github, alla revisione delle evidenze e al rispetto delle policy SLO specifiche dell'esercente.
