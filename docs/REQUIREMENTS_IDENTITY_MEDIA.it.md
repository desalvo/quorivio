# Identità e contenuti multimediali — Quorivio 0.1.0-dev

Implementati nei sorgenti: registrazione locale in stato pending; approvazione e ruolo gestiti da admin; obbligo cambio password iniziale; ingresso anonimo con pseudonimo e cookie tecnico; preferenza di accesso anonimo per sessione; layout JSON con loghi, sfondo e risorse multimediali HTTPS; URL pubblico configurabile; retention delle sessioni chiuse a 60 giorni (configurabile).

Le credenziali di dimostrazione admin@example.com / 000000 sono consentite solo con ALLOW_INSECURE_DEV_BOOTSTRAP=true e NODE_ENV diverso da production, con cambio obbligatorio della password. **Non utilizzare su server pubblici**. Le installazioni esistenti non vengono reimpostate.

Incompleti: SSO, MFA TOTP/email, configurazione SMTP/SMTPS e email di test, upload sicuro e gestione file, editor visivo avanzato/template, personalizzazione risultati live, partecipazione autenticata, self-registration UI, CRUD utenti completo via UI, XLSX, consenso cookie completo, GDPR e audit di sicurezza. URL HTTPS per media esterni non equivale a validazione contenuti o sicurezza del provider. Non dichiarare pronto per produzione.

Aggiornamento: UI per registrazione locale, creazione/modifica/eliminazione utenti admin, accesso anonimo e pubblicazione opzionale dei risultati live introdotti nei sorgenti; la CI e i test di integrazione restano da eseguire.
