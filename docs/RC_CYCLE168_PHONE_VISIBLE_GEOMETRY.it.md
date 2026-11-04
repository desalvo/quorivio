# Quorivio 0.1.0-dev — RC168 — Geometria smartphone dei partecipanti senza spazi fantasma

## Base e problema riprodotto

La RC167 consolida la visibilità dei widget per i partecipanti, ma in modalità smartphone le posizioni automatiche e l'altezza del canvas erano calcolate dall'insieme completo dei widget **prima** di filtrare «Risultati» e «Partecipanti connessi». Il filtraggio successivo impediva di vedere i controlli riservati al presentatore, ma ne conservava i posti nell'impaginazione: spazi vuoti, canvas troppo alto e footer fuori dalla posizione prevista. L'anteprima partecipante utilizzava lo stesso ordine erroneo.

## Modifiche funzionali

1. `participantPhoneLayout()` è la fonte condivisa della geometria smartphone per anteprima e pagina reale: filtra **prima** i widget riservati al presentatore, poi calcola `mobilePageWidgets` e `mobileStageHeight` sullo stesso insieme visibile.
2. Il presentatore conserva i propri widget e il proprio layout. La versione desktop 16:9 rimane invariata. Le posizioni, gli sfondi e la tipografia mobile personalizzati dall'editor vengono rispettati.
3. Le pagine con widget ereditati dallo schema usano la stessa regola: un contatore del presentatore ereditato non deve generare spazi invisibili nella versione smartphone del partecipante.
4. La fixture `ci_browser_participant.py` aggiunge un footer, verifica l'altezza esatta della pagina smartphone (928 px logici per i sei widget pubblici della fixture) e la distanza dal bordo inferiore (24 px), e passa fra modalità 16:9/lettura accessibile. Verifica la corretta successione dei widget su desktop senza esporre dati privati nei log.
5. Gli errori JavaScript raccolti dal browser vengono contati ma non stampati integralmente: potrebbero contenere URL di invito con token di sessione.

## Test e CI

- `apps/web/test/rc168-participant-phone-parity.test.ts`: confronto positivo e mutazioni negative della sequenza errata «filtra dopo»; master, footer e override smartphone.
- `tools/tests/test_rc168_phone_preview_parity.py`: contratti dei due percorsi frontend, fixture autenticata e riferimenti CI.
- `tools/ci_rc168_phone_footer_chromium.py`: Chromium effettivo a 390/1440 px, canvas 16:9, footer al fondo, nessuno scroll orizzontale.
- Preflight Python RC168 anticipato prima di npm; test browser RC168 insieme ai precedenti; inventari storici immutabili, inventario RC168 corrente.

## Criteri ancora aperti

La correzione elimina il difetto di layout individuato, ma la certificazione complessiva resta **85,25% (43 gate accettati, 17 parziali)** in attesa della compilazione TypeScript/Vite e del collaudo Chromium/PostgreSQL nella CI GitHub e del confronto visuale indipendente sui dispositivi reali. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o deploy.
