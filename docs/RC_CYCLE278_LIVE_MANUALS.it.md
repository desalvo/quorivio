# RC278 — Manuali verificabili con schermate autentiche da CI

**Base:** cumulativo RC277, codice applicativo non modificato. **Versione:** Quorivio 0.1.0-dev. **Edizione:** RC278, 9 novembre 2026. **Autore:** Alessandro De Salvo <braket71@gmail.com>. **Licenza:** EUPL-1.2. **Sorgente:** https://github.com/desalvo/quorivio.

## Cambiamenti

- **Metadati centralizzati** in `tools/manual_release_metadata.py`: i sei manuali prendono autore/email/SPDX dalla `LICENSE`, versione da `package.json`, build e data dall'edizione; la CI aggiunge il vero SHA del commit. Prima pagina con logo originale da `docs/assets/quorivio-logo.svg`, piattaforme Linux amd64/arm64, Docker/Podman/Kubernetes, browser desktop/mobile e requisiti hardware **indicativi**, non certificati.
- **Sorgenti bilingui** aggiornati con procedure di scaling a più repliche, precauzioni RWX/CSI, test di continuità WebSocket, limiti autoscaling, Disaster Recovery con RPO/RTO, backup e ripristino DB PostgreSQL 18 e asset, criteri di collaudo; inoltre esercitazioni dettagliate per presentatori e utenti.
- **Acquisizioni autentiche**: `tools/ci_manual_real_screenshots.py` usa la **vera app frontend production** servita dall'API e PostgreSQL 18 temporanei in GitHub Actions. Nessun mock HTML. Sono previste fino a 14 viste: login, workspace, impostazioni, backup, audit, utenti, editor, proprietà widget, anteprime, schermata live e accesso/risposta/feedback smartphone. Alcune viste sono facoltative se i pulsanti non esistono; il gate richiede almeno 9 screenshot validi e tre per ogni ruolo.
- **Provenienza e privacy**: il browser funziona esclusivamente su loopback e con account `example.com` di test. I campi password/email, QR e link contenenti token sono mascherati. `capture.json` registra commit, provenienza, SHA-256 e dimensioni; la generazione dei PDF rifiuta immagini mancanti, alterate, di commit diverso, o di origine non verificata.
- **Pubblicazione CI**: il job produce il pacchetto artifact `quorivio-live-manuals-<sha>` con le immagini e sei PDF **rigenerati con quelle immagini** per ogni build che raggiunge i test browser. La directory di uscita CI è isolata dai PDF versionati, così non causa falsa difformità negli inventari SHA-256. I file scaricabili su GitHub Actions rimangono per 14 giorni; la pubblicazione nell'app richiede review e una successiva RC, non commit automatici.
- **Edizione locale RC278**: sei PDF rigenerati (180 pagine prima del compattamento indice) con illustrazioni esplicitamente etichettate come tali. **Gli screenshot reali non sono stati ancora acquisiti localmente**: in questa sessione `npm ci` non può risolvere `registry.npmjs.org` (EAI_AGAIN) e manca un'istanza reale costruita. Nessuna immagine dimostrativa viene etichettata come screenshot vero.

## Comandi di manutenzione

```bash
python3 -m unittest tools.tests.test_rc277_manuals tools.tests.test_rc278_manual_screenshots -q
python3 tools/generate_manuals.py
# CI soltanto, dopo vero avvio API/PostgreSQL/Chromium:
python3 tools/ci_manual_real_screenshots.py
python3 tools/generate_manuals.py --require-real --output-dir /tmp/quorivio-manual-build
```

## Acceptance e rischi aperti

I test dell'identità della pubblicazione e di provenienza sono deterministici e senza rete. L'acquisizione real-browser end-to-end e l'integrazione dei PDF arricchiti devono essere provate nella prossima CI. Le schermate prodotte da una fixture CI non provano l'affidabilità di un ambiente Kubernetes reale, GDPR/AGID o la correttezza di tutte le funzioni. Verificare anche qualità visiva su macOS/iOS e modalità smartphone tramite real device.

**Stato certificato del prodotto:** 85,25%, 43 gate accettati e 17 parziali; non cambia per una modifica alla documentazione. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag effettuato dall'assistente.
