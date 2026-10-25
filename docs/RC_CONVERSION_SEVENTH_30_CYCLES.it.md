# Settimo lotto conversione — ritaglio modificabile delle immagini PowerPoint (30 casi)

**Baseline:** ultimo commit confermato = Audience 20 Cycles (workflow GitHub 40144692900 verde). I sei lotti precedenti e questo settimo lotto sono ancora non committati: **210 interventi/scenari cumulativi**, non 210 funzionalità distinte.

## Funzionalità

Le immagini PPTX con ritagli nativi rappresentabili diventano widget immagine **modificabili** con quattro coordinate frazionarie. I file originali restano privati, verificati e deduplicati anche quando le diapositive usano ritagli differenti. L'esportazione ricostruisce i ritagli nativi PowerPoint senza rasterizzare l'immagine già tagliata. Proiezione e anteprima partecipante applicano il ritaglio nel browser. L'editor espone quattro campi numerici accessibili da tastiera e un pulsante di ripristino. La validazione server e il preflight del convertitore rifiutano frazioni non valide, valori non finiti, campi inattesi, ritagli eccessivi e metadati crop su widget non immagine.

I ritagli negativi/overscan PowerPoint e quelli che eliminano quasi l'intera immagine restano **non supportati** e sono segnalati come perdita di fedeltà. Il contatore storico `cropped_pictures` rimane informativo; i ritagli supportati non determinano più da soli `lossy=true`.

## Inventario dei 30 casi

1. Ritaglio sinistro e confronto raster.
2. Ritaglio destro e confronto raster.
3. Ritaglio superiore e confronto raster.
4. Ritaglio inferiore e confronto raster.
5. Ritaglio orizzontale bilaterale.
6. Ritaglio verticale bilaterale.
7. Ritaglio sinistra/alto.
8. Ritaglio destra/basso.
9. Ritaglio su quattro lati.
10. Ritaglio ampio su quattro lati.
11. Ritaglio asimmetrico.
12. Ritaglio centrato.
13. Importazione come widget modificabili.
14. Preservazione coordinate in importazione.
15. Preservazione coordinate in esportazione.
16. Deduplicazione immagine originale fra ritagli diversi.
17. Classificazione corretta della fedeltà.
18. Conservazione della forma immagine nativa PPTX.
19. Validazione ritaglio zero.
20. Validazione del limite per lato.
21. Rifiuto eccesso orizzontale.
22. Rifiuto eccesso verticale.
23. Rifiuto valori negativi.
24. Rifiuto valori non finiti.
25. Rifiuto booleani come numeri.
26. Rifiuto chiavi extra.
27. Rifiuto chiavi mancanti.
28. Rifiuto preflight prima della pubblicazione.
29. Rifiuto ritaglio su widget testo.
30. Segnalazione overscan nativo non supportato.

Aggiunti inoltre quattro test Node e sei controlli UI. I primi 12 casi usano **confronti raster reali LibreOffice/Poppler** su un corpus sintetico, non su presentazioni Office di terze parti.

## Evidenze e residui

Locale: **225 test Node PASS; 548 test Python PASS; build TypeScript backend e Vite frontend PASS; 12 confronti raster reali PASS**. Nuova CI GitHub e container non ancora eseguiti; restano aperti rendering Microsoft Office, corpus PPTX complessi e verifica Chromium dell'editor crop. A3/D4 parziali; punteggio RC ufficiale **45,5%**. Nessun commit/push/tag/release.
