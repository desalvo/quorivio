# Verifica RC — anteprima quiz a tempo e gate circoscritti di sicurezza/documentazione

**Data:** 28 ottobre 2026. **Versione:** 0.1.0-dev. **Ultimo commit confermato dall'utente:** `a32ef78902a656262d346a0fa622604a4deda405`.

## Implementato (non ancora committato; nuova CI da eseguire)

* L'anteprima dei quiz a tempo mostra il conto alla rovescia condiviso fra presentatore e partecipante. Il tempo parte quando si entra nella pagina, non cambia passando alla vista affiancata, e riparte navigando su una pagina o ricominciando la prova.
* Il gestore degli invii controlla anche l'orario effettivo, indipendentemente dal pulsante disabilitato: le risposte fuori tempo non aggiornano le statistiche. Gli invii già conclusi non vengono cancellati dopo la scadenza.
* Anche il widget Timer usa il tempo della prova. Scaduto il quiz, opzioni e invio del partecipante sono disattivati e viene annunciato lo stato. Domande indipendenti all'interno di uno stesso quiz condividono la scadenza.
* Test TypeScript, browser Chromium offline 1440/390 px sul modulo reale del timer, e test opt-in nella futura Full CI. **Non** equivalgono a un E2E autenticato, né a una validazione fisica/screen reader.

## Progresso verificabile 63% → 65%, solo per precedenti prove GitHub

`D4-SCAN`, **accettato, peso 2**, separato da `D4` parziale (peso 5→3): la Full CI verde [40638652838](https://github.com/desalvo/quorivio/actions/runs/40638652838), SHA `a32ef78902a656262d346a0fa622604a4deda405`, ha superato scansione vulnerabilità npm alte/critiche, ricerca credenziali e build/scansione immagini. **Non** certifica penetration test esterno, AGID o threat review.

`D5-TECHDOC`, **accettato, peso 2**, separato da `D5` parziale (peso 5→3): medesima CI verde con verifica di licenza EUPL, README IT/EN, GDPR IT/EN e manuali PDF admin/utente IT/EN non vuoti. **Non** certifica revisione editoriale, immagini aggiornate né usabilità dei manuali.

Pesi invariati nel totale, 100; formula immutata (accettato 1, parziale 0,5). **30 gate: 13 accettati, 17 parziali; avanzamento 65,0%; RC NON pronta.** Il nuovo timer non riceve punti prima della prossima CI. Restano Firefox/WebKit, controllo visivo indipendente, screen reader, dispositivi fisici, SSO reali, RWX/ClamAV/Kubernetes/Podman, DR operativo, approvazioni indipendenti di sicurezza/legali.

## Evidenza locale

Build produzione e test Node/Python; Chromium offline verifica confine temporale, blocco invio tardivo, riavvio prova e persistenza del conteggio presentatore. In GitHub eseguire `browser_test=true`, `publish_image=false` dopo il commit dell'utente.
