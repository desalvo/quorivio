# RC205 — Uniformità widget editor/schemi e importazione presentazioni

## Difetti segnalati e correzioni

1. Il canvas e l'editor schemi condividono la resa del font: Arial, dimensione, tipo, colore, grassetto/corsivo/sottolineato/barrato sono gestiti attraverso un unico gruppo di controlli secondo l'ambito scelto. Sono compresi titolo, scelte, pulsante invio e numerazione del footer. Rimossi i campi tipografici duplicati.
2. Se si ritorna da scelta singola/multipla a testo libero, riappare il campo libero anche se rimangono vecchie opzioni nella configurazione. Le risposte lunghe vanno a capo. Le domande valutate mostrano istruzioni di selezione senza svelare la soluzione.
3. La finestra «Formato widget» del footer è compatta, con scorrimento interno se necessario, e non si estende per tutta la pagina.
4. Il widget risultati in editor recupera il titolo della domanda sorgente da altre pagine con formattazione e dati dimostrativi. La privacy delle viste pubbliche resta separata.
5. Importa PDF/PPTX dal menu miniature crea ora pagine che contengono un widget immagine a pieno canvas (non solo il vecchio campo media). La prima pagina importata viene aperta previa conferma delle modifiche non salvate; errori del convertitore visibili in sidebar. L'export PPTX elimina il raster duplicato.

## Dipendenze e limiti

Per importare occorrono `QUORIVIO_ENABLE_CONVERTER=true`, un worker isolato con URL/token corretti e volume di conversione condiviso. L'API non deve mai eseguire LibreOffice non isolato. Le slide sono immagini raster per garantire fedeltà visiva; sopra di esse si possono aggiungere widget Quorivio editabili, ma testo e forme originali non diventano automaticamente oggetti editabili.

## Verifica

Il controllo preventivo `tools/tests/test_rc205_editor_consistency.py` è eseguito senza dipendenze esterne. Il test reale `tools/tests/test_rc205_native_slide_roundtrip.py` avviene dopo l'installazione di Pillow/python-pptx. Conservate le regressioni RC193/RC194/RC200/RC203/RC204. Passano verifiche mirate e parsing TS/TSX; build Node completa, interazioni Chromium, import PostgreSQL e accettazione Kubernetes sono in attesa di full CI.

**Configurazione di rilascio:** `0.1.0-dev`; `rc_strict=false`, `publish_image=false`, `publish_latest=false`; completamento certificato invariato **85,25%**. Nessun commit/push/tag dell'assistente.
