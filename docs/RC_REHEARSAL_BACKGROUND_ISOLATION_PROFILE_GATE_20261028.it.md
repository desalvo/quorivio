# RC — isolamento accessibile dell'anteprima e sottogate profili (28 ottobre 2026)

**Baseline:** Quorivio `0.1.0-dev`, ultimo commit confermato dall'utente `a32ef78902a656262d346a0fa622604a4deda405`; il package al 60,0% è cumulativo e **non ancora committato**. Non eseguire commit, push, tag o pubblicazioni.

## Intervento sull'applicazione

- Le anteprime presentatore, partecipante e affiancata condividono la stessa finestra di prova. Il modulo `apps/web/src/rehearsal-dialog.ts` ora rende temporaneamente **inert** e `aria-hidden=true` ogni ramo DOM di sfondo lungo il percorso dalla finestra al body, senza disabilitare la finestra stessa. Alla chiusura ripristina gli attributi `aria-hidden` originali, anche quando erano esplicitamente `false`, e il precedente stato `inert`; resta il ripristino del focus e dello scorrimento.
- `tools/ci_rehearsal_keyboard_chromium.py` verifica il modulo TypeScript effettivo con Chromium reale, su 1440×900 e 390×844: accessibilità del contenuto, focus, Tab ciclico, Esc, IME, invocatore, scorrimento e valori precedenti.
- Il test opt-in `tools/ci_browser_editor.py` apre ora dall'editor **Anteprime affiancate**, controlla il doppio canvas 16:9 e le coordinate del widget, passa alla modalità partecipante, riapre la modalità affiancata e verifica che Esc ripristini l'editor. Si usa il puntatore reale; **non** si usa `force=True`.

## Score RC — 61,0% (+1 punto)

Unicamente sulla base della **Full CI GitHub verde già verificata** `40638652838` e della precedente `40595463258`, il gate C4 è suddiviso tra `C4-PROFILE` (peso 2/100, **accettato**, lifecycle profilo/foto con Chromium e PostgreSQL reali) e C4 residuo (peso 3/100, **parziale**, storage RWX/ClamAV reale, multi-replica, dispositivi e tecnologie assistive indipendenti). La formula invariata (accettato=100%, parziale=50%) passa da 60,0 a **61,0%**, con 26 gate (9 accettati, 17 parziali). Non si attribuisce alcun punto alle modifiche di questo ciclo prima della nuova CI.

**RC rigorosa NON pronta.** Browser dell'app su localhost è bloccato dall'ambiente locale con `ERR_BLOCKED_BY_ADMINISTRATOR`: il test completo con fixture API è stato aggiunto alla CI ma **non è stato eseguito localmente**. I test offline non costituiscono un audit con NVDA/VoiceOver/TalkBack o su dispositivi reali. La nuova Full CI GitHub con `browser_test=true` e `publish_image=false` rimane necessaria.

Vedere `docs/validation/RC_REHEARSAL_BACKGROUND_ISOLATION_PROFILE_CI_20261028.json` e `docs/RC_GATE_MATRIX.json` per prove e requisiti residui.
