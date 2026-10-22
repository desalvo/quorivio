# Verifica integrata tramite GitHub Actions

Questo package estende il job `validate` della CI. Dopo test Node, build API/frontend e installazione del client PostgreSQL, il job avvia un server PostgreSQL 18 temporaneo, inizializza Quorivio con credenziali **esclusivamente di test**, interroga `/api/health/ready` e `/api/health/live`, verifica la disponibilità della homepage, l'account amministrativo iniziale e alcune tabelle critiche. Controlla inoltre che l'API di identità non autorizzi accessi anonimi.

Il job `image-build` costruisce anche l'immagine del convertitore isolato. Il controllo Trivy rimane bloccante sull'immagine applicativa; la nuova immagine converter necessita ancora di una scansione dedicata prima della pubblicazione e del deployment operativo.

## Intervento richiesto al proprietario del repository

1. Eseguire **il commit e il push** del nuovo package su un branch, senza tag di release. L'assistente non effettua commit né push.
2. Aprire la scheda **Actions** del repository, eseguire la workflow Quorivio CI sul branch o aprire una PR, ed esaminare `Production quality gate` e `Container build gate`.
3. Se la CI fallisce, riportare i log relativi al primo step fallito (senza segreti). Le credenziali per il PostgreSQL CI sono effimere, non utilizzabili in produzione.
4. Non promuovere in produzione finché non sono verificati separatamente provider SSO, invio SMTPS, ClamAV reale, migrazioni dati esistenti e deployment con più repliche.

**Limitazione:** non è stato possibile eseguire questa pipeline nel sandbox locale, dove non sono disponibili né il Docker engine né le dipendenze npm necessarie alla compilazione. Una CI verde non prova il corretto funzionamento del cluster di produzione.
