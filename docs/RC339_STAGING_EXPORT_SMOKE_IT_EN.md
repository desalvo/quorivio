# RC339 — Collaudo dei quattro export PDF/PPTX (staging)

## Italiano

La full CI del commit 4c3c63bc5749 è terminata con successo (run 43535065013), inclusi production quality gate, build OCI AMD64/ARM64 e pubblicazione Docker multiarchitettura abbinata di app e converter. Questo non certifica da solo il funzionamento dei download su un deployment reale.

Lo script tools/ci_visual_export_smoke.py esegue, in maniera esplicita e senza salvare file, un test su staging con converter attivo. Verifica che una richiesta anonima riceva HTTP 401, poi esegue login come presentatore di prova e scarica in memoria PDF e PPTX per le viste presentatore e partecipante. Controlla tipo MIME, Content-Disposition UTF-8 e suffissi dei nomi, limiti di 50 MiB, firma e terminatore PDF, struttura delle slide PowerPoint e presenza di un'immagine acquisita in ciascuna diapositiva.

Esempio di esecuzione con un account di staging temporaneo già inizializzato, senza MFA, e una sessione con almeno una pagina esportabile:

    export QUORIVIO_EXPORT_SMOKE_URL=https://staging.example.org
    export QUORIVIO_EXPORT_SMOKE_SESSION_ID='uuid-della-sessione-di-test'
    export QUORIVIO_EXPORT_SMOKE_EMAIL='presenter@example.org'
    read -rs QUORIVIO_EXPORT_SMOKE_PASSWORD; export QUORIVIO_EXPORT_SMOKE_PASSWORD; echo
    python3 tools/ci_visual_export_smoke.py
    unset QUORIVIO_EXPORT_SMOKE_PASSWORD

Non vengono salvati documenti o cookie e lo script non stampa credenziali, ID di sessione o contenuti scaricati. Sono bloccati reindirizzamenti HTTP e connessioni HTTP non localhost. La validazione funziona con la libreria standard Python. Quattro regressioni offline sono integrate nella suite tools/tests e sono state eseguite localmente.

**Limiti:** questa verifica certifica solo trasporto e struttura dei documenti, non la fedeltà pixel-per-pixel, video, animazioni o interattività. Ripetere il test anche su sessioni con pagine presenter/participant differenti, widget Reazioni, gauge e risultati; effettuare il confronto visivo manuale. Stato di accettazione esterna invariato a 85,25%, 43 gate accettati e 17 parziali.

## English

Main commit 4c3c63bc5749 passed full CI run 43535065013, native AMD64/ARM64 OCI builds and paired app/converter Docker Hub publication. Real deployment acceptance remains separate. The optional tools/ci_visual_export_smoke.py verifies anonymous HTTP 401 and all four authenticated PDF/PPTX presenter/participant exports against a staging origin. It validates MIME, UTF-8 attachment filename, 50 MiB size limit, PDF header/trailer and picture-backed OOXML slides, without persisting documents or cookies or disclosing secrets.

Use the four QUORIVIO_EXPORT_SMOKE_* environment variables in the example above with a disposable non-MFA test presenter. HTTPS is mandatory except for localhost; redirects are forbidden. The smoke test is not a visual pixel comparison or production GDPR/RC signoff. Completion remains 85.25% pending independent acceptance.
