# Ciclo RC 58 — evidenze GitHub e limiti di concorrenza WebSocket

**Baseline committata:** `c0fe7f7b9e41c0295387d84996a7b531b91b69a0`. La CI standard `41152434205` e la CI estesa `41152939003` risultano verdi; il job qualità esteso `124393360139` ha effettivamente eseguito `live_idle_test=true` e `capacity_slo_test=true`.

## Riconciliazione controllata

La prova **70 secondi di sessione inattiva su due processi API con PostgreSQL comune** verifica snapshot autentici, isolamento proprietario/partecipante e assenza di disconnessioni improprie. Il nuovo sottogate `B1-IDLE-TWO-REPLICA` accetta solo questa prova automatizzata (peso 0,5). La prova **500 partecipanti indipendenti, percentile p95 globale e almeno 60 secondi di tenuta, senza errori** accetta il sottogate `B4-500-GLOBAL-SLO` (peso 0,5). Ciascun gate padre parziale `B1` e `B4` viene ridotto di 0,5 di peso senza cambiarne lo stato; la somma rimane 100. Punteggio 81,25 → **81,75%** (55 gate: 38 accettati, 17 parziali). I precedenti B4-LOAD e B1-RECONNECT non sono conteggiati nuovamente.

**Limiti non risolti:** `kubernetes_tls_test=false` nella run verificata; nessuna prova TLS KIND reale nel nuovo cumulativo. Nessun test RWX CSI/NFS attraverso nodi fisici, né carico geografico prolungato o firma indipendente su sicurezza/accessibilità/GDPR/AGID. `rc_strict=false` rimane obbligatorio.

## Nuovo intervento applicativo, da verificare nella prossima CI

`apps/api/src/live-periodic-refresh.ts` limita la lettura degli snapshot di **sessioni distinte** a 8 operazioni database contemporanee, contro il comportamento precedente che partiva con un `Promise.all` senza limiti. Le connessioni di una stessa sessione restano coalescenti. Un timer concorrente non genera una seconda scansione, mentre i worker visitano tutte le sessioni del ciclo; una sessione già priva di socket viene saltata prima della lettura. Gli errori di DB e di logging non fermano gli altri worker. La configurazione rifiuta limiti fuori dall'intervallo intero 1–32.

La prova con 500 sessioni simula query in sospeso e conferma un massimo di 8 operazioni simultanee. **Non** è una certificazione di 500 sessioni reali, né una garanzia di freschezza quando PostgreSQL rimane bloccato oltre 65 secondi. La funzionalità non aggiunge credito RC fino a GitHub. Prossima CI: standard ed estesa, `publish_image=false`, `rc_strict=false`; il test HTTPS richiede esplicitamente `kubernetes_tls_test=true`.
