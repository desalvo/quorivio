# Quorivio 0.1.0-dev — RC182: leggibilità dello stato di conflitto nell’editor

## CI GitHub esaminata

Run `41944096707`, commit `d9b116338ea17019ed6948852a777fe0f53a5e7e`, job `126971883724`: preflight, build, suite browser Chromium e collaudo partecipante/PostgreSQL superati. Il controllo `tools/ci_browser_editor_conflict_visibility.py`, eseguito prima dell’editor/PostgreSQL, fallisce a 1100 px perché il contenitore dello stato di revisione è largo 140 px ma il testo richiede 152 px. Non è un errore di PostgreSQL né dei permessi.

## Intervento funzionale

La regola `RC171` aveva reintrodotto `max-width:140px!important` anche per `.editor-autosave-indicator.has-error`, sovrascrivendo il precedente fix RC120. In RC182 la larghezza compatta rimane valida per la sincronizzazione ordinaria, mentre i messaggi di conflitto o errore possono adattarsi e andare a capo (`width:max-content`, limite viewport, `white-space:normal`, `overflow-wrap:anywhere`). A larghezze <=1100px lo stato d’errore resta visibile sotto l’header, senza occupare lo spazio dei pulsanti.

Il test Chromium ora verifica il testo reale, un font stressato Arial bold 14 px e un messaggio più lungo in quattro viewport (1440, 1100, 960 e 390 px). La mutazione negativa che ripristina il CSS RC181 fallisce come atteso, mentre la versione corretta passa. Il controllo è anticipato nella fase Chromium editor, prima dei collaudi autenticati PostgreSQL, e ha un contratto statico di preflight.

## Sicurezza e stato di rilascio

Nessun dato utente o credenziale di test incluso nel package. Inventari storici immutati; RC182 dispone del proprio inventario SHA-256. I gate certificati restano **85,25% (43 accettati, 17 parziali)** e `rc_strict=false`, `publish_image=false`, `publish_latest=false`. La validazione CI completa del nuovo commit non è ancora disponibile. L’assistente non effettua commit/push/tag/deploy.
