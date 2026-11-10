# RC302 — Una sola autorizzazione per entrambe le immagini Docker

La pubblicazione esplicitamente autorizzata gestisce **sia** `desalvo/quorivio` sia `desalvo/quorivio-converter` in un solo workflow. Le immagini sono costruite su runner nativi linux/amd64 e linux/arm64, usando l'ambiente protetto `production`, digest immutabili, SBOM e provenance. Prima della pubblicazione la build ordinaria sottopone entrambe le immagini alle scansioni Trivy.

## Avvio, tag e immagini

- Il marcatore `[publish-docker]` esplicitamente autorizzato su `main` lancia la full CI RC estesa. Solo se tutti i gate passano vengono prodotte entrambe le coppie native e aggiornati per entrambe i tag `sha-<12>` e `latest` riferiti al commit preciso.
- Con `workflow_dispatch` e `publish_image=true`, una singola esecuzione pubblica **entrambe** dopo validazione, build e scansioni. `publish_tag` è comune; `publish_latest=true` è ammesso soltanto su `main`.
- Su un tag Git semver approvato, la pubblicazione manuale usa il **medesimo tag di versione** per i due repository e non modifica `latest`.
- `converter-image.yml` rimane per manutenzione eccezionale del converter, ma nel flusso normale non serve più un secondo avvio manuale.

## Controlli e sicurezza

`tools/publish_both_multiarch_manifest.sh` verifica prima di qualunque aggiornamento **tutti e quattro i digest** nativi e le relative architetture OCI. Rifiuta immagini mancanti, digest invalidi, piattaforme errate e tag incompatibili. Il publisher esistente crea poi e verifica i singoli manifest multiarch. I test con Docker simulato controllano che un converter incompleto impedisca di spostare anche il tag dell'app principale.

Docker Hub non offre transazioni atomiche tra repository: un'interruzione dopo la modifica dell'app ma prima del converter potrebbe lasciare tag temporaneamente diversi. Conservare i digest immutabili e verificare entrambi dopo ogni pubblicazione.

**Stato RC:** queste verifiche non sostituiscono prove fisiche, accessibilità assistiva, provider reali o collaudi legali/di sicurezza indipendenti. RC stretta bloccata a **85,25%** (43 accepted, 17 partial). Nessun tag Git di release creato.

Messaggio merge suggerito: `ci: publish Quorivio and converter together after full CI [publish-docker]`.
