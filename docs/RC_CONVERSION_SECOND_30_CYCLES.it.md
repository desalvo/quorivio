# Secondo lotto da 30 interventi — conversione nativa PPTX e pubblicazione sicura

**Baseline committata:** Audience 20 Cycles, run 40144692900 verde. **Importante:** anche il lotto precedente `RC_CONVERSION_30_CYCLES` è ancora **non committato**; questo package cumula entrambi i lotti (60 interventi documentati), senza perdere modifiche.

## Inventario

1. Rifiuto delle immagini PNG con sola firma apparente e struttura non decodificabile.
2. Rifiuto di PNG troncati e con integrità dei blocchi non valida.
3. Validazione completa della struttura JPEG anziché del solo magic byte.
4. Confronto tra MIME dichiarato e formato effettivamente decodificato.
5. Limite esplicito di 16 milioni di pixel per le immagini importate.
6. Controllo dei byte immagine decompressi tramite Pillow prima della pubblicazione.
7. Rifiuto di membri OOXML duplicati con differenze soltanto di maiuscole/minuscole.
8. Rifiuto di nomi OOXML con prefissi di unità Windows.
9. Rifiuto di percorsi OOXML non canonici con separatori duplicati.
10. Rifiuto di nomi OOXML con caratteri di controllo o prefisso ./.
11. Estensione della lista dei contenuti eseguibili OOXML proibiti.
12. Parsing XML dei file di relazioni, compresi attributi con entità XML.
13. Rifiuto delle relazioni OOXML XML malformate.
14. Rifiuto dei file sorgenti PPTX simbolici/non regolari.
15. Rifiuto delle directory media importate tramite symlink.
16. Creazione esclusiva degli asset estratti, senza sovrascritture silenziose.
17. Permessi privati 0600 sugli asset importati.
18. Limite di profondità nella conta dei gruppi per il report di fedeltà.
19. Rifiuto di presentazioni vuote o oltre il limite nel percorso di analisi.
20. Validazione dei titoli espliciti delle presentazioni importate.
21. Validazione tipizzata di formato, versione e pagine esportate.
22. Validazione tipizzata di page_design e lista dei widget.
23. Validazione preventiva della geometria con numeri finiti e intervalli ammessi.
24. Validazione preventiva delle rotazioni, inclusi NaN e booleani.
25. Rifiuto di testi con caratteri incompatibili con XML 1.0.
26. Validazione dei tipi di stile e dei campi di formattazione.
27. Validazione della struttura e dei limiti delle opzioni dei quiz.
28. Quota cumulativa sugli asset unici in esportazione PPTX.
29. Pubblicazione esclusiva e atomica di PPTX/JSON, con file temporanei privati e cleanup.
30. Controllo SHA-256 della stabilità del sorgente durante import/export worker e rifiuto delle root di conversione symlink.

## Verifiche

Test Python: **375/375 PASS** (35 nuovi test comportamentali); Node.js **215/215 PASS**; build API TypeScript e web TypeScript/Vite **PASS**. Il precedente lotto ha già superato una conversione PDF di 12 pagine e una PPTX LibreOffice locale. **Non** sono stati eseguiti nuovi test CI GitHub né prove visuali indipendenti di fedeltà su corpus reali.

**Restano aperti:** fedeltà grafica completa, corpus PPTX reale, rendering su dispositivi/browser multipli, audit AV/pentest, test operativi e firma della RC. Gate D4 ancora parziale; audit RC **45,5%**, senza promozioni non dimostrate.
