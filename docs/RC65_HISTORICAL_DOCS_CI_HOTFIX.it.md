# Quorivio 0.1.0-dev — RC65 — CI historical documentation regression (31 ottobre 2026)

**Baseline committata dal manutentore:** `0786ef2f4b064080dd49b42f41d2f04b3d5f4c8a` (include RC64). La CI standard `41189697040` (job `124503743950`) ha superato 546 test API, 99 test web, build, integrazioni PostgreSQL, Kubernetes, verifiche di inventario prima della suite Python; il job si è fermato in `PYTHONPATH=tools python3 -m unittest discover -s tools/tests -v` con 2 failure su 1399 test, perché due regressioni storiche cercano ricevute RC58 solo nei primi 1700/2000 caratteri di documenti ai quali vengono prepese nuove sezioni.

**Correzione RC65:** contratti di regressione RC57/58 ricondotti a documenti completi e ricevute RC58 dedicate, senza tagli di prefisso; corretto anche il controllo RC35 con limitazione a 4000 caratteri e il test RC63 che richiedeva un inventario RC64 come sempre-current. L'inventario RC64 diventa storico immutato e RC65 è nuovo inventario sorgente corrente. Gli hash dei cicli precedenti non vengono riscritti. Non vengono disabilitati test, Gitleaks o limiti di sicurezza. Nessun nuovo credito RC finché non esiste una CI verde sul nuovo commit.

**RC ufficiale:** 81,75% (55 gate: 38 accettati/17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. La nuova CI deve eseguire prima suite Python completa, test Node, checksum e Gitleaks; le prove su veri provider e l'approvazione esterna restano aperte. Nessun commit, push o tag dell'assistente.

