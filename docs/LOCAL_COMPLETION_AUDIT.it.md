# Quorivio 0.1.0-dev — Verifica di completamento software

Questa nota separa le verifiche locali dalle accettazioni da svolgere su un'installazione reale. Non è una dichiarazione di release candidate.

## Modifiche del ciclo

- Aggiunti indicatori di focus visibili per miniature, barra dei widget, pulsanti e controlli delle risposte.
- Aggiunta compatibilità con `prefers-reduced-motion` e `forced-colors` senza cambiare geometrie salvate.
- Aumentata la superficie touch dei comandi miniature su dispositivi piccoli.
- Aggiornato il testo della UI PowerPoint per riflettere immagini PNG/JPEG e forme semplici già convertibili; non promette SmartArt, temi complessi o animazioni.
- Aggiunti test di regressione per questi contratti.

## Evidenza di verifica locale

- Python: 216 test superati.
- Node.js: 116 test superati.
- Build frontend TypeScript/Vite: non rieseguita in questo ambiente (dipendenze npm non installate); CI precedentemente confermata verde dall'utente si riferisce a un precedente commit.
- PostgreSQL live, browser mobile, Kubernetes e benchmark 500 utenti: non eseguiti qui.

## Macroaree software non ancora dimostrate complete

- PowerPoint: OOXML complesso, grafici, tabelle, gruppi, SmartArt e conservazione non distruttiva di parti sconosciute.
- Editor: prove browser per pointer capture, zoom, miniature, ridimensionamento e focus tra pagine.
- MFA: verifica indipendente dei metodi email/TOTP, controllo generale unificato e flusso di recupero.
- Live: risposte, graduatorie, sincronizzazione tra pod e distribuzione di eventi sotto carico.
- Qualità: installazione dipendenze riproducibile con lockfile verificato, audit licenze e aggiornamento completo dei manuali.

RC_GATE_MATRIX.json resta intenzionalmente invariata a 37,5% fino ad acquisizione di nuove prove per i gate.
