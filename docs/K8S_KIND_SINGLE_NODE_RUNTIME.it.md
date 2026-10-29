# Collaudo di distribuzione su KIND mono-nodo — ciclo RC 24

**Ambito:** job GitHub Actions opzionale `kubernetes_runtime_test=true`. Il job
crea un cluster KIND temporaneo con un solo nodo, compila localmente l'immagine
senza pubblicarla, quindi usa il generatore originale `tools/k8s_wizard.py` per
avviare PostgreSQL 18, 2 repliche API, PVC e PodDisruptionBudget.

Lo storage `ReadWriteMany` è ottenuto con **hostPath sullo stesso nodo KIND**, con StorageClass statica senza provisioner,
unicamente per provare che i due pod possono accedere agli stessi asset. Non
rappresenta uno storage RWX su nodi distinti, non è uno StorageClass adatto
alla produzione e non va copiato in un cluster operativo.

Il test attende l'avvio del database e dei due pod, verifica readiness,
liveness e pagina iniziale tramite servizio ClusterIP reale; salva un file
nel volume condiviso da un pod e lo legge dall'altro. Elimina quindi un pod,
controlla la risposta del servizio dal pod superstite e verifica che il
deployment torni a due repliche pronte. Rifiuta l'esecuzione se il contesto
Kubernetes non è esattamente `kind-quorivio-runtime`; non stampa segreti e
non pubblica immagini. Il job richiederà una **CI GitHub verde** prima che
questo ambito sia considerato verificato.

## Verifiche ancora necessarie

Non certifica ingresso NGINX/HAProxy reale, TLS, ClamAV, Podman rootless,
ARM64 nativo, almeno due worker indipendenti, CSI RWX, guasti di rete,
disaster recovery o SLA RPO/RTO. `kubernetes_manifest_test=true` valida gli
schemi sull'API server; `runtime_arch_test=true` testa Docker/QEMU: sono
collaudi diversi e non devono essere contati due volte.

Parametri consigliati per la CI manuale senza pubblicazione:

```yaml
browser_test: true
cross_browser_test: true
capacity_test: true
kubernetes_manifest_test: true
kubernetes_runtime_test: true
runtime_arch_test: true
publish_image: false
publish_latest: false
rc_strict: false
```

Per l'accettazione operativa usare un cluster rappresentativo con più worker,
storage condiviso effettivo, controller ingress installati, TLS, ClamAV e
collaudi di failover documentati da un operatore indipendente.
