# RC271 — Ripristino della CI: promozione inventario e gate RC270

## Causa verificata

La full CI RC270, run [42535872914](https://github.com/desalvo/quorivio/actions/runs/42535872914), commit `c3dd0d4bb4489787f32b76eb50abd58fd4504116`, è fallita nell'azione **Production quality gate** (step «RC230 inventory promotion guard before npm»): i documenti attivi indicavano RC270, ma la CI eseguiva ancora `verify_rc_cycle269_inventory.py` come inventario corrente. `verify_rc_release_status` ha segnalato `COMPLETION_HANDOFF.it.md: ... does not identify RC269`. Il riepilogo «Full automatic RC campaign acceptance summary» è fallito a cascata, mentre ClamAV è riuscito. I job con dipendenza `validate` non sono stati eseguiti.

## Correzione

* Conservato invariato l'inventario RC269, promosso a `--historical` nella CI; aggiunto verificatore corrente `verify_rc_cycle271_inventory.py`, catalogo cumulativo SHA-256 a 8 gruppi e verifica stretta di sorgenti/ZIP/Git index.
* Intestazioni coerenti RC271 in tutti e quattro i documenti di sviluppo/handoff, senza alterare il ledger dei gate (**85,25%**).
* Inseriti nel preflight GitHub Actions i test RC270 già esistenti (backup/audit + wizard) e la regressione RC271 per impedire nuove promozioni incoerenti.
* Inalterati runtime API/web, backup, LDAP, audit e grafici introdotti nella RC270. Nessuna deroga ai controlli CI e nessuna modifica alle ricevute storiche.

## Verifiche e limiti

La correzione è verificabile con `python3 -m unittest tools.tests.test_rc230_inventory_promotion tools.tests.test_rc271_release_promotion -q`, `python3 tools/verify_rc_release_status.py`, `python3 tools/verify_rc_cycle269_inventory.py --historical` e `python3 tools/verify_rc_cycle271_inventory.py --package <zip cumulativo>`. I test applicativi vanno rieseguiti; la nuova full CI e il restore PostgreSQL/NFS/S3/WebDAV in ambiente reale non sono dichiarati superati.

Versione in sviluppo, nessun tag/push/commit eseguito dall'assistente. Policy invariata: `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
