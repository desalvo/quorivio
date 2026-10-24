# Gestione pagine di una sessione

Dalla dashboard scegliere **Modifica le pagine**. Si apre un workspace che occupa la finestra: miniature a sinistra, barra widget orizzontale e canvas centrale. Le miniature possono essere trascinate o riordinate con i pulsanti. Dalla stessa barra laterale si creano pagine vuote, sondaggi, quiz e quiz a tempo, si duplicano e si cancellano le pagine.

**Avvertenza:** cancellare una pagina elimina definitivamente anche le risposte associate. Per le modifiche al canvas utilizzare **Salva layout** prima di cambiare pagina. Utilizzare **Torna alla dashboard** per uscire dall'editor.

Il problema di creazione della pagina vuota era un mismatch fra placeholder e parametri della query SQL. Il nuovo endpoint DELETE esegue la cancellazione in transazione, libera l'eventuale pagina pubblicata e notifica gli utenti connessi.

La verifica browser e il comportamento in cluster restano da collaudare.
