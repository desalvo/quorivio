# RC333 — Brochure Quorivio rieditate secondo il mock a sei pannelli

**Data:** 13 novembre 2026. **Ambito:** solo grafica editoriale, PDF e documentazione; nessuna modifica al runtime e nessuna nuova certificazione CI o Docker.

Il mock fornito dall'utente è ora la sorgente di riferimento versionata in `docs/assets/brochure-editorial/mock-reference-6-pages-2026-11.jpg`.
Le brochure `docs/brochures/quorivio-brochure-{it,en}.pdf` sono **sei pagine A4 verticali a tutta pagina**, con testo PDF vettoriale selezionabile. Le copie per l'app sono in `apps/web/public/docs/brochures/` e devono essere identiche.

**Le sei pagine** seguono il mock: (1) presentazioni interattive, (2) flusso sessione e partecipazione, (3) widget/grafici, (4) percentuale di risposte e gauge, (5) eventi in presenza/remoto/ibrido, (6) esportazione/condivisione/supporto.

**Riproduzione:** `python3 tools/generate_brochures.py && python3 tools/verify_portrait_brochures.py docs/brochures`. Necessari Pillow, ReportLab, PyMuPDF e font Lato. In CI la generazione può essere isolata con `QUORIVIO_BROCHURE_OUTPUT_DIR` e `QUORIVIO_BROCHURE_NO_WEB=1`.

**Precisazioni:** i 500 partecipanti si riferiscono a un benchmark temporaneo CI, non a una garanzia; il codice QR stampato è illustrativo, non un invito scansionabile. Formula gauge: utenti con almeno una risposta / utenti connessi, 0–100%, scala 20–100%, opzione disabilitata per impostazione predefinita. Non si attribuisce alla modifica uno stato di CI verde prima dell'esecuzione dei test.
