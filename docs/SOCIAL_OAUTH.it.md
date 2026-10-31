# OAuth2 GitHub e Facebook — Quorivio 0.1.0-dev

## Aggiornamento RC61

La sezione SSO elenca i collegamenti GitHub/Facebook esistenti e consente di scollegarli dopo conferma e nuova verifica della password, con limite distribuito di 5 tentativi/minuto. Il flow OAuth monouso ora risiede in PostgreSQL condiviso, non più in memoria locale; la relativa prova di scollegamento HTTP/DB è preparata nella CI, non ancora eseguita. Il consenso reale dei provider e l'approvazione dell'operatore rimangono aperti. Le note storiche seguenti risalgono al primo ciclo OAuth.


## Scopo
I provider GitHub e Facebook dispongono di percorsi OAuth2 dedicati, distinti dagli identity provider OIDC. Il collegamento a un account locale approvato è **esplicito**: non è ammesso il collegamento automatico tramite email.

## Configurazione (HTTPS obbligatorio)
- `OAUTH_GITHUB_CLIENT_ID`, `OAUTH_GITHUB_CLIENT_SECRET`, `OAUTH_GITHUB_REDIRECT_URI` (callback: `/api/auth/social/github/callback`)
- `OAUTH_FACEBOOK_CLIENT_ID`, `OAUTH_FACEBOOK_CLIENT_SECRET`, `OAUTH_FACEBOOK_REDIRECT_URI` (callback: `/api/auth/social/facebook/callback`)

I callback registrati nei provider devono coincidere con gli URL HTTPS configurati.

## Sequenza di utilizzo
1. L'utente accede con l'account locale approvato e, nel profilo, seleziona **Collega GitHub** o **Collega Facebook**.
2. La richiesta porta al consenso del provider. Lo stato casuale è verificato e usato una volta; la callback recupera l'ID immutabile dell'utente tramite API HTTPS.
3. Il collegamento è archiviato nella tabella esistente `oidc_identities` per conservare un registro unificato delle identità esterne.
4. Ai successivi accessi è possibile scegliere il provider, purché l'account sia approvato e non richieda cambio password. L'MFA TOTP locale non è aggirabile: per gli utenti con MFA attiva rimane necessario il login locale con secondo fattore.

## Limiti e sicurezza
Le sessioni OAuth sono memorizzate **in memoria sul singolo processo**, quindi non sono pronte per repliche multiple. In questo ciclo non sono stati effettuati login reali contro i provider, test PostgreSQL, browser o verifiche della build completa. Gli endpoint non creano autonomamente nuovi account. Per Facebook viene applicato il parametro `appsecret_proof`; per GitHub viene usato l'endpoint ufficiale `/user`. Evitare segreti nei log. Valutare configurazione proxy sicura, policy applicative Meta e gestione revoche prima della produzione.
