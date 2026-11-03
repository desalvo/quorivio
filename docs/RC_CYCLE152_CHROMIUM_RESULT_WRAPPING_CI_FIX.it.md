# RC152 Correzione CI Chromium per i risultati su più righe

## Problema verificato

La run GitHub Actions `41708756081`, commit `78f784a`, supera 825 test Node e compilazione TypeScript/Vite ma si interrompe nel test browser `ci_rc141_widget_parity_chromium.py`: impone `white-space:nowrap` all'intera riga dei risultati, mentre dalla RC143 le etichette lunghe devono andare a capo e soltanto l'ultima parola con conteggio `[28]` resta indivisibile.

## Interventi

- CSS e comportamento applicativo RC143 preservati.
- Fixture allineata al JSX effettivo con `linked-result-label` e `linked-result-final`.
- Controlli reali Chromium alle risoluzioni 1440/390 nelle viste editor, presentatore, anteprima e partecipante: ritorno a capo, conteggio indivisibile, dimensione reazioni, checkbox e assenza di clipping sulla fixture da 320 px.
- Font salvato da 16 px applicato anche alla fixture del partecipante: il precedente fallback `1.25cqw` produceva artificialmente 3,8 px.
- Test negativi che devono respingere etichetta interamente non-a-capo e separazione del conteggio.
- Nuovo inventario RC152, mantenendo quello storico RC151 immutato.

## Stato

Nessuna modifica al runtime. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; completamento 85,25% (43 accettati/17 parziali). CI GitHub integrale, test database e accettazioni esterne ancora da confermare. Nessun commit/push/rilascio dell'assistente.
