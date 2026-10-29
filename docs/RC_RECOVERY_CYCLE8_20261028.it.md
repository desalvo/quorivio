# Ciclo RC 8 — recupero password verificato e navigazione browser più sicura

**Baseline**: ZIP cumulativo `quorivio-0.1.0-dev-rc-ci-40709447219-gitguardian-checksum-hotfix-cumulative.zip`, 753 file; versione 0.1.0-dev, licenza EUPL-1.2. Nessuna funzionalità preesistente eliminata.

## Evidenze GitHub reali già verificate

La [run GitHub 40717525524, tentativo 2](https://github.com/desalvo/quorivio/actions/runs/40717525524) al commit `f6738592c648bc620e01b92d2bbaa6b90b459287` è verde nei job qualità `123073117101`, build container e pubblicazione manuale. È passato lo step di recupero password con PostgreSQL 18 effettivo e server SMTP TLS temporaneo. Il [test CI](../tools/ci_password_recovery_postgres.py) verifica privacy dell'esistenza account, consegna privata, memorizzazione dell'impronta e non del token, limitazione richieste, consumo singolo con concorrenza, scadenza, password deboli, revoca di più sessioni e invalidazione di MFA pendenti. Non sono controlli già contabilizzati in C1-AUTH (login, cambio password ordinario e MFA).

Il gate C1 di peso 4 è stato separato in C1 residuo di peso 2 (ancora parziale) e **C1-RECOVERY di peso 2, accettato esclusivamente grazie alla run GitHub indicata**. C1-AUTH resta distinto e accettato con peso 2. I pesi totali rimangono 100. Il punteggio passa da 67,0% a **68,0% (+1,0 punto)**, 33 gate: 16 accettati e 17 parziali. Non è un'attribuzione basata sul nuovo codice locale.

## Nuovo sviluppo (solo evidenze locali, senza altri punti)

- `apps/web/src/password-recovery-url.ts`: prelievo del token monouso all'apertura dell'app, eliminazione del parametro dall'URL e dalla history mediante `replaceState`, conservazione soltanto nello stato React in memoria e mantenimento dei parametri non sensibili.
- `apps/web/index.html`: policy `no-referrer` prima di avviare il bundle.
- `apps/web/test/password-recovery-url.test.ts`: regressioni su token vuoti, duplicati, URL, parametri Unicode e cronologia.
- `tools/ci_recovery_url_chromium.py`: Chromium sull'autentico bundle React a 1440 e 390 px, errore da token non valido, nuovo tentativo, conferma, pulizia URL e assenza di persistenza nello storage. Usa API simulate: non equivale a una prova PostgreSQL/SMTP.
- `.github/workflows/ci.yml`: il nuovo browser test è collegato alla CI opzionale, ma non è ancora stato verificato da GitHub.

## Limiti e completamento

Localmente superati build TypeScript/Vite, 474/474 test Node backend, 62/62 Node frontend, 975/975 Python e Chromium desktop/mobile. Qui non è disponibile un server PostgreSQL 18 né Docker/Podman: le prove d'integrazione reali sono quelle della precedente CI GitHub verde.

Ancora necessari: E2E recupero account in browser con PostgreSQL e SMTP sulla nuova revisione; provider esterni; carico prolungato e revoca multi-replica; Firefox/WebKit; screen reader; touch fisico; audit legale/GDPR/AGID e accettazione degli operatori. **RC non pronta**. Non effettuati commit, push, tag, release o pubblicazioni Docker.
