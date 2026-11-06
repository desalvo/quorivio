# RC231 — percorsi di importazione Python CI deterministici

## Problema

La run GitHub `42233651517` si è interrotta durante `python3 -m unittest tools.tests.test_rc230_inventory_promotion -q`, eseguito senza `PYTHONPATH`. Il modulo `tools.verify_rc_current_inventory` cercava `ci_inventory_reference_guard` come modulo globale, invece di registrarne la directory locale. La validazione locale precedente impostava `PYTHONPATH=tools` e non aveva rilevato il difetto.

## Correzione

Il modulo registra esplicitamente la propria directory `tools` in `sys.path` prima dell'import dei moduli fratelli, mantenendo i nomi storici dei verificatori. I test eseguono in sottoprocesso sia unittest dalla radice sia lo script release diretto, entrambi senza `PYTHONPATH`, prima di installare npm. Non è stato ridotto alcun controllo fail-closed sugli inventari o l'indice Git.

## Sicurezza e avanzamento

L'inventario RC230 rimane storico e immutabile; RC231 è quello corrente. Nessun cambiamento a logica applicativa, sicurezza, database o pubblicazione. Percentuale certificata 85,25% invariata; nuova full CI GitHub da certificare. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
