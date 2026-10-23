# Collaudi MFA e calendario — 23 ottobre 2026

Baseline: `quorivio-0.1.0-dev-ci-k8s-credentials-hotfix-cumulative.zip`. Non presumere che hotfix o ciclo siano già committati. Dopo password corretta, l'utente sceglie TOTP oppure Email, senza obbligo di completarli entrambi. Email inviata solo quando richiesta. Recupero mostrato soltanto al secondo fattore. Limite 3 invii/minuto per account e 5 tentativi per sfida; resta da implementare verifica autonoma del possesso della casella email in fase di abilitazione.

Per foto profilo, controllare proprietà e permessi del PVC `/app/assets` e la raggiungibilità di ClamAV; `fsGroup: 1000` è una possibile correzione, dipendente dal CSI. Non disabilitare l'antivirus obbligatorio in produzione.

Provider SSO caricati all'avvio da `OIDC_PROVIDERS_JSON`, `OIDC_GOOGLE_*` e configurazioni social. Senza credenziali il messaggio nessun provider è atteso. Serve verifica reale con callback HTTPS coerente con `PUBLIC_BASE_URL`.

Collaudi ancora necessari: cambio metodo MFA, replay e scadenza, SMTP, recupero, concorrenza, foto sul cluster, calendario e fusi orari, accessibilità, build completa. Nessuna RC dichiarata.
