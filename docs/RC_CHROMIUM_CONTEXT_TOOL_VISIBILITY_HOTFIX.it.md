# Correzione accettazione Chromium e controlli contestuali — 26 ottobre 2026

**Baseline committata:** `a415b2655d4d0e648777c3a65efbc28e011663f0`.
**Evidenza:** GitHub Actions manuale `40385480205`: fallisce `Chromium editor UI acceptance`; build container saltata per dipendenza; pubblicazione Docker saltata correttamente (opt-in).

## Problema

Dopo selezione, undo/redo e altre azioni, `tools/ci_browser_editor.py` cercava il pulsante `Porta selezione davanti` presupponendo che la barra contestuale fosse ancora aperta. L'interfaccia riprogettata nasconde intenzionalmente `.canvas-editor-tools` finché non si apre il menu del canvas (`data-tools-open={backgroundMenu}`). Il log mostra attesa del pulsante e timeout, non intercettazione del puntatore né errori JavaScript. La precedente sovrapposizione del menu miniature non è più la causa del fallimento.

## Correzione

- Aggiunto `tools/ci_editor_context_tools.py` condiviso per aprire, utilizzare e chiudere il menu tramite clic Playwright reali, con controllo su visibilità e abilitazione. Nessun clic forzato o manipolazione dello stato applicativo.
- Collaudo Chromium simulato: tutte le operazioni su selezione, allineamento, appunti, livelli, duplicazione e cancellazione riaprono il menu quando serve; verifica esplicita del ciclo di chiusura/riapertura.
- Collaudo Chromium con PostgreSQL reale: stessi helper per lo spostamento di gruppo e chiusura del menu prima di salvataggio e riconciliazione.
- Aggiornato un test contrattuale obsoleto e aggiunte quattro regressioni per desktop e touch.
- Nessuna modifica ad API o UI di produzione, schema DB, CSS, autenticazione, Docker o gestione dei partecipanti.

## Verifica

Suite locali mirate e test Node verdi. La Full CI Chromium **deve ancora essere rieseguita su GitHub**; nessuna promozione di gate RC e punteggio conservativo **48,0%** invariato. Prossima azione: commit del package, esecuzione manuale con `browser_test=true`, `publish_image=false`, `publish_latest=false`.
