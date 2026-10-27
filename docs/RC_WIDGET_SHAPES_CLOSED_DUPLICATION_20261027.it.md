# Batch Release Candidate — Stili avanzati dei widget e duplicazione sessioni terminate

Data: 27 ottobre 2026. Base: ultimo ZIP cumulativo **non ancora committato** per dashboard/aspetto widget. Ultimo commit esplicitamente confermato: `67a7be939a5930e2f9a49ce3932a4b7f29a682ac`.

## Funzionalità implementate

- **Duplica sessione** dall'elenco Apri sessione, anche per sessioni terminate, se proprietario o collaboratore autorizzato. L'API duplica definizioni, pagine, widget, temi e allegati referenziati in una nuova **bozza** di proprietà del richiedente, con UUID, codice e secret nuovi. Non trasferisce risposte, voti, statistiche, partecipanti, code di moderazione, credenziali o stato live. Prima dell'azione compare una conferma esplicita.
- Collaudo PostgreSQL di duplicazione aggiornato: chiude davvero la sorgente prima della copia e verifica bozza, ID e codici diversi, allegati autonomi.
- **Forme widget:** rettangolo, rettangolo arrotondato, ovale, cerchio, triangolo, rombo, esagono, nuvola, fumetto. Riempimento solido, trasparente/opacità regolabile, gradiente o immagine privata per singolo widget, scegliendo dalla libreria o caricando direttamente. Proprietà rigorosamente validate nell'API, immagini vincolate alla sessione. Esportazione/importazione e copia rimappano gli ID delle immagini indipendenti.
- Palette rapida di formattazione sotto il canvas **solo durante la selezione**, con icone, descrizioni, colori, allineamento, grassetto/corsivo e acceso alle proprietà complete. Clic sullo sfondo vuoto nasconde la palette.
- Conferma obbligatoria di cancellazione da pulsante ×, menu, tastiera, taglio e operazioni multiple. Bordi magnetici e rifiuto delle collisioni rettangolari durante spostamenti, dimensioni e allineamenti; ricerca di posizioni libere in inserimento e duplicazione. La geometria usa i rettangoli non ruotati: servono ancora collaudi con rotazioni e dispositivi reali.
- Gradimento predefinito 0–10 con minimo/massimo indicati, opzione menu combo; reazioni visibili; contatore con valore 0 in anteprima se vuoto; timer con conteggio in anteprima; QR, presentatore e risultati di prova. I risultati restano riservati al presentatore nella sessione reale.

## Accettazione

Test locali Python/Node, validazione e geometria da registrare negli esiti; **Full CI GitHub con Chromium/PostgreSQL ancora da eseguire**. Verifiche indipendenti di aspetto, accessibilità, imaging e collisioni con forme ruotate ancora aperte. Ledger RC **53,0%**, `release_candidate_ready=false`: nessuna promozione automatica dei gate. Nessun commit, push o rilascio effettuato.
