# RC340 — Export PDF/PPTX: SQL PostgreSQL e gestione del 502

## Italiano

**Difetto confermato:** nella versione precedente la funzione di esportazione selezionava `page_ratings.widget_id`, colonna assente nello schema PostgreSQL (i voti hanno soltanto `session_id`, `activity_id`, `participant_id` e `score`). Questa query veniva eseguita sempre, anche quando non esistevano valutazioni. La correzione raggruppa per pagina e punteggio e associa i conteggi ai widget `rating` realmente presenti nella pagina, senza trasferire alcun voto o identificativo individuale. Non sono necessarie modifiche allo schema.

Il nuovo test Node verifica mapping, pagine, conteggi non validi, vincolo massimo e SQL. Un gate CI obbligatorio esegue **la stessa query** contro il database PostgreSQL 18 di test. Non basta una verifica statica del codice.

**Seconda protezione:** un'eccezione imprevista (anche proveniente da Playwright/Chromium) non deve più far terminare senza risposta la richiesta HTTP del converter. Il worker deve restituire una risposta JSON 422 `conversion_failed`, che il server può trasformare nel previsto errore HTTP 502 JSON senza esporre token, cookie o documenti. È previsto un test HTTP con errore simulato.

**Limiti della diagnosi:** l'errore 502 segnalato su `quorivio.apps.desalvo.eu` potrebbe essere prodotto direttamente da ingress, reverse proxy, timeout, OOMKill o immagini app/converter non aggiornate. Il difetto SQL è provato dal codice, ma il server in esecuzione non è accessibile per esaminare i log da questa sessione. Non si deve dichiarare il problema di produzione chiuso senza un test di download reale.

Dopo il superamento della CI e la pubblicazione di entrambe le immagini con lo **stesso SHA**, verificare in Kubernetes:

    kubectl -n <namespace> get pods -o wide
    kubectl -n <namespace> describe pod <nome-pod>
    kubectl -n <namespace> logs <nome-pod> -c quorivio --since=20m
    kubectl -n <namespace> logs <nome-pod> -c converter --since=20m

Oppure, con Docker Compose: `docker compose ps` e `docker compose logs --since=20m app converter`. Controllare anche i log dell'ingress durante l'export. Non pubblicare token, cookie, URL QR contenenti segreti, password o dati dei partecipanti.

Il test RC339 con account di staging è un controllo opt-in e non è stato eseguito sul deployment reale. Stato RC indipendente invariato: **85,25%** (43 gate accettati, 17 parziali).

## English

The PDF/PPTX visual export unconditionally queried nonexistent PostgreSQL column `page_ratings.widget_id`. RC340 executes a page/score aggregate against the actual schema, mapping only sanitized totals to authored rating widgets. A required PostgreSQL CI gate runs the same SQL, and HTTP worker regressions ensure unexpected Playwright failures produce a sanitized 422 rather than a broken upstream connection. The external 502 may still originate from the ingress or converter and must be corroborated with deployment logs. Test four presenter/participant exports using a matching pair of app and converter images before declaring production resolution. External release readiness remains 85.25%.
