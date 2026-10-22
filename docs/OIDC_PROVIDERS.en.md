# Additional SSO providers (OIDC)

Administrators can add OIDC providers without editing application source using `OIDC_PROVIDERS_JSON` containing a JSON array. Example:

```json
[{"id":"university","label":"University Login","issuer":"https://login.example.org","clientId":"quorivio","clientSecret":"REPLACE_ME","redirectUri":"https://app.example.org/api/auth/oidc/university/callback"}]
```

Each ID must be unique, 2-32 lowercase alphanumeric, `_` or `-` characters starting with a letter. The HTTPS callback path must exactly match the ID. Up to 32 additional providers are supported. `label` is returned by the provider-discovery API. Supply credentials through Kubernetes Secrets or a secret manager, never commit them. External provider registration, login checks and MFA-policy checks are required before public use. Authorization state remains process-local and multi-replica use needs shared persistence.
