# Hotfix accettazione Chromium: selettore esatto del salvataggio (2026-10-27)

## Errore verificato

- Run GitHub 40479089027, job qualità 122104572150, commit `238e184e16b658fa97f9ef57de5c3e352ce05615`.
- Bootstrap e test CSS desktop/mobile PASSATI.
- Test `tools/ci_browser_editor.py:190` FALLITO per `strict mode violation`: «Salva layout» individua anche l'icona «Salva layout della pagina». Non è dimostrato un problema con la persistenza.

## Correzione

- Un unico helper `editor_save_button(page)` trova il pulsante esatto nella regione editor (`exact=True`).
- Sostituiti tutti i selettori ambigui nei percorsi Chromium simulato e PostgreSQL reale, comprese le asserzioni sui pulsanti disabilitati.
- Nuova prova Chromium isolata desktop/touch con entrambi i pulsanti, clic reale e stato disabilitato; regressioni AST e avvio anticipato dalla CI manuale.
- Interfaccia e API di produzione invariate. Nessun uso di clic forzati, né scelta arbitraria del primo elemento.

La Full CI deve ancora validare il cambiamento. Punteggio RC conservativo: 48,0%.
