# Quorivio 0.1.0-dev — RC143 — Finestra Formato widget, risultati e anteprima smartphone

## Interventi

- **Formato widget**: pulsante Chiudi sempre visibile nell'intestazione, gruppi distribuiti su più righe, scorrimento verticale per raggiungere tutti i controlli; la finestra si riposiziona quando cambia altezza. La chiusura non deseleziona il widget.
- **Risultati / nuvola**: numero di risultati principali configurabile, default **5**, da 1 a 20. Ordinamento per frequenza discendente e stabile a parità di conteggio. Le etichette lunghe possono andare a capo, senza separare l'ultima parola dal numero. Il rendering è condiviso fra editor, presentatore e anteprime. Con auto-adattamento attivo i risultati sono ridotti per entrare nel riquadro; disattivandolo resta il comportamento manuale di taglio/scorrimento.
- **Prova smartphone**: canvas logico **1280 × 720** riscalato uniformemente in larghezza, senza impilare i widget. Coordinate, dimensioni, rotazioni e impaginazione dei testi restano quelle del desktop; lo sfondo fotografico della pagina viene escluso solo dalla simulazione telefono. Le altre viste restano disponibili.

## Verifiche

- Test Node `apps/web/test/rc143-preview-results.test.ts`, test Python `tools.tests.test_rc143_phone_result_ribbon`.
- Prova Chromium CSS e geometria a 1225/390 px tramite `tools/ci_rc143_format_phone_chromium.py`.
- Verifica integrità inventario e cumulativo RC143.
- **Suite locale completa:** 816/816 test Node superati; 1.734 test Python eseguiti, zero fallimenti e uno saltato; prova Chromium CSS 1225/390 px superata. **Non ancora certificati**: build npm/Vite completa, browser dell'installazione, dispositivo reale e perfetta fedeltà di ogni widget. Lo switch di editing con posizioni mobili indipendenti non è ancora implementato: le modifiche al layout comune continuano dall'editor desktop.

**Flag di rilascio:** `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Completamento certificato invariato: **85,25%** (43 accettati / 17 parziali). Nessuna promozione senza evidenze esterne.
