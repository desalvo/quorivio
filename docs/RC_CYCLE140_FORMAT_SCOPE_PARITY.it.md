# RC140 — Ambiti di formattazione e parità grafica (2 novembre 2026)

Baseline: RC137 già committata e CI completa verde (`41475936282`); RC138–RC140 rimangono cumulative **non ancora committate**.

## Correzioni

- Eliminate dal bordo dei widget le iconcine intrusive di duplicazione/ordine; le stesse azioni sono ancora disponibili nel menu contestuale e nei controlli accessibili. Il titolo rimane cliccabile e modificabile.
- La finestra floating **Formato widget** distingue widget intero, titolo, descrizione e risposte. Il doppio clic entra nel campo realmente scelto, senza riportare sempre il cursore al primo titolo.
- I comandi A−/A+ modificano proporzionalmente tutte le grandezze del widget, preservando differenze preimpostate fra titolo, risposte, pulsante invio e segmenti di testo. Non presentano più un valore unico di dimensione per testi differenti.
- La modifica generale di font, colore e stile si estende alle risposte e ai segmenti di testo già formattati; quella di un singolo campo o selezione non altera gli altri testi.
- Nell'editor le opzioni usano la stessa funzione di stile `answerOptionStyle` delle anteprime e della proiezione reale. Tipografia e colore provengono dagli stessi dati validati dal backend; il testo lungo può andare a capo.
- Le frecce nei controlli numerici della barra non attivano gli shortcut del canvas. Tutte le modifiche continuano a salvare testo semplice e marcatori di stile per intervallo, senza HTML.

## Verifiche e gate

Verificati localmente Node, contratti Python mirati, parsing TypeScript e integrità SHA-256 del cumulativo. La build completa npm/Vite non è stata eseguita: `npm ci --offline` non dispone di tutti i pacchetti; CI GitHub e confronto grafico nel browser reale rimangono obbligatori.

**Completamento certificato 85,25%** (43 gate accettati / 17 parziali): `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag/release da parte dell'assistente.
