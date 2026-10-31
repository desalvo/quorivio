# Quorivio 0.1.0-dev — RC60: collegamento OAuth e revoca delle credenziali

**Base confermata:** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`; la CI standard `41152434205` e quella estesa `41152939003` riguardano la baseline committata e **non** queste modifiche. Cicli **58–60 cumulativi e non committati**. Versione invariata `0.1.0-dev`.

## Problema risolto nel codice

Lo stato OAuth/OIDC era già monouso e persistente in PostgreSQL, ma i callback di **collegamento dell'identità** verificavano soltanto che l'utente fosse approvato. Un collegamento iniziato con un cookie di autenticazione valido poteva completarsi dopo revoca MFA amministrativa o reset/cambio password. Inoltre l'avvio del collegamento si basava solo sulla firma del cookie e non sempre sul suo stato corrente nell'account.

## Modifiche operative

- Entrambi gli avvii `?link=true` (OIDC Google/custom e Social GitHub/Facebook) verificano in PostgreSQL approvazione, password obbligatoria e revoche successive alla data di emissione del **cookie firmato**.
- `auth_flows` memorizza `link_auth_issued_at_ms` insieme al collegamento locale, mediante migrazione additiva. I flow legacy senza data valida sono rifiutati. Le procedure di accesso federato *senza collegamento* non cambiano.
- Entrambi i callback recuperano il timestamp con `DELETE ... RETURNING`, rifiutano valori nulli/anomali e usano una sola `INSERT INTO ... SELECT ... WHERE` condizionata a validità/approvazione del conto e assenza di revoche successive. Conflitti di identità danno risposta esplicita senza eccezioni SQL sul vincolo `(provider,user_id)`.
- Non si richiede il cookie locale sul callback cross-site: `SameSite=Strict` non lo trasmette dopo la navigazione proveniente dal provider. La prova di autorizzazione è quella archiviata nel flow monouso; la verifica finale è sullo stato attuale nel DB.
- In CI standard è stata inserita una prova isolata PostgreSQL 18, senza provider reali, su collegamento valido, replay, unicità del provider, revoca amministrativa, reset password, approvazione e cambio password obbligatorio. La prova richiede `QUORIVIO_CI_FEDERATED_LINK_TEST=1`, un `GITHUB_RUN_ID` e PostgreSQL loopback `/quorivio`.

## Evidenza e limiti

Locale: **541 test Node API**, **99 frontend Node**, nuovi test di policy/contratto compresi; controlli sintattici per il modulo e per la CI; preflight della campagna RC59 positivo. La **nuova prova PostgreSQL CI non è stata ancora eseguita**. La build completa TypeScript/React non è verificabile qui con dipendenze npm mancanti (installazione locale non completata), né sono testati redirect e consenso reali di Google/GitHub/Facebook, SMTP esterno, dispositivi fisici o reviewer GDPR.

**Matrice RC: immutata a 81,75%**, 55 gate (38 accettati/17 parziali), **RC strict non pronta**. Non inventare crediti per test locali. Mantener `publish_image=false`, `rc_strict=false`, `publish_latest=false`; dopo il commit usare CI standard e poi campagna `rc_acceptance_suite=true` senza pubblicazione. L'utente effettua commit/push/tag: l'assistente non esegue Git.
