# RC71 — Accettazione provvisoria della gestione sessioni e timer

Il countdown di una pagina nasce solo quando viene pubblicata per la prima volta. Riaprirla non ne rinnova la scadenza. L'owner o un presentatore autorizzato può riavviarlo con conferma, eliminando le vecchie risposte e gli allegati personali collegati alle risposte. Il reset della sessione porta allo stato `ready` e cancella definitivamente i dati di partecipazione, preservando la configurazione.

Entrambi i flussi richiedono nuovi test CI PostgreSQL per essere certificati; le verifiche disponibili non provano alcuna approvazione GDPR/AGID esterna. Il presentatore deve essere autenticato anche per aprire lo schermo tramite QR.
