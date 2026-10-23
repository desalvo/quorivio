# Secondo fattore email — stato di implementazione

La verifica email facoltativa è configurabile nella pagina di sicurezza dell'account, purché un amministratore abbia impostato SMTP. Attivazione e disattivazione richiedono password corrente e codice TOTP se configurato, e obbligano a un nuovo accesso.

Dopo password/TOTP corretti, l'API crea una sfida UUID casuale con digest HMAC-SHA256 del codice, scadenza dopo cinque minuti e massimo cinque tentativi in PostgreSQL. Il cookie di accesso viene emesso soltanto dopo il consumo transazionale della sfida. L'accesso SSO è rifiutato per gli account con TOTP o MFA email attivi per evitare l'aggiramento del secondo fattore.

**Limiti di verifica:** le build di produzione e i test di contratto sul codice sono superati. Invio SMTP, concorrenza, migrazione PostgreSQL, flussi browser, prevenzione dell'enumerazione e comportamento multi-replica richiedono test di integrazione. Il codice email non è resistente al phishing: TOTP rimane disponibile. Non attivare in produzione prima dei collaudi.
