# RC241 — Formato risultati, parità smartphone e controlli numerici

Base: cumulativo RC240; ultima full CI integrata confermata verde RC239.

- I testi delle risposte della widget risultati condividono lo stesso stile anche sull'ultima parola; il badge del conteggio resta separato. Ogni opzione di risposta può avere font, dimensione, colore, grassetto, corsivo e decorazioni indipendenti, nella scheda Testo di Formato widget.
- La disposizione smartphone automatica delle domande elimina 40px di riserva superflua per l'intestazione quando sono presenti opzioni. Editor e anteprima condividono margini e coordinate logiche da 390px. Le anteprime presentatore singola/affiancata condividono una scena da 1280x720 con ridimensionamento uniforme.
- Nella barra superiore aggiunti comandi taglia, copia, incolla, informazioni, annulla e ripeti collegati a selezione, appunti e cronologia esistenti.
- Tutti i controlli numerici di Formato widget, incluse le singole opzioni dei risultati, accettano cancellazione/digitazione senza ripristino prematuro; frecce esplicite, Invio o uscita per confermare una sola volta, Escape per annullare, frecce su/giù della tastiera per incrementare.
- Test mirati e preflight CI obbligatori. Ricevuta RC240 storica immutabile. La CI integrata Chromium e TypeScript della RC241 resta da eseguire.

Flag invariati: `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Completamento certificato 85,25% (43 accettati, 17 parziali). Nessun commit/push/tag.
