# Quorivio 0.1.0-dev — decimo lotto editor: 30 interventi e criteri di accettazione

**Baseline confermata:** GitHub Actions 40192172978 (qualità, container, pubblicazione tutti SUCCESS). Il nono lotto sulla concorrenza PostgreSQL è ancora **non committato**; questo decimo lotto è cumulativo con il nono. Non eseguire commit, push o release automaticamente.

## 30 interventi sostanziali di riconciliazione collaborativa

1. Conservazione della **bozza base** da cui il presentatore ha iniziato a modificare la pagina.
2. Recupero della **versione remota aggiornata** tramite snapshot autenticato, senza fidarsi del contenuto locale obsoleto.
3. Integrazione con il **compare-and-swap PostgreSQL** del lotto precedente: ogni salvataggio riconciliato conserva la revisione remota attesa.
4. Merge a tre vie indipendente dell'intestazione domanda.
5. Merge a tre vie indipendente dell'intestazione risultati.
6. Merge separato dei colori di sfondo domanda e risultati.
7. Merge separato degli URL di sfondo domanda e risultati.
8. Merge separato degli asset di sfondo domanda e risultati.
9. Riconciliazione dei widget tramite **identificatore stabile**, non tramite indice di array.
10. Merge ricorsivo delle proprietà indipendenti di uno stesso widget.
11. Riconciliazione separata delle coordinate X/Y e delle dimensioni.
12. Riconciliazione delle proprietà annidate di stile, senza perdere i cambiamenti indipendenti.
13. Array interni trattati atomicamente in caso di modifiche concorrenti, senza produrre opzioni ibride.
14. Conservazione delle aggiunte locali non conflittuali.
15. Conservazione delle aggiunte remote non conflittuali.
16. Conservazione simultanea di aggiunte locali e remote con ID differenti.
17. Conflitto esplicito in caso di **inserimento simultaneo dello stesso ID** con contenuti diversi.
18. Gestione delle cancellazioni senza conflitto quando l'altro presentatore non ha modificato il widget.
19. Conflitto esplicito in caso di **cancellazione contro modifica** dello stesso widget.
20. Conservazione del riordino locale quando la controparte modifica soltanto i contenuti.
21. Conservazione del riordino remoto quando la controparte modifica soltanto i contenuti.
22. Conflitto esplicito per riordini incompatibili dello stesso insieme di widget.
23. Interfaccia di confronto con descrizione dei campi e **valori locale/server** (anteprima limitata a 240 caratteri).
24. Risoluzione **per singolo conflitto**, scegliendo consapevolmente la versione locale o remota.
25. Comandi di scelta locale/server per tutti i conflitti, senza selezione automatica predefinita.
26. **Esportazione JSON della bozza locale** prima di eventuale scarto, con identificativo pagina e revisione base.
27. Nuova lettura server **prima dell'applicazione** del merge: se la revisione è cambiata, annullamento dell'applicazione e nuova analisi.
28. Blocco dell'applicazione se la bozza cambia mentre si attende il controllo di freschezza; nessuna pubblicazione automatica.
29. Pannello responsive, selettori da almeno 44 px, focus visibile, etichette accessibili e messaggi di stato.
30. Accettazione Chromium opt-in estesa su **PostgreSQL reale**: merge disgiunto, CAS, conferma che il merge non salva da solo, conflitto sullo stesso campo, scelta locale e ricarica distruttiva confermata.

## Evidenza e limiti

- **40 test Node.js** di comportamento del merge (inserimenti, cancellazioni, proprietà annidate, riordini, sicurezza, immutabilità); **12 test Python** di contratti UI/CI.
- Build API TypeScript e frontend Vite; test Node eseguiti localmente.
- La prova Chromium/PostgreSQL di questo lotto **non è stata eseguita** in locale. Deve essere eseguita con `browser_test=true` nella CI.
- La riconciliazione avviene nella **bozza locale**: il salvataggio finale è manuale e soggetto nuovamente al CAS PostgreSQL. Non è un editor collaborativo real-time con presenza/cursori condivisi.
- La percentuale RC resta **45,5%** fino a evidenze CI e revisione formale della matrice.
