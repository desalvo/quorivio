# RC293 — Manuali visuali compatti e brochure IT/EN

Data editoriale: **10 novembre 2026**. Intervento **esclusivamente documentale**: nessuna modifica al runtime dell'applicazione e nessun aumento dichiarato del completamento funzionale (baseline **85,25%**).

## Manuali rinnovati

- Rimossa la forzatura di una pagina nuova per ogni titolo di capitolo: le sezioni scorrono normalmente, con separatori e impaginazione compatta.
- Inserito un atlante bilingue di **20 icone della toolbar reale**, ricavato dalle catture autentiche RC291, con spiegazioni concrete di proprietà, formattazione, schemi, anteprime e risultato R.
- Aggiunti percorsi visivi specifici per amministratore (impostazioni server, backup, audit, ruoli) e partecipante (QR, domanda, invio, feedback smartphone).
- In ogni pagina è presente un piccolo inserto fotografico; gli spazi finali significativi vengono utilizzati per schede operative con schermate autentiche d'archivio e fotografie **sintetiche esplicitamente dichiarate**.
- Le schermate archiviate restano attribuite all'RC di origine; **nessuna stringa di commit viene stampata**. La raccolta generata dalla CI per il commit corrente resta verificata separatamente tramite manifest, SHA-256 e `--require-real`.
- I sei PDF, nelle due posizioni pubblicate, sono generati dagli stessi sorgenti e devono essere identici.

## Due brochure pubblicitarie

`docs/brochures/quorivio-brochure-it.pdf` e `docs/brochures/quorivio-brochure-en.pdf`, **due pagine A4 ciascuna**, offrono grafica editoriale, fotografie sintetiche riconoscibili, screenshot autentici archiviati, descrizione delle funzioni, deployment, `.quo`, autore, email, logo ufficiale, EUPL-1.2, repository e requisiti hardware indicativi. Testo PDF selezionabile; immagini editoriali mantenute nei sorgenti.

## Rigenerazione riproducibile

```bash
python3 tools/manual_icon_atlas.py
python3 tools/generate_manuals.py
python3 tools/generate_brochures.py
python3 -m unittest tools.tests.test_rc293_visual_manuals_brochures -q
```

La generazione richiede le dipendenze editoriali Python (Mistune 3, WeasyPrint, Pillow, PyMuPDF, ReportLab, CairoSVG) solo sul computer di authoring; la CI applicativa usa gli artefatti versionati e non li rigenera implicitamente. Prima della pubblicazione ispezionare i PDF visivamente, verificare i limiti delle istanze e far revisionare almeno un flusso reale da personale tecnico.
