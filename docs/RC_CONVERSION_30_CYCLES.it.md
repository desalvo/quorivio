# Quorivio 0.1.0-dev — 30 interventi su conversione e pubblicazione

**Baseline committata e confermata:** `quorivio-0.1.0-dev-audience-20-cycle-real-browser-cumulative.zip`. Workflow GitHub `40144692900`: qualità e build container **SUCCESS**, pubblicazione SKIPPED. Collaudi Chromium dell'editor e dei partecipanti con PostgreSQL reale **PASS**. Il test opt-in da 500 partecipanti è passato nella precedente run `40141894130`, non ripetuta in questo lotto.

## 30 interventi sostanziali in un solo package

### A. Sicurezza dell'importazione e OOXML (1–6)
1. Applicazione della stessa validazione OOXML nativa all'importazione PPTX rasterizzata e a quella modificabile.
2. Rifiuto dei riferimenti esterni OOXML prima di avviare LibreOffice.
3. Rifiuto di macro ed eseguibili inclusi nell'archivio.
4. Rifiuto di traversal, percorsi assoluti e separatori pericolosi nell'archivio.
5. Rifiuto di membri duplicati, cifrati o simbolici.
6. Applicazione dei limiti su numero di file, dimensioni estratte, singoli file e rapporto di compressione.

### B. Ciclo di vita di sorgente e destinazione (7–12)
7. Rifiuto di sorgenti collegate simbolicamente.
8. Accettazione esclusiva di file sorgente regolari.
9. Limiti dimensionali, estensioni e firme esplicitamente consentite.
10. Calcolo SHA-256 incrementale senza caricare l'intero file in memoria.
11. Rilevamento delle modifiche al sorgente durante la conversione.
12. Rifiuto di output già presenti e directory genitrici simboliche.

### C. Conversione PDF e ordine delle pagine (13–18)
13. Lettura rigorosa di un solo valore valido `Pages` da `pdfinfo`.
14. Rifiuto di documenti vuoti o con oltre 200 pagine prima del rendering.
15. Timeout vincolati e gestione esplicita degli errori dei subprocessi.
16. Nessuna restituzione dello stderr potenzialmente contenente percorsi privati.
17. Ordinamento numerico delle pagine Poppler, corretto anche oltre 9 pagine.
18. Rifiuto di file renderizzati mancanti, duplicati, fuori intervallo o imprevisti.

### D. Integrità PNG e privacy (19–24)
19. Controllo della firma PNG e della struttura IHDR.
20. Verifica CRC IHDR e dei metadati del formato PNG.
21. Limiti su larghezza, altezza e numero totale di pixel.
22. Limite dimensionale per singola pagina.
23. Limite cumulativo di byte per tutte le pagine renderizzate.
24. Permessi privati per immagini e manifest; pubblicazione soltanto dopo checksum e manifest completi.

### E. Atomicità del worker (25–28)
25. Rifiuto di workspace simbolici/non sicuri e output di importazione preesistenti.
26. Staging privato di media e JSON, pubblicazione solo dopo la verifica di fedeltà, pulizia completa in caso di errore.
27. Export PPTX su file temporaneo privato, limite dimensionale e pubblicazione esclusiva senza sovrascritture.
28. Rifiuto di chiavi JSON duplicate, numeri non finiti e media simbolici nell'export.

### F. HTTP e accettazione CI (29–30)
29. Richieste HTTP vincolate a JSON, Content-Length decimale, solo campo `job`, risposte `no-store` e `nosniff`.
30. **58 nuove regressioni** (PDF reale di 12 pagine, PPTX reale con LibreOffice, errori atomici e HTTP); dipendenze LibreOffice/Poppler obbligatorie in CI.

## Verifiche e limiti

- **Python locale:** 340/340 PASS (282 precedenti + 58 nuovi).
- **Node.js locale:** 215/215 PASS.
- **Build TypeScript API e TypeScript/Vite frontend:** PASS.
- **PDF reale Poppler di 12 pagine:** PASS, inclusi ordine e hash nel manifest.
- **PPTX reale LibreOffice:** PASS in locale.
- **Nuova CI GitHub:** NON ANCORA ESEGUITA; le nuove dipendenze e i test devono passare nella prossima run.
- **Punteggio RC:** 45,5/100, invariato. D4 resta parziale: la sicurezza del convertitore non certifica ancora la fedeltà PowerPoint completa.

Restano corpus PPTX/PDF rappresentativo, confronto grafico, roundtrip di oggetti modificabili, font/effetti/transizioni, esecuzione del container in ambiente reale, test di esaurimento risorse e verifica indipendente di accessibilità/sicurezza. Nessun commit, push, tag o release effettuato dall'assistente.
