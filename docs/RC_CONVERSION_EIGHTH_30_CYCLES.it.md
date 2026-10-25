# Ottavo lotto conversione — riempimenti e contorni nativi PowerPoint modificabili (30 casi)

**Baseline:** ultimo commit confermato = Audience 20 Cycles, workflow GitHub `40144692900` verde. Otto lotti di conversione, **240 interventi/scenari cumulativi**, non sono ancora committati. Non equivalgono a 240 funzionalità indipendenti.

## Funzionalità sviluppate

- Le forme native PowerPoint modificabili (rettangoli, rettangoli arrotondati, ellissi e triangoli) conservano **spessore del contorno (0,25–12 pt)**, **linea continua/tratteggiata/puntinata**, **nessun riempimento** e **nessun contorno**. Le forme restano modificabili, senza rasterizzazione.
- L'editor canvas espone controlli accessibili da tastiera per colore/assenza di riempimento, colore/assenza di contorno, spessore e tratteggio. I dati usano il salvataggio persistente del layout già esistente.
- Proiezione, anteprima partecipante, canvas e miniature rispettano le nuove proprietà. Colori di tema PowerPoint, spessori fuori intervallo e tratteggi non supportati restano limitazioni di fedeltà dichiarate.
- Validazione API PostgreSQL e preflight Python bloccano larghezze non finite, booleane, fuori intervallo, tratteggi sconosciuti e flag trasparenza non booleani. Restano attive le protezioni su media, ritagli e pubblicazione atomica.

## Inventario dei 30 casi di accettazione

1. Confronto raster contorno 0,25 pt.
2. Confronto raster contorno 1 pt.
3. Confronto raster contorno 2 pt.
4. Confronto raster contorno 4 pt.
5. Confronto raster contorno 8 pt.
6. Confronto raster tratteggio.
7. Confronto raster tratteggio spesso.
8. Confronto raster puntinato.
9. Confronto raster puntinato con riempimento trasparente.
10. Confronto raster riempimento pieno senza contorno.
11. Confronto raster senza riempimento né contorno.
12. Confronto raster contorno continuo e riempimento trasparente.
13. Le 12 forme restano widget modificabili.
14. Conservazione spessore in importazione.
15. Conservazione spessore in esportazione.
16. Conservazione tratteggio in importazione.
17. Conservazione tratteggio in esportazione.
18. Conservazione assenza di riempimento in importazione.
19. Conservazione assenza di contorno in importazione.
20. Esportazione trasparenza come riempimento PowerPoint nativo.
21. Esportazione assenza contorno come linea PowerPoint nativa.
22. Conservazione geometria delle quattro tipologie di forma.
23. Nessuna falsa classificazione come conversione con perdita per proprietà supportate.
24. Rifiuto spessore negativo.
25. Rifiuto spessore zero.
26. Rifiuto spessore eccessivo.
27. Rifiuto NaN.
28. Rifiuto booleano usato come spessore.
29. Rifiuto tratteggio sconosciuto.
30. Rifiuto flag riempimento come stringa.

Aggiunti inoltre **7 test Node.js** e **5 controlli di integrazione UI**. I 12 confronti visivi usano rendering reale LibreOffice Impress e Poppler su corpus **sintetico**: non certificano Microsoft PowerPoint o presentazioni complesse di terze parti.

## Evidenze e residui

Nuovi 30 casi PASS, 232 test Node.js PASS, build TypeScript backend e Vite frontend PASS. Suite Python completa **583/583 PASS** in locale; nuova CI GitHub da eseguire. Punteggio RC ufficiale **45,5%**; gate A3/D4 parziali. Mancano accettazione Chromium dei nuovi controlli, confronto indipendente Microsoft Office, corpus reale PPTX, accessibilità su dispositivi e gate di produzione. Nessun commit/push/tag/release.
