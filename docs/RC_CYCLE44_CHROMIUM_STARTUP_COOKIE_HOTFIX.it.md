# Quorivio 0.1.0-dev — RC ciclo 44 — avvio Chromium e informativa cookie (30 ottobre 2026)

**Ultimo commit confermato:** `1857ebb22560d0ddcc1fec439dfe865eb0183e98` (ciclo 43). La CI standard `41103165554` ha superato 500 test Node backend, 84 frontend, build TypeScript/Vite e la prova separata ClamAV reale. Il quality gate si è fermato in `tools/ci_browser_editor.py` attendendo «Apri sessione». Lo screenshot allegato è interamente bianco: quando si è verificato il timeout il frontend non era visibilmente montato. La vera causa sottostante (JavaScript o caricamento freddo Vite) non era riportata nei log e non può essere dichiarata identificata.

**Modifiche ciclo 44, non ancora verificate nella CI:** lo smoke Chromium attende il montaggio di React in `#root .app`, con un solo nuovo caricamento della pagina per gestire il caso dell'optimizer Vite in avvio. Se l'app non compare, fallisce esplicitamente con diagnostica minimale. I test desktop, mobile e PostgreSQL ora chiudono l'informativa modale cookie *prima* di cercare i comandi nella pagina. Aggiunti test dei contratti e prova Chromium isolata dell'intercettazione dei clic da parte del dialogo, senza bypass del consenso o clic forzati. La suite editor reale deve ancora essere confermata nella prossima CI.

**RC ufficiale invariata: 80,75%** (52 gate, 35 accettati, 17 parziali). `rc_strict=false`, `publish_image=false`. Nessun commit/push/tag/pubblicazione da parte dell'assistente.

