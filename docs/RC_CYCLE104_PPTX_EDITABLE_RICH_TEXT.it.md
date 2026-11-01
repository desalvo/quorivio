# RC104 — Testo formattato modificabile in PowerPoint

**Ambito:** esportazione PPTX e importazione PPTX nel modello Quorivio 0.1.0-dev, senza incremento del punteggio RC finché non sono eseguiti i gate GitHub.

## Cosa è stato completato

- Formattazione di intervalli selezionati nei widget **Testo**, **Post-it**, **Titolo**, **Footer**, **Domanda** e nelle opzioni top-level dei quiz: famiglia di caratteri consentita, dimensione, grassetto, corsivo, sottolineato, barrato e colore RGB.
- Le proprietà esplicite di una porzione prevalgono sullo stile generale del widget, inclusa la disattivazione del grassetto nel titolo normalmente grassetto. Le altre porzioni restano inalterate.
- Intervalli identificati dai medesimi campi (`label`, `description`, `option:<id>`) della proiezione React. Importazione di PPTX con run diversi in `textMarks` sul campo `description`, affinché l'editor possa modificarli.
- Rispetto dei ritorni a capo e della separazione delle opzioni. Il testo in PowerPoint rimane selezionabile/modificabile: non è rasterizzato.
- Offset da JavaScript/DOM in UTF-16 convertiti senza spezzare caratteri Unicode non-BMP (emoji). Convalida `textMarks` a livello del worker indipendente dal backend; massimo 64 intervalli e lunghezza 500 unità UTF-16 per intervallo. Rifiuto di CSS, HTML, font, colori e valori fuori specifica.
- I widget QRCode esportati in RC103 continuano a funzionare con immagine scansionabile e URL modificabile/cliccabile.

## Verifiche di accettazione

Eseguire `python3 -m unittest tools.tests.test_rc104_pptx_inline_text_roundtrip -v` dopo avere installato `python-pptx`. La CI standard esegue questo comando dopo l'installazione delle dipendenze e ripete la suite Python completa; non spostarlo nel preflight precedente a pip.

Controllare anche in Microsoft PowerPoint o LibreOffice: (1) testo con formattazione mista, (2) secondo clic su Bold in un titolo (solo caratteri selezionati), (3) Footer ereditato, (4) opzioni con stili distinti, (5) importazione/edit/nuova esportazione. Il test automatizzato conferma la struttura OOXML e i run ma non l'equivalenza visiva pixel-per-pixel tra editor e Office.

## Limiti espliciti

Non sono certificati gli effetti tipografici specifici di Office, lo stile con font esterni non ammessi, i campi multipli `questions` nidificati nel PPTX, le animazioni né le interazioni live (il PPTX è statico). Le opzioni di risposta rimangono testo statico; non diventano elementi interattivi PowerPoint. L'importazione converte i testi supportati in `text`/`postit`, non ricostruisce i ruoli logici di Titolo/Footer. Rimangono necessari corpus PowerPoint di terze parti e verifica visuale indipendente del gate D4. Nessuna pubblicazione automatica Docker Hub e nessun commit eseguiti da questa revisione.
