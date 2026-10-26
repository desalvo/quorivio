# Quorivio 0.1.0-dev — ciclo cumulativo di 40 interventi su profili, immagini e amministrazione

**Baseline committata:** CI estesa GitHub Actions `40304413948` verde. **Baseline successiva:** package profilo `presenter-profile-atomic-save-public-avatar` (non confermato come committato). Questo package include cumulativamente anche il ciclo profilo precedente.

I 40 punti sotto sono interventi e verifiche raggruppati in **un batch**, non 40 release, esecuzioni CI o macroaree completate. Le prove di PostgreSQL/Chromium reali sono **aggiunte al workflow ma non ancora eseguite** per questo package.

## 40 interventi/verifiche

### A. Validazione foto e sicurezza media
1. Ispezione dei metadati dopo lo streaming e prima della pubblicazione.
2. Controllo dimensione fisica massima di 5 MiB.
3. Controllo signature PNG.
4. Controllo PNG IHDR e lunghezza.
5. Controllo profondità, colore, compressione, filtro e interlacciamento PNG.
6. Rifiuto di dimensioni PNG nulle.
7. Rifiuto del lato oltre 4096 px.
8. Rifiuto di più di 16 milioni di pixel.
9. Controllo SOI JPEG.
10. Scansione bounded dei segmenti JPEG.
11. Estrazione dimensioni JPEG dai marker SOF.
12. Rifiuto segmenti JPEG corrotti o privi di SOF.
13. Controllo contenitore RIFF/WebP e lunghezza dichiarata.
14. Supporto metadati WebP VP8X.
15. Supporto metadati WebP VP8L.
16. Supporto metadati WebP VP8 lossy.
17. Rifiuto MIME discordanti e SVG non supportati.
18. Rifiuto immagini tronche, vuote o con intestazioni corrotte.
19. Tre fixture realmente codificate PNG/JPEG/WebP e regressioni Node parametrizzate.
20. Rifiuto immagini corrotte anche in lettura, senza divulgarne il contenuto.

### B. Profilo, privacy e interfaccia
21. GET `/api/auth/profile` autenticato, indipendente dal ruolo di presentatore.
22. Proiezione del profilo limitata ai campi necessari.
23. Risposta profilo con `Cache-Control: private, no-store`.
24. Caricamento automatico del profilo dall'endpoint universale.
25. Stato di salvataggio profilo con prevenzione doppio invio.
26. Stato di caricamento/eliminazione foto condiviso per impedire operazioni concorrenti.
27. Eliminazione foto disabilitata se non esiste una foto.
28. Aggiornamento immediato dell'anteprima con cache busting.
29. Messaggi e vincoli dimensione immagine visibili nell'interfaccia.
30. URL pubblici delle foto legati a sessione e presentatore, senza esporre URL privati.
31. Verifica HTTP pianificata dell'accesso anonimo alle foto nella sessione attiva.
32. Verifica HTTP pianificata del rifiuto dell'URL privato per utenti anonimi.
33. Verifica HTTP pianificata della revoca della foto sostituita.
34. Verifica HTTP pianificata della revoca dopo eliminazione.
35. Verifica HTTP pianificata della chiusura della sessione.

### C. Amministrazione utenti e accettazione
36. Salvataggio atomico di nickname, ruolo e approvazione in un solo UPDATE PostgreSQL.
37. Lock di riga, transazione e rollback per modifiche concorrenti.
38. Gestione esplicita delle collisioni nickname senza aggiornamenti parziali.
39. Protezione amministratore principale e divieto di auto-declassamento; revoca WebSocket solo per variazioni di permessi.
40. Unico pulsante «Salva utente», approvazione modificabile in bozza, ruolo moderatore, prevenzione doppio invio; test HTTP PostgreSQL e browser Chromium reali integrati nella CI opt-in.

## Esiti locali
- **375/375** test Node.js superati (317 baseline precedente; 58 aggiunti in questo ciclo).
- **692/692** test Python superati (660 baseline precedente; 32 nuovi contratti).
- Build backend TypeScript e frontend TypeScript/Vite **PASS**.
- Test di integrazione PostgreSQL e Chromium del nuovo ciclo **non eseguiti localmente**; eseguire la CI estesa con `browser_test=true`.
- Audit RC ponderato **45,5%**, invariato fino a nuove evidenze verificate. Non è una RC certificata.

**Commit suggerito (dopo il commit della baseline profilo, se confermato):** `feat: unify presenter profiles, secure avatar lifecycle and atomic admin user management`

Nessun commit, push, tag o release eseguito da ChatGPT.
