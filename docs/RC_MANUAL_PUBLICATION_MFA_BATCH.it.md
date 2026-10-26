# Batch RC 0.1.0-dev: pubblicazione opt-in, MFA email PostgreSQL/SMTP TLS, evidenze

**Baseline committata:** `dd806243e2dff0c8b608ff43d5ae9848d48361ad`; run 40335963980: quality, container e pubblicazione **SUCCESS**. Il precedente workflow **ha davvero pubblicato** `desalvo/quorivio:latest`. Questo nuovo batch non è stato committato né pubblicato e comprende l'intero sorgente a partire dalla baseline.

## 1. Pubblicazione Docker esclusivamente volontaria

- Push normali, tag e PR continuano test, build e scansioni, **senza pubblicare** immagini.
- Il job `publish` viene eseguito esclusivamente con `workflow_dispatch`, `publish_image=true` e riferimento autorizzato (`main` o tag semver `vX.Y.Z[-prerelease]`). Valori predefiniti: pubblicazione disattivata.
- Lo script `tools/resolve_image_tags.sh` controlla di nuovo consenso, evento, repository, SHA, ref e sintassi delle etichette **prima** dell'accesso a Docker Hub.
- Su main, tag predefinito `sha-<12 cifre hash>`; su tag semver, versione corrispondente. `publish_tag` è facoltativo e non può essere `latest`.
- Il tag `latest` è aggiunto solo spuntando `publish_latest=true` **su main**. Conservati gli obblighi di quality gate, container build, ambiente `production`, permessi repository di sola lettura, SBOM e multiarchitettura.
- **L'amministratore deve configurare esplicitamente i revisori obbligatori** dell'ambiente GitHub `production`: la sola presenza di `environment: production` non ne garantisce l'approvazione. Nessun tag già pubblicato viene rimosso automaticamente.

### Utilizzo

GitHub Actions → **Quorivio CI and Docker Hub** → Run workflow → scegli `main` → spunta `publish_image` solo quando vuoi pubblicare. Imposta eventualmente `publish_tag=rc-0.1.0`. Lascia `publish_latest=false` se non vuoi aggiornare `latest`. Per eseguire test Chromium/capacità senza pubblicare, lascia `publish_image=false`.

## 2. MFA email: accettazione integrata

- Nuovo server SMTP TLS temporaneo su loopback, con autenticazione reale, certificato generato per ogni prova, verifica rigorosa del certificato, credenziale effimera, file OTP privato (0600) ed eliminazione finale.
- `tools/ci_email_mfa_postgres.py` usa una vera API e PostgreSQL effimero: utente isolato, cambio password, conferma email entro dieci minuti, tentativi invalidi, sessioni revocate, login con codice di cinque minuti, uso singolo anche sotto concorrenza, blocco dopo cinque errori, scadenza, disattivazione e recupero del login con sola password.
- Risolto un rischio concorrenziale: un invio SMTP fallito non elimina la challenge più recente quando un altro codice è già stato emesso. Il testo della mail di attivazione distingue correttamente dieci minuti dai cinque per login.
- Le verifiche di protocollo del server SMTP TLS sono locali. **Il nuovo flusso PostgreSQL completo deve ancora passare la CI GitHub**. Il simulatore non sostituisce test di consegnabilità con provider reali.

## 3. Evidenze e gate RC

- Nuovo sommario GitHub Actions di punteggio e gate residui. L'opzione manuale `rc_strict=true` fallisce se anche un solo gate non è accepted: non va usata come quality gate ordinario.
- La CI verde 40335963980 costituisce evidenza verificata per retention/erasure, due repliche, disaster recovery e scansioni. **D6 passa da open a partial**, senza considerare completato il GDPR: mancano RWX/ClamAV operativi e revisione AGID/GDPR indipendente.
- Avanzamento ponderato da **45,5% a 48,0%**; C2 rimane partial e D3 open. I nuovi test CI sono soltanto preparati, non eseguiti nella nuova GitHub CI.
- Segue documentazione di quello che è verificato e di quello che rimane prima della RC. Nessun commit, push, tag o rilascio eseguito.

**Prossimi passi:** commit del cumulativo, CI standard obbligatoria (pubblicazione skipped), poi esecuzione manuale dei test Chromium con `publish_image=false`; revisione indipendente dei gate rimanenti.

## Local validation / Verifiche locali (2026-10-26)
- Full Python suite: **726/726 PASS**, including manual-publisher policy and real TLS SMTPS protocol fixtures.
- Full Node suite: **433/433 PASS**.
- Generated Kubernetes credential stability check: **PASS**.
- Bash publisher and TypeScript source parse checks: **PASS**. GitHub Actions YAML/boolean defaults parsed: **PASS**.
- Full local TypeScript/Vite production build: **NOT VERIFIED** because pre-existing incomplete local `node_modules/@types` includes empty type packages (`TS2688`). Last committed CI build PASS, but it does not validate the new patch. Mandatory new GitHub CI is required.
- Real PostgreSQL+SMTPS application fixture: **AUTHORED, NOT YET RUN**; green local SMTP protocol tests alone do not certify the endpoint.
