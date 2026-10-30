# Quorivio RC ciclo 29 — multi-nodo e Ingress NGINX (30 ottobre 2026)

**Regressione locale:** 1.193 test Python eseguiti, uno saltato, nessun fallimento. Build npm e KIND reale non eseguiti localmente.

## Risultati effettivi

Dopo il commit del ciclo 28 (`016beea25d5e2d2fab21b0730aa15baf0b573e12`), GitHub Actions ha confermato **SUCCESS** per runtime OCI AMD64+ARM64 emulato (`40980312270`, job `123820527902`), e per **Podman rootless con PostgreSQL 18** (`40982728705`, job `123827805762`). Non è certificata l'esecuzione su ARM64 fisico.

Queste evidenze permettono di separare 0,5 punti di peso dal gate D3 ancora parziale e accettarli come sottogate tecnico automatico: il contributo già computato era 0,25 punti (parziale); ora vale 0,5 punti (accettato), quindi **RC 79,00% → 79,25% (+0,25 punti percentuali)**. Matrice di 48 gate: 31 accettati, 17 parziali. Non è stato accettato nessun nuovo test non eseguito.

## Nuovi sviluppi del ciclo 29

- **Wizard Kubernetes:** `enforce_node_diversity=true` richiede almeno due repliche, `ReadWriteMany`, impone `DoNotSchedule` con `minDomains: 2` e assicura la separazione per hostname di due repliche. Il default rimane compatibile con KIND mono-nodo.
- **URL pubblico corretto:** Ingress HTTP senza TLS genera `PUBLIC_BASE_URL=http://...`, con TLS resta `https://...`. Evita link/reindirizzamenti HTTPS errati nei deployment HTTP interni. In produzione è preferibile utilizzare TLS.
- **Helm:** `enforceNodeDiversity` opzionale; vincolo RWX quando `replicaCount > 1`; rolling update `maxUnavailable: 0`, `maxSurge: 1`, PDB con `minAvailable = replicas-1`. Rischio significativo di blocco deliberato delle repliche se nodi RWX insufficienti; la configurazione non crea alcuno storage condiviso.
- **CI opzionale indipendente:** `kubernetes_multinode_test=true` avvia KIND con due worker e un control-plane, costruisce un'immagine locale non pubblicata, avvia PostgreSQL 18 e due pod Quorivio distribuiti obbligatoriamente su worker differenti, verifica la visibilità dei file tra worker, installa un vero controller Ingress NGINX con manifest versionato, verifica routing host/HTTP, rifiuto host errato e continuità attraverso la sostituzione di un pod. Script `tools/ci_k8s_multinode_ingress_smoke.py`.

**Limiti importanti:** il collaudo condiviso usa *bind mount temporaneo del runner Docker* fra i due worker KIND, non NFS/CSI RWX di produzione. Non verifica HAProxy effettivo, TLS pubblico, controllo multi-master, nodi fisici indipendenti, accessibilità AGID, GDPR, RTO/RPO o SLA. Il nuovo job KIND multi-nodo non è stato eseguito in questo ambiente: resta da confermare su GitHub. I test di codice locale e i contratti dello script non certificano un deployment reale.

## Workflow consigliato dopo il commit

Eseguire `workflow_dispatch` su `main` con `kubernetes_multinode_test=true`, `kubernetes_manifest_test=true`, `kubernetes_runtime_test=true`, `rootless_podman_test=true`, `runtime_arch_test=true`, `publish_image=false`, `rc_strict=false`. Come primo passo, si può abilitare soltanto `kubernetes_multinode_test=true` per accelerare il feedback sul nuovo test. La pubblicazione resta solo con opt-in esplicito dell'utente.

**La RC non è pronta:** rimangono 17 gate parziali e le convalide indipendenti obbligatorie. Nessun commit/push/tag o publish effettuato dall'assistente.
