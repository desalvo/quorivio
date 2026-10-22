# Recupero password sicuro — Quorivio 0.1.0-dev

- Il pulsante «Password dimenticata?» nella schermata di login invia una richiesta generica che non rivela l'esistenza dell'account.
- Serve SMTP configurato su SMTPS (TLS implicito). In assenza di configurazione il servizio segnala `recovery_not_configured`.
- I link contengono token casuali di 256 bit, sono validi 20 minuti e utilizzabili una sola volta. In PostgreSQL viene salvato solo SHA-256 del token.
- Richieste successive per coppia IP/email vengono limitate a un tentativo al minuto; il limite supplementare globale API resta in vigore.
- Dopo la modifica, la sessione del browser viene cancellata. I token di autenticazione esistenti precedenti al cambio di password vengono respinti dal middleware di autorizzazione per le API protette.
- La modifica della password non disabilita l'autenticazione TOTP: il secondo fattore resta obbligatorio al login.
- I token non vengono mai riportati nel risultato HTTP e il server non stampa link di recupero nei log.

## Limiti e verifiche ancora necessarie
- Verifica end-to-end PostgreSQL, SMTP reale e browser multiutente non eseguita.
- Verificare HTTPS e `PUBLIC_BASE_URL` prima di abilitare il servizio di recupero in produzione.
- Il rate limit è in-memory per processo e non è un controllo distribuito: occorre un backend condiviso (Redis o DB) per cluster.
- Valutare audit, CSRF su client senza header Origin e ulteriori difese contro abusi prima della messa in esercizio.
- SSO Google/GitHub/Facebook e generic OIDC non è ancora implementato.
