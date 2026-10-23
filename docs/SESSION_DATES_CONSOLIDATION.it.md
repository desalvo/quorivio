# Date delle sessioni — editor consolidato

La dashboard utilizza un solo editor principale: data, ora iniziale locale, durata in minuti e fuso orario IANA esplicito. Restano invariati la tabella `session_appointments` e le API esistenti, senza migrazioni.

Le vecchie date senza orario non vengono cancellate. Quando presenti, la sezione espandibile consente di importarle nella lista moderna con ora, durata e fuso attualmente selezionati. Per confermare occorre salvare. Le date con identica data/ora/fuso non vengono duplicate e l'elenco è ordinato per data e ora. Le API legacy rimangono disponibili per compatibilità.

Verifiche locali: 121 test Python e 107 Node.js superati. Sono test in prevalenza unitari/contrattuali, non sostituiscono il collaudo sul cluster. Restano da verificare browser, database reale e transizioni DST. Build completa non verificata per assenza delle dipendenze npm nell'ambiente. RC 37,5% invariata.

Collaudo sul cluster: aggiungere due date con ore e fusi diversi, salvare, ricaricare e verificare il calendario nelle tre viste; importare una data legacy; salvare e ricaricare; controllare duplicati, fusi/DST e sessioni esistenti.
