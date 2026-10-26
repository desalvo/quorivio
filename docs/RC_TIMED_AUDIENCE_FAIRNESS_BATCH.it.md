# Batch RC — quiz temporizzati, domande tematiche e classifiche ex aequo (26/10/2026)

**Baseline già committata:** `d4ccead518f00ce00f6cd58cb0ff93fc81a26f91`. CI standard `40368807527` e completa Chromium/PostgreSQL `40369919680` **PASS**; pubblicazione **SKIPPED**. Le modifiche sottostanti sono **successive al commit**.

## Sviluppi funzionali

1. **B2: connessioni PostgreSQL** — riconoscimento partecipante prima di prendere una connessione dal pool; mantenuti lock transazionali di sessione/pagina, revisioni, controlli di validità e durata. Rilascio della connessione dopo COMMIT e prima di broadcast/WebSocket.
2. **B2: risposte ripetute dopo scadenza** — se una risposta al widget è già salvata, un retry dopo la scadenza restituisce `already_submitted:true` senza sovrascrivere né riassegnare punteggi. Risposte nuove e tardive restano vietate: riferimento orario PostgreSQL (`clock_timestamp()`). Anche il quiz temporizzato tradizionale accetta correttamente i retry, usa solo il proprio tipo per il controllo della durata e rilascia il pool prima delle notifiche.
3. **B2/A3: classifiche e pari merito** — entrambe le classifiche private del presentatore calcolano `rank() over (order by elapsed_ms)` nel database prima della paginazione. Tempi identici producono posizioni identiche (es. 1,1,3). Ordinamento secondario stabile, revisione dei widget, esclusione risposte invalidate e privacy invariati.
4. **B3: limite atomico domande tematiche** — transazione e `FOR UPDATE` sul partecipante dopo aver bloccato la pagina attiva: 12 invii concorrenti non possono superare le 10 domande per widget. Le pagine scadute, cambiate o chiuse non accettano scritture. Notifica dopo commit/rilascio.
5. **A3: interfaccia accessibile** — posizioni a pari merito esplicite e senza chiavi React duplicate; invio al widget protetto dal doppio clic, disattivazione dei pulsanti senza risposta, segnalazione `aria-busy` e messaggi `role=status` per successo/scadenza.

## Verifiche e limiti

- **447/447 test Node PASS**, compresi cinque nuovi contratti di regressione.
- Suite Python selezionate: **21 widget + 18 moderazione + 15 browser + 6 nuovi = 60/60 PASS**.
- Parsing del server TypeScript, compilazione Python e parsing YAML: **PASS**.
- Suite Python complessiva tentata, ma oltre il timeout locale nei test HTTP del convertitore: non considerata superata.
- Build completa TypeScript/Vite, test PostgreSQL 18 e Chromium sul **nuovo batch**: **DA VERIFICARE SU GITHUB**.
- Il nuovo test CI obbligatorio `tools/ci_timed_widgets_postgres.py` verifica dodici client con gli stessi cookie, quota 10/12, classifica con tempi identici tramite fixture SQL, retry e scadenza per widget/quiz tradizionali e isolamento accessi. Richiede esplicitamente server locale effimero, flag dedicato e token sicuro. **Non è stato ancora eseguito con PostgreSQL reale**.

## Gate RC

- B3: PostgreSQL e Chromium passati in CI `40368807527` / `40369919680`, ma resta **partial** per accessibilità/Firefox/WebKit/dispositivi indipendenti e nuovo test della quota.
- B2/A3: **partial** in attesa di nuova CI e verifiche visive, latenza e accessibilità.
- D1: accettato per la precedente baseline CI verde; le modifiche nuove richiedono una nuova CI verde.
- RC ponderata: **48,0% (1 accepted, 15 partial, 2 open)**; non equivale alla percentuale dei test né ad una release pronta.
- Pubblicazione Docker esclusivamente **opt-in manuale**, consenso separato per `latest`. Nessun commit, push, tag o release dell'assistente.

**Verifiche suggerite:** push con CI standard (pubblicazione SKIPPED), poi CI manuale con `browser_test=true` e `publish_image=false`. Il carico opzionale 500 utenti è distinto.
