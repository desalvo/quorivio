# RC226 — Strumenti schemi, vista partecipanti e studio su smartphone

## Funzionalità sviluppate

- Barra «Inserisci», «Allinea», «Distribuisci» e «Schema» nell'editor degli schemi: pulsanti con **icona sopra, nome sotto e descrizione completa come tooltip / nome accessibile**; layout compatto e navigabile anche da tastiera. Il caricamento sfondo usa un comando grafico accessibile, non un input file che occupa tutta la barra. Conservate tutte le operazioni e le limitazioni di modifica.
- Palette widget nello schema: riutilizza `EditorWidgetIcon`, identificativi `data-widget-kind` e stessi accenti cromatici della palette dell'editor pagine (rating, domande, QR, risultati, forme, ecc.). Anche titoli/footer schema mantengono Arial predefinito e i font personalizzati continuano a prevalere.
- Il partecipante in **schermo piccolo** (larghezza <=700 CSS px) o touch con viewport <=960 CSS px apre **per default** il layout smartphone, con le posizioni automatiche o personalizzate della pagina. I pulsanti per scegliere manualmente 16:9, smartphone o lettura accessibile rimangono operativi e hanno sempre la precedenza dopo un intervento esplicito.
- La zona admin/presentatore su telefono è riorganizzata entro 760 CSS px: header e navigazione orizzontale accessibili, apertura sessioni, sidebar/dashboard, form, tabelle scorrevoli, finestre, anteprima e controlli della proiezione. L'editor pagine utilizza una griglia **a colonna singola**: testata compatta, palette orizzontale, miniature orizzontali e canvas nell'area restante; lo schema usa ribbon a scorrimento, canvas a piena larghezza e proprietà sottostanti. Mantiene il desktop inalterato perché le regole sono tutte sotto media query.
- Non si modificano la persistenza delle pagine né gli endpoint API, i permessi, i dati delle sessioni o le impostazioni di pubblicazione.

## Test e limiti

- Node API 628/628 e frontend 394/394; Python mirati 30/30; TypeScript sintattico 0 diagnostics. Chromium CSS effettivo con schermate rappresentative a 320×568, 390×844, 760×920 e 1440×900: sidebar, ribbon e miniatura accessibili, editor a colonna singola solo su mobile.
- Nuovi preflight CI anticipati prima di npm e test Chromium nel job browser. **Il browser con applicazione React compilata, interazioni reali touch, PostgreSQL e full CI GitHub RC226 non sono stati eseguiti localmente**: rimangono gate obbligatori.
- Ultima full CI verde certificata: RC219 `42197607753`. Percentuale certificata invariata: **85,25%**, 43 gate accettati e 17 parziali. Versione 0.1.0-dev, `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o release.
- Tutti gli inventari cumulativi precedenti rimangono intatti; la presente release aggiunge il proprio inventario SHA-256 e una ricevuta di checksum del package.
