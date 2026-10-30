# Quorivio 0.1.0-dev — ciclo 35 — 30 ottobre 2026 — RC 80,75% (+0,50 punti)

**Baseline committata confermata:** `f5ccf9a7545e7c17b4323d067db66aff5eca9b41` (ciclo 33). I cicli 34–35 restano non committati. Nella CI GitHub `41048187760`, job qualità `124037870206`, sono state verificate con PostgreSQL 18 due API avviate simultaneamente (un solo amministratore iniziale) e lo shutdown controllato con readiness `503`, WebSocket `1012` e seconda replica sana.

**Punteggio RC ufficiale: 80,25 → 80,75%**. Il gate B1 (peso 2) è stato suddiviso in residuo B1 parziale di peso 1, `B1-BOOTSTRAP-PG18` di peso 0,5 accettato e `B1-GRACEFUL-DRAIN` di peso 0,5 accettato. 52 gate complessivi, 35 accettati, 17 parziali; peso totale 100. Non vengono conteggiati i nuovi interventi locali.

**Nuovo sviluppo ancora senza certificazione CI:** in caso di errore prima di acquisire l'advisory lock PostgreSQL, la connessione viene distrutta anziché restituita al pool con `lock_timeout` modificato o stato incerto; copertura con regressioni Node per timeout, errore di setup, reset fallito e rilascio non confermato.

**Ancora aperti:** CSI/NFS RWX reale su più macchine, HAProxy, TLS di produzione, ARM64 fisico, collaudi di carico persistenti e guasti, dispositivi/accessibilità, valutazioni GDPR/AGID e sicurezza indipendenti. RC stretta NON pronta. Nessun commit, push, tag o publish dell'assistente.

