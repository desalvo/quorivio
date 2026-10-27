# Bootstrap Chromium GitHub senza apt: CI 40395950707

## Evidenze e causa

- Baseline committata: `a6ecaf1105a78893bbecdb4229677fefe072972e`.
- La Full CI manuale `40395950707`, job qualità `121829112173`, è terminata dopo 8 minuti nel passo di accettazione Chromium: `python3 -m playwright install --with-deps chromium` stava ancora scaricando dipendenze di sistema dai mirror Ubuntu. **I test dell'editor non sono stati eseguiti**; non è stato rilevato un nuovo difetto della UI in questa run. Build container e pubblicazione SKIPPED; Docker resta opt-in.
- I runner GitHub Ubuntu 24.04 dispongono già di Chromium/Google Chrome. Il download di librerie OS in ogni run manuale è superfluo e introduce instabilità dei mirror.

## Intervento

1. Pin del job quality a `ubuntu-24.04`, lasciando invariati i runner degli altri job.
2. Installazione del solo modulo Python Playwright, senza download Chromium né invocazione apt nel passo browser.
3. Nuovo `tools/ci_browser_bootstrap.py`: ricerca del browser preinstallato, verifica con timeout di 8 secondi, smoke Playwright headless reale; `QUORIVIO_CHROMIUM_PATH` viene esportata solo dopo verifica positiva. In caso di assenza/errore, fallimento esplicito e rapido, senza saltare i test.
4. Propagazione del percorso al preflight CSS e a tutti i collaudi browser successivi; gli script esistenti già supportano la variabile.
5. Sette regressioni standard-library sulla policy CI, ricerca browser ed esportazione del percorso.

## Verifica

- Chromium locale preinstallato `/usr/bin/chromium`: smoke Playwright reale PASS, senza apt né download.
- Preflight CSS con clic desktop/mobile: PASS.
- Test bootstrap: 7/7 PASS; parsing YAML PASS.
- **Full CI GitHub e test con browser sul runner devono ancora passare.** Nessun gate RC promosso, punteggio conservativo 48,0% invariato.

Riferimento: https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md
Rieseguire il workflow manuale con `browser_test=true`, `publish_image=false`, `publish_latest=false` dopo commit. Nessuna pubblicazione automatica Docker.
