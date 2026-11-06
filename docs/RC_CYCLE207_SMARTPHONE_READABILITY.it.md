# RC207 — leggibilità dei widget delle domande su smartphone

Base: cumulativo RC206; versione applicazione invariata `0.1.0-dev`.

## Causa e correzione
L'editor smartphone, l'anteprima e la vista pubblica usano un canvas verticale da 390 pixel logici. In precedenza, risposte, caselle e pulsanti utilizzavano ancora dimensioni relative al canvas desktop da 1280 pixel (`cqw`), rendendo ad esempio un testo da 16px circa 4,9px sul telefono. Lo stesso accadeva ai singoli caratteri formattati. Le altezze automatiche delle opzioni erano insufficienti per testi lunghi.

- Titolo domanda predefinito Arial/grassetto da 22px, risposte e pulsanti da 18px; scelte e pulsanti alti almeno 44px e campi liberi almeno 76px. Il desktop non cambia.
- Misure espresse in pixel logici su tutte le tre viste smartphone, senza perdere le dimensioni e i font personalizzati dall'autore.
- Formattazione delle singole porzioni di testo preservata con dimensione smartphone dedicata.
- Layout automatico adattato per risposte su più righe fino a 255 caratteri e sottodomande, senza riscrivere le posizioni personalizzate.
- Test preventivo Python/Node e verifica con Chromium reale integrati nella CI.

## Evidenze locali e verifiche ancora aperte
Test Node API `616/616`, frontend `360/360`, regressioni Python mirate `40/40` e prova CSS Chromium reale superati per editor, anteprima e partecipanti, comprese personalizzazioni a 26/27px. Il typecheck Vite/React completo non è disponibile localmente per assenza di `vite/client`; integrazione PostgreSQL e full CI GitHub RC207 ancora da certificare. Completamento funzionale **85,25%**, 43 gate accettati, 17 parziali. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag dell'assistente. Ultima full CI verde confermata: RC203 `42110429701`.
