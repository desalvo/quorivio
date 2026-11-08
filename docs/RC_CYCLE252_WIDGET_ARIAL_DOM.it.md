# RC252 — Font Arial di default per titoli e risposte delle widget

## Difetto riprodotto

Nell'editor React compilato, dopo la creazione di una widget «Domanda o sondaggio», il titolo risultava in uno `span` con `style="font-family: undefined"`, mentre il contenitore aveva `font-family: Arial`. Lo stesso problema colpiva le opzioni di risposta. `CSSStyleDeclaration.fontFamily = undefined` genera un font CSS letterale `undefined`: il browser non eredita più Arial. I controlli precedenti valutavano soprattutto le regole CSS dei contenitori o fixture di HTML e non il DOM del componente rich-text vero.

## Correzione

`apps/web/src/widget-text-marks.ts` esporta `inlineMarkDomCss`, che rimuove dal dizionario CSS qualsiasi proprietà non definita. `apps/web/src/widget-rich-editor.tsx` utilizza questo dizionario nell'assegnazione imperativa dei segni al DOM; gli stili React restano compatibili. Un testo privo di marche eredita Arial; i font diversi scelti dall'utente, gli stili e le dimensioni delle marche rimangono intatti. Nessuna migrazione database e nessuna riscrittura dei dati è necessaria.

## Verifiche

- Node: `node --experimental-strip-types --test apps/web/test/rc252-rich-dom-aria-default.test.ts`.
- Frontend: `npm run build -w @quorivio/web`.
- Chromium: `python3 tools/ci_rc252_arial_rich_dom_chromium.py` su bundle Vite compilato, a 390×844 e 1440×940. Verifica font effettivo sui singoli `span`, risposta e titolo, widget appena inserita, eredità personalizzata Verdana/Tahoma, segmenti Georgia/Trebuchet MS e zoom editor.
- Inserimento automatico nella full CI: test Node prima di `npm`, Chromium dopo la build e inventario SHA-256 con chiusura archivio.

## Rilascio

RC251 committata dal manutentore, full CI verde [42416170735](https://github.com/desalvo/quorivio/actions/runs/42416170735); immagini pubblicate (main [42417768823](https://github.com/desalvo/quorivio/actions/runs/42417768823), converter [42417918195](https://github.com/desalvo/quorivio/actions/runs/42417918195)). RC252 è un nuovo cumulativo **non committato**, con full CI ancora da eseguire. Inventari storici invariati. Avanzamento prodotto **85,25%** (43 accettati / 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
