# Quorivio 0.1.0-dev — ciclo RC 9: 71,0% (+3,0 punti), 28 ottobre 2026

**Baseline:** ZIP cumulativo ciclo 8 (RC 68,0%), tutte le implementazioni precedenti conservate. Versione `0.1.0-dev`, licenza EUPL-1.2.

## Riconciliazione gate con prove verificate su GitHub

La run GitHub Actions [40717525524](https://github.com/desalvo/quorivio/actions/runs/40717525524), tentativo 2, commit `f6738592c648bc620e01b92d2bbaa6b90b459287`, job qualità `123073117101` è **interamente verde**. I seguenti sotto-gate tecnici distinti erano già dimostrati ma compresi nei gate parziali. Per ciascuno sono trasferiti esattamente 2 punti di peso dal padre parziale al sotto-gate accettato, senza doppia attribuzione:

- **A2-ORDER** (2): miniature/editor e controlli di interazione Chromium desktop/mobile, contratti di riordino da tastiera. A2 residuo parziale (4): fedeltà pixel, DnD Firefox/WebKit, dispositivi reali.
- **A4-FOCUS** (2): focus trap reale TypeScript/React Chromium 1440/390, isolamento `inert`/ARIA dinamico e ripristino del focus. A4 residuo parziale (4): NVDA/VoiceOver/TalkBack, touch e tastiera fisici, approvazione WCAG/AGID.
- **B3-QUESTION-STATS** (2): PostgreSQL 18 reale, tre domande indipendenti, statistiche riservate al presentatore, revisioni e idempotenza per due partecipanti. B3 residuo parziale (2): verifica indipendente browser/dispositivi e tecnologie assistive.

Queste prove non riutilizzano il perimetro già accettato di A3-AUTO (persistenza editor) o B3-AUDIENCE (ingresso QR, votazioni e moderazione). Peso complessivo 100; 33 → 36 gate, 16 → 19 accettati, 17 parziali invariati. **68,0 → 71,0%, +3,0 punti percentuali**. RC rigorosa ancora bloccata.

## Nuovo sviluppo locale (nessun punto assegnato)

Il recupero password richiede nuova password e conferma identiche, almeno 12 caratteri; un blocco sulla richiesta in corso impedisce l'invio doppio. In caso di errore resta possibile ritentare senza ripubblicare il token nell'URL. Il test Chromium sul bundle React compilato, 1440 e 390 px, verifica password difformi, doppio clic (un solo POST), errore/ritentativo, successo e assenza del token nello storage/URL. **La nuova Full CI GitHub è ancora necessaria**.

**Test locali:** build TypeScript backend/frontend e Vite PASS; 474/474 Node backend; 62/62 Node frontend; 979/979 Python; Chromium desktop/mobile PASS. PostgreSQL locale, Firefox/WebKit, dispositivi fisici e verifica indipendente non eseguiti in questo batch.

**Prossimi passi:** commit effettuato dall'utente, CI estesa `browser_test=true`, `capacity_test=true`, `publish_image=false`, `publish_latest=false`, verifiche indipendenti multi-browser, dispositivi, screen reader, distribuzione reale Kubernetes/RWX/ClamAV e GDPR/AGID. Nessun commit, push, tag o pubblicazione automatica.

**Evidenze:** `docs/validation/RC_CYCLE9_VERIFIED_GATE_HARDENING_20261028.json`, `docs/RC_GATE_MATRIX.json`.
