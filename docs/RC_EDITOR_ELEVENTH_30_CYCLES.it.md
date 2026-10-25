# Undicesimo batch editor — 30 interventi/criteri di recupero

Baseline: workflow 40192172978 committato; i batch nono e decimo restano non committati. Questo terzo lotto porta a **90 interventi/criteri cumulativi** dall’ultimo commit.

Gli elementi comprendono comportamenti funzionali e criteri di accettazione distinti; **non** sono 30 nuove macrofunzionalità.

1. Backup JSON della bozza versione 2.
2. Inclusione della versione base verificata nei backup.
3. Conservazione dell’identificativo di sessione.
4. Conservazione dell’identificativo di pagina.
5. Conservazione della revisione per la concorrenza.
6. Conservazione di intestazioni e sfondi.
7. Conservazione dei widget modificabili.
8. Esportazione manuale dall’editor.
9. Importazione da file senza storage automatico.
10. Limite di importazione a 2 MB.
11. Rifiuto JSON non valido.
12. Rifiuto di formati non supportati.
13. Rifiuto di sessioni differenti.
14. Rifiuto di pagine differenti.
15. Rifiuto di revisioni non valide.
16. Validazione degli otto campi testuali.
17. Validazione quantità widget e ID univoci.
18. Validazione dei tipi widget.
19. Blocco chiavi che alterano i prototipi.
20. Limiti a profondità e complessità JSON.
21. Rifiuto di numeri invalidi e testi troppo lunghi.
22. Lettura della versione server prima del recupero.
23. Blocco se la pagina cambia durante l’importazione.
24. Conferma esplicita prima di sostituire una bozza.
25. Ripristino locale senza pubblicazione alla stessa revisione.
26. Merge a tre vie per bozze v2 obsolete.
27. Blocco del recupero non sicuro da v1 obsolete.
28. Scelta esplicita dei campi importati in conflitto.
29. Nuova verifica della revisione prima del merge.
30. Estensione collaudi reali Chromium/PostgreSQL e regressioni.

Evidenze: Node 314/314, Python 621/621, typecheck isolato del modulo TypeScript e analisi sintattica TSX PASS. Build completo API/frontend non eseguibile perché npm ci non è terminato nell’ambiente locale. Collaudo reale Chromium/PostgreSQL esteso nell’opt-in browser_test; **non eseguito localmente**. RC 45,5%, A1 parziale.

Sicurezza/privacy: i backup JSON manuali contengono layout e identificativi asset; proteggere il file scaricato. Non si usa localStorage/sessionStorage e l’importazione non invia PATCH.

Da fare: commit dei tre batch editor, CI con browser_test=true, verifica CAS PostgreSQL/recupero e accettazione indipendente browser/dispositivi/accessibilità.
