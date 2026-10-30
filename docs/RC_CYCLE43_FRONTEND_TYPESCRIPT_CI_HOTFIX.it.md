# Ciclo 43 — compilazione frontend TypeScript

- CI precedente: https://github.com/desalvo/quorivio/actions/runs/41099464679
- Job: 124213731405, `Production quality gate`.
- Commit utente: `55b5ab70dcc3ee772b47c5acd498b47d58874441`.
- Errore 1: `src/main.tsx(1231,2552): TS2339 Property allowAnswerChange does not exist ...`.
- Errore 2: `src/main.tsx(1231,2841): TS2339 Property showEmail does not exist ...`.
- Causa: il tipo editor `newWidgetHistory<{...}>` era più ristretto del tipo backend `PageDesign.widgets`; il codice usa due flag già validati lato server.
- Correzione: `EditorWidgetPermissionFields` deriva i due campi da `PageDesign.widgets[number]`, evitando il drift.
- Verifica: test di regressione Python sul contratto e parity check TypeScript aggiunto a `widget-style-contract.ts`. La compilazione completa deve essere confermata dalla prossima CI.
- Inventario SHA-256 del ciclo 43 sostituisce il catalogo corrente, mantenendo il ciclo 42 come prova storica.
- Stato RC: 80,75% (35/52 gate accettati, 17 parziali). Nessun nuovo punteggio assegnato.
