# Terzo lotto di 30 interventi — sicurezza del convertitore

Data: 2026-10-25. Baseline committata: Audience 20 Cycles. Lotti conversione 1, 2 e 3 **non committati**.

## Inventario dei 30 interventi

1. Decodifica integrale PNG.
2. Verifica CRC della intestazione IHDR.
3. Verifica CRC dei blocchi IDAT.
4. Verifica CRC del terminatore IEND.
5. Rifiuto di PNG senza terminatore.
6. Rifiuto dei byte dopo il terminatore.
7. Rifiuto dei blocchi critici sconosciuti.
8. Rifiuto di intestazioni IHDR duplicate.
9. Verifica della contiguità IDAT.
10. Rifiuto di terminatori IEND con payload.
11. Rifiuto di blocchi PNG troncati.
12. Rifiuto di dati immagine non decodificabili.
13. Validazione dei nomi dei blocchi PNG.
14. CRC di tutti i blocchi ancillari.
15. Compatibilità con metadati PNG legittimi.
16. Verifica del formato colore e della geometria raster.
17. Rifiuto di PDF cifrati.
18. Rifiuto di PDF con JavaScript dichiarato.
19. Compatibilità con PDF normali non cifrati.
20. Rifiuto DTD/ENTITY nei componenti OOXML.
21. Scansione XML completa anche dopo prefissi estesi.
22. Rifiuto di compressioni ZIP non supportate.
23. Rifiuto di componenti ActiveX incorporati.
24. Rifiuto di componenti OLE binari senza bloccare grafici Excel.
25. Rifiuto di contenuti PPTM mascherati da PPTX.
26. Validazione dei target OOXML assoluti e URI.
27. Validazione delle codifiche percentuali anche annidate.
28. Rifiuto delle relazioni OOXML attive.
29. Protezione delle directory worker e dello stato health da symlink.
30. Autenticazione Bearer rigorosa e framing HTTP senza ambiguità.

## Evidenze e limiti

- 43 nuovi test comportamentali su parsing PNG, PDF, OOXML e protocollo HTTP del worker; totale locale 418 Python, 215 Node.
- Build backend TypeScript e frontend Vite PASS. Conversioni PDF/PPTX reali già incluse nella suite Python.
- Dipendenza Pillow esplicita nell’immagine converter e nella CI; nessuna pubblicazione o commit remoto.
- Il test del nuovo container e la nuova CI GitHub **non sono stati eseguiti** in questo lotto.
- La fedeltà grafica su corpus PPTX reali, il pentest indipendente e il collaudo accessibilità restano aperti.
- Gate D4 `partial`; punteggio RC invariato **45,5%**. Non è una release candidate.
