# RC135 — Riconciliazione dei contratti CI dell'editor

2 novembre 2026. Basato sul cumulativo RC134 già committato (`3c75a548b277d179db49f1293fef3d5da5926f8b`). La run GitHub `41435798792` si è fermata al preflight `Validate RC89 editor review regressions before npm`: 7 test su 8 superati, uno cercava ancora l'antica etichetta con apostrofo ASCII `Casella di risposta libera nell'editor`. Da RC132 l'etichetta accessibile usa l'apostrofo tipografico, e RC134 ha sostituito anche l'etichetta della domanda del presentatore. La build e i test browser non sono stati avviati.

## Correzioni

- RC89 verifica il componente condiviso `EditorAnswerFieldPreview`, le etichette attuali, la maniglia da tastiera e il pulsante disabilitato del presentatore.
- Il test di sicurezza del puntatore controlla che `role=slider` non avvii il trascinamento dei widget.
- RC109 controlla il campo risposta nella proiezione reale e l'helper geometrico che disattiva `autoFit` dopo il ridimensionamento manuale, lasciando la possibilità di riattivarlo.
- Il test delle opzioni proiettate verifica i radio/checkbox nativi, disabilitati e formattati, invece della vecchia lista decorativa.
- Aggiunto un preflight anticipato alla CI e una nuova ricevuta SHA-256 RC135, mantenendo immutati gli inventari storici.

**Nessuna modifica al codice applicativo né ai permessi di pubblicazione Docker.** La CI completa, la build e i test Chromium/PostgreSQL RC135 dovranno essere verificati su GitHub. Completamento certificato **85,25%**, 43 gate accettati/17 parziali; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Ultima baseline verde RC130 (`41420021082`). Nessun commit, push o release dell'assistente.

## Verifiche locali

- Suite Python: **1.689 test**, 1.688 superati, 1 saltato, 0 falliti.
- Frontend Node: **209/209** superati.
- Parser TypeScript: nessun errore sintattico nei moduli TSX e delle collisioni.
- Sorgenti e ZIP cumulativo: inventario SHA-256 verificato.
- Build npm/Vite completa e CI GitHub RC135 ancora da verificare.
