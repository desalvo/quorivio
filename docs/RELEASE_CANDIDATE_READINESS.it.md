# Quorivio 0.1.0-dev — Verifiche necessarie per la release candidate

**Stato: RC BLOCCATA fino a CI e collaudi operativi.** Questo documento registra i controlli disponibili e gli interventi da eseguire; non dichiara il prodotto pronto per la produzione. Non creare tag né modificare la versione prima della verifica dei gate.

## Verificato localmente nel package cumulativo del 22 ottobre 2026
- 82 test Node superati.
- 60 test Python superati, compresi test HTTP reali del worker privato, autenticazione, prenotazione dei job, confini di sicurezza e rendering PDF sull'host di preparazione.
- Importazione slide: l'API verifica formato/versione del manifest, tipo e SHA-256 del sorgente, ordine delle pagine, firma PNG, dimensione e SHA-256 delle immagini prima della registrazione.
- Endpoint di salute worker: HTTP 503 se credenziali o area temporanea non disponibili.
- Configurazione CI: installazione Poppler/ReportLab e controllo esplicito della presenza di ReportLab per evitare test PDF saltati; test Python e rendering reale PDF; compilazione API/web, bootstrap PostgreSQL, build di entrambe le immagini, Trivy e Gitleaks.

## Gate esterni da superare (non verificati qui)
1. Commit sul branch di prova e CI GitHub completamente verde, compresi rendering PDF e scansione converter.
2. Avvio immagini dell'esatto commit su Docker/Podman: import PDF/PPTX nel browser, rifiuto antivirus, navigazione sessione e risposte.
3. Collaudi con più browser per collaborazione, quiz, widget multipli, risposte revisionate e WebSocket.
4. Se è richiesto HA, almeno due pod API con RWX e PostgreSQL: callback OAuth, throttling, fan-out WebSocket, worker concorrenti e recupero crash.
5. Configurazioni reali OIDC/SMTP, verifica ripristino backup, accessibilità, sicurezza, privacy e retention con credenziali di prova.

La stima percentuale non sostituisce il collaudo. Mantenere `0.1.0-dev` e lo storico in `docs/DEVELOPMENT_STATUS.it.md`; non effettuare commit o pubblicazioni automatiche.
