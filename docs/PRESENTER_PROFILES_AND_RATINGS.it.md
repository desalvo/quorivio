# Profili, collaborazione e gradimenti multipli — Quorivio 0.1.0-dev

## Scelta del progetto
All'apertura del workspace vengono mostrate le sessioni di cui l'utente è **autore/proprietario** e quelle per cui è **invitato alla collaborazione**, esplicitamente etichettate. Gli amministratori approvati possono essere presentatori, ma le sessioni altrui non diventano automaticamente proprie.

## Profilo
Il presentatore può impostare un nome pubblico (2–100 caratteri) e un URL HTTPS della foto. La foto è attualmente un riferimento remoto e non un upload gestito; utilizzare immagini autorizzate e valutare privacy e trasferimenti di dati verso servizi esterni. Se il nome non è disponibile, l'interfaccia pubblica usa una dicitura neutra, senza esporre l'email.

## Widget profilo
Nell'editor della pagina scegliere `+ profile`, scegliere il presentatore tra quelli della sessione, salvare. Si possono inserire più widget e rimuoverli individualmente. Nelle pagine di partecipazione il widget visualizza nome e foto (se configurata). L'integrazione su tutte le tipologie di pagine e sulla vista risultati resta aperta.

## Valutazioni da 0 a 10
Inserire più widget `rating` con ID diversi; configurare l'oggetto della valutazione: domanda, quiz, sessione o presentatore. Per presentatore selezionare la persona destinataria della valutazione. Ogni partecipante può assegnare una valutazione a ciascun widget nella pagina; i risultati sono raggruppati per widget e oggetto e visibili ai presentatori autorizzati. La corrispondenza `quiz` con un quiz multi-domanda non è ancora implementata; al momento l'ID dell'attività è usato come riferimento.

## Migrazione e validazione
La migrazione aggiunge i campi del profilo e amplia la chiave delle valutazioni da `(activity_id,participant_id)` a `(activity_id,participant_id,widget_id)`, preservando le valutazioni storiche nel widget `legacy-rating`. Eseguire il backup prima di applicare la migrazione e collaudare PostgreSQL reale. Non considerare production-ready senza test di integrazione e privacy.
