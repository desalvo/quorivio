# Quorivio 0.1.0-dev RC266 — Compatibilità sfondi partecipante e CI

## Contesto
La full CI RC265, run [42506410487](https://github.com/desalvo/quorivio/actions/runs/42506410487) (commit `8bbed7462b730ebd7ac334ae092d3d875ab6387e`), fallisce al preflight `RC227 schema backgrounds and mobile participant mode before npm`, test `rc173-public-slide-fidelity.test.ts`: `RC173 participant page paints the authored background once (stage only), not on the page wrapper`.

Il test cercava il ramo precedente `:slideBackgroundCss(entry.activity.page_design`, mentre l'importazione RC265 ora compone il background con `...slideBackgroundCss(...)`, evitando che un fallback smartphone copra il PDF full-canvas. Non è stato rilevato un difetto di rendering in quel punto: il controllo storico è diventato obsoleto.

## Modifica RC266
- Aggiornamento del controllo RC173 al nuovo spread, verificando che lo sfondo sia applicato una volta sola allo stage, mai al wrapper esterno.
- Nuovo controllo RC266 che sorveglia i percorsi desktop, smartphone e lettura accessibile e la soppressione degli elementi schema per il partecipante/presentatore.
- Nuovo gate anticipato in GitHub Actions, prima del controllo RC227 esistente, che **rimane attivo**.
- Nessuna modifica al codice applicativo, al converter, al wizard Kubernetes o ai Secret; RC265 resta integralmente inclusa nel cumulativo.

## Verifica / rilascio
Eseguire `node --experimental-strip-types --test apps/web/test/rc173-public-slide-fidelity.test.ts apps/web/test/rc266-participant-background-legacy-contract.test.ts`; verificare poi l'intera full CI GitHub. Non aggiornare il cluster né pubblicare immagini Docker prima della full CI verde.

## Finestre flottanti editor — correzione aggiuntiva RC266
L'utente ha riscontrato che la finestra «Formato widget» e le finestre «Proprietà widget» e «Impostazioni pagina» non raggiungevano i bordi destro e inferiore: il limite di trascinamento richiedeva che tutta la finestra restasse visibile. Con finestre larghe/alte questo si traduceva in uno stop prematuro, talvolta a metà schermo.

- Posizionamento: vincolo sulla sola zona raggiungibile della barra del titolo (112 px orizzontali; 44 px verticali). Il pannello ora può essere accostato completamente ai bordi, persino lasciandone parte fuori schermo, mantenendo un'area da cui recuperarlo. Non viene alterato il canvas.
- Ridimensionamento: maniglia in basso a destra delle tre finestre, trascinabile col mouse/touch/penna, con vincoli adattivi al viewport (minimo 320×115 px formato; 280×160 px proprietà, se lo schermo lo consente).
- Accessibilità: maniglia raggiungibile con Tab; frecce modificano la rispettiva dimensione di 16 px, Maiusc+freccia di 48 px; campi e selezioni testo non avviano il drag.
- Le dimensioni personalizzate sono applicate tramite variabili CSS, sovrascrivendo le vecchie regole `width:...!important` che impedivano il resize.
- Verifiche: `apps/web/test/rc266-floating-window-docking.test.ts`, test storico RC105 aggiornato e CSS effettivo in Chromium a 1440×900, 390×844, 280×220; preflight CI anticipato RC266 esteso.

Nessuna modifica al database, all'applicazione Kubernetes, al converter o ai Secret. Full CI GitHub RC266 da verificare dopo commit.

### Correzione dello zoom globale
Nel layout Quorivio il tag `<html>` usa CSS `zoom` (di norma 80%). `window.innerWidth` resta in pixel fisici, mentre `position:fixed` usa coordinate logiche; `documentElement.clientWidth` non è affidabile in tutti i layout quando esistono regole `overflow`. Ora la geometria usa `innerWidth/zoom` e `innerHeight/zoom`, dove `zoom` è letto dallo stile calcolato. `ResizeObserver` osserva anche il root per riconciliare i limiti quando l'utente cambia zoom. Verificato in Chromium ai livelli 70%, 80%, 120% e su viewport desktop, smartphone e compatti.
