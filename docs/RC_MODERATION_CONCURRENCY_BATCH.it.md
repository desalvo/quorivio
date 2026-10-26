# Quorivio RC — Lotto moderazione pubblico e concorrenza (26 ottobre 2026)

**Baseline committata:** `c44a3cb884b37ad20cc8c46203e16c24c6520412`, run GitHub `40359804334` completamente verde per qualità/build, pubblicazione SKIPPED. Questo lotto contiene solo modifiche successive.

Lotto articolato in **40 interventi tecnici, comportamentali e di verifica sul percorso B3**: non si tratta di 40 macrofunzionalità indipendenti. Comprende controllo atomico del limite di 3 domande, transazioni e lock fra repliche, blocco dei messaggi su pagine chiuse, voti coerenti con la moderazione, idempotenza, protezioni di privacy e di accesso, coda privata paginata (20 per pagina), filtri e contatori, moderazione singola/reversibile e multipla con rollback globale su ID fuori sessione, UI presentatore e partecipante, test Node, PostgreSQL concorrenti e Chromium opzionale.

**Verifiche locali:** 442/442 Node PASS; 52/52 Python pertinenti PASS; sintassi TS/TSX e parsing del workflow YAML PASS. Suite Python totale non conclusa localmente per timeout dei test di conversione; build TypeScript completa non riprodotta per dipendenze `@types` non disponibili in questo ambiente. Nuovi test PostgreSQL/Chromium **non ancora eseguiti nella CI GitHub**.

**Gate e avanzamento:** B3 rimane `partial` finché non passano i nuovi test PostgreSQL, Chromium e i controlli indipendenti cross-browser/accessibilità. **48,0% RC**, 1 accepted / 15 partial / 2 open. Nessun incremento fittizio.

**Prossimi controlli:** CI standard dopo commit con nuovo test di moderazione, build container, pubblicazione sempre SKIPPED; poi CI manuale con `browser_test=true` e `publish_image=false`. Non effettuati commit, push, tag o release.

Per l'inventario tecnico dettagliato dei 40 interventi verificare `docs/RC_MODERATION_CONCURRENCY_BATCH.en.md`.
