# RC284 — Hotfix runtime Dockerfile e acquisizione reale dei manuali

## Evidenza GitHub Actions

Run [42624246307](https://github.com/desalvo/quorivio/actions/runs/42624246307), 9 novembre 2026: `Production quality gate`, ClamAV, Firefox/WebKit e Kubernetes manifest schema superati. I job Docker, rootless Podman, OCI e KIND (NGINX/HAProxy/HTTPS) fallivano nell'installazione dei pacchetti di sistema all'interno dell'immagine Node Alpine.

## Causa e correzione

La riga `RUN apk add --no-cache postgresql18-client tar` del Dockerfile di produzione conteneva una sequenza testuale di backslash e `n`, non un vero carattere di continuazione seguito da una nuova riga. La shell passava l'argomento `n` a `apk`, che riportava `n (no such package)`. RC284 sostituisce solo quella sequenza con una vera continuazione Dockerfile e conserva i controlli di riduzione della superficie d'attacco npm e `USER node`.

Quattro test in `tools/tests/test_rc284_container_runtime_build.py`, eseguiti prima di npm, verificano i token shell effettivi, `sh -n`, lo stadio runtime, la conservazione dell'utente non-root e la regressione con caratteri di escape errati.

## Screenshot reali e manuali

La stessa run ha pubblicato `quorivio-live-manuals-0bb89e6ac79ed57493130f06fc5042182a166ed6`, con 13 PNG acquisiti in una vera istanza Chromium/PostgreSQL, relativo manifest SHA-256 e sei PDF IT/EN con prove. Il manifest registra il commit `0bb89e6ac79ed57493130f06fc5042182a166ed6` e fixture soltanto sintetiche. I nuovi PDF RC284 sono rigenerati localmente, ma non dichiarano correnti le immagini di un commit precedente; il passo CI di screenshot aggiornerà le prove al nuovo commit.

## Validazione pendente

Non risultano ancora convalidati i job runtime Docker/KIND/Podman/OCI per RC284: richiedono nuova full CI. Non eseguire tag o release finché falliscono.

## Correzione PDF, integrazione delle immagini e provenienza

L'artefatto CI della RC283 conteneva 13 PNG autentici e sei PDF, ma una verifica del rendering ha mostrato che la galleria era stata convertita in stringhe HTML visibili invece che in immagini. Il generatore utilizza ora HTML controllato dei sorgenti Markdown, figure dimensionate entro la pagina A4 (anche smartphone) e verifica che ogni didascalia abbia un'immagine fisicamente incorporata nello stesso foglio del PDF. I PNG originali e il manifest SHA-256 sono conservati in `docs/assets/manual-evidence-rc283/` e i sei PDF RC284 (214 pagine totali) li illustrano marcandoli come **ARCHIVIO RC283** e mostrando il commit di provenienza. La modalità `--require-real` è rigidamente separata: richiede nuove immagini dal commit `GITHUB_SHA` e rifiuta la galleria storica. Test in `tools/tests/test_rc284_manual_pdf_gallery.py`; esecuzione in CI dopo la generazione dei PDF.
