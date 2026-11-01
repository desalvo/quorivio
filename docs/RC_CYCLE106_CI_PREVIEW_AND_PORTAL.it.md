# RC106 — preview Chromium fail-closed per WebSocket e contratto pagina flottante

**Run verificata:** GitHub Actions `41305315027`, commit push `454eaf729c9487146f2c89a47178a64161d5683b`. Un test Python del gate qualità fallisce e il riepilogo esteso fallisce di conseguenza.

## Cause distinte

1. `test_page_context_not_ribbon` chiedeva ancora la struttura inline `pageContextOpen&&<section ...>`. L'implementazione RC105 usa invece `EditorFloatingWindow` con portal nel `body`, spostabile e indipendente dal canvas. Corretto il test affinché verifichi la struttura nuova e non accetti il ritorno al pannello inline.
2. La preview del frontend compilato nella fase Chromium usava un proxy Vite `/live` verso `localhost:8080`; il backend non era ancora avviato e il log segnalava `AggregateError [ECONNREFUSED]` non tradotti in errori Playwright. Non vanno trattati come test riusciti.

## Correzione e protezioni

- `apps/web/vite.config.ts`: sviluppo con proxy API/live intatto, preview offline con `preview.proxy={}` senza connessioni spurie al backend.
- `.github/workflows/ci.yml`: controllo dei log eseguito nel `trap` EXIT a prescindere dal successo o fallimento anticipato dei test, con pulizia del processo preview e codice di errore propagato.
- `tools/ci_preview_proxy_guard.py`: errori WS/proxy e rifiuto TCP bloccanti; prova di avvio preview obbligatoria; nessun URL privato nei messaggi.
- Contratti e regressioni negative per preservare i popup trascinabili e intercettare nuove regressioni del workflow.

## Da verificare

CI completa `[full-ci]` e test reali su browser e PostgreSQL/WebSocket. Il controllo preview non sostituisce i test backend, né certifica audit indipendenti o dispositivi fisici. Nessun avanzamento percentuale o pubblicazione.
