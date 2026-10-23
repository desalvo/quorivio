# Recupero MFA amministrativo — 0.1.0-dev

L'amministratore della piattaforma può azzerare la MFA TOTP di un altro account da **Utenti → dettagli utente → Azzera MFA utente**. I segreti TOTP attivi/in attesa e tutti i codici di recupero vengono revocati in un'unica transazione PostgreSQL. Si chiudono le connessioni WebSocket dell'utente. L'amministratore deve confermare l'azione, digitare la propria password e, se ha TOTP attivo, fornire anche un codice TOTP valido. Non può azzerare la propria MFA né quella dell'amministratore principale protetto. L'elenco utenti espone solo `totp_enabled`, mai i segreti. Il log registra un evento strutturato senza credenziali.

API: `POST /api/admin/users/:id/mfa/reset` con `{ "confirm": true, "admin_password": "...", "admin_totp_code": "..." }`. Richiede il ruolo amministratore piattaforma. L'utente interessato deve effettuare una nuova registrazione MFA.

**Limiti di sicurezza:** Il cookie di autenticazione esistente rimane valido fino alla scadenza; la chiusura WebSocket non equivale a invalidare la sessione. Restano pendenti test E2E PostgreSQL/browser, retention degli audit, rate limiting, verifica della recente autenticazione e notifica email amministrativa. Non considerare questa procedura pronta per il recupero account in produzione senza tali controlli.
