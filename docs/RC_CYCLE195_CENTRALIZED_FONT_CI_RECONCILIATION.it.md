# RC195 — riconciliazione CI del font predefinito RC161

## Evidenze GitHub

La run GitHub Actions `42074647393` (#295; commit `c219d4b2377af721a20fccebe52ea57a30b3114d`), job `127411480855`, fallisce al passo 14 (`RC161 master image, Arial and graphics presets contracts before npm`). Il test storico cercava il testo letterale `fontFamily:'Arial'` in `main.tsx`, mentre RC194 ha centralizzato i valori predefiniti. ClamAV è verde; gli altri job dipendenti sono saltati.

## Correzione

- Nessuna modifica al comportamento applicativo. I font Arial predefiniti sono definiti in `slide-master.ts` e applicati tramite `widgetDisplay`, `stageWidgetTypography` e `widgetTypographyStyle`, senza cancellare le personalizzazioni.
- Il controllo RC161 verifica la sorgente reale delle impostazioni, il font del titolo/footer e la precedenza di master e widget. Nuovi test RC195 Python e Node eseguono prove negative e verifiche effettive, anche per la proiezione smartphone e le risposte dei quiz.
- Aggiunto un preflight immediatamente prima di RC161 nella CI; preservati tutti i manifesti storici e tutte le funzionalità RC194.

## Ulteriori riconciliazioni dei controlli storici

La verifica preventiva dei 96 passi CI prima di npm ha individuato altri controlli letterali obsoleti in RC144, RC167, RC168, RC169, RC131, nel test del timer e in RC91. I controlli ora seguono la **pagina realmente proiettata** (`viewActivity`, `viewWidgets`, `audienceActivity`) e la tipografia centralizzata. Il timer di prova si riavvia soltanto quando cambia la pagina di voto del pubblico; il numero della pagina segue l’ID effettivamente visualizzato. Nessuna modifica al runtime. I test negativi RC195 rilevano regressioni verso la vecchia pagina unica o la perdita delle personalizzazioni.

## Limiti

La validazione locale comprende i test mirati, le regressioni storiche, le suite Node e l'inventario sorgenti/ZIP. Le prove integrate React/Chromium/PostgreSQL/Kubernetes saranno certificate solo dalla prossima CI dopo il commit. Percentuale globale **85,25%** (43 gate accettati, 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag effettuato dall'assistente.
