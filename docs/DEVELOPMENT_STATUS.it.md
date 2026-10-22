# Stato sviluppo (IT) — 2026-10-22
Versione `0.1.0-dev`. Realizzati nei sorgenti: backend/frontend, sessioni, sondaggi/quiz iniziali, QR code, risultati WebSocket, CSV, documentazione bilingue, wizard Kubernetes con output Kustomize, workflow GitHub CI/Docker Hub. I PDF e gli asset grafici sono inclusi e consultabili nell'interfaccia. Non sono ancora verificate build npm, runtime Docker/Podman/Kubernetes, provider social/AAI INFN, cluster reali e test end-to-end. I gate di produzione sono **configurati**, non ancora eseguiti con successo sulla CI reale. Evitare di dichiarare il prodotto pronto per il traffico pubblico prima di risolvere i blocchi e verificare sicurezza, disaster recovery e carico. Si veda il file `DEVELOPMENT_STATUS.md` per il dettaglio tecnico.

**Aggiornamento:** quattro test wizard superati; generati i quattro PDF, logo, grafica copertina e relativi link applicativi. Bloccata la generazione lockfile npm nell'ambiente offline. CI di produzione configurata ma non eseguita. Testo integrale ufficiale EUPL-1.2 da incorporare prima del rilascio pubblico.

## Terzo ciclo — PostgreSQL, Ingress e GDPR (22/10/2026)

- Compose aggiornato a PostgreSQL 18.6 con percorso dati `/var/lib/postgresql`; gli upgrade major richiedono migrazione reale.
- Wizard: database interno StatefulSet/PVC o esterno senza risorse DB; cambio modalità idempotente, annotazioni ingress NGINX/HAProxy per varianti community/haproxytech.
- Deployment con Secret DATABASE_URL; credenziali e certificati devono essere forniti dall'amministratore.
- Creati registri tecnici GDPR IT/EN con lacune aperte; nessuna dichiarazione di conformità.
- Test Python wizard ampliati; build npm, test reali PostgreSQL/Kubernetes e deployment non verificati. PDF precedenti non rigenerati in questo ciclo.
