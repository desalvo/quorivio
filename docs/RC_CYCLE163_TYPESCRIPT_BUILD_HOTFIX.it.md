# RC163 — Correzione regressione compilazione TypeScript

La CI GitHub 41756050958 sul commit `e926015e12952643ec08ea7d35e4fc9dee4ed7ee` si è interrotta nello step **Compile frontend and backend** per quattro errori TypeScript in `apps/web/src/main.tsx`:

- TS2339 alla riga 2119: `showQrUrl` assente nel tipo locale `Pick<>` della cronologia dei widget, benché presente nel tipo canonico `PageDesign` e validato dall'API.
- TS2367 per tre volte alla riga 2145: il ramo che inserisce widget non grafici controllava ancora `k==='shape'` o `k==='line'`, valori già esclusi dal restringimento del tipo.

La correzione include `showQrUrl` nel tipo `EditorWidgetPermissionFields` ed elimina le condizioni grafiche irraggiungibili nel ramo non grafico. Rimangono il componente `GraphicInsertTool` specifico per linee e forme, l'editor desktop/smartphone, le proprietà del QR e le altre funzioni RC162; inventario RC162 preservato senza modifiche.

Il nuovo `test_rc163_frontend_typescript_build.py` viene eseguito *prima* di npm e comprende mutazioni negative. Compilazione TypeScript/Vite e collaudo autenticato richiedono conferma nella prossima CI GitHub; nessun gate promosso. **85,25% certificato** (43 accettati / 17 parziali), `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
