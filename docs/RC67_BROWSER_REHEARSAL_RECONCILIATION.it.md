# Quorivio 0.1.0-dev — RC67 — Accettazione verificata anteprima interattiva (31 ottobre 2026)

**Baseline committata dal manutentore:** `487c960f09b3c9adb996d489f44b52d059da12b2`. CI standard `41191213305` e campagna estesa `41191751069` superate sullo stesso codice, 11/11 job obbligatori verdi, senza pubblicazione. L'assistente non effettua commit.

**Riconciliazione delle prove:** il job qualità `124509777927` ha verificato con Chromium reale 1440/390 le risposte in anteprima, le reazioni singole, le statistiche del presentatore e le scadenze che impediscono risposte tardive. Il job Firefox/WebKit `124511576966` ha verificato il doppio preview React compilato su desktop/mobile con gestione del focus. Il nuovo gate `B2-CLIENT-REHEARSAL` certifica solo questo comportamento client: non replica il credito PostgreSQL `B2-DB` né i controlli di focus A1/A4. Rimangono aperti i collaudi B2 con latenza variabile, più repliche e dispositivi fisici.

**Completamento RC: 83,75%** (40 gate accettati, 17 parziali, 57 totali), +1,00 punto rispetto a RC66. Il peso complessivo è 100: B2 parziale passa da peso 4 a 2, il nuovo gate accettato pesa 2. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. **RC strict NON PRONTA**: provider reali, TLS pubblico, RWX tra macchine fisiche, accessibilità assistiva e approvazioni indipendenti GDPR/AGID/sicurezza. La nuova CI andrà verificata dopo il prossimo commit del manutentore.

---
