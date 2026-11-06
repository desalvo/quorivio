# RC204 — Esportazioni statistiche con protezione delle coorti ridotte

**Base:** RC203, full CI GitHub [42110429701](https://github.com/desalvo/quorivio/actions/runs/42110429701) verde con immagini native AMD64/ARM64 e pubblicazione Docker Hub multiarch verificata. Versione invariata: `0.1.0-dev`.

## Novità

- L'export **anonimo CSV/XLSX** mostra una riga solo se quella stessa risposta/valutazione/reazione proviene da **almeno cinque partecipanti distinti**. Risposte ripetute dello stesso partecipante non fanno crescere artificialmente la coorte e il conteggio indica le persone distinte. Le voci con coorti insufficienti vengono omesse; per piccole sessioni il file può contenere solo le intestazioni.
- Identificativi e orari individuali non vengono esportati. Testi liberi, commenti e riferimenti ad allegati personali sono sostituiti da un testo fisso solo quando la relativa coorte è sufficientemente ampia.
- Il nome del file anonimo non contiene più il codice di accesso della sessione. L'anonimizzazione resta selezionata di default; la richiesta di dati identificabili richiede esplicita disattivazione ed è riservata al proprietario primario.
- I CSV proteggono dai prefissi di formula, mentre gli XLSX codificano le celle come testo non eseguibile. La dashboard spiega la nuova soglia.

## Limiti e verifiche

La soppressione delle coorti piccole **non garantisce l'anonimato matematico**; differenze fra export successivi o informazioni esterne possono consentire inferenze. Restano necessarie le approvazioni GDPR e i collaudi indipendenti. Non vengono creati falsi zeri per i gruppi soppressi.

Test locali: 615 API Node, 352 frontend Node, test RC204 specifici e parsing XML del foglio XLSX verdi. Full CI RC204 da verificare. Completamento certificato **85,25%** (43 gate accettati e 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag dell'assistente.
