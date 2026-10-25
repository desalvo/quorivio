# Quinto lotto da 30 verifiche sostanziali di fedeltà PPTX — 25 ottobre 2026

**Baseline committata:** Audience 20 Cycles, CI GitHub 40144692900 verde. I cinque lotti di conversione (150 interventi/scenari cumulativi) **non sono ancora committati**.

## Funzionalità realizzate

- Import/export PowerPoint modificabile: conservazione degli sfondi RGB solidi, dell’allineamento orizzontale uniforme e dell’ancoraggio verticale dei testi.
- API con validazione rigorosa di `backgroundColor`, `textAlign`, `verticalAlign`; proiezione e anteprima con sfondi RGB; controlli nel designer per colore e allineamento.
- Report di fedeltà con conteggi specifici e indicazione delle perdite per sfondi sfumati e paragrafi con allineamenti misti. Sicurezza OOXML e pubblicazione atomica mantenute.

## Inventario dei 30 scenari eseguiti

1. Import a black slide background as an editable RGB page color.
2. Import a white slide background without converting it to an image.
3. Import an arbitrary brand-color solid background.
4. Import a red slide background.
5. Import a blue slide background.
6. Export an arbitrary RGB page background to native PPTX.
7. Roundtrip a black exported background.
8. Roundtrip a white exported background.
9. Normalize lowercase RGB export colors through OOXML.
10. Report retained solid backgrounds in the fidelity audit.
11. Do not fabricate a background for an inherited/default fill.
12. Report unsupported gradient backgrounds as lossy.
13. Import left-aligned text as editable widget style.
14. Import centered text as editable widget style.
15. Import right-aligned text as editable widget style.
16. Import top-anchored text boxes.
17. Import middle-anchored text boxes.
18. Import bottom-anchored text boxes.
19. Export left text alignment into PPTX paragraph formatting.
20. Export centered text alignment into PPTX paragraph formatting.
21. Export right text alignment into PPTX paragraph formatting.
22. Export top vertical anchor into PPTX text frame.
23. Export middle vertical anchor into PPTX text frame.
24. Export bottom vertical anchor into PPTX text frame.
25. Flag mixed paragraph alignment rather than claiming a lossless import.
26. Reject invalid named background colors before publication.
27. Reject unsupported alpha backgrounds before publication.
28. Reject nonstring backgrounds before publication.
29. Reject unsupported horizontal alignment values before publication.
30. Reject unsupported vertical alignment values before publication.

## Evidenze e limiti

30 nuovi test comportamentali PowerPoint + 6 test Node/API. Restano aperti confronto pixel su corpus PPTX reale, temi complessi, accettazione browser/dispositivi e nuova CI. **RC 45,5% invariato**; nessun commit/push/tag/release.
