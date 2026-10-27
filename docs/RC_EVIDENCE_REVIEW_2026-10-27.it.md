# Quorivio — Revisione delle evidenze RC del 27 ottobre 2026

## Avanzamento ponderato certificato: 53,0% (da 48,0%)

È un **indice prudenziale di preparazione**, non la copertura dei test o una certificazione normativa. `accepted=100%` del peso, `partial=50%`, `open/blocked=0%`.

| Gate | Peso | Prima | Dopo | Incremento | Evidenza |
|---|---:|---|---|---:|---|
| A4 — accessibilità e mobile | 6 | open | partial | +3,0 | Chromium reale desktop/touch, uso da tastiera e controlli accessibili |
| D3 — distribuzione multipiattaforma | 4 | open | partial | +2,0 | Pubblicazione manuale Buildx amd64+arm64, SBOM e provenienza |
| **Totale** | | | | **+5,0** | **53,0%** |

### CI verificata

- Run `40517573850` sul commit `e372a3aec8ba6b028283e9d00f68305a39562ed8` già committato dall'utente.
- Quality `122235650919`: SUCCESS, compresi Chromium editor, PostgreSQL reale, Q&A, fairness quiz temporizzati, privacy, WebSocket con due repliche e 500 partecipanti.
- Container `122238333840`: SUCCESS, build e scansioni.
- Pubblicazione autorizzata `122239629249`: SUCCESS; `docker.io/desalvo/quorivio` tag `latest` e `sha-e372a3aec8ba`; digest `sha256:2be79bc6ca99fa22b6f970c8bb97d9162b4943dafd27c80d3eb1b60ebc474e41`.

**Attenzione:** il manifesto multiarchitettura non dimostra che l'immagine sia stata effettivamente avviata su hardware ARM64. I test Chromium non sostituiscono prove con screen reader e dispositivi reali. I gate A4 e D3 passano solo da *open* a *partial*, non ad *accepted*.

### Nuovi sviluppi dopo il commit (CI da rieseguire)

- Miniature riordinabili anche con `Alt+Freccia su` / `Alt+Freccia giù`, separatamente dalla navigazione con frecce normali.
- `Esc` chiude il menu contestuale della miniatura e restituisce il focus al pulsante di apertura.
- Annunci `aria-live` per riordino in corso, successo o fallimento, senza coprire il canvas.
- Test di regressione per focus, ordine persistito, guardia delle modifiche non salvate e mantenimento delle verifiche di concorrenza.

### Rischi ancora aperti

Accessibilità AGID/WCAG e GDPR richiedono verifiche indipendenti; sono ancora da validare Firefox/WebKit, hardware mobile reale, ARM64 nativo, Podman rootless, Kubernetes con storage condiviso, prove di durata/latency, provider SSO/SMTP reali e documentazione operativa. B2/B3 restano *partial* perché il risultato positivo della CI non equivale a queste accettazioni indipendenti.

La release candidate **non è dichiarata pronta**. Il prossimo commit e la relativa CI appartengono all'utente, non all'assistente.
