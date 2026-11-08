# RC257 — Correzione CI RC193 e aggiornamento converter Kubernetes esistente

**Baseline:** RC256 commit `9023bff41adf05863b7c2c508f836b012c3e2416`, full CI [42479602496](https://github.com/desalvo/quorivio/actions/runs/42479602496) fallita al job *Production quality gate*, step 128 “RC193 editor focus ownership and font controls before npm”. Il test `test_rc193_focus_and_font.py` cercava la vecchia espressione `style?.fontFamily||'Arial'` che accettava il font letterale `undefined`; ora obbliga `safeWidgetFontFamily(...)` nei controlli opzioni e pulsante invio. Conservati i test sul focus e la selezione dei font. Nuovo controllo anticipato RC257 che esamina le asserzioni storiche e lancia RC193 e i test runtime Node RC254 prima dei gate successivi. Il codice applicativo è **identico a RC256**.

## Aggiungere il converter PDF/PPTX a un cluster già installato

Comandi dalla radice repository con `kubectl` e il contesto del cluster già selezionato. **Richiedono i permessi di lettura Deployment/Secret e patch del Secret e Deployment.** La procedura modifica soltanto il Secret del token e il pod template del Deployment, non PostgreSQL, ingress, PVC, cert-manager o le altre risorse. Il converter viene aggiunto come **sidecar** (container `converter` accanto all'API), non come nuovo Deployment/Service.

```bash
kubectl config current-context
kubectl -n quorivio get deployment quorivio
python3 tools/k8s_wizard.py --ensure-converter-token --set namespace=quorivio --set name=quorivio
python3 tools/k8s_wizard.py --upgrade-converter --set namespace=quorivio --set name=quorivio \
  --converter-image 'desalvo/quorivio-converter@sha256:95223a548ca5e813199216e80ce565c6a203c6b6105c8655e8d62048e94d74f7' \
  --output ./converter-upgrade-rc257
```

L'immagine specificata è il digest multiarch verificato nel workflow [42417918195](https://github.com/desalvo/quorivio/actions/runs/42417918195). È possibile usare `desalvo/quorivio-converter:latest`, ma il digest evita sorprese dovute a tag mutabili e alla policy `IfNotPresent`. Se il cluster non può scaricare l'immagine, risolvere prima DNS, connettività e ImagePullSecret; non applicare la patch senza un'immagine disponibile.

Prima di modificare il Deployment, leggere `converter-plan.json` e `converter-patch.json` nella directory appena generata, poi:

```bash
kubectl -n quorivio patch deployment quorivio --type=json \
  --patch-file=./converter-upgrade-rc257/converter-patch.json --dry-run=server -o name
python3 tools/k8s_wizard.py --apply-converter --output ./converter-upgrade-rc257
kubectl -n quorivio rollout status deployment/quorivio
kubectl -n quorivio logs deployment/quorivio -c converter --tail=80
```

Il wizard verifica context/UID/resourceVersion e il piano prima di applicare. Se un altro operatore modifica il Deployment, rigenerare in una nuova directory. Se il Deployment è gestito da Helm, l'upgrade può essere rifiutato: non aggirare la protezione. Per nomi personalizzati usare `--converter-deployment`, `--app-container` e `--converter-secret` **in pianificazione**; per l'applicazione sono proibiti override aggiuntivi. Al termine: **Amministratore → Configurazione server → Convertitore PDF/PowerPoint → Verifica stato worker → Abilita importazione PDF/PPTX**, quindi provare importazioni reali e verificare che la sessione non perda dati. Il worker è solo interno al pod su `127.0.0.1:8099`, non esporre il servizio su Ingress.

**Validazione:** test preventivi Python/Node, build e manifesto SHA-256 corrente; full CI GitHub da confermare dopo commit. Completamento **85,25%** (43 accettati/17 parziali), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag dall'assistente.
