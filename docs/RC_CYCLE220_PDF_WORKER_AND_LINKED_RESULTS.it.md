# RC220 — Importazione PDF/PPTX e risultati collegati

**Baseline:** RC219 full CI verde, run 42197607753 (14 job success, tre job di pubblicazione/immagini finali saltati). Versione 0.1.0-dev, avanzamento certificato 85,25% invariato.

## Configurazione server

Amministratore piattaforma → **Configurazione server → Convertitore PDF / PowerPoint (worker isolato)**. Il pannello mostra le tre condizioni di disponibilità: deployment abilitato, configurazione worker valida, health check del worker. I pulsanti **Abilita importazione PDF/PPTX**, **Disabilita importazione PDF/PPTX** e **Verifica stato worker** salvano o mostrano lo stato, senza riportare token o URL interno nel browser. Solo gli amministratori possono cambiare lo stato; una configurazione non pronta non può essere bypassata. La preferenza è persistente in `platform_settings.converter_enabled`, letta a ogni richiesta di conversione.

**Compose:** impostare nel file `.env` dello stack un `QUORIVIO_WORKER_TOKEN` casuale di almeno 32 caratteri (`openssl rand -hex 32`). `compose.yaml` configura già `QUORIVIO_ENABLE_CONVERTER=true`, `QUORIVIO_CONVERTER_WORKER_URL=http://converter:8099`, volume privato condiviso e servizio `converter`. Avviare lo stack completo (`docker compose up -d`). Non esporre la porta 8099. Il token di esempio `REPLACE_...` non è accettato. **Kubernetes/Helm:** predisporre il Secret `QUORIVIO_WORKER_TOKEN` e il sidecar `converter`, poi verificare i pod e l'endpoint `/health` tramite il pannello. Se il deployment non è abilitato, l'API deve essere riconfigurata e riavviata dall'amministratore dell'infrastruttura; un clic nell'app non installa o avvia container. I documenti convertiti diventano immagini full canvas; PDF non è una presentazione modificabile.

## Widget Risultati

Nelle proprietà: **Mostra titolo della widget collegata** e **Mostra risposte della widget collegata** sono indipendenti; i vecchi progetti con `showSourceQuestion=true` mantengono entrambi i contenuti finché non vengono sovrascritti. Il titolo appare in cima al widget più grande e in grassetto. Testo della domanda: pallino e colore distintivo (default `#2563eb`), configurabile in **Formato widget → Domande → Colore testo domanda nelle statistiche**. Le risposte sorgente sono elencate con pallino e grassetto, testo a capo; nessuna chiave di correzione è inviata ai partecipanti. La funzione resta limitata alle viste autorizzate del presentatore.

**Sicurezza:** `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Non attivare il worker senza container isolato, limiti di risorse, scanner e token privato. Full CI RC220 non ancora confermata. Nessun commit, push o tag dell'assistente.
