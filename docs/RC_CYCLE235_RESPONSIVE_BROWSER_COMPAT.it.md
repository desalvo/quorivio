# RC235 — compatibilità dei test Chromium dell'editor responsive

**Evidenza:** GitHub Actions 42249042835 al commit `774c8431972fdff1a73ad780352c1cf6550e17ad` fallisce nel quality gate del test Chromium RC226, finestra di 320 px. Il test pretende lo scorrimento orizzontale della palette, mentre RC234 lo ha sostituito con il comportamento corretto a capo verticale.

**Correzione:** riconciliate inoltre la fixture RC143 del formato con il ruolo reale di tabpanel e quella RC178 con la barra delle miniature superiore nello smartphone. Fixture RC226 aggiornata con `.editor-icon-wrapper` come nel prodotto; i precedenti pulsanti isolati raggiungevano un'altezza artificiale di 302 px. La prova ora richiede layout a colonna unica, miniature delle pagine con scroll orizzontale, palette con righe a capo, nessun overflow orizzontale, scroll verticale e raggiungibilità dell'ultimo controllo. Nessuna modifica al CSS o TypeScript dell'applicazione. Test RC235 eseguito prima di npm con verifiche negative delle regressioni.

**Controlli locali:** Chromium RC226 4/4, RC171 3/3, RC234 9/9, RC143 2/2, RC178 4/4. Gate RC235 Python 5/5. Full CI integrata ancora da verificare; RC234 storica, RC235 corrente. Versione 0.1.0-dev invariata. Completamento 85,25%, 43 gate accettati e 17 parziali. Nessun commit/push/tag eseguito.
