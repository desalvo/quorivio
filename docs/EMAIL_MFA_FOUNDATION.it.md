# MFA email opzionale — fondamenta implementative (NON ATTIVA)

Questo ciclo aggiunge codici casuali di sei cifre, digest HMAC-SHA256 separati per utente e sfida, verifica a tempo costante, trasporto SMTP con TLS e test. Questi componenti **non sono collegati al login** e non costituiscono un secondo fattore già funzionante.

Prima dell'attivazione servono sfide monouso in PostgreSQL, scadenza dopo 5 minuti, massimo tentativi, consumo atomico, emissione sicura rispetto alle gare, limiti sugli invii, login in due fasi senza cookie prima della verifica, attivazione opzionale autenticata con conferma password/TOTP, recupero account, blocco sicuro se SMTP non funziona, UI e test end-to-end. SMTP configurato è requisito obbligatorio per il fattore email.

Nessuna dipendenza npm nuova e nessuna migrazione. Versione 0.1.0-dev invariata. CI esterna da confermare.
