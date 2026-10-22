# Managed antivirus and preconfigured SSO providers

Quorivio manages ClamAV inside its application deployment without publishing port 3310 externally. Docker/Podman Compose starts the `clamav` service with the app; signatures persist in `clamav-signatures`, the database receives updates and the app waits for the antivirus health check. Uploads fail closed (`QUORIVIO_AV_REQUIRED=true`). Helm bundles ClamAV as a pod sidecar on `127.0.0.1:3310`. Allow sufficient memory, startup time and signature-update connectivity. It is **not embedded into the Node.js process** and does not require an independently managed external service.

Google OIDC uses issuer `https://accounts.google.com`; GitHub OAuth uses `https://github.com/login/oauth/authorize`; Facebook OAuth uses `https://www.facebook.com/v22.0/dialog/oauth`. Known provider endpoints are already built into source. An administrator must still register a client with each provider and set client ID, secret and HTTPS redirect; no credentials are distributed. `OIDC_PROVIDERS_JSON` allows adding custom providers.

Remaining limitations: actual containerized ClamAV and provider authentication cannot be validated in this environment. Validate signature updates, harmless and detection test uploads, production resource sizing and image update policy before rollout.
