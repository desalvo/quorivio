# Registro GDPR e privacy by design — 0.1.0-dev

**Stato:** salvaguardie tecniche iniziali e pianificazione; **non si dichiara conformità GDPR**. Prima della produzione, titolare e responsabili devono definire ruoli, basi giuridiche, informative artt. 13/14, eventuali accordi art. 28, trasferimenti internazionali, conservazione e procedura incidenti. Serve revisione legale e valutazione dell'eventuale necessità di DPIA (art. 35).

## Dati trattati

- Presentatore: email, hash protetto della password e organizzazione; finalità: gestione sessioni e accesso.
- Partecipante: credenziale pseudonima casuale e risposta associata alla sessione; può costituire comunque dato personale. La modalità «anonima» dell'interfaccia non equivale all'anonimato giuridico.
- Dati di rete/log: dipendono anche da ingress e gestore infrastrutturale; minimizzare i tempi di conservazione ed escludere token e credenziali dai log.
- SSO esterni: **non implementati**; servono informative e verifiche specifiche per provider.

## Requisiti e lacune

| Requisito | Evidenza attuale | Ancora da completare |
| --- | --- | --- |
| Minimizzazione | identificativi pseudonimi nei sondaggi | registro finalità e basi giuridiche |
| Accessi | controlli del proprietario API | test isolamento organizzazioni e audit |
| Sicurezza archivio | PostgreSQL e Secret referenziati | policy cifratura, TLS, backup |
| Conservazione | non applicata automaticamente | scadenze, cancellazione, retention backup |
| Diritti interessati | non implementati | accesso, portabilità, rettifica, cancellazione |
| Incidenti | sola documentazione | procedura e registro degli incidenti |
| Responsabili trattamento | hosting autonomo possibile | DPA e trasparenza sui fornitori |
| Informative | non implementate | informative IT/EN al momento della raccolta |
| DPIA | pendente | valutazione necessità ed eventuale esecuzione |

Non definire una sessione «rigorosamente anonima» senza prove sulla non riconducibilità dei dati. PostgreSQL non deve essere esposto pubblicamente. I manuali sono istruzioni, non una certificazione di conformità.

## Ciclo di sviluppo: controlli operativi introdotti
- `PATCH /api/sessions/:id/retention` consente al proprietario di fissare la conservazione della sessione fra 1 e 3650 giorni (predefinito: 90). Il valore conta dalla creazione; la cancellazione automatica avviene solo quando la sessione è chiusa o scaduta.
- `POST /api/sessions/:id/revoke` chiude la sessione, fa scadere l'accesso pubblico, ruota link e codice, disconnette le sottoscrizioni WebSocket.
- `DELETE /api/sessions/:id` cancella la sessione e, con i vincoli PostgreSQL `ON DELETE CASCADE`, attività, risposte e partecipanti associati. Non cancella copie già esportate e backup: documentare il ciclo di vita dei backup prima del rilascio.
- Le esportazioni CSV neutralizzano le celle potenzialmente interpretabili come formule.
- Un partecipante che ripete il join con un cookie valido mantiene la stessa identità tecnica e le risposte confermate.

**Limiti:** prove reali con PostgreSQL, verifica del TTL dei backup, formalizzazione delle basi giuridiche, esercizio dei diritti GDPR e verifica legale restano aperti. Le funzioni non costituiscono certificazione di conformità GDPR.
