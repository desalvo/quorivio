# Quorivio RC180 — accessibilità contemporanea di palette e strumenti contestuali

## Errore GitHub

Run `41913987787`, job `126868661600` (`Production quality gate`): il test Chromium RC179 sulla selezione passa su desktop, tablet e smartphone, ma `tools/ci_browser_editor.py` fallisce con timeout cliccando `button.editor-icon-tool[data-graphic-palette="line"]`. Il pannello `.canvas-editor-tools` sovrapposto intercetta l'evento. In RC179 era stato elevato lo stacking context dello stage per risolvere il problema inverso.

## Correzione

I pannelli di selezione e allineamento sono ora collocati in flusso nello stage, **sotto la palette di inserimento**, con scorrimento indipendente e canvas ancora navigabile. Non si usano click forzati, eventi sintetici o bypass di `pointer-events`. Lo z-index dello stage torna normale; restano inalterati i menu contestuali dello sfondo e i livelli dell'header.

## Verifica

`tools/ci_rc180_editor_palette_context_coexist_chromium.py` usa i CSS effettivi e una palette a icone con wrapping; prova in sequenza i clic nativi **Duplica selezione → Linee → Sinistra → Linee** lasciando aperti gli strumenti, a 1440×940, 960×800 e 390×844. `document.elementFromPoint` deve identificare il vero pulsante prima del click. Contro RC179 falliva su Linee in desktop; con RC180 passa. La CI lo esegue prima dell'E2E editor ed è presente un controllo unittest anticipato. Conservati gli inventari storici.

I controlli locali non sostituiscono la CI React/PostgreSQL autenticata e i collaudi fisici. Punteggio certificato invariato a **85,25% (43 gate accettati, 17 parziali)**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
