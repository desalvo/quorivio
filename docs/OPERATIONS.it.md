# Operazioni e lista di controllo release
- Configurare HTTPS e `PUBLIC_BASE_URL` con URL pubblico effettivo; non salvare segreti nel repository.
- Validare migrazioni e ripristino PostgreSQL; testare periodicamente i backup.
- Imporre gate CI su test, build, audit dipendenze e immagine; verificare digest e label pubblicati.
- Testare partecipanti smartphone, riconnessione, voti simultanei, autorizzazioni multi-tenant e WebSocket dietro proxy.
- Il wizard Kubernetes genera manifest, non li applica: revisionare Secret, ingress TLS e risorse.
- Questa versione dev NON è qualificata per produzione finché non supera prove d'integrazione, carico, backup e ripristino.
