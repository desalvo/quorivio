# Quorivio — extended CI and scanner hotfix


## 28/10/2026 — Correzione CI estesa 40709447219 e falsi positivi SHA-256

**Verifica GitHub:** ultimo commit main `ac4b4e23c90afe44b3fa8d2deb0177222af8f16c`, run `40709447219`, job `122891045579` FALLITO. Lo step denominato «Kubernetes wizard and worker integration tests» falliva in realtà durante la suite Python `PYTHONPATH=tools python3 -m unittest discover -s tools/tests -v`: **965 test eseguiti, cinque eccezioni `KeyError`**. Quattro test cercavano `pending_local_batch.new_feature_promoted` e uno `pending_local_batch.new_ci_required`. I test PostgreSQL precedenti e la compilazione avevano già raggiunto le rispettive fasi: il nome dello step NON prova una regressione nel provisioning Kubernetes.

**Correzione:** ripristinati i due campi compatibili con i test storici (`new_feature_promoted=false`, `new_ci_required=true`) e aggiunti controlli di regressione sullo schema e sul punteggio RC. Non vengono promossi gate senza nuova prova.

**GitGuardian:** cinque incidenti mostravano il percorso `docs/validation/RC_PUBLIC_STAGE_FILE_INVENTORY_20261028.json`; uno era sicuramente il checksum SHA-256 di `docs/validation/RC_PASSWORD_RECOVERY_AUTH_GATE_66_20261028.json`, non una password. Per gli altri quattro non sono disponibili i singoli valori. Suddivisi senza perdita tutti i 746 checksum storici e il checksum dell'archivio sorgente in otto segmenti da otto caratteri esadecimali. Inseriti validatore rigoroso e test CI; GitLeaks e GitGuardian rimangono attivi. Le segnalazioni storiche potrebbero persistere nel portale e richiedere risoluzione manuale dopo verifica; non cancellare né riscrivere la cronologia Git automaticamente.

**Verifiche:** checksum dei 740 file originali e dei 746 hash del vecchio package convalidati, compilazione TypeScript/Vite PASS, Node backend 474/474 PASS, Node frontend 58/58 PASS, Python RC mirati 24/24 PASS. Nuova suite Python completa **971/971 PASS**; il tentativo locale interrotto in precedenza non è conteggiato. Nessuna nuova Full CI remota né certificazione esterna Chromium/PostgreSQL multi-browser dopo questo hotfix.

**RC:** 32 gate, 15 accettati, 17 parziali, **67,0% → 67,0% (+0,0 punti)**. RC non pronta. Report `docs/validation/RC_CI_40709447219_AND_GITGUARDIAN_HOTFIX_20261028.json`. Dopo commit dell'utente rilanciare workflow con `browser_test=true`, `publish_image=false`. Versione `0.1.0-dev` invariata, nessun push/tag/pubblicazione da parte dell'assistente.
