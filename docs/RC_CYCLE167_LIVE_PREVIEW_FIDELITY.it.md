# Quorivio 0.1.0-dev — RC167 — Parità del rendering reale e protezione delle prove browser

## Base verificata

La run GitHub Actions **41808754419** sul commit RC166 `7138cecc2260` è conclusa con `success`: quality gate, prova cross-browser, ClamAV, PostgreSQL, Kubernetes, Podman, native OCI AMD64/ARM64 e pubblicazione Docker Hub. La segnalazione GitGuardian «Generic Password» è stata chiusa dall'operatore con **ignore**: questa scelta amministrativa non dimostra né la natura del rilevamento né l'assenza di altre credenziali, pertanto i controlli di sicurezza rimangono attivi.

## Correzioni funzionali

1. `apps/web/src/live-slide-policy.ts` definisce l'unica politica di visibilità per titolo, QR, Linee e Forme e i widget esclusivi del presentatore. Editor, anteprima presentatore, anteprima partecipante e pagina reale condividono la regola del titolo.
2. **Linee e Forme:** anche quando un file storico conserva `label` e `showTitle: true`, il partecipante reale vede **solo il disegno SVG**, senza testi né descrizioni. La stessa regola vale per editor e anteprime.
3. **Risultati e Partecipanti connessi:** la pagina partecipante e la sua anteprima escludono completamente i contenitori di questi widget riservati al presentatore. Non restano box vuoti o superfici sovrapposte al canvas. Il presentatore continua a vederli.
4. QR: titolo visibile soltanto dopo esplicita attivazione; URL ancora regolata da `showQrUrl` e senza modifica alla geometria salvata. Il layout automatico smartphone e i widget dello schema rimangono invariati.

## Collaudo autentico aggiunto

`tools/ci_browser_participant.py` allestisce una sessione usa-e-getta con sette widget: Titolo, Domanda, Domande sul tema, Linea con etichetta legacy, Forma con etichetta legacy, Risultati e Partecipanti connessi. Sia Chromium desktop (1366 px) sia la vista mobile (390 px) verificano la presenza degli SVG senza testo, l'assenza totale dei widget riservati al presentatore e l'assenza di pannelli extra. Restano attivi i controlli di voto reale, isolamento tra partecipanti, idempotenza e dati PostgreSQL, QR e chiusura sessione.

## Sicurezza delle fixture

- La destinazione CI viene ora analizzata con `urlsplit`, con porta obbligatoria e hostname **effettivo** `localhost` o `127.0.0.1`; vietati user-info, query, frammenti e percorsi diversi dalla radice. Un prefisso ingannevole come `http://127.0.0.1:8080@host-remoto` viene rifiutato prima di mutare un database.
- Gli artifact su errore browser non contengono più HTML completo, URL `/join/<token>`, body delle risposte o errori raw. Rimangono screenshot con QR mascherato e conteggio sintetico degli errori; nessuna credenziale viene stampata nei fallimenti HTTP.
- Regressioni RC167 (Node, Python e test negativi) sono in CI **prima** di installare npm; i controlli esistenti non vengono disabilitati.

## Stato e limiti

Completamento certificato **85,25%**, 43 gate accettati / 17 parziali, `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Non promuovere A3 senza confronto indipendente su sessione reale, browser mobile fisici e immagini di riferimento approvate. CI Github per RC167, build TypeScript/Vite, test PostgreSQL autenticati e verifica manuale restano necessari dopo il commit.

Commit/push/tag/deploy **non** eseguiti.
