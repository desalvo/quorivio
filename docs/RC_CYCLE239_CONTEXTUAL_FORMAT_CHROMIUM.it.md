# RC239 — Finestra contestuale di formattazione nel test Chromium reale dell'editor

## Errore GitHub osservato

La full CI [42274460486](https://github.com/desalvo/quorivio/actions/runs/42274460486) della RC238, commit `e1f7d2f234a712a112f98b23e3774905825a28d8`, si è interrotta durante **Chromium editor PostgreSQL persistence and conflict acceptance**. Il test reale precedente di autosalvataggio, gestione dei conflitti ed esportazione JSON **era passato**. La fixture successiva `tools/ci_rc193_editor_focus_chromium.py` cercava senza successo il selettore `Ambito della formattazione` dopo avere aperto solamente **Proprietà widget**. Da RC223 le opzioni di formattazione appartengono a una finestra distinta, aperta esplicitamente con **Formato widget** dal menu contestuale.

## Correzioni

- Conservate tutte le prove RC193 di focus e scrittura continua delle opzioni e dei campi ispettore.
- Chiusura di **Proprietà widget**, riapertura del menu contestuale del widget domanda, selezione di **Formato widget** e verifica della toolbar `Formattazione rapida widget selezionato`.
- Selezione di «Widget intero» e ricerca di dimensione, incremento e font nella toolbar visibile; conservate le verifiche di ereditarietà Georgia/Arial.
- Aggiunti test negativi RC239 obbligatori prima di npm: azione sbagliata, ordine sbagliato, mancata chiusura, controlli non confinati alla finestra, rimozione dei gate. Test Chromium/PostgreSQL compilato mantenuto obbligatorio.
- Promosso RC239 come inventario sorgente corrente; RC238 e i precedenti rimangono storici, senza modifica dei manifest originari.

## Certificazione

Sorgenti tratti dal cumulativo RC238; hash blob dei principali file confrontati con il commit GitHub. Il runtime applicativo React, CSS, API e DB non cambia. Occorre una nuova full CI GitHub sul commit controllato dall'utente. Ultima full CI verde verificata: RC219 (`42197607753`). Completamento certificato invariato **85,25%** (43 gate accettati, 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o pubblicazione dell'assistente.
