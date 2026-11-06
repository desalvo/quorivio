# RC215 — Contratto Chromium per allineamento del conteggio risultati

## Diagnosi della CI
La run `42144060435` (job production `127651153649`) ha superato le verifiche preliminari e ha fallito nello step «Chromium editor UI acceptance», script `tools/ci_rc141_widget_parity_chromium.py`. In tutte e quattro le viste (editor, presentatore, prova e partecipante), `tailInline` risultava falso nonostante il testo dell'ultima parola e quello del conteggio fossero allineati. La prova confrontava il limite superiore del *text Range* dell'ultima parola con il **border box** dell'elemento `output`, che include uno scarto fisso di 2,076 px rispetto ai glifi. La campagna RC è fallita e tutti i job dipendenti sono stati saltati; ClamAV ha superato il suo controllo. Nessuna pubblicazione Docker Hub.

## Correzione
La verifica Chromium confronta ora due DOM `Range` (parola finale e testo `output`) e controlla che il conteggio sia sulla stessa riga, dopo la parola, entro una separazione orizzontale ragionevole. Restano immutati i test per a capo del testo lungo, assenza di tagli, titolo nascosto, reazioni, checkbox, quattro superfici e due viewport (1440 e 390 px). Nessuna modifica alla grafica o al runtime React. Aggiunto `tools/tests/test_rc215_chromium_result_text_alignment.py` con mutazioni negative e preflight prima di npm; il browser fallisce intenzionalmente spostando il conteggio di 8 px tramite CSS.

## Validazione e rilascio
Riprodotto il fallimento RC214 in Chromium locale; RC215 passa a 1440 e 390 px su tutte le superfici e rifiuta l'offset artificiale. Eseguite le regressioni Python mirate. La full CI GitHub RC215 è da verificare. Versione `0.1.0-dev`, **85,25%** certificato (43 gate accettati/17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Cumulativo con inventario SHA-256 e tutti i controlli storici. Nessun commit, push o tag eseguito dall'assistente.
