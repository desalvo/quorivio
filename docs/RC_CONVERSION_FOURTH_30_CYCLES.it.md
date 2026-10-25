# Quarto lotto da 30 interventi — validazione PPTX e percorsi

**Baseline committata:** Audience 20 Cycles. I quattro lotti di conversione sono ancora non committati; questo cumulativo contiene 120 controlli/interventi dichiarati. I 30 punti seguenti corrispondono a 30 scenari di regressione distinti, non a 30 macrofunzionalità autonome.

1. Controllo delle relazioni OOXML anche con estensione .RELS maiuscola.
2. Blocco di percorsi assoluti codificati due volte.
3. Blocco di attraversamento directory con separatori codificati a più livelli.
4. Rifiuto di relazioni che risalgono oltre la radice del pacchetto.
5. Applicazione dello stesso controllo alle relazioni della radice OOXML.
6. Compatibilità verificata con le relazioni ../media interne legittime.
7. Rifiuto delle relazioni con destinazione vuota.
8. Rifiuto dei caratteri di controllo XML normalizzati nei target.
9. Rifiuto di schemi URI mascherati con codifica percentuale.
10. Rifiuto dei componenti ZIP con segmenti /./ non canonici.
11. Rifiuto di CR/LF nei target anche se codificati come entità XML.
12. Compatibilità verificata con le relazioni interne della radice.
13. Esportazione verificata con una famiglia di caratteri valida.
14. Rifiuto di famiglie di caratteri vuote o contenenti soli spazi.
15. Limite esplicito alla lunghezza del nome della famiglia di caratteri.
16. Rifiuto di surrogati Unicode non validi nei nomi dei font.
17. Convalida del colore testo con formato RGB esadecimale completo.
18. Convalida del colore di riempimento delle forme.
19. Convalida del colore del bordo delle forme.
20. Elenco consentito per i tipi di forma esportabili.
21. Rifiuto delle dimensioni font negative.
22. Rifiuto delle dimensioni font fuori scala.
23. Rifiuto di coordinate booleane interpretate erroneamente come numeri.
24. Rifiuto delle coordinate numeriche trasmesse come stringhe.
25. Compatibilità preservata per la geometria omessa con default sicuri.
26. Convalida anticipata dell’identificativo media prima della costruzione PPTX.
27. Rifiuto anticipato degli identificativi UUID di versione non supportata.
28. Rifiuto dei page_design esplicitamente null anziché sostituzione silenziosa.
29. Rifiuto delle liste widget esplicitamente null anziché sostituzione silenziosa.
30. Rifiuto di directory media con antenati symlink; serializzazione delle immagini dai byte già verificati, senza riaprire il percorso.

**Risultati locali:** 448/448 test Python, 30 nuovi; nessuna modifica TypeScript. Node e build non rieseguiti perché le dipendenze npm non sono disponibili nel container corrente. CI GitHub e container build da verificare. **D4 parziale, 45,5% invariato.** Nessun commit/push/tag/release.
