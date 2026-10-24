# Quorivio 0.1.0-dev — Lotto 20 interventi: percorso partecipante

**Baseline committata dall'utente:** `quorivio-0.1.0-dev-editor-20-cycle-rc-evidence-cumulative.zip`. Workflow GitHub `40143475939`: quality gate e container build gate SUCCESS; pubblicazione SKIPPED. Questa baseline ha già superato Chromium editor ampliato (205 test Node e 277 Python nella run) e, nella precedente run `40141894130`, il carico opt-in di 500 partecipanti.

## Inventario delle 20 chiusure e miglioramenti

1. Normalizzazione sicura del codice sessione digitato, con conversione maiuscola del codice esadecimale.
2. Supporto all'incolla di URL QR completi e segreti alfanumerici case-sensitive.
3. Rifiuto di codici malformati, segmenti aggiuntivi e percent-encoding non valido.
4. Stato di caricamento esplicito della pagina pubblica.
5. Errore «sessione non disponibile» con possibilità di riprovare e cambiare codice.
6. Endpoint `GET /api/join/:code/participation` per ripristinare una partecipazione esistente dal cookie HttpOnly.
7. Protezione della risposta di recupero: solo booleano, `Cache-Control: no-store, private`, senza token/pseudonimo.
8. Rispetto della revoca della partecipazione anonima nel controllo di recupero.
9. Verifica della partecipazione prima di mostrare il modulo di nuovo accesso, evitando duplicazioni dopo reload.
10. Accesso protetto contro invii simultanei; pseudonimo normalizzato solo dopo consenso ai cookie funzionali.
11. Invio delle risposte protetto contro doppi clic e invii concorrenti.
12. Validazione client per modalità singola, multipla, testo e allegato, lasciando la validazione autoritativa al server.
13. Stato `aria-pressed` delle opzioni, gruppo semanticamente etichettato e feedback di conferma `aria-live`.
14. Collegamento «Vai al contenuto principale» e focus visibile per navigazione da tastiera.
15. Su smartphone, i widget assoluti diventano un elenco leggibile, senza sovrapposizioni o rotazioni forzate.
16. Pulsanti partecipante di almeno 44px e protezioni CSS per larghezze ridotte/forced-colors.
17. Riconnessione WebSocket con backoff limitato e gestione offline/online, evitando retry su chiusure definitive.
18. Selezione pagina live vincolata allo stato attivo e all'ID pubblicato; risultati filtrati esclusivamente dal server.
19. Nuovo collaudo opt-in Chromium **sulla UI di produzione servita dall'API PostgreSQL reale**, non sulla fixture Vite: due cookie jar indipendenti, URL QR e codice breve, risposte, privacy report, idempotenza, reload e mobile.
20. Estensione del collaudo HTTP PostgreSQL con recupero cookie, test negativi di identità e rifiuto a sessione chiusa; caricamento diagnostica CI, contratti Node/Python e documentazione IT/EN.

## Verifiche e limiti

- Test locali: Node **215/215**, Python **282/282**, build API TypeScript e web TypeScript/Vite **PASS**.
- Chromium locale: non eseguibile per il blocco dell'ambiente `net::ERR_BLOCKED_BY_ADMINISTRATOR` su localhost. Il **nuovo** collaudo Chromium/PostgreSQL non è ancora stato eseguito su GitHub.
- La precedente CI `40143475939` è verde su qualità e container; il carico di 500 partecipanti resta confermato nella precedente `40141894130`. Non confondere queste prove con una certificazione di produzione.
- Gate A4 ancora **open**, B4 ancora **partial**, A1 ancora **partial**: l'accessibilità reale con screen reader, il laboratorio dispositivi, la privacy browser e il carico sostenuto in staging devono essere accettati dopo test indipendenti.
- Score ponderato RC **45,5/100 invariato**: nessuna nuova accettazione è rivendicata senza esecuzione CI dei nuovi test.
- Nessun commit, push, tag, release o deploy eseguito dall'assistente.

## Prossima azione

Commit dell'unico ZIP cumulativo e workflow manuale con `browser_test=true`. Il nuovo step «Chromium participant UI and PostgreSQL lifecycle (opt-in)» eseguirà il browser contro la UI servita da `127.0.0.1:8080` e l'API PostgreSQL 18; i fallimenti producono l'artifact `chromium-participant-failure` (retention 3 giorni). `capacity_test=true` non è necessario per questa modifica, poiché il test da 500 è già passato e la logica di carico non è stata modificata.
