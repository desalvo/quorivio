# RC238 — Riconciliazione Chromium del layout smartphone automatico

## Errore della CI GitHub

La [full CI 42269302109](https://github.com/desalvo/quorivio/actions/runs/42269302109), commit RC237 `4c4b7ee0451e0a20abb791da2a0ea585eddc8f63`, si è arrestata nel **Production quality gate**, passo **Chromium participant UI and PostgreSQL lifecycle (opt-in)**. La fixture `tools/ci_browser_participant.py:132` esigeva che «Diapositiva 16:9» avesse `aria-pressed=true` anche nel browser mobile. L'applicazione seleziona correttamente «Layout smartphone» su un dispositivo touch stretto, come previsto dalla RC227. ClamAV ha superato i controlli; gli altri job dipendenti sono stati saltati o chiusi in modalità fail-closed.

## Interventi RC238

- Nessuna modifica al comportamento dell'applicazione, dell'API, del CSS o del database.
- All'ingresso, controllare il default 16:9 su desktop e il default smartphone con `.stage-phone` su mobile; passare esplicitamente a `.stage-fidelity` prima di confrontare la geometria dei widget tra i dispositivi.
- Dopo il reload del browser mobile, verificare il ripristino del default smartphone e riattivare 16:9 prima del confronto geometrico. Conservare i test successivi di layout smartphone e lettura accessibile.
- Correggere il test storico RC176 che confondeva lo stato automatico iniziale con il successivo cambio esplicito di modalità.
- Aggiungere regressioni RC238 fail-closed prima di npm, conservando l'accettazione reale PostgreSQL + Chromium nella full CI.

## Stato

Test locali Python/Node e integrità dell'archivio da riportare nella consegna finale. **La full CI GitHub resta da certificare.** Completamento certificato **85,25%** (43 gate accettati, 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o tag dell'assistente.
