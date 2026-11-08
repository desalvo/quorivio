# RC260 — Riconciliazione manifest Kubernetes `generated`

La RC260 estende il wizard **standalone** (`python3 k8s_wizard.py --version` → `0.1.0-dev-rc260`) in modo che il Deployment Kubernetes aggiornato con il converter PDF/PPTX non divergano più dai manifest Kustomize originali. **Nessuna operazione sul cluster è stata effettuata da ChatGPT.**

## Procedura per un converter già installato

Dal nodo con `kubectl` configurato, nella directory del wizard:

```bash
python3 k8s_wizard.py --version
python3 k8s_wizard.py --sync-generated --generated-dir ./generated \
  --set namespace=quorivio --set name=quorivio
kubectl kustomize ./generated > /dev/null
```

`--sync-generated` è una **sincronizzazione locale**: legge Deployment e Secret dal cluster e aggiorna esclusivamente la directory dei manifest; non modifica Kubernetes. Se i manifest originari sono in `./k8s-generated`, usare quel percorso. Il wizard può anche rilevare univocamente `generated`/`k8s-generated` nella directory corrente o accanto allo script; percorsi ambigui devono essere esplicitati.

## Procedura nuova installazione del converter

```bash
python3 k8s_wizard.py --ensure-converter-token --generated-dir ./generated \
  --set namespace=quorivio --set name=quorivio
python3 k8s_wizard.py --upgrade-converter --generated-dir ./generated \
  --set namespace=quorivio --set name=quorivio \
  --converter-image desalvo/quorivio-converter:latest \
  --output ./converter-upgrade-rc260
# Leggere converter-plan.json e converter-patch.json; dry-run server kubectl.
python3 k8s_wizard.py --apply-converter --output ./converter-upgrade-rc260
kubectl kustomize ./generated > /dev/null
```

**Integrazione Kustomize:** `95-converter-sidecar-patch.json` è una strategic merge patch che preserva le altre proprietà del Deployment; `kustomization.yaml` la include con `patches`; `05-app-secret.yaml` mantiene le credenziali iniziali e aggiunge il solo `QUORIVIO_WORKER_TOKEN` identico a Kubernetes. Il token è segreto; non è mai scritto nei log o nel piano di upgrade. Il manifest Secret locale è in modalità `0600`, così come il backup privato nella directory `generated/.quorivio-manifest-backups/`. Conservare e proteggere questa directory, **non committarla in Git**.

**Sicurezza:** il wizard verifica l'identità del namespace/Deployment/Secret, confronta le credenziali locali con i dati live prima della modifica, lega il piano ai checksum dei manifest e interrompe l'upgrade se i file sono cambiati. Il comando `--apply-converter` interviene sul cluster solo dopo dry-run server e applica la patch; aggiorna `generated` **dopo** la riuscita del rollout. In caso di interruzione tra l'upgrade live e la sincronizzazione locale, eseguire `--sync-generated` dopo aver verificato il deployment. Per `--sync-generated` un converter deve già essere presente e validabile nel Deployment. Non sono alterati PostgreSQL, PVC, Ingress o Service.

**Regenerazione:** la generazione successiva nella stessa directory conserva l'overlay del converter e il worker token; per tutte le altre differenze tra file locali e risorse Kubernetes non è implementata una riconciliazione completa. Evitare `kubectl apply -k` prima della verifica del diff, specialmente su Secret e database modificati manualmente. Se le credenziali locali divergono dal cluster, il wizard fallisce in modo sicuro e richiede intervento esplicito.

**Validazione:** test senza cluster reale su file singolo, simulatore `kubectl`, rollout, fallback rigenerazione, drift Secret, symlink, file modificati tra piano e apply, backup, identificazione dei target e path ambigui. Full CI RC260 da eseguire dopo il commit. Avanzamento complessivo 85,25% (43 accettati, 17 parziali).
