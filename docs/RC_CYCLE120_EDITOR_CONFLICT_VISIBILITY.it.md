# RC120 — Stato conflitto visibile

La CI 41338170505 supera Chromium editor base, ma il test di autosalvataggio e concorrenza PostgreSQL trova il conflitto e non lo vede a causa della compressione del suo badge nella barra. La correzione è esclusivamente visiva e mantiene intatto il percorso di risoluzione conflitti, il salvataggio con design_revision e la validazione lato backend. Il nuovo gate Chromium usa il CSS reale nei viewport desktop e mobile.
