# RC291 — Due diversi comandi Smartphone nell'anteprima reale

## Evidenza

La [full CI #42674623251](https://github.com/desalvo/quorivio/actions/runs/42674623251) ha superato il ridimensionamento della finestra «Formato widget» e ha acquisito quindici schermate autentiche su PostgreSQL e Chromium, comprese le anteprime presentatore, partecipante e affiancata. Successivamente Playwright si è fermato perché in modalità affiancata sono presenti due comandi `Smartphone` distinti, appartenenti ai gruppi **Modalità anteprima** e **Dispositivo partecipante**. Il selettore generico era ambiguo: il problema appartiene al test e non dimostra un malfunzionamento dell'applicazione.

## Correzione e nuove immagini

L'acquisitore seleziona dapprima Smartphone nel gruppo «Dispositivo partecipante», verifica che la parte affiancata del partecipante passi a smartphone e scatta una schermata. Poi seleziona Smartphone nel gruppo «Modalità anteprima», controlla il passaggio alla modalità mobile dedicata e acquisisce un'altra schermata. Ogni controllo è esplicitamente univoco, abilitato e verifica `aria-pressed`. Test anticipati respingono selettori generici o pulsanti non corretti. La nuova immagine `rehearsal-side-by-side-smartphone` è registrata nel catalogo con didascalie in entrambe le lingue.

## Verifica e limiti

I test locali convalidano i selettori, le regressioni negative e il collegamento al vero componente React. Le fasi successive (editor degli schemi, vista live e partecipanti) dovranno essere confermate dalla prossima CI completa. Nessuna modifica al runtime, nessun accesso a dati reali e nessuna immagine obsoleta attestata come attuale. Baseline complessiva **85,25%** (43 accettati / 17 parziali), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Non sono stati effettuati commit/push/tag.
