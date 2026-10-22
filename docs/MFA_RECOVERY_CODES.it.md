# Codici di recupero MFA — Quorivio 0.1.0-dev

Ogni attivazione TOTP crea dieci codici monouso casuali di 128 bit, mostrati una sola volta nella UI. Memorizzarli offline in luogo sicuro. Durante il login, in assenza di autenticatore, inserire un codice nel campo alternativo. Un codice usato viene eliminato atomicamente da PostgreSQL; non può essere riutilizzato. Nel pannello MFA è possibile rigenerare i codici (invalidando i precedenti) fornendo password e TOTP. La disattivazione MFA elimina i codici.

I codici sono persistiti esclusivamente come HMAC-SHA256 con chiave AUTH_SECRET. La modifica di AUTH_SECRET invalida i codici esistenti. Non includere mai i codici nei log. Il sistema non dispone ancora di un processo amministrativo di recupero per perdita simultanea di autenticatore e codici: richiede una procedura verificata fuori banda. Test E2E PostgreSQL/browser non eseguiti. SSO esterni ancora aperti.
