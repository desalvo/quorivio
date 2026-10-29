# Quorivio 0.1.0-dev — ciclo RC 10: 74,0% (+3,0 punti), 29 ottobre 2026

**Baseline:** archivio cumulativo ciclo 9, RC 71,0%; conservati i 768 file originali. Nessun commit, tag, push o pubblicazione Docker eseguiti dall'assistente.

## Riconciliazione delle evidenze verificate

La Full CI GitHub [40717525524](https://github.com/desalvo/quorivio/actions/runs/40717525524), tentativo 2, commit `f6738592c648bc620e01b92d2bbaa6b90b459287`, job qualità `123073117101` aveva già superato quattro verifiche automatizzate indipendenti ancora incluse in gate parziali:

- **A1-EDITOR-INTERACTION** (peso 2): controlli dell'editor Chromium, canvas, pointer e tastiera. A1 resta parziale (4): approvazione indipendente, più browser e dispositivi. Non duplica A3-AUTO (WYSIWYG/persistenza) né A2-ORDER (miniature).
- **A3-GEOMETRY** (peso 2): geometria 16:9 coerente tra editor, anteprima e pubblico a 1440/390 px, lettura accessibile. A3 resta parziale (2): fedeltà pixel con corpus, Office, Firefox/WebKit, dispositivi. Non duplica i contratti di autosave o focus.
- **D3-K8S-GENERATOR** (peso 1): wizard/worker Kubernetes e generazione persistente di segreti distinti in CI. D3 resta parziale (1): ARM64 nativo, Podman rootless, Ingress/ClamAV/RWX reali. Distinto dalla compilazione immagini D3-IMAGE.
- **D4-CONVERTER-BOUNDARY** (peso 1): regressioni reali di conversione, input malevoli e pubblicazione atomica. D4 resta parziale (2): pentest indipendente e revisione delle minacce. Distinto dagli scanner generici di D4-SCAN.

Peso complessivo invariato: 100. **71,0 → 74,0%**, gate **36 → 40**, accettati **19 → 23**, parziali **17** invariati. Le verifiche automatiche non sono accettazioni esterne o operative; la RC rigorosa è ancora bloccata.

## Nuove correzioni funzionali, soltanto locali

Il recupero password dispone di un vero form HTML accessibile con invio anche mediante **Invio** da tastiera; restano conferma password, deduplicazione POST e ritentativo. Nell'anteprima, quando un portale viene spostato dentro il dialogo, `inert` e `aria-hidden` tornano allo stato precedente; se torna all'esterno viene nuovamente isolato. Test Chromium desktop 1440 e mobile 390 per entrambi i flussi.

**Test locali:** build TypeScript backend/frontend e Vite PASS; 474/474 Node backend, 62/62 Node frontend, 984/984 Python; Chromium form recupero, focus e portali a 1440/390 PASS. Nuova CI GitHub **non eseguita** sul codice non committato; SMTP/PostgreSQL reali, Firefox/WebKit, tecnologie assistive, dispositivi fisici, infrastruttura reale e verifiche indipendenti restano in sospeso.

**Prossimo passo:** commit dell'utente e CI estesa manuale con `browser_test=true`, `capacity_test=true`, `publish_image=false`, `publish_latest=false`. Nessuna RC pronta finché rimangono gate parziali.

**Evidenze:** `docs/RC_GATE_MATRIX.json`, `docs/validation/RC_CYCLE10_VERIFIED_GATE_RECONCILIATION_20261029.json`, inventario SHA-256 raggruppato.
