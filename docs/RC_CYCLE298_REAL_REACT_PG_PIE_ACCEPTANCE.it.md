# RC298 — Collaudo reale React/PostgreSQL dell'accessibilità dei grafici a torta

**Base tecnica:** RC297 integrata in `main` al commit `5707b7d938531d161e97e1e0beb3d767ae4411a9`. [CI post-merge 42830750852](https://github.com/desalvo/quorivio/actions/runs/42830750852) verde. Percentuale formalmente certificata ancora **85,25%**: 43 gate accettati, 17 parziali. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Quale lacuna viene chiusa tecnicamente

I controlli RC295–RC297 verificavano percentuali, dimensioni e accessibilità con geometrie CSS e DOM di prova, ma **non** verificavano la schermata realmente prodotta dall'applicazione con una sessione salvata su PostgreSQL.

RC298 introduce un test **end-to-end obbligatorio** in Chromium con frontend React compilato e API autenticata su PostgreSQL, senza simulare le richieste HTTP o costruire a mano la UI. Due sessioni indipendenti vengono create e salvate nel database; una contiene percentuali attive, l'altra le disabilita. La domanda sorgente determina `resultsView=pie` della widget risultati.

Si verificano: presenza di tutte le etichette sorgente e percentuali nell'albero di accessibilità desktop, conteggio coerente e percentuali identiche al grafico; legenda desktop fuori dal flusso visivo; passaggio vero del selettore «Modifica layout Smartphone» e assenza di debordamento; ritorno al desktop; anteprima effettiva del presentatore con grafico e anteprima partecipante senza statistiche riservate; nessuna legenda o percentuale nei tooltip SVG quando l'opzione è disattivata; persistenza verificata con nuova lettura API; assenza di errori JavaScript.

I conteggi della **simulazione** in anteprima rimangono intenzionalmente simulati dall'app. Sono reali l'interfaccia React, il salvataggio PostgreSQL, i dati della sorgente e le preferenze del grafico. Il test non dichiara di aver registrato voti reali di partecipanti.

## Validazione automatica

La CI esegue prima `python3 -m unittest tools.tests.test_rc298_real_pie_postgres -q`, che controlla sintassi, restrizione all'origine HTTP localhost e presenza dei test veri nel workflow; dopo il bootstrap Chromium e PostgreSQL esegue `python3 tools/ci_rc298_real_pie_pg_chromium.py`. I risultati devono essere verificati nei log insieme a compilation, test PostgreSQL, integrità SHA-256 e build container.

## Operazioni ancora necessarie per chiudere formalmente A4 e B3

**A4 — Accessibilità:** prove indipendenti su macchine fisiche con NVDA, VoiceOver e TalkBack, verifica di tastiera, focus, annuncio di opzioni/risposte/conteggi/percentuali. **B3 — Risultati dei partecipanti:** prove reali su browser desktop e smartphone, lettura accessibile dei grafici, comportamento dopo risposte/connessioni e controllo privacy. Redigere verbali e schermate *oscurati*, senza nomi o token, firmati da revisore indipendente e riferiti allo SHA esatto.

Raccogliere le prove in un archivio privato fuori Git con `tools/rc_external_evidence.py`, usando i facet A4 `nvda`, `voiceover`, `talkback`, `keyboard-audit` e B3 `physical-results`, `screenreader-results`. **Nessun gate viene promosso automaticamente**: la prova tecnica non sostituisce l'accettazione umana. I restanti 15 gate parziali richiedono a loro volta le prove indipendenti previste nel catalogo.

Nessun merge, tag, pubblicazione Docker Hub o rilascio rigoroso è autorizzato dalla sola esistenza di questo collaudo. Consultare `docs/RC136_EXTERNAL_ACCEPTANCE_IT.md`.
