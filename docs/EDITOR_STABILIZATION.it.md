# Stabilizzazione gesti editor — 23 ottobre 2026

Questo ciclo rafforza la manipolazione delle slide senza modificare lo schema salvato né la versione.

- La rotazione usa ora la differenza angolare del puntatore rispetto alla rotazione già salvata; il primo movimento non reimposta l'orientamento.
- L'annullamento di un gesto ripristina la geometria iniziale del widget, inclusa la rotazione. La perdita della cattura del puntatore azzera lo stato del gesto.
- Nei widget del canvas viene evitata l'interferenza dei gesti touch del browser; il testo dei campi modificabili rimane selezionabile.

Verifiche: build produzione TypeScript/backend e Vite/frontend superate; suite Node superata; suite Python 102/102, inclusi tre nuovi controlli statici. Restano non verificati touch reale, annullamento in browser, persistenza e integrazione PostgreSQL. I test statici non equivalgono a E2E browser. I gate editor e RC restano aperti.
