# Quorivio RC274 — Correzione CI, evidenziazione vero/falso

## Diagnosi full CI

Esecuzione GitHub Actions [42548617989](https://github.com/desalvo/quorivio/actions/runs/42548617989/job/128938965495): dopo typecheck e numerosi test reali la suite Python fallisce perché `npm install` modifica il `package-lock.json` rispetto all'inventario SHA-256 RC273; un secondo test di erasure privacy include accidentalmente le nuove route di backup e rileva un `SELECT *` al di fuori della route di erasure. RC274 usa `npm ci` e adegua i 33 controlli di ordinamento CI al nuovo comando, senza ridurre la copertura. Il test privacy resta restrittivo sulla sola route di metriche privacy.

## Presentazione delle risposte

- Partecipante: dopo risposta realmente registrata e feedback dal server, stato corretto/sbagliato con bordo verde/rosso e simboli visto/croce direttamente su ogni opzione, senza blocco 'Soluzione' sotto. Non usare i segreti di valutazione della pagina pubblica prima dell'invio.
- Risultati presentatore: un pulsante circolare R verde nel widget condiviso mostra/nasconde vero e falso per le opzioni nei risultati e nella domanda sorgente. Il toggle funziona anche per i grafici a barre, a torta, tabellari e nuvola.
- Editor e anteprime: il pulsante R è renderizzato dallo stesso widget di risultati, e le risposte in anteprima partecipante sono valutate localmente solo dopo l'invio simulato; il codice di grading è condiviso con l'API.
- Le risposte principali e indipendenti possono essere configurate nelle proprietà e in Formato widget → Contenuti. La semantica a scelta singola mantiene al massimo una risposta vera.

## Verifiche e rischi residui

Test Node di comportamento vero/falso, proprietà API e regressioni UI, test Python privacy e controlli CI eseguiti localmente. Verifica sintattica TypeScript via transpiler; build completo React/API e full CI GitHub ancora da confermare. Restano le verifiche reali di backup/storage/LDAP/SMTP e il collaudo interattivo del layout R su schermi desktop/mobile. Baseline generale **85,25%**: nessuna promozione automatica dei gate senza evidenze. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag dell'assistente.
