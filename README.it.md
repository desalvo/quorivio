# Quorivio — 0.1.0-dev

**Autore:** Alessandro De Salvo <braket71@gmail.com>  
**Sorgenti:** https://github.com/desalvo/quorivio  
**Licenza:** EUPL-1.2 (vedere LICENSE; inclusione del testo integrale ufficiale ancora da completare)  
**Docker:** `desalvo/quorivio`

Quorivio è una piattaforma web autonoma per presentazioni interattive, sondaggi, quiz e risultati in diretta. Supporta sessioni indipendenti dalle presentazioni esterne e QR code riutilizzabili. Questa è una **versione iniziale di sviluppo, non ancora validata per produzione**.

- Manuali: `docs/manuals/user-guide.it.pdf`, `docs/manuals/admin-guide.it.pdf` (disponibili anche nell'interfaccia).
- Configurazione GitHub/Docker Hub: `docs/GITHUB_DOCKERHUB.it.md`.
- Wizard Kubernetes Kustomize: `docs/KUBERNETES.it.md`.
- Stato effettivo: `docs/DEVELOPMENT_STATUS.it.md`, dettaglio `docs/DEVELOPMENT_STATUS.md`.

Per avviare l'ambiente locale, leggere anche il [README inglese](README.md) e configurare il file di esempio `.env.compose.example`; verificare `PUBLIC_BASE_URL`, credenziali e policy prima di ogni esposizione Internet.

### Kubernetes e GDPR (lavori in corso)

Il wizard supporta NGINX, due annotazioni HAProxy legacy, PostgreSQL 18 interno o PostgreSQL esterno con TLS. Vedi [Kubernetes](docs/KUBERNETES.it.md) e [registro GDPR](docs/GDPR.it.md). Nessuna prova su cluster reale o attestazione di conformità GDPR.
