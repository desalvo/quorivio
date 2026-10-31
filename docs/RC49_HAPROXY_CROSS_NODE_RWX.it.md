# Quorivio 0.1.0-dev — ciclo 49: HAProxy verificato e prova RWX tra nodi

## Evidenze GitHub riconciliate

- **Baseline confermata dal manutentore:** `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c` (ciclo 48).
- **CI standard:** run `41120048115`, qualità `124284164769` e container `124285663501` verdi.
- **CI estesa:** run `41123318359`, completata con esito verde per tutti gli 11 job. Qualità `124295253885`; HAProxy Technologies `124297991439`; NGINX multiworker `124297991261`; schema Kubernetes reale `124297991263`; OCI AMD64/QEMU ARM64 `124297991308`; Firefox/WebKit `124297991462`; rootless Podman `124297991557`; Kubernetes single-node `124297991520`; ClamAV reale `124295253787`; container `124297991450`; pubblicazione opt-in `124298997000`.
- **Nuovo credito RC:** il gate `B4-HAProxyTECH-KIND` (peso 1, accepted) viene scorporato dal precedente B4 parziale (peso 2 → 1). Stato ufficiale **81,25%**, **36 gate accettati e 17 parziali** su 53. Nessun doppio credito per i gate NGINX, OCI, Firefox/WebKit e altri già riconciliati.

### Perimetro dimostrato per HAProxy

Due worker KIND con scheduling separato, PostgreSQL 18, condivisione degli asset mediante *bind temporaneo del runner*, controller HAProxy Technologies reale, instradamento HTTP con host corretto, rifiuto host diverso, entrambe le origini API e disponibilità dopo sostituzione di un pod. **Non** è una prova di CSI/NFS RWX reale, nodi fisici distinti, TLS pubblico, cluster geografici, carico sostenuto o SLO di produzione. Non abilitare la release candidate strict per questi risultati.

## Nuovo strumento operativo RWX (non ancora eseguito su cluster reale)

`tools/k8s_rwx_cross_node_probe.py` è un controllo Kubernetes **esplicito** e fail-closed, distinto dalla simulazione KIND su bind temporaneo. Legge Deployment, pod, PVC e PV mediante `kubectl` usando il contesto atteso, rifiuta hostPath/local, RWO, volumi non Bound, mount read-only/subPath, repliche non pronte o sullo stesso nodo. Non legge Secret, credenziali o contenuti degli asset.

Preflight esclusivamente read-only (comando illustrativo; adattare ai veri nomi del cluster):

```sh
python3 tools/k8s_rwx_cross_node_probe.py --context NOME_CONTESTO \
  --namespace quorivio --deployment quorivio --mount-path /app/assets
```

Soltanto previa approvazione dell'operatore e su un ambiente amministrato con possibilità di scrittura, prova bidirezionale di piccoli file casuali **dentro una directory univoca dedicata**, con sync e pulizia tentata in entrambi i pod:

```sh
python3 tools/k8s_rwx_cross_node_probe.py --context NOME_CONTESTO \
  --namespace quorivio --deployment quorivio --mount-path /app/assets --confirm-write
```

L'esito `API_CONTRACT_ONLY_NO_IO` non è una prova dati; soltanto `CROSS_NODE_RW_EXCHANGE_PASS` indica l'effettivo scambio A→B e B→A. Il test potrebbe lasciare una piccola directory `.quorivio-rwx-probe-*` se entrambi i pod diventano indisponibili durante il cleanup: in tal caso richiedere verifica manuale del solo percorso di test prima di riprovare. Non eseguito sul cluster dell'utente in questo ciclo.

**Limiti ancora aperti:** RWX/CSI reale tra macchine fisiche indipendenti, volume persistente dopo perdita di nodo e storage, recupero sotto partizione, TLS con certificato pubblico, carico 500 utenti prolungato, accettazione con dispositivi reali, valutazioni indipendenti WCAG/AGID, GDPR e sicurezza. Il nuovo script prepara una prova operativa; **non aggiunge punti RC finché non è eseguito e verificato su un ambiente esterno idoneo**.
