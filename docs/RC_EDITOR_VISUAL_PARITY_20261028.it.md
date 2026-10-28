# Quorivio 0.1.0-dev — Allineamento editor, anteprima e partecipante (28 ottobre 2026)

**Baseline:** commit utente `e2dc3a97bd15d82a50c23a98b1fb83c2bd1841c9`; Full CI precedente `40595463258` verde. **Nuove modifiche ancora non committate e non confermate in GitHub CI.** Nessuna pubblicazione Docker eseguita in questo ciclo.

## Consegnato nel cumulativo

- Il canvas editor mostra i contenuti di prova dei widget usando la logica di proiezione, non solo il titolo: Timer, gradimento, reazioni, QR, immagini/media, partecipanti, risultati, profilo, testo e opzioni.
- Anteprima partecipante nel medesimo editor senza uscire né salvare forzatamente: riceve la bozza corrente. Pulsante nativo «Tutto schermo» e navigazione locale che non invia risposte.
- Editor, anteprima, proiezione e vista partecipante usano posizionamenti percentuali su un piano 16:9. Rimossi i reflow impliciti che alteravano le coordinate su mobile; le vecchie regole `!important` sono superate dai dati posizionali salvati.
- Font, colore, dimensioni, allineamento e stili del widget vengono applicati in modo scalabile rispetto alla larghezza della pagina.
- Doppio clic: modifica titolo e opzioni direttamente nel widget. Menu contestuale per aggiungere opzioni (max 12). La palette offre font, grandezza, colore e allineamenti.
- Aggiunta formattazione persistente per intervalli selezionati di titolo/opzioni tramite `textMarks`, validata dall'API su testo semplice (non HTML né CSS arbitrario). I tooltip delle palette hanno entrambi forma rettangolare.
- Nuovo preflight Chromium della geometria reale su desktop 1440px e mobile 390px, incluso nel job browser opt-in.

## Verifiche eseguite localmente

- `npm run build`: TypeScript backend/frontend e build Vite **PASS**.
- `npm run test`: **454/454 PASS**.
- Test Node frontend: **38/38 PASS**.
- Test Python di contratto mirati: **26/26 PASS**.
- `python tools/ci_widget_visual_geometry_20261028.py`: **PASS** a 1440 e 390 px con Chromium reale, senza network.
- Suite Python integrale: timeout nell'ambiente locale, **non certificata**.

## Attività residue reali

La conferma finale del rendering pagina per pagina, su Firefox/WebKit, touch fisico, screen reader, proiezione e backend PostgreSQL resta aperta. L'editing di testo con formattazione a intervalli è memorizzato/renderizzato, ma il campo nativo in fase di digitazione non disegna ancora gli stili dei singoli caratteri: occorre un vero editor WYSIWYG inline. L'aggiunta di opzioni è implementata, non ancora la gestione di più domande distinte nello stesso widget. L'uso in scala 16:9 sui telefoni deve essere valutato per accessibilità e interazione.

**Score RC = 53,0%** (1 gate accepted, 17 partial). A1–A4 non promossi: evidenze locali non equivalgono a Full CI e approvazione indipendente. La release candidate **non è pronta**.
