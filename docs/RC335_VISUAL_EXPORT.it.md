# RC335 — Esportazione delle viste reali in PDF e PowerPoint

## Obiettivo

Quattro documenti distinti per ogni sessione: PDF e PPTX *presentatore*, PDF e PPTX *partecipante*. Il nome è `<Nome sessione> - presentatore.pdf` (o `partecipante.pptx`), con sanitizzazione dei caratteri incompatibili e intestazione HTTP UTF-8 conforme a RFC 5987.

## Sorgente grafica

La vecchia esportazione OOXML ricostruiva solo testo/forme/immagini supportati e non riproduceva la pagina proiettata. La nuova esportazione **visiva** usa Chromium nel convertitore isolato per catturare il medesimo renderer React 1280×720 dell'anteprima reale. Ogni diapositiva del PPTX contiene l'immagine completa della rispettiva pagina; il PDF viene derivato dal PPTX. Questo favorisce la fedeltà **visiva** rispetto all'editabilità dei singoli widget nel PPTX.

Il rendering distingue pagine del presentatore e mappature `audiencePageId` / `presenterHidden` per i partecipanti; una pagina nascosta può essere esportata solo nel deck partecipante. Snapshot statico: animazioni, video dal vivo, conto alla rovescia e dati che cambiano dopo il download non possono essere interattivi nei documenti; si usano gli aggregati disponibili al momento dell'esportazione senza includere risposte individuali, email o credenziali.

## Sicurezza e runtime

Le richieste restano autenticate e permesse al proprietario/collaboratore. Per il rendering viene creato un token effimero confinato alla directory privata del singolo job. Chromium può raggiungere soltanto l'origine applicativa interna configurata dal deployment e gli asset PNG/JPEG del job verificati dal server; gli endpoint API non necessari e gli URL esterni sono bloccati. Nessun cookie dell'utente viene inviato al convertitore. Le istanze Docker Compose e Helm configurano `QUORIVIO_CAPTURE_BASE_URL` per il container convertitore (rispettivamente `http://app:8080` e `http://127.0.0.1:8080`). 

## Test

- Test delle quattro denominazioni, accenti, sequenze pericolose e routing di pagine nascoste;
- Test del deck PPTX visuale con un PNG 16:9 esatto per pagina e controlli di quota;
- Test dell'autenticazione del capture token, restrizioni URL, contratti UI e dei quattro link.
- Full CI e pubblicazione immagini Docker sono prerequisiti, non dati per scontati.
