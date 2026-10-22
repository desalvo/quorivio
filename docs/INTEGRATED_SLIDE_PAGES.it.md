# Pagine slide integrate — Quorivio 0.1.0-dev

Le immagini PNG, JPEG e WebP dei presentatori possono ora diventare pagine slide nella sequenza di una sessione. La procedura via browser consente la selezione multipla (fino a 100 file) e crea una pagina per ciascuna immagine nell’ordine fornito dal browser. Per garantire l’ordine rinominare i file `page-0001.png`, `page-0002.png`, ecc.

## PDF e PPTX

Prima convertire il documento con `python3 tools/import_presentation.py presentazione.pdf /tmp/pages`, poi caricare le immagini generate dal workspace presentatore. La conversione automatica dentro il container web non è ancora disponibile. I documenti vanno convertiti in un worker isolato quando sarà completata la macroarea.

## Sicurezza

La creazione di pagine richiede autorizzazione come presentatore sulla sessione e risorse immagine non appartenenti a partecipanti anonimi. L'immagine slide pubblica è accessibile soltanto mentre quella pagina è la corrente di una sessione attiva e non scaduta. Non vengono pubblicate risposte, credenziali o allegati privati.

## Limiti e verifica

Sono necessari test browser e migrazione PostgreSQL reale. Le slide non richiedono una risposta e non alterano le risposte dei quiz. Video, animazioni PowerPoint e transizioni non sono preservati. Conversione non sandboxed del tool offline: eseguire fuori dal server su file affidabili o in container isolato.
