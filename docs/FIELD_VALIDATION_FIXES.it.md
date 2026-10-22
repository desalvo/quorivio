# Esito della validazione — fasi 1 e 2

## Fase 1
Docker Compose avviato su ARM64 utilizzando `clamav/clamav:stable-debian`. Il compose di default usa ora questa variante. Verificare sempre la disponibilità dell’immagine per la propria architettura e le scansioni effettive.

## Fase 2 — Correzioni
- Login: email oppure nickname univoco; l’admin principale è `admin` anche se cambia email.
- Dopo il cambio obbligatorio della password compare la schermata di login senza reload.
- Account principale protetto da declassamento, revoca dell’approvazione ed eliminazione.
- Separazione delle aree utente, server, SSO, MFA, profilo e workspace.
- Approvazione utenti con stato cromatico e attivazione/disattivazione immediata.
- SMTPS configurabile nell'interfaccia; le credenziali sono cifrate nel DB con la chiave AUTH_SECRET. Usare SMTP su connessioni TLS con certificato valido.
- MFA: richiede SMTP configurato; TOTP URI completo e QR PNG visibile soltanto all’utente autenticato durante l’enrollment.
- Sessioni con zero o più appuntamenti di calendario.

## Da verificare / mancante
- Nuovo ciclo CI, migrazione DB su installazione già esistente, navigazione browser e email reali.
- La modalità email come secondo fattore opzionale non è ancora implementata; non abilitarla come alternativa TOTP senza validazione completa.
- Configurazione e provisioning amministrativo completo degli SSO e attivazione MFA per conto degli utenti non ancora completati.
- Un calendario grafico avanzato non è ancora presente: è disponibile la selezione di più date native.
- Non etichettare come release candidate approvata fino a completamento dei collaudi.
