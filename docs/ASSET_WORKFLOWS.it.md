# Allegati e report — procedure del presentatore (0.1.0-dev)

1. Accedere con account presentatore approvato e aprire una sessione di propria competenza.
2. Nel riquadro **Allegati della sessione** selezionare un file PNG, JPEG, GIF, WebP, PDF, MP4 o WebM. Il limite iniziale è 100 MB per singolo file. Il backend controlla dimensione, formato dichiarato e firma binaria; può rifiutare il file.
3. Premere **Aggiorna allegati** per vedere gli asset caricati, aprire il collegamento autenticato oppure eliminare un asset non più necessario. Non distribuire questo collegamento ai partecipanti: è riservato ai presentatori autenticati. La gestione nel frontend non costituisce ancora un editor grafico degli asset.
4. Nel riquadro **Dati della sessione** usare **Report JSON aggregato e audit**. Il report comprende metadati sessione, attività, conteggi di risposte valide/invalidate, audit delle invalidazioni e inventario degli allegati con hash. Non contiene i file binari, non è un backup completo, non include identità dei partecipanti.
5. Come amministratore, cambiare il campo **Limite upload (MB)** in **Amministrazione**. Per Kubernetes occorre rigenerare/applicare la configurazione dell'Ingress attraverso il wizard. Il valore deve essere coerente con limite del proxy e capacità storage.

**Operazioni ancora non disponibili:** backup/ripristino integrale con PostgreSQL e media, upload in streaming, scanner antivirus, storage S3 condiviso, inserimento media visuale con anteprime per tutti i ruoli e cancellazione garantita di file orfani. In produzione non considerare sufficiente questa implementazione per dati non fidati ad alto rischio.
