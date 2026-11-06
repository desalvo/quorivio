# RC223 — Finestra Formato contestuale e geometria delle widget

**Baseline:** RC222; ultima full CI GitHub confermata verde **RC219**, run `42197607753` (14 job riusciti). RC220–RC223 ancora da convalidare in CI. Versione invariata **0.1.0-dev**. Completamento verificato **85,25%**, 43 gate accettati e 17 parziali. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag.

## Interfaccia Formato widget

- La finestra non compare più semplicemente selezionando o facendo doppio clic su una widget: si apre esclusivamente con **menu contestuale della widget → Formato**. La chiusura non deseleziona la widget. I menu con tastiera e touchscreen conservano il percorso contestuale.
- La finestra flottante ha cinque schede, **Testo, Bordi, Effetti, Contenuti, Collegamenti** (l'ultima solo per le widget risultati), con larghezza/altezza limitata allo schermo; l'elenco delle schede scorre orizzontalmente sui telefoni.
- **Testo:** carattere, dimensione, stile, allineamento orizzontale e verticale, campi dedicati a risposte, titolo e numero pagina. **Bordi:** colore, spessore, stile continuo/tratteggiato/punteggiato, forma, riempimento. **Effetti:** tema, animazione, effetti e trasparenza. **Contenuti:** visibilità del titolo o della domanda principale, opzioni di visualizzazione risultati, URL QR e footer. **Collegamenti:** pagina, widget e sottodomanda sorgente dei risultati, preservando la validazione server.
- Le configurazioni salvano soltanto campi già ammessi da `validWidgetTextStyle` / `validPageDesign`, senza CSS o URL arbitrari.

## Correzioni di geometria

- **Footer:** rimosso l'allineamento centrale imposto dai vecchi stili CSS; rispettati gli allineamenti orizzontali sinistra/centro/destra e verticali alto/centro/basso in editor, anteprima e proiezione, senza spostare il numero di pagina.
- **QR:** il link pubblico effettivo è una URL cliccabile e selezionabile su **una sola riga**, con fascia dedicata non ridimensionata dall'immagine. Su una widget molto stretta, la URL completa resta raggiungibile con scroll orizzontale (non è possibile mostrarla tutta insieme a dimensione leggibile in qualunque larghezza). Il QR usa lo spazio rimanente; mai ridurre insieme URL e immagine.
- **Partecipanti connessi:** eliminato il padding/gap eccessivo; dimensioni del numero e del titolo calcolate in base alla geometria della widget (`cqw/cqh`), con titolo opzionale e senza ridimensionamento globale della widget.

## Validazione locale

- Suite Node API: **625/625**; frontend: **385/385**.
- Test Python mirati: **34/34**, inclusi 7 nuovi test RC223, inclusi mutanti negativi.
- Chromium reale, con CSS consegnato e DOM rappresentativo, **390 e 1440 px**: footer, URL QR e contatore validati. Non equivale al browser acceptance React compilato/PostgreSQL completo.
- Verifica sintattica TypeScript dei file modificati, inventory hash SHA-256 del package e controlli di release al momento del confezionamento.

## Residui / handoff

Verificare la full CI GitHub della RC223, in particolare React compilato (editor, anteprima, partecipante), auto-fit, resa footer con testo multilinea, QR con URL estremamente lungo su widget minime e comportamento dello scroll con accessibilità tastiera. Non attribuire gate aggiuntivi finché la CI e la validazione manuale non sono verdi.
