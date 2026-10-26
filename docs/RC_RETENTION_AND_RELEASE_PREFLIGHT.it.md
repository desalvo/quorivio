# Batch di accelerazione RC — conservazione, cancellazione e preflight

Data: 26 ottobre 2026. Il package cumulativo include anche il precedente batch da 40 interventi, per cui non è stato ancora confermato un commit.

## Interventi effettivi

1. La cancellazione automatica PostgreSQL applica finalmente `retention_days` della singola sessione.
2. L'impostazione globale determina solo il valore iniziale delle nuove sessioni, anche importate.
3. Solo il proprietario può cambiare la conservazione; il collaboratore riceve HTTP 403.
4. Sessioni attive non scadute sono protette; decorrenza dalla chiusura o dalla scadenza.
5. Cancellazione database e accodamento della rimozione dei media sono atomici.
6. I job media rimangono in PostgreSQL dopo un errore filesystem e sono riprovati.
7. Lease di cinque minuti e `FOR UPDATE SKIP LOCKED` evitano collisioni tra repliche.
8. La CI include test PostgreSQL reali, con rollback, su retention, isolamento proprietario, coda e lease.
9. L'interfaccia usa il default coerente di 60 giorni.
10. Il comando `tools/rc_release_preflight.py --strict` impedisce di dichiarare la RC finché restano gate aperti.

## Limiti e operatività

I test locali Node/Python e le build sono stati eseguiti, ma la nuova integrazione PostgreSQL e il cleanup multi-replica richiedono la prossima CI. **RC non ancora approvata: 45,5%**, senza promozioni automatiche dei gate. Restano i collaudi di accessibilità, dispositivi, DR operativo, ARM64/Podman/Kubernetes, provider SSO reali, sicurezza, GDPR/AGID e corpus PowerPoint indipendente.

Per ispezionare la coda: `SELECT session_id,queued_at,attempts,claimed_until,left(last_error,120) FROM session_asset_cleanup_jobs ORDER BY queued_at;`. La cartella `QUORIVIO_ASSET_DIR` deve essere condivisa e cancellabile da tutte le repliche. Le copie nei backup richiedono politiche di scadenza separate. Prima del tag RC eseguire `python3 tools/rc_release_preflight.py --strict` e completare tutte le verifiche indipendenti. Nessun commit/push/tag/release automatico.
