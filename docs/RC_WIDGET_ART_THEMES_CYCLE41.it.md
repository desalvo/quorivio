# Quorivio RC ciclo 41 — Temi artistici configurabili

Quattro temi grafici, salvati nel campo `style.artTheme` di ogni widget: `studio` (predefinito), `glass`, `playful` e `minimal`. Quattro effetti indipendenti in `style.artEffect`: `none` (predefinito), `float`, `glow` e `tilt` (profondità senza alterare coordinate o rotazione). L'editor espone entrambi i selettori nella sezione Aspetto del widget.

I valori sono una allowlist del contratto server e rimangono nel JSON delle pagine, anche in export/import. Il tema grafico è condiviso nelle quattro superfici: editor, prova interattiva, presentatore e partecipante. Le visualizzazioni personalizzate (`fillNone`, colori, gradiente o immagine caricata) hanno priorità sulle decorazioni: **uno sfondo esplicito non va perso né coperto da un nuovo tema**. Non sono ammesse URL CSS arbitrarie o risorse remote introdotte dalla selezione del tema.

Il timer è riconoscibile tramite una clessidra decorativa, un anello di progressione e cifre leggibili; sul canvas viene mostrata una miniatura statica e nella proiezione/anteprima il conto alla rovescia reale. Gli effetti animati rispettano `prefers-reduced-motion`; le decorazioni non diventano controlli interattivi e non modificano l'ordine di lettura.

**Limitazione:** i nuovi temi impiegano illustrazioni/texture CSS, non nuove fotografie di catalogo. Il presentatore può aggiungere fotografie proprie come riempimento immagine già supportato, senza licenze o accesso esterno aggiuntivi. Non è stata verificata visivamente la resa in browser reale: è richiesta CI frontend Chromium e un collaudo editor/anteprime/pubblico, anche su schermi piccoli, dopo il commit.
