# RC244 — Arial predefinito nelle widget dell'editor e regressione Chromium

**Origine:** full CI GitHub [42377514266](https://github.com/desalvo/quorivio/actions/runs/42377514266), RC243 committata `a0e7dbcf22b6f73ce8a04caa028ef4745825698e`.

**Errore:** il test Chromium dell'editor `tools/ci_rc224_thumbnail_menu_chromium.py` a 320×240 ha trovato due elementi Arial e due in `DM Sans`. La regola CSS RC242 impostava `font-family:inherit` sulla *radice* `.widget-canvas-item` e annullava il default Arial del canvas degli schemi, ereditando il font generale dell'app.

**Correzione:** Arial è dichiarato sulla radice di ciascuna nuova widget sia nell'editor pagine sia in quello schemi. I discendenti ereditano il font della widget e continuano a rispettare i font personalizzati salvati inline, quali Georgia e Verdana. Nessuna modifica ai caratteri delle pagine generali dell'app.

**Verifiche:** il test Chromium RC242 ora lascia intenzionalmente *senza* `font-family` inline le widget predefinite dei 20 tipi, su entrambi gli editor; vengono comunque verificate le scelte esplicite. Rimane il test Chromium RC224 anche a 320×240. Quattro nuovi test Python RC244 vengono eseguiti prima di npm e includono mutazioni negative del CSS e del test browser. Nessun controllo obbligatorio rimosso.

**Rilascio:** RC243 storica immutata, RC244 inventario corrente, versione `0.1.0-dev`. Completamento certificato **85,25%** (43 gate accettati, 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. L'assistente non ha eseguito commit, push, tag o pubblicazioni. La full CI RC244 rimane da verificare.
