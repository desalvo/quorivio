# Quorivio 0.1.0-dev — RC177: correzione CI contratti storici della presentazione

GitHub Actions run 41865155281, job 126697411992 (2026-11-04): il primo blocco è `tools.tests.test_rc167_live_preview_fidelity`, in `test_shared_policy_is_used_in_all_projection_surfaces`. Il contratto RC167 richiedeva la selezione binaria originale (smartphone/desktop), mentre RC176 utilizza tre modalità (smartphone, accessibile, 16:9). Non si tratta di una regressione del rendering identificata dal job: è un'asserzione letterale obsoleta.

Riconciliati RC144, RC167, RC168 e RC169 con la selezione attuale. RC168/169 richiedevano ancora l'altezza 1174px della fixture PostgreSQL, benché la fixture RC176 abbia 998px di widget pubblici e rimuova i controlli del presentatore prima del calcolo della geometria. Conservati i controlli negativi su privacy, QR, grafica e diagnosi con token oscurati. Aggiunto test di regressione RC177 e nuova preflight prima dell'installazione npm. Gli inventari RC176 e precedenti restano immutabili; RC177 pubblica un nuovo checksum dell'intero cumulativo.

Evidenza locale: 65 test focalizzati verdi; primo passaggio di 579 preflight con soltanto 4 errori attesi di inventario non ancora aggiornato. Dopo la generazione della ricevuta RC177, **589 test preflight** (nessun errore, 1 saltato), **313/313 test web** e **588/588 test API** superati. Verificati anche gli header di rilascio e l’integrità del ZIP cumulativo da 1770 file.

**Gate globali:** 85,25% certificato (43 accettati, 17 parziali). Questo intervento non certifica da solo alcun nuovo gate. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o deploy. Build npm/Vite, prova Chromium/PostgreSQL autenticata e CI sul nuovo commit da eseguire.
