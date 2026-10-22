# Importazione di presentazioni PDF e PowerPoint — IT

Versione applicazione: 0.1.0-dev. Build documentale: dev-20261022.

## Funzione introdotta

Il comando **offline** `tools/import_presentation.py` accetta PDF e PowerPoint `.pptx`, ne controlla firma e dimensione (massimo 100 MiB), limita a 200 le pagine e converte ogni pagina in un PNG di massimo 1600 pixel sul lato lungo. Registra numero delle pagine, checksum del sorgente e checksum di ogni PNG in `manifest.json`. Richiede `pdfinfo`, `pdftoppm` e, per PPTX, `libreoffice`.

```bash
python3 tools/import_presentation.py /secure/slides.pdf /secure/output-slides
python3 tools/import_presentation.py /secure/slides.pptx /secure/output-pptx
```

Il percorso di destinazione deve essere **inesistente** per evitare sovrascritture. La conversione in produzione deve essere eseguita in un container/worker separato, senza accesso alla rete, con utente non privilegiato, sandbox, quote CPU/RAM, filesystem limitato e gestione di cancellazione GDPR. **Queste misure sono da implementare nel runtime integrato**: lo script da solo non è un servizio di upload sicuro.

## Limiti attuali

Non esistono ancora endpoint o UI per associare il manifest a una sessione: le immagini vengono preparate solo per il successivo import. Il rendering appiattisce slide e perde animazioni, transizioni, audio e video incorporati. I font mancanti e la conversione PPTX possono modificare l'aspetto. Il formato PowerPoint legacy `.ppt` non è supportato. L'import PDF/PPTX nella sessione, con pagine modificabili e anteprime browser, resta aperto.

## Collaudo e sicurezza

Sono disponibili test locali per rilevare formati falsi, contenuti non consentiti e conversione di un PDF di esempio. Non sono stati eseguiti collaudi di cluster, browser o database. I checksum di `manifest.json` attestano integrità del risultato, non sicurezza degli allegati.
