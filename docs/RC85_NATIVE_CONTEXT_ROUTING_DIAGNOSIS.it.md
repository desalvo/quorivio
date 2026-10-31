# RC85 — menu contestuale nativo, evento del tasto destro

- Base commit `2d081ae95594ab79a743822476dee77336f6ea9e`; fallimento GitHub `41237085040` / job `124643010292`. I test Node e la compilazione passano; la CI estesa arresta il collaudo Chromium sul menu widget, mentre il menu canvas risulta aperto.
- Il vecchio `onPointerDown` eseguiva `toggleSelection` anche per `e.button===2` quando un widget non era selezionato. Questo può cambiare la geometria del layout tra `pointerdown` e `contextmenu`.
- RC85 sposta la selezione del pulsante destro al solo `contextmenu`, con recupero dell'identità widget acquisita durante lo stesso `pointerdown`, limitata temporalmente e spazialmente. Nessun click forzato/sintetico in Chromium.
- Diagnostica: `native_target_trace` contiene esclusivamente tipo evento, pulsante e appartenenza a widget, senza contenuti/credenziali. Se fallisce ancora, usare questi dati prima di altre modifiche.
- Test: backend/frontend Node, contratti Python, inventario e ZIP da verificare prima del commit. Build TypeScript completa e browser Chromium end-to-end non verificabili localmente; richiedono CI successiva. `rc_strict=false`, `publish_image=false` e nessun nuovo gate accettato.
