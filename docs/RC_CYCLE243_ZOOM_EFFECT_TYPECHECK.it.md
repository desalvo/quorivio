# RC243 — Correzione cleanup zoom React e typecheck TypeScript

- **Errore:** run GitHub [42376234500](https://github.com/desalvo/quorivio/actions/runs/42376234500), commit `f2899cc76320667a442b504d9e89f38c6f1611ff`; job `Production quality gate`, tipo `TS2345` in `apps/web/src/main.tsx`.
- **Causa:** `CSSStyleDeclaration.removeProperty` restituisce una stringa. Il cleanup arrow di `useEffect` la restituiva implicitamente, mentre React richiede `void`.
- **Correzione:** `return()=>{root.style.removeProperty('zoom');};`. Zoom persistente 70–150%, valore predefinito 100%, controlli accessibili e pulizia dell'effetto preservati.
- **Regressione:** `tools/tests/test_rc243_global_zoom_effect_cleanup.py` respinge esplicitamente il vecchio codice e controlla che la CI esegua il test prima di npm e conservi `tsc --noEmit` obbligatorio.
- **Rilascio:** RC242 storica immutata, RC243 corrente. Full CI GitHub RC243 ancora da verificare; progresso 85,25% (43 accettati / 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
