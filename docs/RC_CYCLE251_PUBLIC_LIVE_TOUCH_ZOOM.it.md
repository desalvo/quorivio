# Quorivio 0.1.0-dev — RC251 — Ripristino dimensioni touch nelle pagine pubbliche

**Base certificata a livello di sorgenti:** cumulativo RC250 (`f4c83c2316f39554cac75868bdc906b647c8a151940cc26a37488e398a6f2eec`, 68.381.628 byte), presente in Dropbox. Il pacchetto RC251 è costruito a partire dai 2.235 membri originali e conserva invariati tutti gli inventari storici, incluso RC250.

**Difetto CI:** la full CI [42412981696](https://github.com/desalvo/quorivio/actions/runs/42412981696), commit `63e877449bb4821be14292f3f4cf8cc8770922a0`, è fallita in `tools/ci_browser_participant.py` per `AssertionError: RC207 44px answer targets shrank`. Il documento HTML aveva zoom globale 80% anche sulla route partecipante: il CSS specificava 44px ma il browser disegnava 35,2px reali.

**Correzione:** la preferenza di zoom compatto continua ad applicarsi a dashboard, editor pagine e schemi; su `/join/*` e `/screen/*` il documento viene renderizzato a 100% fisico, indipendentemente dalle preferenze memorizzate. Il controllo dello zoom dello studio viene nascosto dalle pagine pubbliche, senza perdere la preferenza. Il canvas 16:9 e i layout smartphone mantengono dimensioni e geometrie definite dai rispettivi sistemi; non vengono aggiunti margini vuoti nell'editor.

**Prove:** test Node per le route e il ripristino della scala; controllo Python con mutazioni negative; Chromium offline con `getBoundingClientRect()` su due viewport, confronto 80% (35,2px, regressione riprodotta) e 100% (44px). Le precedenti prove Chromium di editing e l'integrazione reale React+PostgreSQL restano obbligatorie. Il rilascio non è certificato fino alla nuova full CI GitHub, né sostituisce i 17 collaudi indipendenti ancora parziali.

**Stato:** **85,25%** (43 gate accettati, 17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o pubblicazione eseguiti. La CI deve essere rieseguita dal commit successivo mediante `[full-ci]`.
