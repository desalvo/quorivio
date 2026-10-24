# Quorivio 0.1.0-dev — consegna cumulativa (24 ottobre 2026)

## Baseline e perimetro
Archivio completo dei sorgenti basato sulla baseline `ci-jsx-build-hotfix-cumulative` con CI verde confermata dall'utente. **Non è una Release Candidate approvata**. Nessun commit, push, tag o intervento sui server; versione invariata.

## Implementazioni successive all'ultimo commit confermato
- Import `.quorivio` con nuovi UUID globali degli asset e rimappatura dei riferimenti in tema, pagine e risultati; prevenzione delle collisioni nelle reimportazioni.
- Duplicazione di sessione con copia indipendente dei media e dei record associati.
- Controlli degli archivi su MIME effettivo, hash crittografici, integrità e percorsi.
- Attivazione MFA email solo dopo conferma del codice recapitato; TOTP indipendente da SMTP. Rafforzamento dei cambiamenti transazionali delle impostazioni amministrative e della gestione delle foto profilo.
- Sei manuali PDF IT/EN rigenerati, test di regressione e test HTTP di integrazione aggiuntivi.
- CI configurata con smoke test su PostgreSQL reale e istanza temporanea: doppia importazione, duplicazione, media, profilo, rifiuto archivi alterati.

## Evidenze locali
- `npm run build`: PASS TypeScript backend e TypeScript/Vite frontend.
- Node.js: 126/126 test superati.
- Python: 224/224 test superati.
- Matrice RC: **40,0/100**, misurazione convenzionale dei criteri di accettazione, non della quantità di codice scritto.
- **Non** eseguiti qui: smoke HTTP con PostgreSQL, sessioni distribuite e collaudi su browser/dispositivi reali.

## Gate residui
1. Collaudi reali dell'editor su browser, smartphone, tablet e tecnologie assistive.
2. Round-trip PowerPoint per grafici avanzati, SmartArt e OOXML complesso.
3. MFA SMTP e SSO/OIDC con provider effettivi; collaudi multi-replica.
4. Import portabile fra due database e storage indipendenti; fuzzing.
5. PostgreSQL 18, carico verificato di 500 partecipanti, Docker/Podman, Kubernetes con NGINX e HAProxy.
6. Revisione sicurezza, verifiche GDPR e licenze, accuratezza manuali e approvazione operativa.

## Decisione
**RC NON PRONTA**. Mantenere `0.1.0-dev` e usare `docs/RC_GATE_MATRIX.json` come fonte dei gate ancora aperti.
