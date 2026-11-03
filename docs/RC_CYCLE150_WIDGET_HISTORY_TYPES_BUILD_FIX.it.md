# Quorivio RC150 — Correzione compilazione TypeScript della cronologia widget

**Cumulativo RC150 successivo al commit RC149:** risolti due errori TS2339 nella run GitHub Actions `41700222536`, includendo `position` e `resultTopCount` nel tipo `EditorWidgetPermissionFields` che attinge a `PageDesign.widgets`. Comportamento di Undo, sfondi mobile e risultati preservato. Aggiunti test, documentazione e inventario corrente; RC149 conservato storico. **Completamento certificato 85,25%** (43 accettati / 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Compilazione npm completa e accettazioni di integrazione da confermare nella prossima CI. Nessun commit/push/rilascio dell’assistente.

## Verification

- Run `PYTHONPATH=tools python3 -m unittest tools.tests.test_rc150_widget_history_types -q`.
- Run `npm ci --ignore-scripts` and `npm run build` in CI; no local npm dependency certification.
- Verify `PYTHONPATH=tools python3 tools/verify_rc_release_status.py` and new inventory/ZIP integrity.
