# RC203 — Correzione griglia editor e palette avvolta

Origine: [GitHub Actions run 42107111552, job 127524721412](https://github.com/desalvo/quorivio/actions/runs/42107111552/job/127524721412).

- I controlli dipendenze Python, build e suite Node passano. Il test Chromium `ci_editor_mock_layout_chromium.py` fallisce su una palette alta 140 px in un contenitore alto 122,765625 px.
- Causa: l'intestazione compatta RC200 aveva introdotto due righe CSS (header e stage), sovrascrivendo le tre righe della RC178 (header, palette, stage).
- Ripristinata la riga centrale `minmax(72px,auto)` su desktop, tablet e smartphone, senza modificare titolo e proprietario primario sotto la fila dei pulsanti. Estesa da 240 a 280 px la riserva verticale della slide 16:9 per eliminare il lieve overflow residuo.
- Test Chromium effettivo: 1440×900, 1200×900, 960×760 e 390×844. Aggiunta regressione veloce RC203 prima dell'installazione delle dipendenze, con mutazioni negative del CSS.
- Conservate le funzionalità RC200/RC201 e lo staging RC202. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Completamento **85,25%** invariato. Full CI RC203 da verificare.
