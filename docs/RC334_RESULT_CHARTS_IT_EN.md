# Quorivio — RC334: quattro nuovi grafici risultati / Four new result charts

**IT.** I nuovi tipi di rappresentazione dei risultati sono **Linee**, **Area**, **Donut** e **Radar**. Sono visualizzazioni di dati aggregati, disponibili sulla widget dei risultati e nella selezione di visualizzazione delle domande. Il componente è condiviso tra editor, simulazione e schermo presentatore: i valori sono tratti dagli stessi conteggi senza includere identità dei partecipanti. Le impostazioni si trovano in **Formato widget**; vengono validate e salvate insieme al progetto, anche nei file `.quo`.

* **Linee:** visualizzazione ordinata per opzioni, curva smussata opzionale, punti e valori visibili configurabili, spessore della linea 1–8.
* **Area:** come Linee con riempimento sottostante e opacità 0–100%; impostazioni per curva, punti e valori.
* **Donut:** distribuzione proporzionale delle risposte, foro centrale regolabile 20–80%, percentuali opzionali sulle sezioni abbastanza grandi, etichetta centrale con il totale.
* **Radar:** confronti per almeno tre opzioni, griglia radiale regolabile da 2 a 8 livelli, riempimento/opacità, spessore, punti e valori opzionali. Per meno di tre opzioni appare un messaggio non ambiguo.

L'ordinamento delle opzioni è disponibile anche per i nuovi tipi. Nessuna risposta => grafico vuoto, nessuna percentuale inventata. Gli SVG sono accessibili con nome, descrizione e dati aggregati; il rendering preserva i riquadri ridimensionabili e le configurazioni preesistenti.

**EN.** Added **Line**, **Area**, **Donut**, **Radar** views for result widgets. Configure smoothing, value/point labels, line thickness, fill opacity, donut hole percentage and radar ring count in **Widget format**. The same SVG renderer serves authoring, rehearsals and live projection. Data are anonymous aggregates; empty data and under-specified radar categories are handled explicitly. Settings are validated, persisted and transported with the `.quo` session bundle.

## Validation / Verifiche

Run the existing full suite and additionally:

```bash
node --experimental-strip-types --test apps/web/test/result-advanced-chart-geometry.test.ts
node --experimental-strip-types --test apps/api/test/result-advanced-chart-config.test.ts
```

The release workflow performs the full RC acceptance plus the two native Docker image builds (`linux/amd64`, `linux/arm64`) and coordinated manifest publication. The images must not be declared published before that workflow finishes successfully.
