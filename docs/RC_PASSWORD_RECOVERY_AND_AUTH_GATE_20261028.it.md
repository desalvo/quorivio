# Quorivio 0.1.0-dev — Recupero password e gate autenticazione

Data: 28 ottobre 2026. Ultimo commit confermato dall'utente: `a32ef78902a656262d346a0fa622604a4deda405`. Tutte le modifiche precedenti ancora non committate sono presenti nel cumulativo. Nessun commit, tag o Docker push è stato eseguito dall'assistente.

## Nuova prova di integrazione (in attesa della CI GitHub)

`tools/ci_password_recovery_postgres.py` verifica il backend reale con un account temporaneo, PostgreSQL 18 e un server SMTP TLS di prova, controllando:

- Risposta generica 202 tanto per email esistenti quanto per indirizzi inesistenti; invio della mail solo all'account valido e limite di emissione per minuto.
- Link di recupero consegnato tramite TLS, archiviazione del solo digest SHA-256 del token e assenza di credenziali/token nei log.
- Rifiuto delle password deboli, riscossione concorrente atomica monouso del token, blocco del riutilizzo e scadenza.
- Revoca di due sessioni autenticate preesistenti, rifiuto della password precedente e accesso con la nuova.
- Protezioni per impedire l'esecuzione su API/database esterni o con un SMTP non privato.

Correzione aggiuntiva: **sia il reset tramite email sia il cambio password autenticato eliminano atomicamente i challenge MFA di accesso e di iscrizione preesistenti**, impedendo il completamento con un codice rilasciato prima del cambio credenziali. Il nuovo test inserisce challenge temporanei e ne verifica la rimozione dopo il reset.

Il test è collegato alla Full CI, dopo la prova SMTP/MFA esistente. **Non è ancora stato eseguito su GitHub sul nuovo codice** e non contribuisce al completamento.

## Riconciliazione RC

La Full CI già verde [40638652838](https://github.com/desalvo/quorivio/actions/runs/40638652838) ha verificato autenticazione, ciclo profili/account su PostgreSQL, cambio credenziali e MFA email con revoca. Il gate parziale C1 (peso 6) diventa un sotto-gate automatizzato **C1-AUTH accettato** (peso 2), mantenendo **C1 parziale** (peso 4) per i collaudi non ancora completati. Peso globale 100 invariato, progresso **65,0% → 66,0%**, 31 gate: 14 accettati e 17 parziali.

**RC NON pronta.** Rimangono il recupero password completo su browser, revoca in più repliche, SMTP reale, SSO esterni, accessibilità su dispositivi e screen reader, fedeltà visiva, Kubernetes RWX/ClamAV e verifiche indipendenti di sicurezza/AGID/GDPR.

Verifica successiva dopo il commit dell'utente: `workflow_dispatch` con `browser_test=true`, `publish_image=false`, `rc_strict=false`.

**Verifiche locali dopo la correzione:** build TypeScript API/Web e Vite PASS, 468/468 test backend Node, 58/58 frontend, 944/944 Python. Prova PostgreSQL/SMTPS da eseguire in CI: nell’ambiente locale non sono disponibili PostgreSQL, psql e Docker.
