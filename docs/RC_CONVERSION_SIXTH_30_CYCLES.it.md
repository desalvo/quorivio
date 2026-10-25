# Sesto lotto di 30 verifiche — fedeltà visiva e interoperabilità

**Baseline:** ultimo commit confermato Audience 20 Cycles, CI `40144692900` verde. I sei lotti di conversione (180 interventi/scenari) sono **ancora non committati**.

## Sviluppi

- Corpus riproducibile di **12 diapositive PPTX realmente renderizzate** con LibreOffice Impress e Poppler prima e dopo importazione Quorivio/esportazione PPTX. Verifica della differenza media RGB (<18/255) per ciascuna delle 12 pagine. Comprende sfondi RGB, allineamenti, grassetto, forme modificabili e colori.
- Preservazione degli spazi iniziali/finali, dei ritorni a capo e di testo Unicode nell'importazione (entro il limite esistente di 500 caratteri). Corretto il presentatore: niente duplicazione etichetta/descrizione, tipografia applicata e spazi preservati.
- Report di fedeltà più trasparente per stili misti, colori dei temi, riempimenti sfumati, contorni dei temi, immagini ritagliate e testi oltre il limite.
- Restano invariati i limiti di 16 widget, 200 pagine, quote media, protezioni OOXML e pubblicazione atomica.

## Inventario dei 30 casi eseguiti

1–12. Dodici confronti pixel per pixel dei rendering LibreOffice/Poppler dopo roundtrip nativo.
13. Numero di pagine del deck esportato.
14. Dodici colori di sfondo modificabili.
15. Geometria delle forme modificabili.
16. Tre allineamenti del testo.
17. Alternanza grassetto/normale.
18. Colore di riempimento delle forme native.
19. Colore del carattere esportato.
20. Report non-lossy per corpus supportato.
21. Spazi iniziali.
22. Spazi finali.
23. Ritorni a capo.
24. Testo Unicode/diacritici/CJK.
25. Stili di run misti segnalati come lossy.
26. Stili uniformi senza falsi allarmi.
27. Colori testo dipendenti dal tema segnalati.
28. Riempimenti sfumati segnalati.
29. Contorni dipendenti dal tema segnalati.
30. Testi oltre 500 caratteri segnalati come lossy.

Altri quattro test controllano la tipografia della proiezione e l'assenza di duplicazione del testo.

## Risultati e limiti

- Python **512/512 PASS**; Node **221/221 PASS**; build TypeScript/Vite **PASS**; audit matrice RC **PASS**, punteggio **45,5% invariato**.
- Il corpus è **sintetico**, non sostituisce presentazioni PowerPoint reali e non certifica fedeltà pixel-perfect né rendering Microsoft Office. Nuova CI GitHub/container ancora da eseguire.
- Nessun commit, push, tag, release o deploy.
