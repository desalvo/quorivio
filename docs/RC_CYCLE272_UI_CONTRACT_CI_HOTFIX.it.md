# RC272 — Correzione del contratto RC241 sui colori dei risultati

## Diagnosi CI verificata

La full CI [42537006971](https://github.com/desalvo/quorivio/actions/runs/42537006971) si interrompe nel **Production quality gate** allo step «RC241 results, smartphone preview, toolbar and editable numeric format preflight». Il test `tools.tests.test_rc241_widget_editor_contract` segnala `RC241 UI contract missing: per-row-result-style`. Il componente, dopo RC270, conserva lo stile indipendente `resultTextCss(widget.resultTextStyles, resultElementKey('row', ...))` ma lo compone ora con un colore derivato dalla palette del grafico a torta (`style={{...resultTextCss(...),...(chart==='pie'?...}}`). Il test storico controllava una singola forma lessicale `style={resultTextCss(...)}` invece della semantica comune; non è un difetto della grafica applicativa.

## Correzione e verifica

* Aggiornato il contratto RC241 per rilevare l'applicazione di `resultTextCss` sullo *stesso elemento JSX* `linked-result-pair`, accettando forma diretta e composta senza disattivare il controllo.
* Aggiunto test negativo: la rimozione dello stile per riga genera obbligatoriamente errore. Aggiunto test che preserva anche l'originale stile diretto.
* Lo storico RC271 resta immutabile; il suo test di promozione ora segue automaticamente il verificatore corrente e conserva i vincoli sugli inventari storici. Inventario cumulativo RC272 corrente; controllo di integrità e metadata ancora fail-closed.
* Nessun cambiamento al codice runtime API/web, alle funzionalità RC270 di backup, LDAP, audit e grafici.

Resta da ripetere la full CI GitHub, inclusi i job saltati in questa esecuzione. Nessuna certificazione sul restore reale PostgreSQL/NFS/S3/WebDAV, LDAP/SMTP o sul browser matrix. Avanzamento ledger invariato: **85,25%**. Flag: `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o tag eseguito.
