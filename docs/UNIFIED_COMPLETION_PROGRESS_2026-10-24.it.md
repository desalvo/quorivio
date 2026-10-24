# Completamento software unificato — verifica del 24 ottobre 2026

Questo cumulativo rappresenta **un completamento parziale**, **non una Release Candidate**. Non chiude tutte le macroaree funzionali.

## Modifiche realizzate
- PPTX: attraversamento delle forme raggruppate e annidate, recuperando testo, figure compatibili e media come widget indipendenti con coordinate trasformate. I gruppi nativi, le geometrie di rotazioni complesse e gli effetti OOXML non sono conservati: il rapporto di fedeltà segnala esplicitamente la perdita.
- Test su gruppi, dimensionamento, annidamento e limite di 16 widget per pagina.
- Conservate le precedenti correzioni relative a TOTP senza SMTP, integrità degli archivi `.quorivio`, recupero delle celle PowerPoint e interfaccia mobile.

## Evidenze di test
- Python: **223 test superati**.
- Node.js API: **120 test superati**.
- Build `npm run build`: **non superata** nell'ambiente locale offline per le definizioni di tipo Node mancanti (`TS2580`, `Buffer`). Una CI verde precedente non certifica questo archivio.
- Nessun collaudo reale su PostgreSQL, browser Playwright, Kubernetes, provider SSO, due istanze indipendenti o carico distribuito a 500 partecipanti per questa revisione.

## Macroaree ancora aperte
1. PowerPoint avanzato: grafici, tabelle native, SmartArt, round-trip dei gruppi, master, animazioni e fedeltà OOXML.
2. Ciclo end-to-end dei widget: creazione, pubblicazione, risposta anonima, punteggio e risultati live su database e browser reali.
3. MFA email/TOTP e switch generale, amministrazione SSO, recupero account.
4. Accessibilità e QA visivo editor/mobile sui dispositivi fisici.
5. Trasferimento `.quorivio` tra installazioni indipendenti.
6. Installazione pulita e build completa, audit sicurezza/licenze, prove GDPR e deployment.
7. Manualistica completa IT/EN e benchmark distribuito di 500 partecipanti.

Versione `0.1.0-dev` invariata. Nessun intervento su GitHub o Kubernetes.
