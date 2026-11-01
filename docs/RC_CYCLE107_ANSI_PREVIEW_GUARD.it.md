# RC107 — Avvio preview Vite con messaggi ANSI

Nei log CI RC106 `logs_111954785384.zip` i test Chromium passano, ma il controllo nel trap finale non riconosce il banner Vite colorato e fallisce con `compiled-preview readiness evidence is absent`.

## Modifica

- Normalizzazione dei codici ANSI nel testo analizzato, senza cambiare il log originale.
- Rimangono obbligatori il banner di avvio e l'indirizzo loopback con la porta prevista.
- `ECONNREFUSED` e gli errori proxy WebSocket/HTTP continuano a bloccare la CI, anche se colorati.
- Test di regressione positivi e negativi prima della build, test live su PostgreSQL invariati.

La correzione è verificata localmente, non ancora certificata da GitHub. Completamento invariato a 85,25%.
