# Provider SSO aggiuntivi (OIDC)

L’amministratore può aggiungere nuovi provider OIDC, senza modificarne il codice, usando `OIDC_PROVIDERS_JSON` con un array JSON. Esempio:

```json
[{"id":"university","label":"University Login","issuer":"https://login.example.org","clientId":"quorivio","clientSecret":"REPLACE_ME","redirectUri":"https://app.example.org/api/auth/oidc/university/callback"}]
```

L’ID deve essere univoco e composto da 2-32 caratteri minuscoli, numeri, `_` o `-`, iniziando con una lettera. Il callback HTTPS deve corrispondere esattamente all’ID. Sono ammessi fino a 32 provider addizionali. Il nome visualizzato (`label`) compare nella risposta API dei provider. Configurare i segreti tramite Secret Kubernetes o secret manager, non inserirli nel repository. La registrazione presso il provider reale, la prova di login e la verifica delle policy di MFA rimangono necessarie prima dell’utilizzo pubblico. Lo stato di autorizzazione è ancora locale al processo: non utilizzare più repliche senza persistenza condivisa.
