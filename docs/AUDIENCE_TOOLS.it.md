# Nuvola di parole e Q&A moderato — Quorivio 0.1.0-dev

Le nuove API consentono a partecipanti già entrati tramite cookie tecnico di inviare una parola o una domanda durante un'attività aperta. Il limite è di una parola per attività e tre domande per attività e partecipante. Le domande sono inizialmente in attesa di moderazione e non sono pubbliche.

Il presentatore può ottenere una frequenza aggregata delle parole, consultare le domande e approvarle o rifiutarle. Solo le domande approvate appaiono alla pagina del partecipante; ogni partecipante può votare ogni domanda una volta.

Endpoint: `POST /api/join/:code/activities/:aid/words`, `POST /api/join/:code/activities/:aid/questions`, `GET /api/join/:code/activities/:aid/questions`, `POST /api/join/:code/activities/:aid/questions/:qid/upvote`, `GET /api/sessions/:id/activities/:aid/words`, `GET /api/sessions/:id/activities/:aid/questions`, `PATCH /api/sessions/:id/activities/:aid/questions/:qid`.

Le tabelle PostgreSQL sono `audience_words`, `audience_questions` e `audience_question_votes`. I contenuti sono dati potenzialmente personali, soggetti a moderazione, privacy e retention. I test reali PostgreSQL/browser/concorrenza restano da eseguire.
