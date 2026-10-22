# Collaudo fase 2 — 23 ottobre 2026

## Correzioni implementate in questo cumulativo
- Login con identificativo email o nickname: input web non più limitato a `type=email`.
- Campo di conferma della nuova password al primo accesso.
- Popup dismissibili e avvisi temporizzati; messaggio sui cookie funzionali con scelta tecnica memorizzata in cookie.
- Form nuovo utente con nickname facoltativo; editing nickname dall'amministrazione, bloccato per l'amministratore principale.
- Utenti: dettaglio collassabile, filtro e paginazione client-side 10/20/50/100; lista limitata a 1.000 record dal backend (paginazione server-side ancora da realizzare).
- Workspace: elenco sessioni non più nella sidebar, ricerca, paginazione client-side e schede collassabili.
- SMTP: TLS implicito e STARTTLS obbligatorio, indirizzo mittente email e nome mittente personalizzabile, riscontro visibile sul controllo configurazione e invio email di prova.
- Duplica sessione: assegna un nome differente con suffisso Copia.

## Funzionalità ancora aperte
- Paginazione, ordinamento e ricerca server-side su tutto lo storico senza limite fisso; calendario grafico mensile/settimanale con eventi multi-giorno, orario e durata.
- Session editor separato in tab tematiche, pausa/ripresa coerente su API/UI; toggle cromatici standardizzati per tutti i booleani.
- Validazione browser integrata dei componenti amministrativi e dei CSS, della UI responsive e del consenso cookie.
- Prove STARTTLS/SMTPS reali e verifica delle migrazioni su database esistente.

## Verifiche tecniche
La suite Node/Python locale è eseguita prima della pubblicazione; la compilazione frontend npm completa e la CI richiedono verifica successiva. La nuova versione non modifica il numero `0.1.0-dev`.
