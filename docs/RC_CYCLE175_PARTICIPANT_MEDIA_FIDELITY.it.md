# RC175 — Geometria fedele dei media nella pagina partecipante

**Data:** 04/11/2026. **Base cumulativa:** RC174. Versione `0.1.0-dev` e licenza EUPL-1.2 invariate.

## Difetto verificato e correzione

Un test reale in Chromium, con il CSS dell'applicazione, ha riprodotto un errore della vista partecipante: restringendo il browser, un'immagine tornava alle proporzioni native del file invece di occupare l'altezza del widget disegnata sulla diapositiva 16:9. Inoltre il contenitore interno non aveva un'altezza definita, e alcuni video usavano l'altezza standard del browser (150 px).

I widget **immagine, logo e video** ora occupano l'intero spazio assegnato nelle modalità 16:9 e smartphone personalizzata. `object-fit:contain` impedisce di deformare il contenuto; i ritagli PowerPoint rimangono geometricamente validi. La modalità **Lettura accessibile** conserva il flusso lineare e lo sfondo bianco, senza forzare le dimensioni della slide.

## Verifiche locali

- **309/309 test frontend Node**, **588/588 test API Node**.
- Nuovi test di regressione Node/Python e prova browser Chromium a **1280, 390 e 320 px**, comprendente immagini normali, immagini ritagliate e video.
- La prova Chromium riguarda il DOM/CSS, non una sessione autenticata. Restano da verificare build TypeScript/Vite, React/PostgreSQL autenticato, confronto con le cinque schermate ricevute, smartphone fisico e prova carico 500 partecipanti.

**Stato di rilascio:** 85,25% certificato (43 gate accettati, 17 parziali); percentuale invariata senza validazione indipendente. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o rilascio.
