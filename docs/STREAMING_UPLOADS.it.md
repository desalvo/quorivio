# Caricamenti binari in streaming — 0.1.0-dev

Gli endpoint `POST /api/sessions/:id/assets` e `POST /api/join/:code/activities/:aid/widgets/:wid/upload` scrivono ora i file progressivamente su disco, con limiti applicati durante la lettura. Il trasferimento usa file temporanei privati e nomi UUID; SHA-256 e controlli della firma binaria sono calcolati senza mantenere l'intero file in memoria. Se il trasferimento non coincide con `Content-Length`, supera il limite o non presenta una firma valida, il temporaneo è rimosso. Il riferimento nel database viene creato solo dopo il completamento della scrittura.

## Procedura di prova

1. Configurare `QUORIVIO_ASSET_DIR` su un volume persistente privato e il limite upload nella pagina amministrativa (100 MB di default).
2. Con una sessione aperta inviare PNG, JPG, GIF, WebP, PDF, MP4 o WebM autorizzati. Ripetere con Content-Length errato, MIME falso e corpo troncato, verificando la risposta di errore e l'assenza di temporanei.
3. Per gli allegati dei partecipanti verificare cookie, sessione aperta, widget `file` attivo e proprietà dell'allegato.
4. Verificare checksum, download autenticato, ripristino da backup, quota disco e riavvio del servizio.

## Limiti aperti

Non esiste ancora una scansione antivirus/antimalware, né un archivio S3 condiviso per più repliche, né una coda durevole per pulizia/riparazione dopo crash. L'header Content-Length resta obbligatorio. Il limite di quota per partecipante va reso atomico rispetto agli upload concorrenti. Le firme binarie basilari non sostituiscono un'ispezione profonda dei file. Non dichiarare l'upload pronto alla produzione senza test reali su PostgreSQL, browser, proxy e filesystem.
