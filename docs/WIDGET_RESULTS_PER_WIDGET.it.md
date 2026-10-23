# Risultati del presentatore per singolo widget — 23/10/2026

Il pannello Risultati, riservato al presentatore, ora include una sezione autonoma per ogni widget `question`. Le risposte provengono dall'endpoint autenticato esistente `/api/sessions/:id/widget-answers/detail` e rimangono separate per ID del widget e revisione. Nell'editor ogni widget domanda dispone di una scelta persistente della visualizzazione (barre, torta, tabella). Le opzioni vengono aggregate senza esporre risposte personali; sono indicati anche i conteggi di testi e allegati. Aggiornamento ogni tre secondi. Restano disponibili risultati aggregati della pagina e classifiche dei quiz a tempo a livello di attività.

**Non concluso:** i widget `timed-quiz` nel canvas non possiedono ancora canali di risposta cronometrati indipendenti; sono marcatori di layout delle attività temporizzate. Mancano collaudi E2E browser/PostgreSQL, accessibilità, etichette storiche specifiche delle revisioni, test multi-client e aggiornamento dei manuali PDF. Nessuna migrazione o modifica autenticazione. I gate RC restano al 67% in attesa di accettazione.

Controlli locali: build backend e frontend TypeScript/Vite PASS; suite Node 90/90 PASS. L'ultima CI confermata dall'utente riguarda soltanto il cumulativo `presenter-results-canvas`; i cicli successivi non sono ancora committati.
