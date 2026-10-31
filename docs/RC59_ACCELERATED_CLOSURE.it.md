# Quorivio 0.1.0-dev — Sprint RC59: chiusura per macroaree

**Baseline confermata:** commit `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`.
**Evidenze CI confermate:** standard `41152434205`, estesa `41152939003`.
**Completamento certificato:** **81,75%**, **55 gate: 38 accettati, 17 parziali**. **RC strict NON PRONTA**.
Le modifiche del ciclo 58 e dello sprint 59 attendono ancora un commit del manutentore e nuova CI.

## Cambio operativo: niente microcicli

Usare **un solo lotto di sviluppo per una macroarea funzionale completa**, poi CI standard e un unico dispatch di accettazione automatica; acquisire gli errori in un lotto correttivo, senza generare ZIP per singoli test. Gli inventari precedenti rimangono immutabili. A ogni lotto mantenere `DEVELOPMENT_STATUS`, handoff, score derivato dal JSON, regressioni e package cumulativo. Il manutentore resta l'unico autorizzato a commit/tag/push/pubblicazione.

## Un solo comando CI estesa e nessun falso verde

Dalla scheda **GitHub Actions → Quorivio CI and Docker Hub → Run workflow** sulla revisione appena committata, scegliere:

- `rc_acceptance_suite=true`
- `publish_image=false` (obbligatorio, fail-closed)
- `rc_strict=false` (obbligatorio finché i gate indipendenti sono parziali)
- `publish_latest=false`

La campagna attiva insieme le **13 famiglie** normalmente opzionali: Chromium, Firefox/WebKit, capacità 500 utenti, p95 SLO globale, refresh quieto 70s, manifest K8s, runtime K8s, NGINX e HAProxy multiworker, TLS KIND entrambi i controller, OCI AMD64/ARM64, Podman rootless e ClamAV. Si esegue **soltanto su infrastrutture CI usa-e-getta**: nessun cluster dell'utente, nessuna immagine pubblicata. CI standard prima; evitare un nuovo workflow sulla stessa ref mentre il precedente è in esecuzione perché la concorrenza GitHub può annullarlo.

Il nuovo job `rc-campaign-conclusion` controlla **tutti gli 11 job principali**: `skipped`, `failure` e `cancelled` sono sempre un fallimento della campagna anche quando i job eseguiti passano. Il job finale scrive una tabella in `GITHUB_STEP_SUMMARY`. La campagna non conferma per definizione i gate manuali e **non cambia da sola la matrice RC**. Il tool locale `python3 tools/rc_campaign_preflight.py --check-workflow` verifica input, guardie e dipendenze in CI.

## Macroaree residue, da chiudere in parallelo

1. **Infrastruttura / resilienza** — B1, B4, C4, D2, D3: eseguire TLS KIND (non eseguito nella CI `41152939003`), poi su ambiente separato vero CSI/NFS/CephFS RWX tra macchine fisiche/VM indipendenti; testare lettura/scrittura a due vie con lo script del ciclo 49, failure di nodo e storage, restore con RTO/RPO misurati e SLO sotto degrado. I controller KIND e gli host-bind condivisi **non** certificano queste prove.
2. **SSO, email e amministrazione** — C1, C2, C3: prove reali di redirect/callback e consenso per Google/GitHub/Facebook, reset/revoca/replay cross-replica, deliverability SMTP esterna, abuso e MFA. OAuth flow già archiviato PostgreSQL con consumo singolo; il ciclo 59 impone limiti streaming per le risposte del provider. Le prove in CI con mock **non** sostituiscono i provider reali.
3. **UX, collaborazione e accessibilità** — A1, A2, A3, A4, B2, B3: revisione operatore su desktop/mobile fisico, drag-and-drop, editor/anteprima/partecipazione, strumenti assistivi e verifica in real time delle statistiche. Conservare screenshot, data, dispositivo, evidenza del difetto o approvazione.
4. **Conformità e documentazione** — D4, D5, D6: verifica sicurezza indipendente, GDPR, AGID e accessibilità, manuali IT/EN e corpus PowerPoint di terzi con fedeltà visiva. Non attribuire credito finché i responsabili non hanno approvato le evidenze.

## Criteri di chiusura

Per ciascun gate: ambito delimitato + modifica funzionante + regressione + evidenza CI/operatore esterno + aggiornamento del JSON. Conservare peso totale 100, nessun doppio credito ai vecchi test, RC strict soltanto con tutti i gate accettati. In assenza di laboratorio multi-macchina o attestazioni esterne, mantenere il gate **partial** e documentare il blocco effettivo; niente percentuali stimate.
