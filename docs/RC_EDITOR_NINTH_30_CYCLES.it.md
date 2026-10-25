# Batch 9 — 30 interventi sostanziali: editing concorrente, persistenza reale e recupero conflitti

**Baseline confermata:** commit dell'ottavo batch e CI GitHub Actions 40192172978: qualità, container e pubblicazione **SUCCESS**. I 240 interventi/scenari precedenti **non sono** parte delle modifiche del nuovo commit.

## Inventario verificabile dei 30 interventi

1. Colonna PostgreSQL `design_revision` per pagina.
2. Versione grafica indipendente dalla `revision` usata dalle attività live.
3. Compatibilità di migrazione `ADD COLUMN IF NOT EXISTS` per database già esistenti.
4. Lettura della versione sotto `SELECT … FOR UPDATE` durante il salvataggio.
5. Campo facoltativo `expected_design_revision` per client API esistenti.
6. Validazione stretta di interi positivi sicuri, esclusi float/stringhe/booleani.
7. Rifiuto HTTP 409 di salvataggi da versioni obsolete.
8. Risposta di conflitto con sola versione corrente, senza contenuti o dati privati.
9. Rollback della transazione in caso di conflitto prima di modificare widget e revisioni.
10. Incremento atomico della versione nel medesimo `UPDATE` dei due layout.
11. Restituzione della nuova versione nel risultato HTTP.
12. Esposizione della versione nel normale snapshot PostgreSQL delle attività.
13. Memorizzazione della versione letta quando si apre una pagina nell'editor.
14. Invio automatico della versione attesa da ogni salvataggio del browser.
15. Aggiornamento della versione locale soltanto dopo conferma di salvataggio.
16. Messaggio di conflitto comprensibile e accessibile all'autore.
17. Conservazione integrale della bozza locale dopo HTTP 409.
18. Blocco dei successivi salvataggi mentre esiste un conflitto irrisolto.
19. Pulsante dedicato di recupero dalla versione server.
20. Conferma esplicita prima di scartare la bozza locale.
21. Ripristino di widget, colori, sfondi, intestazioni e versione dal server.
22. Correzione della rilevazione delle modifiche allo sfondo domanda.
23. Correzione della rilevazione delle modifiche allo sfondo risultati.
24. Firma unica e deterministica della bozza caricata e di quella modificata.
25. Test unitari per tutte le proprietà della bozza e versioni malformate.
26. Smoke PostgreSQL obbligatorio con due cookie jar autenticati indipendenti.
27. Smoke di concorrenza PostgreSQL: due writer sulla stessa revisione, un solo vincitore.
28. Test HTTP reali per versioni errate, validazione geometrica, colori/contorni, pagine indipendenti e sessioni chiuse.
29. Accettazione Chromium opt-in **senza mock**, con salvataggio PostgreSQL, ricaricamento, conflitto e recupero.
30. Integrazione CI con artifact diagnostici solo in caso di errore, aggiornamento inventari IT/EN e matrice RC.

## Stato delle verifiche

- Build TypeScript API e frontend Vite: PASS in locale.
- Node.js: **244/244 PASS**.
- Contratti Python del nuovo batch: **18/18 PASS**.
- Test PostgreSQL concorrente e Chromium reale: **scritti ma non eseguiti** in questo ambiente (mancano PostgreSQL locale e navigazione Chromium su localhost).
- GitHub CI per il nuovo batch: **da eseguire**. Per la prova browser eseguire `browser_test=true`; il test PostgreSQL HTTP viene sempre eseguito.
- Gate A1 ancora **partial**, score RC invariato **45,5%**. Nessun commit/push/tag eseguito.
