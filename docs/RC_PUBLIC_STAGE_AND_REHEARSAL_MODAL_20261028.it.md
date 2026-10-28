# Fedeltà della sessione pubblica e focus delle anteprime


## Ciclo RC — 28/10/2026: fedeltà della sessione reale e robustezza delle anteprime

**Baseline:** ZIP cumulativo con 740 file (hotfix istanza unica/mobile Chromium). **Versione:** `0.1.0-dev`, licenza EUPL-1.2 invariata. **GitHub main verificato:** `8899c24155473ab8ff88cfa1ba767aa949be1ded`; ultimo commit esplicitamente confermato dall’utente: `1a0bea5918098af52fdf9958b8e8e664d09c11d5`. Ultima run `40689633215`: FALLITA nello step Chromium editor UI acceptance prima dei test PostgreSQL; il nuovo hotfix singleton è ancora da convalidare in GitHub.

**Sviluppo effettivo:** sessione pubblica su stage 16:9 con coordinate, dimensioni e rotazione persistite; sfondo autorizzato e ritaglio delle immagini importate; marcature testuali inline nei widget testo/nota. Aggiunta modalità alternativa «Lettura accessibile», predefinita su smartphone, e scorrimento orizzontale quando viene selezionata la fedeltà geometrica. L'anteprima protegge anche dai portali dello sfondo aggiunti dopo l'apertura: `inert`/`aria-hidden` temporanei e ripristino dello stato precedente, focus e Tab migliorati. Due nuovi controlli Chromium eseguiti in locale e inseriti nella CI opt-in.

**Verifiche locali:** `npm run build` PASS (TypeScript backend/frontend e Vite). Test Node 474/474 backend e 58/58 frontend PASS. Suite Python completa 965/965 PASS, suite RC mirata 383/383 PASS. Chromium sul React compilato: istanza unica da dashboard/editor 1440/390 PASS; gestore TypeScript reale con portali dinamici 1440/390 PASS; CSS pubblico con fedeltà percentuale/rotazione e target touch 44px 1440/390 PASS. Un tentativo precedente della suite Python era stato interrotto; la ripetizione integrale è poi passata.

**RC globale:** 32 gate pesati (15 accettati, 17 parziali), **67,0% → 67,0% (+0,0 punti percentuali)**. Nessun gate promosso sulla sola evidenza locale. Release candidate ancora NON pronta.

**Da eseguire:** nuova Full CI GitHub dopo commit con `browser_test=true` e `publish_image=false`; test React partecipante/editor su PostgreSQL 18 reale, confronto visivo indipendente tra le quattro superfici, Firefox/WebKit, telefoni fisici Android/iOS, lettori di schermo e verifica WCAG/AGID; prove infrastrutturali reali Kubernetes/Helm, replica e failover. Nessun commit/push/tag/pubblicazione Docker eseguito.

**Report:** `docs/validation/RC_PUBLIC_STAGE_REHEARSAL_PORTALS_LOCAL_20261028.json`, con gate non modificati per assenza di Full CI nuova.
