# Correzione intercettazione dell'header nella CI estesa Chromium

**Data:** 27 ottobre 2026 · **Versione Quorivio:** `0.1.0-dev` (invariata) · **Baseline committata:** `0bb8fb7856727699384dfe51aea6ee6d961ea022` · **Licenza:** EUPL-1.2

## Evidenze GitHub

- CI standard: https://github.com/desalvo/quorivio/actions/runs/40588408394 — **SUCCESSO**, quality gate e build container superati, pubblicazione Docker saltata.
- CI estesa manuale: https://github.com/desalvo/quorivio/actions/runs/40589103128 — **FALLIMENTO** nel passo `Chromium editor UI acceptance (opt-in)`; `tools/ci_browser_editor.py:106`, apertura della voce `Strumenti di selezione e allineamento`. Playwright segnala che l'header intercetta il puntatore. Sei verifiche Chromium preliminari passate; prove successive su PostgreSQL non raggiunte.

## Intervento

Il CSS mantiene il menu contestuale dello sfondo e i pannelli di disposizione sotto l'header anche quando il canvas è parzialmente nascosto dallo scrolling. La funzione condivisa controlla il vero punto di clic (`document.elementFromPoint()`), senza clic forzati. Nuovo test Chromium reale desktop/touch che riproduce la posizione coperta: fallisce con il CSS precedente e passa col nuovo. Test integrato nella Full CI; aggiunti cinque contratti Python di regressione.

## Verifiche

- Build TypeScript backend/frontend e Vite: PASS.
- Node backend 450/450 PASS, frontend 23/23 PASS.
- Chromium isolato desktop/touch PASS; altri tre preflight PASS.
- Python mirati 5/5 PASS; suite Python complessiva in timeout locale, quindi NON certificata.
- Browser applicativo completo con API locale non disponibile in questo ambiente (navigazione bloccata); nuovo workflow GitHub con Chromium e PostgreSQL ancora da eseguire.

**Avanzamento ponderato RC: 53,0% invariato; nessuna promozione gate; RC non pronta.** Nessun commit, push o pubblicazione Docker eseguiti dall'assistente.
