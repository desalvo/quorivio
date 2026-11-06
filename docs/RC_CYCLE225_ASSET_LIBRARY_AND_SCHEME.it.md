# RC225 — Allegati, nomi dei file e selettori visivi degli sfondi

## Modifiche effettive

- Il caricamento di allegati e sfondi memorizza il nome originale come metadato `display_name`, mentre i file fisici mantengono UUID opachi. I nomi vengono normalizzati, limitati a 120 caratteri e non utilizzati nei percorsi del filesystem.
- Duplicati confrontati senza distinzione maiuscole/minuscole: la API risponde `409 duplicate_filename` e propone `file (2).ext`, poi `file (3).ext`. Il frontend ripete il caricamento con suffisso numerico **solo dopo conferma esplicita**. Vincoli univoci DB prevengono sovrascritture concorrenti.
- Gli allegati della sessione espongono Rinomina/Elimina. La rinomina è validata lato server. La cancellazione gestisce correttamente `HTTP 204 No Content`, aggiorna subito l'elenco e ricarica la lista per riconciliare lo stato.
- La libreria degli sfondi supporta rinomina e cancellazione con conferma e controllo delle immagini in uso; anche le immagini prese in prestito dai collaboratori hanno nomi distinguibili.
- I selettori di sfondi nel canvas, nella pagina, nei risultati, nello smartphone e negli schemi mostrano **miniature e nomi sotto le immagini**, selezionabili con tastiera e touch; elenco scorrevole su schermi piccoli.
- Corretto il CSS dell'editor degli schemi affinché mostri lo sfondo globale già prima del salvataggio. Lo sfondo continua a essere propagato alle pagine al salvataggio dello schema.
- Le copie dello sfondo in sessione mantengono i propri metadati anche dopo rimozione della libreria. Lo schema migra eventuali vecchie etichette duplicate. L'archivio `.quorivio` conserva il nome delle risorse referenziate; resta compatibile con gli archivi senza nomi.
- Per gli allegati caricati dai partecipanti viene conservato il filename sanificato, senza includerli nel vincolo di unicità degli allegati dei presentatori.

## Verifiche e limiti

- API Node 628/628, frontend Node 390/390, unit test Python RC225 7/7, Chromium CSS reale a 320×240, 390×844 e 1440×900 superati.
- Implementati controlli CI anticipati prima di npm e Chromium nel gate browser.
- Da verificare in GitHub: test TypeScript completo, PostgreSQL reale, browser React compilato, Kubernetes e intera campagna CI. Nessuna full CI RC225 dichiarata verde.
- Baseline ultima full CI verde: RC219, run `42197607753`. Completamento certificato invariato: **85,25%**, 43 accettati e 17 parziali. Versione 0.1.0-dev; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
- Nessun commit/push/tag; il pacchetto cumulativo include l'inventario SHA-256 e le ricevute storiche immutate.
