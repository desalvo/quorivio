# RC119 — Misura autofit senza maniglie e duplicazione Chromium

La run `41336263788` ha rilevato 3 widget invece di 5 dopo la duplicazione. La schermata di errore mostra widget con brevi etichette estesi fino al fondo del canvas. L'autofit misurava lo `scrollHeight` di `.widget-canvas-item`, comprensivo delle maniglie di ridimensionamento che sporgono dal bordo, provocando una crescita ripetuta indipendente dal testo e togliendo spazio alla duplicazione del gruppo.

La RC119 legge `.widget-fit-content.scrollHeight` e `.widget-fit-frame.clientHeight`. Conserva l'espansione per contenuti realmente troppo lunghi, le collisioni bloccanti, il ridimensionamento manuale e l'Undo singolo. Chromium ora rileva un'espansione anomala prima dell'azione e riporta gli avvisi di impossibilità di inserimento prima di aspettare un conteggio che non arriverà. La full CI GitHub resta obbligatoria; nessun punto percentuale aggiunto.
