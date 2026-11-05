# Quorivio 0.1.0-dev — RC201 — QRCode live aggiornati dopo cambio URL

**Baseline:** cumulativo RC200 (full CI non ancora confermata); ultima full CI verificata verde RC199 `42096705867`. Versione `0.1.0-dev` e flag invariati: `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Comportamento

- Dashboard autenticata e tutti i widget QR per i partecipanti (editor, anteprima, presentatore, pubblico) usano l'URL canonico restituito dal server; il link non viene dedotto dal codice pubblico né dall'origine del browser.
- Dopo un reset il codice di accesso ruota: la vecchia immagine scompare subito, i WebSocket autenticati dei presentatori restano connessi e ricevono lo snapshot aggiornato. I partecipanti invalidati vengono disconnessi senza conoscere il nuovo token.
- Ogni QR verifica l'URL ogni 12 secondi e alla riattivazione della finestra, della rete o della pagina. Richieste precedenti abortite, URL revocati o temporaneamente irraggiungibili non lasciano vecchi codici scansionabili.
- QR dashboard, collegamenti e scaricamenti PNG/SVG, nonché QR dello schermo presentatore, includono una revisione nel percorso dell'immagine e si aggiornano senza reload del browser.
- Tutti gli endpoint QR consultano `public_base_url` nel database condiviso, evitando discrepanze fra repliche Kubernetes; anche il QR in PPTX esportato utilizza la configurazione corrente.

## Verifiche

Quattro test di stato eseguibili superati; 21 test Python mirati superati. Il test PostgreSQL reale del ciclo RC71 verifica ora anche il cambio dell'URL QR ed è da eseguire nella CI integrata, insieme alla compilazione React/TypeScript/Vite. La compilazione locale è impedita dalla cache incompleta (`vite/client` mancante), non da un errore applicativo dimostrato. L'analisi sintattica dei due file principali modificati è pulita. La full CI RC200 non è ancora confermata.

I partecipanti con link revocato **non** ricevono automaticamente il nuovo token privato: il widget pubblico mostra link non disponibile. PDF/PPTX e immagini già esportate sono file statici e non possono aggiornarsi a posteriori.

Completamento certificato invariato: **85,25%** (43 gate accettati e 17 parziali). Nessun commit, push, tag o pubblicazione dell'assistente.
