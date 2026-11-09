# RC286 — Portabilità `.quo`, miniature complete, menu contestuali e manuali visuali

## Modifiche all'applicazione

- La nuova estensione **`.quo`** sostituisce completamente il vecchio suffisso degli archivi portabili di sessione, nelle rotte HTTP `/api/sessions/:id/export.quo` e `/api/sessions/import.quo`, download, file picker, documentazione e test. Il nome MIME `application/vnd.quorivio.session+zip` mantiene l'identità del produttore e **non** costituisce una vecchia estensione. I percorsi temporanei privati `.quorivio-*` non sono archivi di sessione.
- L'area **Allegati della sessione** nella dashboard usa un elemento nativo `details/summary` **chiuso per impostazione predefinita**, con contatore e controlli accessibili da tastiera e touch.
- Le miniature delle pagine riflettono testo, opzioni della domanda, timer, forme, linee, logo/immagine, reazioni, rating, elementi di presentazione e grafici schematici. La miniatura della pagina attiva segue lo stato del draft non ancora salvato. In assenza di risposte non vengono simulati valori di statistiche reali.
- I menu contestuali dei widget vengono portati nel visual viewport con posizionamento CSS `fixed`, altezza limitata e scrolling proprio; wheel/touch scroll non li chiudono. Le configurazioni V/F utilizzano testo compattato nel menu, mentre la spiegazione completa resta nelle Proprietà.

## Documentazione e acquisizione prove

- Sei PDF IT/EN rigenerati, 247 pagine totali in RC286, con nuovi workflow su editor, schemi, anteprime, sessioni live, backup/DR/scaling, `.quo` e partecipazione mobile.
- Sei diagrammi originali con forme e frecce; due inserti fotografici sintetici esplicitamente etichettati. Screenshot autentici precedentemente verificati presenti come immagini con provenienza **di release**, senza identificativo di commit stampato nel manuale.
- La pipeline Chromium è stata estesa per acquisire una galleria più ampia sul *sistema reale* temporaneo con PostgreSQL: miniature, menu contestuale, editor schemi, quattro anteprime, schermo live, allegati collassati/aperti e telefono 16:9. Hash SHA-256 e commit continuano a essere conservati nel manifest tecnico **non stampato** nel PDF.
- Le schermate aggiuntive saranno verificabili end-to-end solo dalla nuova full CI. Non è stata inventata alcuna nuova schermata spacciata per reale.

## Validazione e limiti

- Suite locale web: 473 test superati. API: 652 test superati. Contratti RC286 dedicati superati. La build npm completa, l'acquisizione Chromium estesa e la full CI RC286 sono **da verificare**.
- La percentuale funzionale resta 85,25%, in attesa di nuovi gate di accettazione completi. Nessun commit, push, tag o rilascio è eseguito dall'assistente.
