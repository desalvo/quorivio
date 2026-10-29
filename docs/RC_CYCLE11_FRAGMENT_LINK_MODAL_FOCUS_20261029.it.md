# Ciclo RC 11 — link recupero password in frammento, focus anteprima e inventari immutabili

**Quorivio 0.1.0-dev / EUPL-1.2 / 29 ottobre 2026**

## Interventi

- Le nuove email di recupero password usano un frammento URL `#reset_token=…`, non trasmesso al server nella richiesta HTTP. L'applicazione React rimuove immediatamente il frammento dalla cronologia e mantiene il token soltanto nello stato del componente. I vecchi link con token in query rimangono validi e vengono anch'essi ripuliti.
- Il test PostgreSQL 18/SMTP TLS in ambiente CI isolato verifica che i nuovi link contengano il token soltanto nel frammento, preservando scadenza, digest, consumo singolo e revoca delle sessioni. HTTP ammesso solo per loopback CI; fuori da loopback è richiesto HTTPS nello script. **Il nuovo percorso non è ancora passato sulla CI GitHub.**
- L'anteprima intercetta anche gli spostamenti di focus effettuati via script o navigazione assistiva, non solo Tab. Alla chiusura ripristina focus e attributi `aria-hidden`/`inert`. L'automazione Chromium non sostituisce le prove indipendenti con screen reader.
- Preservati gli inventari SHA-256 storici senza modificarne i checksum. I controlli del formato storico rimangono attivi, mentre il nuovo inventario del ciclo 11 valida la sorgente corrente e lo ZIP completo in CI.

## Limiti e prossimi passi

Build e test locali TypeScript, Node, Python e Chromium superati. Mancano PostgreSQL/SMTP TLS reale sulla nuova revisione, Firefox/WebKit, touchscreen/screen reader, infrastrutture e approvazioni indipendenti. L'ultima Full CI verde `40717525524` riguarda il codice precedente (`f6738592c648bc620e01b92d2bbaa6b90b459287`).

**RC: 74,0%, invariata; 40 gate, 23 accettati e 17 parziali.** Nessuna promozione di gate con sole prove locali. RC rigorosa bloccata.

Dopo il commit dell'utente, avviare manualmente `browser_test=true`, `capacity_test=true`, `publish_image=false`, `publish_latest=false`; verificare PostgreSQL/SMTP TLS, Chromium e sicurezza prima di riconciliare i gate. Nessun commit/push/tag/Docker push automatico.
