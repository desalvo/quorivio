# Correzione del gate Gitleaks, 27 ottobre 2026

**Run GitHub 40583756455:** compilazione frontend/backend e integrazione PostgreSQL 18, SMTP MFA e altri test obbligatori superati. Unico passaggio fallito: `Detect credential leaks`, con 22 rilevazioni della regola `generic-api-key`, tutte nel manifest `docs/RC_DASHBOARD_WIDGET_APPEARANCE_MANIFEST.json`. I valori sono hash SHA-256 dei file, non credenziali.

**Correzione:** nessuna disattivazione del controllo di sicurezza e nessuna allowlist. Ogni digest storico è conservato in otto gruppi esadecimali ordinati da otto caratteri (`sha256_hex_groups_by_file`), ricostruibili mediante concatenazione. Aggiunti validatore e regressioni per garantire integrità e prevenire nuovi falsi positivi della stessa categoria.

**Risultati:** test locali mirati e validazione manifest superati; una nuova run GitHub CI è necessaria prima di dichiarare verde il controllo Gitleaks. La suite Chromium/PostgreSQL opzionale non è stata eseguita in questa run. RC rimane 53,0%; nessuna promozione gate, release candidate non pronta. Nessuna pubblicazione Docker.
