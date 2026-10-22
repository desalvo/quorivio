# Canvas grafico dei widget — 0.1.0-dev

## Stato
Implementato nei sorgenti, testato tramite validazione del layout e parsing TypeScript/TSX; non collaudato con browser o PostgreSQL reali.

## Uso
Nell'editor di una pagina trascinare ciascun widget sul canvas. Fare doppio clic sul titolo per selezionarlo e modificarlo nel campo del blocco. Ridimensionare la larghezza con +/− e rimuovere singolarmente i widget. Salvare tramite **Salva layout**. L'elenco tradizionale mantiene tutte le opzioni del widget, l'ordinamento e i pulsanti da tastiera.

## Persistenza
Le coordinate `position: {x,y,width}` sono percentuali rispetto all'area di impaginazione, con x/y >= 0, larghezza 12–100, x+width <=100, y<=96. Il backend rifiuta coordinate non finite e proprietà sconosciute. Il rendering pubblico usa le coordinate memorizzate.

## Limiti e prossimi passi
Nessuna protezione automatica da sovrapposizioni e nessuna disposizione responsive personalizzata per dispositivo. Mancano test E2E React/PostgreSQL, gestione completa della tastiera per posizionamento spaziale, editor media per singolo widget, sandbox di conversione e storage multi-replica.
