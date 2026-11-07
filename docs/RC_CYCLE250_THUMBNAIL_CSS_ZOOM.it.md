# RC250 — Correzione menu miniature con zoom CSS reale

Baseline: RC249 committata `cf0a1e45048ad49e6d320eddf610f205e4d4bc53`, workflow GitHub `42410387603`, job quality `128517050772`. Chromium sull'editor React compilato si fermava in `ci_browser_editor.py:266`, dopo l'espansione dei gruppi di azioni, perché il menu sovrapposto intercettava il clic sul pulsante che doveva chiuderlo.

## Causa e correzione

`getBoundingClientRect()` misura coordinate visive già ridotte dallo zoom CSS sull'elemento radice, mentre il portale `position:fixed` viene nuovamente scalato. La RC249 non compensava questo secondo fattore. La posizione e le dimensioni del menu sono ora calcolate nel viewport fisico per evitare collisioni e poi convertite nelle coordinate CSS dividendo per il fattore effettivo di zoom. L'apertura, lo scroll, il resize e le modifiche dello zoom globale usano lo stesso algoritmo.

## Verifiche

- Mantenuti i controlli precedenti RC249 e il test integrato React/Chromium originale.
- Nuovo test negativo Node che riproduce la sovrapposizione del vecchio calcolo al zoom 80%.
- Otto prove Chromium con zoom CSS reale e sezioni «Crea e importa pagine» ed «Esporta e dati» espanse; chiusura mediante clic reale sul pulsante, senza forzature.
- Nessuna modifica alle API, allo schema DB, ai manifest Kubernetes o alla pubblicazione Docker. La full CI RC250 resta necessaria.

Punteggio ufficiale **85,25%**, 43 gate accettati / 17 parziali; RC rigorosa bloccata. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; nessun commit, push o tag da parte dell'assistente.
