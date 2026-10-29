# Quorivio 0.1.0-dev — protocollo di accettazione indipendente RC

**Ambito:** 17 gate attualmente parziali. I test locali e CI automatizzati **non** sostituiscono la verifica indipendente. Non promuovere gate soltanto perché questo protocollo o una checklist sono stati generati.

## Raccogliere le evidenze

Per ogni prova annotare ID gate, versione/commit e hash dell'immagine effettivamente installata, data/ora UTC, revisore indipendente, ambiente, browser/versione e dispositivo, dataset di test, risultato PASS/FAIL/BLOCKED, screenshot/video senza dati personali, log redatti e collegamento al ticket. Le credenziali e i token devono rimanere fuori dai report. Un gate può essere accettato soltanto quando **tutti** i criteri residui di `docs/RC_GATE_MATRIX.json` hanno evidenza verificabile e approvazione del responsabile.

## Percorso browser multi-engine

La CI possiede un'opzione **`cross_browser_test=true`** indipendente da `browser_test=true`. Su GitHub installa Firefox e WebKit nativi, compila TypeScript e testa sia il modulo reale di focus, sia il CSS pubblico 16:9, sia il bundle React reale in due viewport (1440 e 390 pixel). Una run verde costituisce evidenza tecnica **limitata**, non certificazione di pixel-parity, screen reader o dispositivi fisici. Il job opzionale ha superato su GitHub la run [40847463104](https://github.com/desalvo/quorivio/actions/runs/40847463104), commit cf49c3e1, job 123360950163, con Firefox e WebKit a 1440/390px sul modulo TypeScript e CSS 16:9. La **nuova estensione al bundle React completo** richiede ancora una CI dopo il ciclo 14. Resta necessaria la verifica indipendente su dispositivi fisici, screen reader, fedeltà visiva e infrastruttura.

Esecuzione locale (solo quando gli eseguibili Playwright sono già disponibili):

```bash
npm run build
python3 tools/ci_cross_browser_rc.py --engines firefox webkit
python3 tools/ci_rehearsal_singleton_offline_chromium.py --engines firefox webkit
```

In mancanza di uno dei browser il test **deve fallire**, mai ripiegare su Chromium. Dopo commit, lanciare `workflow_dispatch` con `browser_test=true`, `cross_browser_test=true`, `capacity_test=true`, `publish_image=false`, `publish_latest=false`, `rc_strict=false` fino alla chiusura di tutti i gate.

## Verifiche fisiche e indipendenti ancora necessarie

- **A1/A2/A3/A4:** confronto reale editor/anteprima/pubblico di un corpus campione con widget sovrapposti, ritagli, gradienti, testo ricco e miniature; riordino drag/touch; tastiera-only; Firefox/WebKit; NVDA su Windows, VoiceOver su iOS/macOS e TalkBack su Android. Annotare problemi di focus, ridimensionamento, zoom, contrasto, orientamento, perdita dati e piena navigabilità, con revisione WCAG/AGID.
- **B1/B2/B3/B4:** esercizi di durata operativa con due o più repliche, reti a latenza variabile, perdita e ripresa del WebSocket, concorrenza reale, revisione delle statistiche private e dei quiz a tempo, misure percentile latenza/memoria e verifica SLO su un dataset concordato. I 500 partecipanti della CI sono un test circoscritto, non un SLO di produzione.
- **C1/C2/C3/C4:** account recovery e MFA con provider reali e guasti SMTP, URL/link/token dopo redirect, revoca multi-replica, OAuth Google/GitHub/Facebook con consenso reale, test ClamAV e storage RWX su installazione reale, privacy/ruoli e cancellazione definitiva, controllo operatori e security review indipendente.
- **D2/D3/D4/D5/D6:** drill di disaster recovery con obiettivi concordati, backup cifrati e rotazione chiavi, Podman rootless, ARM64 nativo, HAProxy e NGINX ingress, storage RWX e ClamAV, pentest indipendente, fedeltà PPTX Office di terzi, revisione manuali IT/EN, GDPR/AGID e approvazione legale/operativa.

## Criterio di uscita

Le nuove evidenze devono essere registrate nella matrice e nei report di validazione, con hash e URI della run o del documento di approvazione. Solo allora si ricalcola il punteggio con `python3 tools/rc_gate_audit.py`; il controllo `python3 tools/rc_release_preflight.py --strict` deve passare. Fino a quel momento la RC **non è pronta**.

## Aggiornamento ciclo 16 — 29 ottobre 2026
La run GitHub [40855898307](https://github.com/desalvo/quorivio/actions/runs/40855898307) passa anche sul **bundle React reale Firefox/WebKit** (quattro combinazioni motore/viewport), oltre al controllo CSS/TypeScript. I limitati sotto-gate A1-NATIVE-REACT-ENTRY e A4-NATIVE-REACT-FOCUS sono accettati, mentre il parent resta parziale per dispositivi e revisione indipendente. Il recupero password Chromium React ottiene un sotto-gate distinto C1-RECOVERY-UI; SMTP esterno e multi-replica restano aperti. Nuovo scenario WebSocket di disconnessione/riconnessione e probe fuori dialogo richiedono ancora CI. Nessuna approvazione manuale implicita.
