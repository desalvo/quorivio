# Quorivio 0.1.0-dev — Autosalvataggio resiliente e geometria condivisa (27 ottobre 2026)

## Baseline e progresso verificabile

- Baseline GitHub confermata dall'utente: `67a7be939a5930e2f9a49ce3932a4b7f29a682ac`.
- Workflow `40553571012`: qualità, Chromium (editor/partecipanti e PostgreSQL), build container e pubblicazione riusciti. Questa prova riguarda **la baseline**, non il presente batch.
- Punteggio RC ufficiale: **53,0%**, senza promozioni non giustificate. Il report richiede ancora accettazioni indipendenti per A1–A4 e altre aree.

## Modifiche apportate, dopo il commit

1. L'autosalvataggio distingue errori di trasporto da errori applicativi; prima di ogni eventuale ripetizione consulta PostgreSQL tramite GET autorevole.
2. Se un PATCH è stato confermato dal database ma la risposta è andata persa, la revisione viene riconosciuta dal server e il client **non ripete** la scrittura.
3. Il retry automatico è limitato a tre tentativi con backoff fino a 6,5 secondi, soltanto dopo avere verificato che la revisione server non sia cambiata.
4. Se il server risulta avanzato ma il contenuto diverge, si blocca il salvataggio e si apre la riconciliazione, preservando la bozza.
5. L'identità dei retry include sessione corrente, pagina e firma della bozza, così le operazioni non vengono trasferite a un'altra pagina.
6. La geometria CSS percentuale è condivisa dall'editor, dalla proiezione presentatore e dalla pagina di partecipazione. La fedeltà visiva **pixel per pixel** resta da validare con dati reali.
7. Il Chromium con API simulate simula due perdite di trasporto consecutive (prima del commit, dopo il commit) e verifica una sola scrittura finale. La prova PostgreSQL reale non utilizza intercettazioni e resta obbligatoria.
8. Aggiunto al quality gate un passo obbligatorio con i test TypeScript del frontend per recupero e geometria.

## Verifiche locali

- Python completa: **842/842 PASS** (ambiente con `PYTHONPATH=tools`).
- Node backend: **447/447 PASS**.
- Node frontend: **12/12 PASS**.
- Parsing TypeScript/TSX (3 sorgenti): **PASS**.
- Sintassi browser Python: **PASS**.
- Build integrale Vite e il nuovo test Chromium completo con PostgreSQL: **da eseguire su GitHub Actions**.

## Blocchi RC ancora aperti

Il consolidamento di A1/A3 richiede esecuzione integrata Chromium con i nuovi scenari, prove browser e dispositivi indipendenti, confronto visivo editor/proiezione e verifica manuale di accessibilità. Non si considera pronto il rilascio né si converte un test isolato in sign-off.

**Regola Git:** nessun commit, push, tag o rilascio automatico; suggerire messaggio monoriga cumulativo dal commit sopra.
