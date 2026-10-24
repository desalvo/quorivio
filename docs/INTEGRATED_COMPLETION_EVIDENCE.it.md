# Evidenze del ciclo integrato — 24 ottobre 2026

## 2026-10-24 — Prosecuzione integrata delle macroaree: titoli grafici e controlli OIDC

- I titoli dei grafici PPTX nativi vengono importati come widget di testo modificabili, rispettando il limite esistente di 16 widget/pagina. Serie, assi, dati e formattazione dei grafici non sono conservati e sono dichiarati esplicitamente nel rapporto di fedeltà.
- I token ID OIDC vengono respinti se la data `iat` è troppo remota, la durata è superiore a 24 ore o i valori temporali non sono finiti, mantenendo le verifiche di firma, emittente, destinatario e nonce. Aggiunti test.
- Evidenze locali: 224 test Python OK e 121 test Node.js OK. La build npm completa è stata tentata ma interrotta perché mancano le definizioni TypeScript Node (`TS2580`). Non è quindi certificata per questa revisione.
- **Ancora aperti:** Release Candidate globale, grafici PowerPoint completi/SmartArt, MFA/SSO end-to-end, flussi live con PostgreSQL, trasferimento archivi tra istanze, verifica accessibilità su browser/dispositivi, capacità reale di 500 partecipanti, audit sicurezza/GDPR e CI riproducibile di questa revisione. Servono ulteriori sviluppi o verifiche esterne.
- Nessuna modifica a repository, server o Kubernetes.

Baseline RC invariata al 37,5%; nessun nuovo gate end-to-end chiuso.
