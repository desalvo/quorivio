# SSO OIDC — autenticazione federata (sviluppo)

Quorivio implementa un primo flusso OpenID Connect Authorization Code + PKCE S256, con state/nonce monouso, cookie HttpOnly SameSite=Lax per il solo callback e verifica della firma RS256 mediante JWKS. L'identità si basa su (provider, sub), non sul solo indirizzo email. Le identità vanno collegate esplicitamente a un account locale autenticato e approvato prima del primo login federato. Chi ha attivato TOTP deve continuare a utilizzare il login locale con MFA: il login OIDC viene rifiutato per impedire il bypass del secondo fattore.

## Provider

Si configurano mediante variabili d'ambiente `OIDC_GOOGLE_ISSUER`, `OIDC_GOOGLE_CLIENT_ID`, `OIDC_GOOGLE_CLIENT_SECRET`, `OIDC_GOOGLE_REDIRECT_URI`, e, analogamente, `OIDC_PROVIDERS_JSON*` oppure `OIDC_CUSTOM_*`. Il callback deve corrispondere all'URL pubblico HTTPS `/api/auth/oidc/<provider>/callback` e deve essere registrato presso l'identity provider. Configurare l'issuer esatto dichiarato dal provider, non inventarlo. Un provider viene esposto solo se tutti i parametri sono presenti, HTTPS e sintatticamente validi. Per Google, verificare l'issuer nella documentazione del provider. Per generic OIDC il servizio richiede che il suo identity provider OIDC sia effettivamente abilitato e che il client sia registrato: non è stato eseguito alcun login reale con generic OIDC.

Sono disponibili `GET /api/auth/oidc/providers`, `GET /api/auth/oidc/:provider/start`, `GET /api/auth/oidc/:provider/start?link=true` e `GET /api/auth/oidc/:provider/callback`. Nel profilo di un utente già autenticato viene mostrato «Collega»; in login compare «Accedi con ...». Gli account non collegati non vengono creati o associati automaticamente in base all'email.

## Sicurezza e limitazioni

- **Stato sperimentale**: nonce e verifier sono in memoria locale, quindi callback e avvio devono raggiungere la stessa replica; predisporre storage condiviso per produzione multi-replica.
- Il token ID è verificato usando chiave RSA di JWKS, issuer, audience, nonce, scadenza, emissione ed email verificata. Non viene supportato il token ID con algoritmi diversi da RS256.
- Il collegamento di un'identità deve essere eseguito solo attraverso il proprio account, con login locale precedentemente completato.
- Non sono ancora disponibili OIDC login con TOTP step-up, disconnessione identità, pannello amministrativo dei provider, SAML, Facebook OAuth o GitHub OAuth: questi ultimi due non sono provider OIDC standard con ID token e richiedono integrazioni specifiche o un broker (ad esempio Keycloak).
- Non è stata verificata una sessione reale con alcun provider, né la migrazione `oidc_identities` su PostgreSQL.
- In produzione sono indispensabili TLS pubblico, rate limiting distribuito, audit di sicurezza, revoca/rotazione dei segreti, storage distribuito dello stato e browser test.
