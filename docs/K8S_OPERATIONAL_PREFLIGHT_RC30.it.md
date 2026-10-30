# Quorivio 0.1.0-dev RC ciclo 30 — preflight operativo Kubernetes (30 ottobre 2026)

Questa revisione introduce **un controllo non distruttivo del cluster reale**. A differenza della generazione di manifest o del collaudo KIND locale, `tools/k8s_operational_gate.py` interroga oggetti correnti tramite `kubectl get` e fallisce se non rileva disponibilità e separazione effettive.

## Verifiche

1. Deployment: almeno due pod Ready e Available, controller aggiornato, rolling update con `maxUnavailable=0`, due nodi distinti, scheduling rigido per hostname e almeno 30 secondi di termination grace.
2. PodDisruptionBudget operativo: selettore corrispondente ai pod, disponibilità e possibilità di almeno una eviction volontaria.
3. Volumi: claim Bound RWX associato al Deployment e PV consistente. `hostPath` e `local` sono **rifiutati anche quando dichiarano RWX**; il controllo supporta identificazione di CSI, NFS e CephFS, ma non prova la durabilità o l'effettiva qualità dello storage.
4. Ingress: nome host, classe, servizio, route `/` e TLS se esplicitamente richiesto. EndpointSlice devono esporre endpoint Ready su almeno due nodi.
5. Sonda esterna opzionale HTTPS (validazione certificato e hostname standard) o HTTP, risposta 200 non vuota da `/api/health/ready`; i redirect non valgono come successo.

**Esempio con il wizard:**

```sh
python3 tools/k8s_wizard.py --unattended --output ./k8s-private \
  --set replicas=2 --set asset_access_mode=ReadWriteMany \
  --set enforce_node_diversity=true --set asset_storage_class=YOUR_REAL_RWX_CLASS
# Dopo il deploy da parte dell'operatore sul cluster corretto:
python3 tools/k8s_operational_gate.py \
  --context YOUR_KUBE_CONTEXT --namespace quorivio --app quorivio \
  --service quorivio --ingress quorivio \
  --pdb quorivio-availability --host quorivio.example.org \
  --ingress-class nginx --replicas 2 --require-tls --probe-external
```

**Esempio Helm:** per release `myrelease`, usare `--app myrelease-quorivio --service myrelease-quorivio --ingress myrelease-quorivio --pdb myrelease-quorivio-availability`. I valori Helm sono indipendenti dal wizard; verificare un vero PVC RWX e una credenziale PostgreSQL gestita esternamente.

Il comando non esegue `apply`, `delete`, `drain`, `exec`, non legge Secret e non raccoglie log di pod. Per un cluster interno senza DNS pubblico omettere `--probe-external` e ripetere la verifica dalla rete corretta. Usare `--output /path/nuova-ricevuta.json` per una ricevuta sanificata **mai sovrascritta**. La ricevuta indica `API_CONTRACT_PASS`: non una certificazione di HA o sicurezza.

## Limiti e lavoro residuo

- PostgreSQL interno come singolo StatefulSet resta un **single point of failure**: la disponibilità della sola API non certifica HA end-to-end.
- Nessun failover CSI/NFS reale, nessuna misura RPO/RTO, nessun test di carico prolungato, nessun guasto di rete/di zona, nessuna verifica indipendente di ClamAV, HAProxy, AGID/GDPR o accessibilità.
- Il job KIND multi-nodo aggiunto nel ciclo 29 deve ancora passare su GitHub e il suo bind mount non sostituisce lo storage reale. Il nodo control-plane KIND è ora etichettato per il controller Ingress NGINX e il wizard CLI interpreta correttamente `--set enforce_node_diversity=true`.
- In Helm è ora disabilitato il montaggio automatico dei token ServiceAccount per i pod applicativi.

**Score ufficiale: 79,25%, invariato; 31 gate accettati, 17 parziali.** Non si aggiungono punti per codice non collaudato e valutazioni indipendenti mancanti. Non eseguire `rc_strict=true` e non pubblicare immagini senza accettazione completa.
