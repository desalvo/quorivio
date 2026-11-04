# Quorivio RC170 — Fedeltà numerazione footer smartphone e schemi

## Problema riprodotto

Il numero della pagina usa sul desktop unità `cqw` con base logica 1280 px. La stessa dimensione veniva applicata erroneamente sul documento smartphone da 390 px, rendendola minuscola; inoltre un override CSS imponeva margini diversi (5 px anteprima e 10 px sessione reale), ignorava le impostazioni utente e riportava al bordo i numeri posizionati manualmente.

## Modifica applicativa

- La funzione `SlideCanvasNumber` conserva font e padding desktop in `cqw`, ma fornisce anche font e padding smartphone in pixel logici tramite tre proprietà CSS dedicate.
- CSS comune a editor smartphone, anteprima interattiva smartphone e URL partecipante; rispetto rigoroso degli spostamenti personalizzati `footerNumberX/Y` senza imporre margini fissi.
- L'editor della pagina legge il footer ereditato dallo schema per la sola sovraimpressione del numero, senza trasformare il widget ereditato in widget locale e senza cambiare il comportamento dell'editor degli schemi.
- Il layout desktop 16:9 e il numero nella proiezione presentatore mantengono il precedente ridimensionamento relativo alla larghezza del canvas.

## Verifiche

- Test Node RC170: presenza del numero ereditato, priorità della scelta locale, persistenza delle unità desktop.
- Test Python RC170: preflight e mutazioni negative sui parametri, sui margini manuali e sulla CI.
- Chromium reale: due viewport (390 e 1440), tre superfici, numeri da 14 e 23 px, margini 5/5 e 17/13 px, posizionamento libero a coordinate relative; confronto delle geometrie senza credenziali e senza server esterno.
- L'accettazione browser su PostgreSQL è stata estesa per verificare anche numero 14 px e margini 5 px nella URL reale; andrà confermata in GitHub Actions.

**Stato certificato:** 85,25% (43 gate accettati, 17 parziali). La build TypeScript/Vite completa e il collaudo autenticato RC170 richiedono ancora la CI GitHub. Nessun commit/push/tag/deploy.
