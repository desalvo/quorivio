# Quorivio 0.1.0-dev — RC64 — Falso positivo Gitleaks nei test (31 ottobre 2026)

**Ultimo commit del manutentore:** `118480606d97e3e32ddf92991889c7a577ebfc02` (include RC63). La CI standard `41188841418`, job `124501245873`, ha superato 546 test API, 99 test web, build, integrazioni PostgreSQL, Kubernetes, Python e 50 verificatori d'inventario. Si è fermata all'ultimo controllo Gitleaks: la stringa fittizia statica nel test del rate limit RC62 viene interpretata come `generic-api-key`. Non è una credenziale reale trapelata.

**Correzione RC64:** sostituita la stringa con un valore di prova SHA-256 deterministico calcolato in esecuzione. In CI il vero token resta casuale, solo in ambienti non di produzione e per richieste loopback. Aggiunti controlli preventivi prima di npm; Gitleaks rimane obbligatorio senza allowlist o bypass, inventario RC63 mantenuto immutabile, nuovo inventario RC64 corrente. Per verificare il risultato occorre un nuovo commit dell'utente e una nuova esecuzione CI; rilanciare la CI sul vecchio commit non basta.

**Stato RC ufficiale:** **81,75%** (55 gate: 38 accettati e 17 parziali), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Le precedenti CI verdi `41152434205`, `41152939003` e `41123318359` non certificano RC64. Restano collaudi su provider reali, RWX fisico multi-nodo, approvazioni indipendenti GDPR/AGID/sicurezza, accessibilità multi-dispositivo. Nessun commit/push/tag dall'assistente.

---
