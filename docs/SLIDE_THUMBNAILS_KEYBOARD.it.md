# Barra delle slide: miniature geometriche e riordino da tastiera (23 ottobre 2026)

La barra del presentatore disegna il titolo di ogni pagina e fino a 24 widget con coordinate x/y, larghezza, altezza e rotazione salvate. Se presente, viene utilizzato lo sfondo grafico della pagina; i widget immagine/video sono rappresentati da simboli, **non** dalla decodifica del contenuto multimediale. La miniatura usa DOM/CSS, non uno screenshot né il rendering completo del partecipante; gli stili dei singoli widget e il ritaglio sono quindi approssimati. Per le pagine con widget non compare più soltanto una scritta simbolica.

Trascinare una pagina su un'altra per riordinarla. Da tastiera, selezionare una pagina con il focus e premere **Alt+Sinistra** o **Alt+Destra**. Si utilizza l'endpoint esistente di riordino sul server; il riordino è disabilitato per le sessioni chiuse. Restano disponibili i comandi della lista pagine. Il rendering delle miniature non modifica le risposte.

Verificato localmente: 85 test Node e 88 test Python, inclusi due controlli statici di regressione della funzione. Non verificati: build completa Vite/TypeScript (dipendenze npm offline mancanti), uso drag/tastiera multi-browser, screen reader, integrazione PostgreSQL/sessione e resa precisa degli asset multimediali. La RC non è dichiarata completa.
