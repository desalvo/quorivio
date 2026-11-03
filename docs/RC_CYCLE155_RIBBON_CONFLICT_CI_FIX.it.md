# RC155 — Correzione regressione CI barra flottante nei conflitti

La run GitHub [41719228484](https://github.com/desalvo/quorivio/actions/runs/41719228484) sul commit RC154 si è fermata al passaggio **Editor autosave recovery and shared geometry unit tests**. Il test storico `closing format widget does not clear active widget selection` in `apps/web/test/rc139-rating-editor-selection.test.ts` richiedeva ancora la condizione incompleta `&&widgets.some(...)`.

L'editor attuale include intenzionalmente `!suspendFormattingRibbon`; il canvas riceve `suspendFormattingRibbon={pageConflict}`. Durante un conflitto, la barra flottante è sospesa e non può coprire il pulsante di riconciliazione. La selezione del widget e la bozza restano disponibili. **Nessuna modifica al runtime**, solo alla verifica del contratto.

## Verifiche

- Node: `node --experimental-strip-types --test apps/web/test/rc139-rating-editor-selection.test.ts apps/web/test/rc155-conflict-ribbon.test.ts`.
- Python preflight: `python3 -m unittest tools.tests.test_rc155_conflict_ribbon -q`.
- I test negativi rifiutano la rimozione della sospensione, l'interruzione del collegamento al conflitto e la cancellazione accidentale della selezione.
- Da validare con Chromium autenticato e PostgreSQL: provocare modifiche concorrenti, aprire il conflitto, cliccare realmente su «Confronta e riconcilia le modifiche», risolvere senza perdere la bozza, verificare la ricomparsa della barra.
- La CI completa e la prova reale di 500 utenti descritta nel manuale amministratore RC154 rimangono da confermare. Non eseguire carichi su server non autorizzati.

**Distribuzione:** mantenere storico e immutabile il manifesto RC154, usare solo RC155 come inventario corrente.
