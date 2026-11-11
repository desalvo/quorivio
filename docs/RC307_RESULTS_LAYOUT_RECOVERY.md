# RC307 — Render risultati coerente e resilienza dashboard

**Data:** 11 novembre 2026. **Baseline:** commit `d227825ab9aeb6fe2a4494aedcb7ef68a36194be`, RC306 con CI verde e immagini multiarch già pubblicate.

## Difetti corretti
1. **Layout** — Editor pagine/schemi, anteprima e presentazione reale utilizzano lo stesso risultato `LinkedResultChart` senza comportamenti diversi di shrink-to-fit: tutte le statistiche mantengono la dimensione di testo configurata e usano scorrimento interno quando la loro altezza eccede il widget. L'editor applica `stageWidgetTypography` come le altre viste, con contenitore di anteprima `display:contents` per eliminare la differenza del wrapper.
2. **Titolo nell'editor** — Non si forza più `showTitle:false` nella widget risultati. Quando l'editor non sta modificando il testo, il titolo viene renderizzato internamente al grafico come avviene in preview e proiezione. In modalità modifica è visualizzato il campo rich edit esterno senza doppio titolo.
3. **Ordinamento** — `resultSortOrder` è condiviso da barre, torte, tabelle e nuvole. Quattro modalità: indice crescente/decrescente e conteggio crescente/decrescente. La selezione superiore applica ordinamento + limite per tutte le viste; anche la lista sorgente segue la scelta. Le torte mantengono numeri e colori associati alle opzioni originali quando la fetta cambia posizione.
4. **Resilienza** — Due error boundary delimitano i risultati live e il contenitore pagina, per non far ripartire l'intera applicazione né obbligare al reset della sessione in caso di errore di render. Il fallback permette `Riprova grafico` senza eliminare cookie o stato server.

## Verifiche e limiti
- `apps/web/test/rc307-results-layout-recovery.test.ts` — parità statica del renderer, ordinamento dei dati, numerazione della torta, controlli editor e presenza dei boundary.
- Full npm/unit, TypeScript, browser live e Kubernetes sono obbligatori nella full CI prima di pubblicare app e converter multiarch.
- Le simulazioni possono avere valori diversi dal live, ma con la stessa geometria e ordine impostati.
- I 17 gate di accettazione esterna rimangono indipendenti: completamento certificato ancora 85,25% finché non si acquisiscono le relative prove.

## Operatività
Riavviare la sessione non è più necessario per un errore isolato del grafico, la schermata presenter continua a mantenere i propri controlli. Il percorso canonico dell'handoff rimane `/Quorivio-HANDOFF-current.md` nella Libreria.
