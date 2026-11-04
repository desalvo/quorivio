# Quorivio RC159 — Pulsanti sessione, gradimento, limiti e parità presentazioni reali

Stato: modifiche locali pronte per verifica CI; nessun commit o pubblicazione automatica.

## Evidenze GitHub

- Run 41730792802 sul commit RC157 (`a1155ac`): conclusione **success**, inclusi quality gate, Chromium/Firefox/WebKit, Podman, Kubernetes, native OCI e riepilogo RC.
- Run 41739841860, sullo stesso commit RC157: conclusione **success**, con Container build gate, immagini AMD64/ARM64 e **pubblicazione Docker Hub multiarch**.
- La RC158 continua ad includere la correzione preventiva dei prerequisiti Playwright del workflow manuale; la RC159 ne conserva le modifiche.

## Interventi RC159

- Dashboard: **Termina rosso**, **Pausa verde chiaro**, **Riporta a non avviata celeste**, contrasto del testo verificato.
- Gradimento: campo **Commento facoltativo** con sfondo bianco e testo scuro in editor e anteprime (sola lettura), modificabile nella sessione reale. Conservati voti da 0 a 9.
- Domande: unica dicitura **«Invia risposta»** senza suffissi non richiesti.
- API: limiti per classe di richiesta autenticata: letture presentatore 360/minuto, navigazione pagina 180/minuto, default/sensibili 100/minuto. I limiti sono persistiti nel database, fail-closed, condivisi tra repliche. Non sono un bypass del rate limiting.
- Partecipante reale: la visualizzazione iniziale è **16:9**, non la modalità accessibile o smartphone automatica; larghezza dedicata al canvas, senza limite storico di 640 px. La modalità di lettura resta selezionabile esplicitamente.
- Rimosso il titolo di pagina duplicato **fuori** dal canvas partecipante. Titolo/footer/testo/note/grafica usano il renderer condiviso con anteprima e schermo presentatore, con le stesse proprietà di titolo master.
- Presentatore reale: il titolo nel canvas non eredita più la regola globale `.projection h2` che forzava una dimensione diversa dall'anteprima. Le dimensioni vengono dal font salvato e dalla larghezza del canvas.
- Sfondo pubblico: applicato anche il colore o URL di sfondo salvato quando non c'è asset, come nelle anteprime.
- Guard di regressione RC131 aggiornato per la nuova risoluzione corretta del titolo master; non è stato disabilitato.

## Verifica

- 586 test Node backend e 255 frontend superati localmente.
- Test contrattuali RC159 e RC131 e regressioni negative superati.
- Chromium reale di prova CSS a 1440 e 390 px: proporzioni 16:9, coordinate del titolo (8%, 3%), tipografia scalata sul canvas e controlli/colori del gradimento superati.
- **Da confermare**: rendering visivo end-to-end autenticato con le tre schermate reali fornite dall'utente, compilazione TypeScript/Vite completa, intera nuova GitHub CI e prova sul server reale con 500 utenti. Non attribuire validazione completa finché assenti.
- Completamento certificato mantenuto 85,25% (43 gate accettati, 17 parziali) in attesa di accettazione ulteriore.
