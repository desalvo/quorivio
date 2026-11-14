# RC338 — Minimo accessibile per commenti dei widget Gradimento
## Italiano
La full CI #43531911477 ha superato i nuovi test RC337 e la compilazione. Il test Chromium del partecipante, in modalità «Lettura accessibile» su smartphone a 390 px, ha rilevato un campo di commento inferiore a 44 px. Una precedente regola CSS `min-height:3em!important` prevaleva sui 44 px. L'override più specifico applicato ora impone 44 px **solo** nella lettura accessibile. La proiezione 16:9 e la geometria salvata restano intatte. Il test Chromium reale conserva il controllo dei 44 px e rimane obbligatorio in CI.

Questa correzione completa l'integrazione del fix RC337 per gli export PDF/PPTX (SQL delle reazioni e download autenticati). La pubblicazione delle immagini Docker app + converter richiede tutti i gate verdi e la verifica dei digest, separata dalla validazione operativa dell'installazione reale.

## English
The Chromium phone participant test rejected a rating comment input below 44 CSS pixels in the accessible reading view. A legacy `min-height:3em!important` outranked the prior 44px rule. The reading-only specific override restores 44px while preserving the pixel-accurate 16:9 geometry. A regression guards the selector, and real Chromium acceptance remains mandatory. Paired multiarch Docker publication requires full green CI.
