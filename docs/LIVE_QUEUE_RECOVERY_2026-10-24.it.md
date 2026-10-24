# Coda snapshot live: recupero errori e limiti di accettazione

La coda per sessione accorpa le notifiche concorrenti in una lettura finale del database. Le chiamate durante una lettura attendono ora il completamento effettivo. Gli errori vengono registrati e propagati anche quando una successiva lettura riesce, consentendo la riconnessione del listener PostgreSQL e la risincronizzazione. Dopo un errore la coda è riutilizzabile.

## Evidenze
- `npm run build`: TypeScript backend e frontend TypeScript/Vite PASS.
- `npm run test -w @quorivio/api`: 152/152 PASS.
- `python -m pytest -q tools/tests`: 252 PASS, 10 sottotest PASS.
- Nuovi test per completamento concorrente e recupero dopo errore.

## Ancora da collaudare
- Multi-replica PostgreSQL 18, due browser, 500 partecipanti e latenza reale non verificati in questo ciclo.
- Gate RC B1 ancora parziale. Nessuna modifica a server reali, GitHub o release.
