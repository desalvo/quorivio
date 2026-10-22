# Autenticazione TOTP e servizio SMTP — 0.1.0-dev

## MFA TOTP

Quorivio supporta l'autenticazione locale mediante password e un secondo fattore TOTP standard a 6 cifre, con intervallo di 30 secondi e tolleranza di ±1 intervallo. Dopo il login, aprire la sezione MFA e scegliere **Configura MFA**. Importare il segreto nell'app autenticatore usando il link `otpauth://` o il codice visualizzato; inserire un codice valido per confermare. La protezione del login entra in funzione solo dopo la conferma. Per accedere successivamente inserire email, password e codice MFA. Per disattivare sono richiesti password e codice MFA corrente.

I segreti attivi e in fase di attivazione sono cifrati a riposo con AES-256-GCM, utilizzando una chiave derivata da `AUTH_SECRET`. **Conservare `AUTH_SECRET` in modo permanente e protetto**: modificarlo impedisce la decifratura dei segreti esistenti. Non includere il segreto TOTP in log o ticket. Non sono ancora disponibili codici di recupero, blocco per singolo account e recupero amministrativo verificato; prevedere una procedura di emergenza prima dell'uso obbligatorio. La tolleranza e il replay dei codici richiedono ulteriore hardening.

## Email SMTPS

Configurare nell'ambiente `SMTP_HOST`, `SMTP_PORT` (default 465), `SMTP_SECURE=true`, `SMTP_USER`, `SMTP_PASSWORD` e `SMTP_FROM`. Non scrivere password nei file pubblicati. Nella schermata **Amministrazione → SMTP/SMTPS** usare **Verifica configurazione** e inviare un messaggio di test a un destinatario esplicito. L'API non espone password e utilizza TLS con certificato verificato. La modalità SMTP in chiaro e STARTTLS opportunistico non sono abilitate.

L'invio del messaggio di test richiede l'installazione della dipendenza runtime `nodemailer`, prevista nel package API. Non è stato effettuato un test con un SMTP reale. Questo ciclo non abilita automaticamente email di approvazione, reset password o notifiche. Le credenziali SMTP sono gestite esclusivamente tramite variabili d'ambiente: l'editor amministrativo delle credenziali non è ancora disponibile.

## Ambiti ancora aperti

SSO Google, GitHub, Facebook e generic OIDC non sono connessi a provider reali. Sono da realizzare: collegamento account, callback OIDC/SAML, protezione state/nonce/PKCE, configurazione per tenant, reset password sicuro tramite email, recovery MFA, anti-bruteforce distribuito e test browser/PostgreSQL/SMTP/CI. Nessuna certificazione AgID o GDPR viene rivendicata.
