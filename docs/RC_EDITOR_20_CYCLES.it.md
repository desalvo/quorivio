# Quorivio 0.1.0-dev — lotto cumulativo di 20 interventi (25 ottobre 2026)

**Baseline:** ultimo commit confermato dall'utente, hotfix Chromium selection-state. Workflow GitHub Actions `40141894130`, job `121015403855`: production quality SUCCESS; container build SUCCESS; Chromium opt-in PASS; test PostgreSQL/WebSocket con 500 partecipanti indipendenti PASS, picco osservato dal presentatore >= 475, zero errori. La pubblicazione in produzione è stata correttamente saltata.

## Venti interventi verificabili, senza ZIP intermedi

1. Riconciliazione delle prove della CI con la matrice RC, separando evidenze reali da test ancora da eseguire.
2. Normalizzazione della selezione di widget esistenti, rimozione di ID orfani e duplicati.
3. Eliminazione di gruppi di widget senza toccare gli altri oggetti della pagina.
4. Duplicazione multipla in ordine di livello con nuovi identificativi indipendenti.
5. Protezione della duplicazione contro collisioni di identificativi già presenti nella pagina.
6. Spostamento di gruppo mediante incrementi limitati ai confini del canvas.
7. Spostamento di tutta la selezione mediante frecce da tastiera sul widget focalizzato.
8. Eliminazione della selezione multipla con Canc/Backspace e supporto Annulla.
9. Porta selezione davanti, preservando l'ordine relativo dei widget.
10. Porta selezione dietro, preservando l'ordine relativo dei widget.
11. Sposta selezione avanti di un livello, anche se i widget non sono contigui.
12. Sposta selezione indietro di un livello, anche se i widget non sono contigui.
13. Distribuzione di spazi orizzontali uguali basata sui bordi (non sui centri).
14. Distribuzione di spazi verticali uguali basata sui bordi.
15. Centratura orizzontale del gruppo sull'intero canvas, senza alterare gli scarti relativi.
16. Centratura verticale del gruppo sull'intero canvas; ammesso anche un solo widget.
17. Incolla multipla ripetuta con offset progressivo limitato e nuove identità.
18. Collaudo Chromium ampliato con riordino, nudge, duplicazione, eliminazione e Annulla.
19. Collaudo Chromium ampliato con salvataggio PATCH simulato, reload e verifica del layout; prova aggiuntiva su viewport touch 390×844 e tastiera.
20. Nuovi test Node/Python, compilazione API/frontend, documentazione IT/EN e riallineamento punteggio RC riproducibile.

## Risultati e limiti

- **205/205 test Node.js PASS** (179 nella baseline, 26 nuovi).
- **277/277 test Python PASS** (274 nella baseline, 3 nuovi; aggiornati due controlli sorgente per la nuova implementazione del riordino e della cancellazione).
- **Build API TypeScript e web TypeScript/Vite PASS.**
- La nuova suite Chromium è **scritta ma non eseguita end-to-end localmente**: Chromium risponde `ERR_BLOCKED_BY_ADMINISTRATOR` su `http://127.0.0.1:5173/`. Occorre ripetere il workflow opt-in in GitHub Actions.
- Il salvataggio/reload della nuova suite usa una fixture HTTP in memoria, **non un database reale**. La persistenza PostgreSQL e i dispositivi fisici restano criteri distinti.
- Nessun nuovo test con 500 utenti è stato lanciato localmente; il successo citato proviene dal workflow verde precedente.
- **Punteggio RC: 45,5/100** (43,0 → 45,5) per il passaggio del gate D4 da `open` a `partial`, grazie alla prova effettiva di capacità e alle scansioni CI. Non sono stati promossi altri gate sulla base di codice non ancora collaudato.

## Rimanenti per RC

Editor: test browser ampliato, salvataggio PostgreSQL reale, accessibilità e dispositivi. PowerPoint: corpus reale e fedeltà visuale. Sessioni: latenza e fairness sotto carico, privacy browser. DR: ripristino in staging con dati rappresentativi, RPO/RTO. Infrastruttura: ARM64, Podman rootless, Kubernetes HA. Sicurezza: provider SSO/SMTP reali, AV, pentest, GDPR e licenze.

**Non è una Release Candidate.** Nessun commit, push, tag o deploy è stato eseguito da questo lotto.
