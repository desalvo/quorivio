# RC300 — Polling dei risultati live robusto e immagini Docker scaricabili

**Base:** RC299 integrata al commit `6f48a9de9f2c`. La versione rimane `0.1.0-dev`.

- Il polling single-flight impedisce richieste HTTP sovrapposte nel presentatore e dati vecchi che sovrascrivono nuovi conteggi.
- Errori di rete temporanei mostrano un avviso senza cancellare i risultati precedentemente autenticati. Un nuovo successo cancella l'avviso; cambiare sorgente elimina i vecchi conteggi e chiudere la pagina ignora le risposte tardive.
- Test Node deterministici per concorrenza, ripristino, annullamento e collegamento React.
- La CI costruisce e scansiona con Trivy le immagini Docker di app e converter. Un commit su main con il marcatore esplicito `[full-ci]` produce anche archivi `docker save` gzip **linux/amd64**, con checksum SHA-256, scaricabili dagli artifact GitHub Actions per sette giorni. Ripristino con `sha256sum -c SHA256SUMS` e `docker load -i <archivio>.tar.gz`. Lo stesso marcatore attiva browser, carico, Kubernetes e OCI native.
- **Nessun push su Docker Hub**, tag o release: serve una pubblicazione autorizzata distinta. Il gate ARM64 nativo non rende multiarch gli archivi scaricabili.

Le verifiche fisiche A4/B3 sull'accessibilità e sui partecipanti sono ancora aperte: punteggio certificato **85,25% (43 accepted / 17 partial)**, `rc_strict=false`, `publish_image=false` e `publish_latest=false`.

**Titolo merge suggerito:** `fix: stabilize live results and archive Docker images [full-ci]`

## Correzione full CI dopo la run 42887563358

La prima esecuzione estesa `[full-ci]` ha trovato una stringa JavaScript a tripli apici con escape Python non valido nello script storico `tools/ci_rc295_results_layout_chromium.py`, non eseguito dalla qualità ordinaria. Rimossi i backslash errati. Ora la CI controlla **tutti** gli script Chromium opt-in prima di npm ed esegue anche il test Chromium reale del layout del tasto R nel gate PR, prima della full CI. È un controllo preventivo, non una dichiarazione di full CI verde. Necessaria una nuova run su main; nessuna immagine pubblicata su Docker Hub.
