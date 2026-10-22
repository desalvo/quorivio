# Autenticazione e rate limiting condivisi fra repliche

La nuova tabella `auth_flows` conserva solo l'hash dello `state` OAuth, il tipo del flusso, il provider e i dati temporanei richiesti per completare il callback. Lo stato scade dopo cinque minuti e viene eliminato atomicamente dal primo callback valido. Il callback mantiene i controlli del cookie dello state e l'associazione esplicita dell'identità. Le colonne sono eliminate automaticamente quando viene eliminato l'utente collegato.

La tabella `api_rate_windows` memorizza un hash dell'IP e un bucket temporale di un minuto. La soglia globale attuale è 100 richieste/minuto per indirizzo IP, condivisa da tutte le repliche; la risposta è HTTP 429 oltre soglia. In caso di errore PostgreSQL l'API risponde con 503. La manutenzione cancella gli stati scaduti e i bucket obsoleti ogni ora.

**Limiti:** questo non sostituisce WAF/reverse proxy; richiede configurazione affidabile di IP client e proxy, test di concorrenza, verifica delle migrazioni e collaudo degli SSO reali. La soglia globale riguarda l'IP, non l'utente. Le credenziali dei provider devono essere fornite separatamente tramite Secret, mai nel repository.
