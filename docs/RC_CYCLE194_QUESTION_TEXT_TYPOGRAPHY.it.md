# RC194 — Tipografia uniforme e selezione rich-text

## Funzioni implementate

- Le risposte lunghe delle domande e dei sondaggi vanno automaticamente a capo in editor, anteprime e proiezione reale: la casella cresce secondo il contenuto e non applica l'ellissi su una sola riga. La disposizione dei controlli radio/checkbox rimane invariata.
- La formattazione selettiva tramite «Formato widget» mantiene la selezione visibile dopo l'applicazione del font e degli altri attributi: al termine dell'aggiornamento React il cursore ritorna alla casella originaria e la selezione è ripristinata, salvo chiusura manuale dell'editor.
- I nuovi widget domanda/quiz hanno come impostazioni predefinite **Arial**, domanda **grassetto 22** e risposte **normali 16**. Lo stesso fallback viene applicato alle vecchie domande prive di valori espliciti, senza modificare i campi personalizzati già salvati. Sono incluse le sottodomande.
- «Widget intero» propaga il **tipo di font** e gli altri parametri di testo al widget, alle risposte e alle marcature rich-text, comprese quelle delle sottodomande. La famiglia desiderata non viene più cancellata dal vecchio CSS `font:inherit!important`.
- La digitazione all'interno di testo formattato eredita **il font e gli altri attributi del carattere immediatamente precedente**. Ciò vale anche sul confine tra due segmenti, con caratteri Unicode e con le opzioni di risposta delle sottodomande.

## Verifiche

- Suite Node frontend e API complete; regressioni specifiche Node e unittest Python; TypeScript rigoroso dei moduli condivisi.
- Browser Chromium su CSS reale a 1440 e 390 px: font calcolato, gerarchia domanda/risposte e opzioni effettivamente su più righe.
- I controlli Node/Python RC194 sono inseriti prima di npm nella CI. Il test Chromium di impaginazione completa quello integrato dell'editor già previsto per PostgreSQL/React. La validazione end-to-end del nuovo cumulativo è ancora **da confermare su GitHub**, non è certificata localmente.
- Versione di prodotto invariata: `0.1.0-dev`; punteggio globale certificato invariato **85,25%** (43 gate accettati, 17 parziali); non eseguire commit/push/tag automaticamente; nessuna pubblicazione Docker automatica.
