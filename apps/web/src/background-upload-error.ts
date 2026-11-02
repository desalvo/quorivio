/** Safe, actionable reason for a background upload rejection. Never embed raw server HTML. */
export function backgroundUploadError(status:number,code:string):string{
 const messages:Record<string,string>={
  session_closed:'La sessione è chiusa: non è possibile modificare lo sfondo.',
  invalid_upload_size:'File troppo grande o vuoto. Controlla il limite di caricamento nelle impostazioni del server.',
  unsupported_background_media:'Formato non supportato dal server: usa JPG, PNG, GIF o WebP.',
  invalid_media_content:'Il contenuto del file non corrisponde al tipo immagine dichiarato.',
  invalid_asset_content:'Il file non è un’immagine valida per questo formato.',
  antivirus_unavailable:'Scanner ClamAV non disponibile o non pronto in Kubernetes (HTTP 503). Controlla i log del container clamav: il caricamento resta bloccato per sicurezza.',
  background_storage_unavailable:'Volume degli allegati Kubernetes non accessibile (permessi, spazio o PVC, HTTP 507/503). Verifica /app/assets nel pod.',
  background_database_unavailable:'PostgreSQL non disponibile per il salvataggio dello sfondo (HTTP 503). Controlla i log del container quorivio.',
  background_processing_failed:'Errore interno durante la preparazione dello sfondo (HTTP 500). Controlla la fase background_upload_failed nei log Kubernetes.',
  invalid_media_signature:'I dati del file non corrispondono al formato immagine dichiarato.',
  upload_length_mismatch:'Il trasferimento del file è incompleto. Riprova e controlla il proxy Ingress.',
  malware_detected:'Il file è stato rifiutato dal controllo antivirus.',
 };
 if(code&&messages[code])return messages[code];
 if(status===401||status===403)return 'Accesso scaduto o permessi insufficienti per modificare la sessione (HTTP '+status+').';
 if(status===404)return 'Sessione o servizio di upload non trovato (HTTP 404).';
 if(status===409)return 'La sessione non accetta modifiche (HTTP 409).';
 if(status===413)return 'Il file supera il limite massimo configurato sul server (HTTP 413).';
 if(status===415)return 'Formato immagine rifiutato dal server (HTTP 415).';
 if(status===507)return 'Spazio o permessi del volume degli allegati insufficienti (HTTP 507).';
 if(status>=500)return 'Errore del servizio di caricamento (HTTP '+status+'). Verifica i log del server e lo scanner antivirus.';
 return 'Caricamento rifiutato dal server (HTTP '+status+(code&&/^[a-z0-9_]{1,64}$/i.test(code)?', '+code:'')+').';
}
