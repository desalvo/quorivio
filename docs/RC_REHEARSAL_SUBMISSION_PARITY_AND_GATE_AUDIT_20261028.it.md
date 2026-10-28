# Ciclo RC — invio nelle anteprime fedele alla sessione e audit dei gate

Data: 28 ottobre 2026. Versione invariata **0.1.0-dev**, licenza EUPL-1.2.

## Baseline

Package sorgente: `quorivio-0.1.0-dev-rc-accessible-rehearsal-profile-gate-61-cumulative.zip` (711 file). Ultimo commit confermato dall'utente: `a32ef78902a656262d346a0fa622604a4deda405`. Tutti gli sviluppi successivi, ancora non committati, sono mantenuti in questo cumulativo. Nessun commit, push, tag, release o Docker push eseguito dall'assistente.

## Funzioni del ciclo

1. Nell'anteprima partecipante **selezione e invio sono distinti**: il grafico del presentatore cambia solamente dopo **Invia risposta di prova**, anche per più domande indipendenti nel medesimo widget.
2. Protezione dai duplicati: una risposta per domanda, un voto per valutazione e una sola reazione per pagina, anche con più widget Reazioni.
3. Domande con allegato: selettore file locale, ma il browser conserva solo il **nome** in memoria, senza upload né chiamate al server.
4. Ricomincia prova azzera bozze, risposte inviate, reazioni, domande simulate e campioni statistici; il contatore delle interazioni mostra gli invii effettuati, non le scelte ancora provvisorie.
5. Il limite di dieci domande sul tema è verificato anche nell'aggiornamento atomico dello stato React, contro clic ravvicinati.
6. Full CI opzionale estesa con una prova Chromium del modulo TypeScript effettivo a 1440 e 390 px. Si tratta di Chromium **offline**, non di un collaudo autenticato con PostgreSQL.

## Verifiche locali

- **468/468** test Node backend; **55/55** frontend; **934/934** Python: PASS.
- Build API/Web TypeScript + Vite: **PASS**.
- Cinque preflight Chromium offline: **PASS** per invio, focus/inert, layout 16:9, geometria editor/preview/utente e WYSIWYG desktop/mobile.
- Ancora mancanti: nuova Full CI GitHub, prova browser autenticata PostgreSQL sul nuovo codice, Firefox/WebKit, dispositivi fisici, screen reader e valutazioni indipendenti GDPR/AGID.

## Completamento ufficiale

**61,0% -> 63,0% (+2 punti)** grazie a due sottogate automatici già verificati dalla Full CI verde GitHub [40638652838](https://github.com/desalvo/quorivio/actions/runs/40638652838), commit `a32ef78902a656262d346a0fa622604a4deda405`:

- `B3-AUDIENCE` (peso 2, accettato): Chromium/PostgreSQL reali per partecipazione, accesso QR, votazioni, moderazione e privacy. `B3` resta parziale (peso 4) per altri browser, dispositivi e tecnologie assistive.
- `D6-ERASURE` (peso 2, accettato): retention, code di cancellazione fisica, retry e protezione dei lease su PostgreSQL. `D6` resta parziale (peso 3) per audit legale/AGID, cifratura, chiavi e verifiche operative.

**28 gate (11 accettati, 17 parziali). RC NON pronta.** Nessun punto riconosciuto alle nuove modifiche in attesa della CI. Pesi totali invariati a 100 e formula di valutazione invariata.

## Prossimi passi

Dopo il commit dell'utente: CI standard e Full CI `browser_test=true`, `publish_image=false`. Successivamente prove indipendenti di fedeltà visiva, Firefox/WebKit, telefoni/tablet, screen reader, RWX/ClamAV e provider social reali. Nessuna promozione automatica dei gate generali in assenza di accettazione completa.
