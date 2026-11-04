# RC165 — Collaudo partecipante con widget espliciti

La run GitHub Actions `41764378267`, job `126359189722`, ha superato compilazione e test Chromium precedenti, ma il collaudo partecipante/PostgreSQL cercava erroneamente «Invia risposta» in un sondaggio legacy contenente solo il widget **Titolo**. Dopo la RC160, i comandi di risposta e le domande del pubblico non vengono montati automaticamente fuori dal canvas.

Il test crea ora in una sessione temporanea locale un widget **Domanda** a scelta singola (Sì/No) e un widget esplicito **Domande sul tema**, salvandoli prima dell'avvio con PATCH e `expected_design_revision`. Chromium verifica il 16:9, desktop e smartphone a 390 px, i controlli radio accessibili, due risposte indipendenti, la persistenza effettiva in `widget-answers`, il recupero dopo reload, l'idempotenza, la privacy dei report e l'assenza del pannello automatico. Il widget Domande sul tema viene verificato tramite il suo endpoint specifico, con risultati privati al presentatore.

Il test autonomo `tools/ci_audience_moderation_postgres.py` mantiene i controlli legacy di approvazione, revoca, voto, quota, paginazione, concorrenza e privacy: non vengono ripristinati i pannelli automatici non desiderati. Nuovi test anticipati simulano la preparazione della fixture e mutazioni negative prima dell'installazione npm.

Il runtime applicativo rimane invariato; la prossima CI deve confermare il test reale PostgreSQL/Chromium. Completamento certificato **85,25%** (43 accettati / 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o deploy eseguito dall'assistente.
