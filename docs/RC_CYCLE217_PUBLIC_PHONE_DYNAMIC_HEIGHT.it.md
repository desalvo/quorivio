# RC217 — Altezza dinamica del canvas smartphone pubblico

## Anomalia GitHub
La full CI RC216, run `42150766799`, job `127673188105`, ha superato le verifiche precedenti e ClamAV, ma è fallita nello step "Chromium participant UI and PostgreSQL lifecycle (opt-in)", `tools/ci_browser_participant.py:279`. La verifica RC176/RC165 assumeva un'altezza **fissa di 998 px**: domanda 248 px, due risposte più basse rispetto alla RC207. La RC207 ha introdotto righe tattili da **almeno 44 px**, aumentando la domanda a 278 px e la pagina del campione a **1.028 px**. Il test rigido non rifletteva più la funzionalità approvata.

## Correzione e garanzie
Invece di aggiornare semplicemente la costante a 1028, il test browser calcola la dimensione attesa utilizzando le dimensioni dei **soli widget pubblici realmente visibili**: margini superiore/inferiore di 16 px, 8 px tra ciascun widget, altezze dei sette contenuti pubblici. Verifica che il canvas coincida con il valore calcolato, che non vi siano spazi fantasma tra widget, che l'altezza della domanda preservi i controlli RC207 e che il footer termini il documento. Rimangono obbligatori i controlli che vietano la presenza nel DOM di `results-button` e `participant-count` privati.

Sono stati riconciliati i test storici RC168, RC169, RC177 senza rimuovere le verifiche negative. Il nuovo preflight `tools/tests/test_rc217_public_phone_stage_ci.py` include mutazioni negative contro l'uso di un'altezza fissa, la perdita del filtro delle widget riservate e la riduzione delle righe tattili. Il test Node `apps/web/test/rc217-public-phone-stage.test.ts` esegue il planner originale e verifica 1028 px con opzioni brevi, crescita per risposte da 255 caratteri e invarianza con widget privati aggiuntivi. I due test sono eseguiti **prima di npm**, mentre la prova PostgreSQL + Chromium rimane nella full CI.

## Validazione
Il Chromium locale con CSS reale e planner TS conferma 1028 px, top/footer ~16 px e gap ~8 px alle larghezze 390 e 1440. Test Python dedicati e Node superati. L'intera prova integrata con PostgreSQL deve essere riconfermata in GitHub Actions RC217. Nessuna modifica al runtime React, API, CSS, layout desktop o dati; versione `0.1.0-dev`, certificazione **85,25%** (43 gate accettati, 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o tag da parte dell'assistente.
