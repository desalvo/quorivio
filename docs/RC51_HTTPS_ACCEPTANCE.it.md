# RC51 — protocollo di accettazione HTTPS Kubernetes

Versione **0.1.0-dev**. Evidenza di laboratorio locale: test dei parametri keyword-only, simulazione del flusso completo in Python per NGINX/HAProxy, prova client Node contro TLS locale reale. **Nessuna prova reale KIND del nuovo codice eseguita**, pertanto score RC = **81,25%**.

## Colleghi e comandi

1. Applica il package cumulativo 51 che include i cicli 49/50, senza sovrascrivere modifiche successive al commit `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`.
2. Prima del commit verifica `python3 -m unittest tools.tests.test_rc_cycle50_https_tls tools.tests.test_rc_cycle51_https_route_contract` e `python3 tools/verify_rc_cycle51_inventory.py`.
3. Dopo commit avvia CI standard, poi workflow dispatch esteso con `kubernetes_tls_test=true`, `publish_image=false`, `rc_strict=false`.
4. Richiedi SUCCESS per entrambi `kubernetes-https-ingress` (NGINX e HAProxy Technologies), compresi TLS/SNI con certificato temporaneo, Host errato 404, catena TLS non attendibile, disponibilità durante il rimpiazzo di pod e nuova lettura/live.
5. Controlla separatamente `tools/k8s_rwx_cross_node_probe.py` su cluster **di prova** CSI/NFS con nodi fisici distinti. Non abilita scrittura finché l'operatore non seleziona `--confirm-write`.

## Garanzie e limiti

Usa soltanto il contesto Kubernetes KIND effimero `kind-quorivio-multinode`, certificato e chiave temporanei e volume di prova host-bound. Non è una prova di CA pubblica, CSI RWX su host indipendenti, perdite di rete, SLO a 500 utenti sostenuti, audit GDPR/AGID, browser su dispositivi fisici o sicurezza indipendente. Nessun punteggio aggiuntivo finché GitHub non conferma la nuova prova. I nuovi test riducono i falsi positivi e i falsi blocchi, non certificano produzione.
