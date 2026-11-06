# RC219 — Ripristino della discovery Python globale (italiano)

## Errore GitHub e causa
La run RC218 `42194028262` è fallita nel `Production quality gate`, fase `Kubernetes wizard and worker integration tests`, sul comando `PYTHONPATH=tools python3 -m unittest discover -s tools/tests -v`: **2.115 test, 4 fallimenti e 2 errori**. ClamAV superato; nessuna pubblicazione Docker Hub.

Due test storici importavano l'helper RC214 mediante percorso relativo (`from .test_rc214...`): l'esecuzione con nome di package riusciva, ma la discovery globale usa nomi di modulo semplici e generava `ImportError`. I due import sono ora assoluti e validi in entrambi i contesti.

Altri quattro fallimenti erano aspettative obsolete introdotte prima di RC205/206: vecchio controllo nel click delle miniature, etichette separate per font/dimensione/colore del numero pagina ora unificate in `Formato widget`, e pulsanti separati per sottolineatura/barratura delle risposte. Le nuove verifiche controllano la protezione delle modifiche non salvate in `beginPageDesign()`, la mappatura del numero pagina e i due toggle indipendenti con validazione booleana API.

## Modifiche e verifiche
- Aggiornati cinque moduli storici di test, senza cambiare il codice applicativo.
- Creato `tools/tests/test_rc219_full_discovery_contract.py`, con due modalità di importazione, mutazioni negative e protezione dei contratti correnti.
- Nuovo step CI prima di npm che esegue i cinque test con `unittest discover -s tools/tests -p`, mantenendo la suite globale successiva.
- Inventario RC219 SHA-256, ricevute precedenti immutate, aggiornamenti dei quattro documenti di sviluppo e handoff.

La discovery completa di 2.115 casi non è terminata nell'ambiente locale perché un altro test d'integrazione si è bloccato; serve la full CI GitHub per il risultato complessivo. Nessuna modifica al runtime React/API, database, permessi o pubblicazione Docker.

Versione `0.1.0-dev`, completamento certificato **85,25%** invariato. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o tag.
