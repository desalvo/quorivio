# Quorivio 0.1.0-dev — RC ciclo 37 — Correzioni editor e salvataggio (30 ottobre 2026)

**Completamento formale invariato: 80,75% (52 gate, 35 accettati e 17 parziali).** Il codice di questo ciclo non è ancora verificato in una nuova CI GitHub. Ultimo commit confermato `f5ccf9a7545e7c17b4323d067db66aff5eca9b41` (ciclo 33); i cicli 34–37 sono cumulativi e non committati. Nessun commit, push, tag o pubblicazione effettuati dall'assistente.

**Quattro problemi segnalati con screenshot:** (1) testi chiari su widget bianche: colore predefinito nero, senza sovrascrivere quello scelto dall'utente; (2) menu widget tagliati: portal nel `document.body` e posizionamento compatibile con mouse, touch e tastiera; (3) anteprime presentatore/partecipante/affiancate che possono bloccare l'editor: boundary React recuperabile con uscita esplicita, chiusura con Escape/sfondo e refresh rallentato; (4) sondaggio a scelta multipla: preparazione atomica delle prime due opzioni e validazione locale secondo il contratto effettivo del server prima del salvataggio automatico.

**Test locali:** cinque nuovi test Node passati, 180 contratti Python sull'editor e 20 test specifici sui portal superati, TSX senza errori sintattici. Lo script Chromium già presente ora controlla il colore nero e il menu esterno al canvas, ma non è stato eseguito localmente per mancanza delle dipendenze. Build TypeScript/Vite, browser reale, backend PostgreSQL e conferma dell'utente ancora da eseguire. Il punteggio RC resta invariato. I 17 gate parziali richiedono prove esterne e revisioni indipendenti.

**Dopo il commit:** quality gate e `browser_test=true`, possibilmente `cross_browser_test=true`, con `publish_image=false`, `rc_strict=false`. Ripetere i quattro casi in browser reale; HAProxy rimane da collaudare separatamente.

---

