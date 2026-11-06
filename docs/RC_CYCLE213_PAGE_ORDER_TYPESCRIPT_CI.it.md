# RC213 — Correzione TypeScript della gestione ordine pagine

## Errore CI
GitHub Actions run `42140973603`, job qualità `127640902633`, bloccata nello step `RC196 strict frontend TypeScript typecheck before extended CI` per `TS2448`/`TS2454`: la dipendenza dell'effetto delle scorciatoie delle miniature leggeva `pageOrderPending` prima della dichiarazione `useState` (`main.tsx`, riga 2132). Il controllo TypeScript API e i precedenti preflight erano riusciti; i job dipendenti sono stati saltati. Non si tratta di un test storico obsoleto, ma di un vero errore di compilazione frontend.

## Correzione
Spostata l'inizializzazione dello stato `pageOrderPending` nel blocco incondizionato di stato `App()`, accanto a `pageBatchBusy`, prima dell'effetto che lo usa. Conservate selezione multipla Ctrl/Cmd, scorciatoie D/R/Backspace, blocco durante riordino, conferme e tutte le funzionalità RC204–RC212. Aggiunto test RC213 preventivo con tre mutazioni negative e relativo step prima di npm. Mantenuto il typecheck TypeScript rigoroso obbligatorio.

## Validazione
Versione **0.1.0-dev**, completamento **85,25%** (43 gate accettati, 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Inventario SHA-256 completo e ricevute storiche preservate. Test Python mirati locali; typecheck frontend completo e full CI ancora da certificare. Nessun commit/push/tag. Ultima full CI verde RC203 `42110429701`.
