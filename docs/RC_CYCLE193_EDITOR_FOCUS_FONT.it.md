# RC193 — Stabilità del focus e formattazione font (Quorivio 0.1.0-dev)

## Problemi corretti

- Il problema era intermittente e dopo il reload scompariva: le caselle rich-text conservavano selezioni ormai scadute. Durante il rerender causato da una modifica a un altro campo, tutte le caselle con un cursore memorizzato tentavano di ripristinarlo. La gestione della selezione è ora limitata all'elemento effettivamente attivo; il blur cancella la vecchia posizione e le caselle immutate non ricreano il DOM.
- «Formato widget» mostra una box numerica **sempre presente** per la dimensione del font, in ogni ambito, con frecce su/giù azionabili da mouse e tastiera; digitazione libera e conferma mediante Invio o perdita del focus, ripristino del valore su input non valido. Rimangono i controlli proporzionali A−/A+ per «Widget intero».
- Font Arial predefinito per domande/sondaggi e relative opzioni anche nei layout precedenti privi di override. Il font selezionato per «Widget intero» raggiunge risposte e domande indipendenti. Corretto il CSS storico che sovrascriveva i font delle opzioni; la dimensione delle risposte resta configurabile autonomamente.

## Verifiche e limiti

- Suite Node complete API/frontend, preflight Python RC193, test delle regole di formattazione e dei marcatori rich-text.
- Compilazione sintattica isolata dei moduli TS/TSX modificati.
- Alla CI è stato aggiunto un test Chromium sul React compilato con PostgreSQL locale, autenticazione e sessione temporanea: crea tre opzioni, memorizza un caret nell'ultima, scrive una frase nella prima e nelle proprietà senza ricaricare; verifica frecce dimensione e Arial/Georgia. Richiede la prossima CI per la certificazione.
- Nessuna modifica ad API, persistenti dati risposte, chiavi Vero/Falso o autorizzazioni.
- Versione mantenuta `0.1.0-dev`, punteggio certificato invariato **85,25%**. Flag: `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag dell'assistente.
