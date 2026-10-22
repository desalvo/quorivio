# Recupero delle prenotazioni di conversione

Dopo un arresto anomalo del worker PDF/PPTX, la directory `.conversion-lock` resta intenzionalmente presente per impedire modifiche concorrenti a eventuali risultati parziali.

1. Arrestare **tutti** i worker che montano lo stesso volume condiviso, non soltanto un singolo pod.
2. Individuare l'ID del lavoro (32 caratteri esadecimali) e verificare che nessun worker operi sul volume.
3. Ispezionare senza modifiche: `python3 tools/recover_conversion_lock.py JOBID --root /conversions`.
4. Controllare log ed eventuali risultati parziali, conservando le evidenze necessarie.
5. Soltanto se esistono una sorgente valida, nessuna directory `pages` e un blocco vuoto, eseguire `python3 tools/recover_conversion_lock.py JOBID --root /conversions --recover --workers-stopped`.
6. Riavviare il worker e ripetere la conversione autorizzata.

Lo strumento rifiuta ID sconosciuti, collegamenti simbolici, blocchi non vuoti, sorgenti mancanti/ambigue e output esistenti. Non può verificare automaticamente che i worker siano spenti: `--workers-stopped` è una dichiarazione esplicita dell'operatore. Non esporre lo strumento come endpoint HTTP pubblico.
