# Hotfix RC CI MFA: quota IP condivisa

### 2026-10-26 — Hotfix CI MFA: quota condivisa per IP (dopo commit della pubblicazione opt-in)

**Baseline committata**: SHA `723dda022eedb6412bb305f58f6ddab48be0e8ef`; run GitHub Actions `40349577790`, quality job `121675471288` FAILED in `tools/ci_email_mfa_postgres.py` (ultimo `GET /api/auth/me`: atteso 200, ricevuto **429**). I **433 test Node**, la build frontend/backend e il collaudo PostgreSQL dei profili sono PASS; build container SKIPPED; pubblicazione Docker correttamente SKIPPED.

**Causa**: la suite profili e quella MFA condividono lo stesso IP loopback e il limite PostgreSQL di **100 chiamate API/minuto**. Il test MFA esauriva la quota prima dell'asserzione finale; non è provato un errore dell'OTP. Il bypass già esistente `LOAD_TEST_TOKEN` è permesso esclusivamente fuori produzione, con segreto di almeno 32 caratteri e confronto `timingSafeEqual`. Il test MFA ora richiede questo token solo nel contesto CI effimero e locale, lo invia su entrambe le funzioni HTTP (anche verifiche concorrenti), e il workflow lo passa esplicitamente. Rimangono invariati il rate limiting di produzione e i controlli specifici MFA (tentativi, scadenza, anti-replay).

**Sicurezza log CI**: mascheramento immediato dei due segreti generati con `::add-mask::`; il processo SMTP riceve la password dall'ambiente anziché da una interpolazione GitHub esposta nei comandi. Aggiunti **5 test Python** per richieste, esiti OTP negativi, precondizioni loopback/token e limite di produzione.

**Da verificare in GitHub**: dopo il commit dell'hotfix, CI standard con MFA PostgreSQL/SMTP TLS, retention, concorrenza, build container PASS e pubblicazione SKIPPED. Matrice RC invariata **48,0%** (1 accepted / 15 partial / 2 open). Nessuna promozione dei gate basata solo sui test locali. Nessun commit/push/tag/release eseguito dall'assistente.
