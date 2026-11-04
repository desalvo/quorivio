# Quorivio RC174 — Un solo canvas partecipante e scala 16:9 verificata

**Base cumulativa:** RC173. **Versione prodotto:** `0.1.0-dev` invariata, licenza EUPL-1.2 invariata. Nessun commit, push, tag o deploy effettuato.

## Problemi riprodotti e modifiche

1. **Loghi e titolo ripetuti fuori dalla diapositiva attiva.** La vista pubblica mostrava i loghi dell'organizzazione e il titolo grande della sessione *anche dopo* l'accesso alla diapositiva. Ora rimangono sulle schermate di accesso/consenso e stato; la diapositiva attiva mostra solo il canvas progettato. L'`h1` della sessione resta nel DOM per i lettori schermo, ma non viene dipinto una seconda volta. Il contenitore esterno non disegna uno sfondo a forma di slide né una card opaca intorno al canvas.
2. **Media legacy duplicati.** Le risorse multimediali in `page_design.media` non vengono più montate fuori dal canvas quando la pagina dispone già di widget, che sono responsabili di disegnare il contenuto della diapositiva. La visualizzazione storica senza widget è preservata.
3. **Controlli HTML a dimensione fissa nel 16:9 mobile.** Il test Chromium, sulla CSS effettiva, riproduceva la regressione: con stage da 1.229 px a 374 px di larghezza, un campo di testo `textarea` da due righe restava alto **57,2 px** anziché ridursi. Le regole di etichette, padding, bordi e controlli nella *sola* modalità 16:9 fedele sono ora in `cqw` logici, riscalando la textarea a **18,0 px** su stage da 374 px e a **15,0 px** su stage da 304 px. La lettura accessibile conserva invece input di almeno 44 px.
4. **Regressioni storiche.** Alcuni test isolavano il componente React cercando il vecchio `className` letterale. Gli estrattori sono stati aggiornati al marker stabile del route e due contratti Python precedentemente non più allineati con RC172/RC173 sono stati adattati senza indebolire gli scenari negativi.

## Verifiche locali

- **307/307 test Node frontend** superati (302 precedenti più 5 RC174).
- **588/588 test Node API** superati.
- **18/18** test Python mirati RC159/RC160/RC173 e **5/5** nuovi test Python RC174 superati.
- **Chromium reale (fixture DOM/CSS)**: stage 16:9, tre larghezze (1280, 390, 320 px), posizioni dei tre widget invariate, heading nascosto visivamente, card non ridisegnata, lettura accessibile senza background, controllo `textarea` ridimensionato e niente overflow orizzontale.
- La fixture Chromium è eseguibile anche nella fase Chromium facoltativa di CI (`tools/rc174_browser_geometry.py`); la CI completa e il browser React con sessione autenticata non sono ancora confermati.
- **TypeScript/Vite non compilato localmente:** dipendenze npm non disponibili nell'ambiente offline; è obbligatoria la compilazione CI prima di validare il package.

## Stato di accettazione

**85,25%**, 43 gate accettati / 17 parziali, **immutato**: queste verifiche non sostituiscono il collaudo reale su smartphone/browser e il test con PostgreSQL autenticato. Mantenere `rc_strict=false`, `publish_image=false`, `publish_latest=false` fino alle prove finali.
