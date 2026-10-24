# Strategia di chiusura accelerata dei gate RC — 24 ottobre 2026

**Versione invariata**: 0.1.0-dev. La matrice RC determina l'avanzamento; test unitari verdi non equivalgono ad accettazione end-to-end.

## Ordine delle macroaree da chiudere, senza fermarsi a singoli helper

1. **B1–B4: sessioni live**. Collaudo presentatore/partecipante in due browser e due repliche API su PostgreSQL 18: avvio, apertura, risposta, chiusura, revoca, punteggi, presenze, latenza. Test reale con 500 partecipanti nella stessa sessione e riconciliazione dei report.
2. **A1–A4: editor**. Collaudo mouse, tastiera, touch, salvataggio/riapertura, rotazione, ridimensionamento, riordino, miniature, accessibilità, smartphone e tablet.
3. **C1–C4: account e amministrazione**. MFA email e TOTP indipendenti, SMTP, reset, revoche, SSO Google/Facebook/GitHub/INFN OIDC reali, foto profilo su volume RWX con antivirus e impostazioni concorrenti.
4. **D2–D4 e D6: infrastruttura e sicurezza**. Migrazioni e ripristino PostgreSQL 18, Docker AMD64/ARM64, Podman rootless, Helm NGINX/HAProxy, scansioni, licenze, GDPR e revisione sicurezza.
5. **PowerPoint**. Matrice separata di fedeltà OOXML e prove round-trip; non dichiarare supportati grafici/SmartArt senza confronto reale.
6. **D5: manuali**. Riconciliazione IT/EN dopo i collaudi funzionali.

Ogni gate si chiude solo con ambiente, procedura, risultati osservati, log/artefatti e decisione di accettazione datata. I collaudi reali esterni non sono simulabili dai test statici.

## Interventi effettivi di questo ciclo

L'audit periodico WebSocket (10 secondi) ora ricontrolla tutte le sessioni aperte, il ruolo e la delega del presentatore, revoche/password, nonché la permanenza del partecipante nella sessione. Sessioni chiuse/scadute, partecipanti rimossi, presentatori revocati e indisponibilità DB provocano chiusura fail-closed alla successiva verifica. Restano da eseguire i collaudi reali multi-replica e browser.

Build backend TypeScript PASS; frontend TypeScript/Vite PASS; Node.js 138/138 PASS; Python 235/235 PASS. Matrice RC invariata: 40/100.
