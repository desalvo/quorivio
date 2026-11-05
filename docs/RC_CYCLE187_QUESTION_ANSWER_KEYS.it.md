# Quorivio 0.1.0-dev — RC187 — Risposte vere/false opzionali

## Funzione

Le widget **Domanda**, nelle modalità **risposta singola** e **risposta multipla**, possono avere una chiave di valutazione **facoltativa**. La funzione è disponibile nelle proprietà della widget, nel menu contestuale (clic destro o pressione prolungata sul testo della domanda) e nelle domande indipendenti della stessa widget. La prima attivazione attribuisce automaticamente lo stato **Falso** a tutte le opzioni; è possibile impostare una o più opzioni **Vero**. Per le domande a scelta singola è ammessa al massimo una risposta vera; per quelle multiple è richiesta la corrispondenza esatta con l'insieme delle opzioni vere. La funzione **Resetta stati vero/falso** disabilita completamente la valutazione delle normali domande e ripristina il comportamento precedente.

Per i quiz a tempo, la chiave di risposta preesistente resta obbligatoria: si può modificare lo stato delle risposte senza eliminare l'ultima vera. Le domande aperte e con allegati non propongono questa impostazione. Nessuna domanda esistente viene modificata automaticamente.

## Riscontro ai partecipanti

Il server convalida e salva la risposta, poi restituisce **esclusivamente nella risposta HTTP al partecipante** l'esito *Risposta corretta!* oppure *Risposta errata.*, seguito da ogni opzione con indicazione **Vero/Falso**. L'elenco delle soluzioni non compare nelle proiezioni pubbliche, nei messaggi di aggiornamento live o prima dell'invio. I tentativi ripetuti e idempotenti restituiscono il riscontro della risposta **effettivamente registrata**, non dell'eventuale nuovo tentativo. I risultati ordinari rimangono privi di valutazione se la chiave non è abilitata.

La correzione viene associata alla revisione della domanda; cambiarne la chiave non ricalcola le risposte storiche. Il salvataggio controlla la validità dei riferimenti delle opzioni e conserva l'isolamento delle domande indipendenti. La correzione ha visibilità solo dopo l'invio riuscito, inclusi i casi in cui tutte le opzioni sono state definite false (nessuna risposta singola inviata risulta corretta).

## Verifica e limiti

- Test API Node su correttezza, scelta singola/multipla, stati iniziali, reset, revisioni, riservatezza della proiezione e risposte ripetute.
- Test frontend Node sull'accessibilità dei controlli in proprietà/menu contestuale e sul riscontro dopo l'invio.
- Preflight Python anticipato in CI per privacy, protezioni e precedenza rispetto ai test costosi.
- La build TypeScript/Vite e la prova end-to-end autentica con React/PostgreSQL sono ancora **da verificare nella nuova CI**; non vengono dichiarate superate localmente.

RC186 è la baseline cumulativa precedente, RC184 l'ultima campagna automatica completamente verde confermata (run `41993094578`). Progresso certificato **85,25%**, con 43 gate accettati e 17 parziali. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o pubblicazione effettuati dall'assistente.
