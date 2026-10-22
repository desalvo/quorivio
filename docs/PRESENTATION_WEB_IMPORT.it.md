# Importazione documenti dal browser

La pagina Allegati del presentatore accetta PDF e PPTX in modo sperimentale. Il server verifica sessione autorizzata e formato, esegue il convertitore Python con limite temporale, controlla manifest e hash di ogni pagina e crea pagine slide in una transazione. In caso di errore rimuove gli asset creati e annulla le operazioni DB. Massimo 100 MiB, massimo 200 pagine.

**Blocco di sicurezza:** QUORIVIO_ENABLE_CONVERTER è disattivato per default. Il subprocess non costituisce isolamento sufficiente per documenti non attendibili: worker sandboxed separato, limiti di memoria/CPU, antivirus, upload streaming e test end-to-end sono ancora requisiti di produzione.
