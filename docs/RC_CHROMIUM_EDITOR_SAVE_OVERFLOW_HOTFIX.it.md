# Chromium editor PostgreSQL: canvas sovrapposto al salvataggio — 27 ottobre 2026

**Run fallita:** 40513571247, job 122222001046, commit `45145d73c23b3466c2944e385decd336df129765`.

- La CI editor Chromium con API simulate è **verde**, come la prova partecipanti Chromium con PostgreSQL reale.
- Il collaudo editor Chromium/PostgreSQL fallisce alla riga 154 di `tools/ci_browser_editor_postgres.py`: il pulsante `Salva layout` è visibile, ma `Porta in primo piano Third` nei controlli accessibili espansi ne intercetta il clic reale.
- **Causa:** nello stage flex scorrevole, il canvas aveva `flex:1` e figli in overflow; la lista accessibile delle tre miniature/widget invadava l'area di salvataggio e i controlli inferiori potevano restringersi.
- **Correzione UI:** canvas, barra inferiore e area di salvataggio/riconciliazione mantengono l'altezza richiesta dal contenuto (`flex:0 0 auto`); lo stage centrale scorre normalmente. Nessun clic forzato, nessuna disabilitazione dei controlli accessibili, nessun ritorno della toolbar fissa sopra al canvas.
- **Preflight Chromium obbligatorio:** `tools/ci_editor_save_flow_chromium.py` usa il CSS reale e riproduce tre widget con controlli accessibili espansi a 1440×1000 e 390×844 touch; controlla `elementFromPoint`, il clic ordinario su `Salva layout` e l'uso successivo del controllo del widget. **Il CSS vecchio fallisce entrambe le prove**, quello corretto passa. Quattro regressioni contrattuali in `tools/tests/test_ci_editor_save_flow.py`.
- Nessuna modifica alle API, al database, ai segreti o al billing. La **Full CI con PostgreSQL reale resta da verificare** e l'avanzamento RC certificato è invariato al **48,0%**.
