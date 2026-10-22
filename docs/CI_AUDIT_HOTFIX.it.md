# Correzione CI security gate — 22 ottobre 2026

La CI GitHub Actions `107927415489` ha superato l'installazione, gli 82 test Node, la compilazione frontend/backend, l'avvio API su PostgreSQL 18 e i controlli di salute, schema e autorizzazione. Il job `Production quality gate` è fallito soltanto durante `npm audit --omit=dev --audit-level=high`, che segnala Nodemailer 6 come dipendenza vulnerabile.

Correzione: usare Nodemailer `^10.2.1` e rimuovere `@types/nodemailer`, non più necessario dalla versione 10. Restano invariati SMTPS obbligatorio e Node.js 22. La build e l'audit devono essere ripetuti in GitHub Actions. Non disabilitare il security gate.

Per continuare: applicare il package, eseguire commit e push su un branch di test e consultare l'esito dei job di qualità e di build container. In caso di errore, riportare il primo step fallito. Nessuna operazione Git viene effettuata dall'assistente.
