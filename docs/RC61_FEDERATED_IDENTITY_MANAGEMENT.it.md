# Quorivio 0.1.0-dev — RC61: gestione identità SSO e revoca self-service

**Data:** 31 ottobre 2026. **Baseline Git confermata dall’utente:** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0` (standard `41152434205`, estesa `41152939003`, per la baseline precedente). **Cicli 58–61 cumulativi NON committati.** Versione sempre `0.1.0-dev`.

## Chiusura funzionale nel codice

Prima di questo ciclo la UI consentiva di **collegare** Google/GitHub/Facebook ma non di elencare le identità già collegate e scollegarle. La gestione SSO ora offre:

- elenco privato `GET /api/auth/identities`: soltanto provider e timestamp; nessun subject/ID esterno né collegamento di altri utenti; risposte `Cache-Control: private, no-store`;
- `POST /api/auth/identities/unlink`: conferma esplicita e password locale attuale obbligatoria, transazione PostgreSQL con `SELECT users ... FOR UPDATE`, controllo revoche/cambi password anche *dopo* l'acquisizione del lock e `DELETE` vincolata all'utente autenticato;
- limite di **5 tentativi al minuto per account** sullo scollegamento, persistente in PostgreSQL e su più repliche, conteggiato prima della transazione così i tentativi falliti non vengono annullati dal rollback;
- interfaccia «SSO / Identità» con elenco, pulsante «Scollega», conferma, campo password, «Annulla» e refresh; le identità già collegate non sono proposte per un nuovo collegamento;
- nessuna alterazione dell'autenticazione MFA: il login federato resta vietato a chi ha MFA locale attivo; nessun account viene creato automaticamente tramite email.

Il collegamento federato è persistito e cross-replica dal ciclo precedente; il ciclo 61 non richiede nuove colonne/schema. Se la password locale non è disponibile, si usa il normale recupero password e il relativo secondo fattore prima dell'operazione. Lo scollegamento ha effetto su futuri login federati; non revoca automaticamente sessioni locali già attive.

## Test e CI

**Localmente PASS:** 546 test API, 99 test frontend Node, parsing TypeScript dei 3 sorgenti modificati, `rc_campaign_preflight.py --check-workflow`. Nuovi 5 test di contratto/policy, oltre alle regressioni precedenti. La prova `tools/ci_federated_identity_management_pg.mjs` è inserita nella **CI standard**, con database loopback esplicitamente effimero e `GITHUB_RUN_ID`: avvia login HTTP e verifica elenco privato, account separati, password errata/corretta, richiesta senza autenticazione, replay di scollegamento e revoca dopo cambio password. È **ancora da eseguire** in CI; non sostituisce Google/GitHub/Facebook reali.

**Non verificati in questo ambiente:** installazione completa npm (`@types` mancanti nella copia ZIP), build completa TypeScript/Vite, backend PostgreSQL HTTP reale, consent provider esterni, browser/accessibilità su dispositivo fisico, GDPR/AGID e produzione multi-nodo. Nessun test locale certifica questi requisiti.

## Gate e rilascio

**Gate RC certificato invariato: 81,75% (38 accepted, 17 partial, 55 gate, peso 100).** `C3` rimane parziale: i provider reali e la revisione operatore sono ancora assenti. Il nuovo ambito di self-service è un progresso funzionale **non conteggiato** nel punteggio formale finché mancano la CI sul nuovo commit e la sua revisione. La matrice precedente non è stata alterata artificiosamente.

Dopo il commit del manutentore: eseguire prima la CI standard (controllare «PostgreSQL federated identity management HTTP acceptance»), poi un solo dispatch esteso con `rc_acceptance_suite=true`, `publish_image=false`, `rc_strict=false`, `publish_latest=false`. Nessun commit, push, tag o publish automatico.
