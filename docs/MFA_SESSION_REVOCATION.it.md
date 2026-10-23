# Invalidazione delle sessioni dopo il reset MFA amministrativo

Il reset privilegiato della MFA aggiorna `users.auth_revoked_at` nella stessa transazione che elimina segreti TOTP e codici di recupero. Il middleware `requireAuth` respinge i cookie di accesso firmati, con durata di otto ore, se emessi prima del timestamp di revoca. L'upgrade WebSocket del presentatore applica la stessa regola, insieme alla revoca per modifica della password; le connessioni già presenti nell'istanza che esegue il reset vengono chiuse. La migrazione SQL è incrementale e idempotente.

**Limiti:** le connessioni WebSocket attive su altre repliche non vengono interrotte preventivamente; la revoca viene applicata alla riconnessione. In questo ciclo non sono stati eseguiti test PostgreSQL reali e multi-replica. L'istante di emissione del cookie è ricavato dalla scadenza legacy di otto ore; una tabella delle sessioni server-side consentirebbe audit più accurati.
