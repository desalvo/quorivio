# RC — Consolidamento dashboard e personalizzazione widget (IT)

Data: 27 ottobre 2026. **Base cumulativa: `quorivio-0.1.0-dev-rc-autosave-widget-inspector-page-rename-preview-cumulative.zip` (non confermato come committato).** Baseline Git dichiarata: `67a7be939a5930e2f9a49ce3932a4b7f29a682ac`.

## Funzionalità implementate

- **Dashboard:** eliminata la sezione «Grafica e media (legacy)»; «Crea contenuti con i widget» guida all'editor con accesso diretto. Il vecchio pannello delle pagine è ripiegato in «Controllo proiezione live e manutenzione avanzata», mantenendo controlli necessari in sessioni attive, migrazione e compatibilità. Eliminato il tab «Interazione», che ripeteva informazioni già disponibili nelle Impostazioni. «Risultati» diventa «Monitoraggio live», separato dalle Impostazioni perché aggiornato durante l'evento.
- **Intestazione editor:** il servizio autenticato `/api/sessions/:id/presenter-profiles` contrassegna il proprietario con `is_owner`; badge del proprietario in oro e collaboratori in azzurro. La vista pubblica non è stata modificata.
- **Palette widget:** ogni icona conserva il suo simbolo distinto; aggiunti temi colorati e gradiente con contrasto, rispettando nomi accessibili e tooltip.
- **Menu widget:** rimosso il pulsante permanente; accesso mediante clic destro, pressione prolungata touch o Menu/Maiusc+F10. Le azioni sono contestuali; il pannello unico delle proprietà rimane richiudibile.
- **Aspetto di ogni widget:** impostazioni visibili nell'unico ispettore per sfondo trasparente/colore, bordo presente/assente, colore, tratto continuo/tratteggiato/puntinato, spessore 0,25–12 pt, angoli arrotondati. I campi erano già validati dall'API; estesi dal solo post-it a tutti i widget. Rendering condiviso tra editor, prova partecipante, proiezione del presentatore e partecipante. Autosalvataggio già presente nel cumulativo di base.

## Evidenze e limiti

- 447/447 test Node backend passati, 15/15 Node frontend; suite Python completa 856/856 passata dopo l'aggiornamento dei contratti. Una ripetizione successiva della suite Python completa non si è conclusa nell'ambiente locale (test HTTP di conversione); cinque regressioni mirate owner/appearance/layout passate.
- Test Chromium isolato con menu widget senza pulsante e clic destro: PASS. Parsing TSX/TypeScript: PASS. **Build integrale Vite, Chromium reale dell'intera app, PostgreSQL + nuove proprietà dei widget e dispositivo mobile fisico: non verificati in questo batch.**
- **Indice RC rimane 53,0%.** L'accettazione della macroarea non è promossa senza nuova Full CI e revisione di un operatore; `release_candidate_ready=false`.
- Pubblicazione Docker, commit, push e tag non eseguiti. Pubblicazione automatica non richiesta.

## Prossimi passi

1. Applicare il cumulativo (include i precedenti sviluppi non committati); eseguire commit dell'utente.
2. Full CI manuale `browser_test=true`, `publish_image=false`, `publish_latest=false`.
3. Verificare in browser reale il pannello aspetto, l'autosalvataggio dopo refresh e il rendering degli stessi widget nel partecipante e nella proiezione. Verificare menu touch e operazioni live dal pannello avanzato.
