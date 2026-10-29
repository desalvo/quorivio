# Quorivio 0.1.0-dev — ciclo RC 14: evidenze native Firefox/WebKit verificate

**Risultato formale: 74,0% → 75,0% (+1,0 punto).** Pesi totali 100, 42 gate, 25 accettati e **17 parziali**. La release candidate resta bloccata: nessun credito per nuovi test ancora non eseguiti su GitHub.

## Evidenze GitHub controllate

La CI standard [40846201940](https://github.com/desalvo/quorivio/actions/runs/40846201940) e la CI estesa [40847463104](https://github.com/desalvo/quorivio/actions/runs/40847463104) sul commit `cf49c3e1d3e58d4ec4d65862a92b742348a11435` sono **SUCCESS**. Il job Firefox/WebKit nativi **123360950163** è verde: Firefox 1440/390 px e WebKit 1440/390 px, sulle vere routine TypeScript del dialogo e sul CSS della diapositiva pubblica 16:9. Motori Playwright Linux Firefox 157.0 / WebKit 27.2. Passano anche Chromium, PostgreSQL 18, repliche, capacità e controlli container. Pubblicazione Docker saltata.

**A3-NATIVE-STAGE (peso 1, accettato)** registra la prova autonoma dei due motori su geometria 16:9, rotazione e modalità accessibile; **A4-NATIVE-MODAL (peso 1, accettato)** registra focus, Tab, contenteditable, inert/ARIA, portali dinamici e ripristino del focus. I rispettivi pesi sono sottratti ai gate parziali **A3 (2→1)** e **A4 (4→3)**. Non duplicano Chromium A3-GEOMETRY e A4-FOCUS. L'incremento netto è di **1 punto**, non 2. I gate principali rimangono parziali per hardware reale, screen reader, pixel accuracy e accettazione indipendente.

## Sviluppo aggiuntivo locale, ancora senza credito

Il job GitHub nativo include ora anche il test del **vero bundle React compilato**, con apertura da dashboard/editor, un solo dialogo, portale fuori dagli antenati inert, modalità presentatore/partecipante/affiancata e ritorno del focus a 1440/390 px. Il test è passato localmente su Chromium; **la nuova verifica Firefox/WebKit di questo test deve ancora passare su GitHub**. Nessun fallback sui motori. Aggiornati i contratti storici della matrice, l'inventario corrente e i test di regressione.

**Ancora aperti:** iOS/Android fisici, NVDA/VoiceOver/TalkBack, comparazioni grafiche indipendenti, OAuth/provider reali, prove ingress/RWX/ClamAV/Podman/ARM64, sicurezza/GDPR/AGID e approvazione operativa. Il protocollo non costituisce approvazione. Dopo il commit: `browser_test=true`, `cross_browser_test=true`, `capacity_test=true`, `publish_image=false`, `publish_latest=false`, `rc_strict=false`.

Report: `docs/validation/RC_CYCLE14_NATIVE_GITHUB_VERIFIED_20261029.json`; inventario attuale: `docs/validation/RC_CYCLE14_PACKAGE_INVENTORY_20261029.json`.
