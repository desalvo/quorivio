# Quorivio 0.1.0-dev — RC 53 — Content Security Policy di produzione e permessi del browser (30 ottobre 2026)

**Baseline:** cumulativo ciclo 52; nessun nuovo commit dall'hash `64aa34379a07ba6a91c7eebf6f91e6dc12e3ad5c`. Il package conserva i cicli 49–53. **RC certificata sempre all'81,25%**: mancano il collaudo del runtime GitHub e la revisione indipendente di sicurezza.

## Sviluppi applicativi

`apps/api/src/security-headers.ts` introduce una CSP **effettivamente applicata in produzione** quando `NODE_ENV=production`: nega script inline ed eval, blocca oggetti eseguibili, vincola WebSocket all'origine pubblica configurata e preserva gli iframe dello stesso dominio per anteprima e presentazione. Immagini/media mantengono il supporto a upload, QR/data image, sfondi HTTPS opzionali, PDF e blob. Il CSS inline necessario a posizionamento, animazioni e personalizzazioni dei widget resta autorizzato, senza estendere l'esecuzione JavaScript. `Permissions-Policy` nega camera, microfono, posizione, pagamenti, USB e browsing-topics; lo schermo intero del presentatore rimane utilizzabile. La modalità di sviluppo Vite non applica la CSP di produzione.

## Verifiche e limiti

Cinque nuovi test Node verificano i vincoli CSP, quattro contratti Python verificano l'integrazione API e i test di runtime. I collaudi OCI AMD64/ARM64 e Podman rootless ora rifiutano un container che non restituisce i due header HTTP. **Il nuovo codice non è ancora stato provato in GitHub né su browser con questo aggiornamento**, e non sostituisce penetration test o certificazioni AGID/GDPR.

L'81,25% non aumenta: i collaudi HTTPS KIND, SLO globale 500 utenti, RWX esterno e approvazioni indipendenti D4/D6 sono ancora aperti. Eseguire CI standard e successivamente estesa con runtime OCI/Podman e browser, `publish_image=false`, `rc_strict=false`.
