# Quorivio 0.1.0-dev — Profile integration cycle

## 26 ottobre 2026 — Profilo presentatore e avatar pubblico (dopo CI verde 40304413948 già committata)
- L'utente ha confermato il commit dell'ultimo hotfix menu contestuale. GitHub run `40304413948`: quality gate `121510438909` e container build `121512122765` SUCCESS; pubblicazione SKIPPED. Nuova baseline committata: non ripetere i vecchi hotfix nel messaggio di commit successivo.
- **Correzione funzionale:** il widget profilo pubblico utilizzava l'URL privato `/api/auth/profile/photo/:id`, inaccessibile ai partecipanti anonimi. L'endpoint pubblico ora restituisce soltanto `id`, `name` e `photo_url` riferito alla sessione, con segmenti URL codificati. Non espone URL privati né altre colonne dell'utente; `Cache-Control: no-store`.
- **Un solo salvataggio:** nickname e nome visualizzato vengono validati e aggiornati atomicamente in PostgreSQL, con lock per utente, un solo UPDATE, protezione nickname admin primario e gestione dei duplicati. Restano compatibili gli endpoint legacy di modifica singola.
- **Concorrenza foto:** il PATCH legacy del nome non riscrive più una `profile_photo_url` letta prima, evitando di annullare caricamenti o cancellazioni concorrenti.
- **Interfaccia:** caricamento automatico del profilo, un solo pulsante «Salva profilo», caricamento/rimozione foto separati. Il widget pubblico usa esclusivamente `photo_url`.
- Verifiche locali: 3 nuovi test Node e 8 contratti Python; **317/317 Node**, **660/660 Python**, build API TypeScript e web TypeScript/Vite PASS. Transazione PostgreSQL reale e visualizzazione avatar nel browser anonimo ancora da collaudare in CI. RC **45,5%**, C4 parziale. Nessun commit/push/tag/release eseguito in questo ciclo.

