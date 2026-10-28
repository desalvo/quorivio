# Quorivio 0.1.0-dev — statistica domande sul tema e revisione gate RC

**Baseline:** commit verificato `a32ef78902a656262d346a0fa622604a4deda405`; Full CI GitHub `40638652838` completamente verde, senza pubblicazione Docker.

Il widget **Risultati** può selezionare anche **Domande sul tema** sulla stessa pagina. Nuovo endpoint `GET /api/sessions/:id/activities/:aid/topic-widgets/:wid/stats`: risponde soltanto con il numero di domande ricevute, richiede autenticazione e proprietà/collaborazione alla sessione, e verifica pagina e widget. Non trasferisce al grafico né testi né nominativi degli utenti. Il test PostgreSQL 18 della CI controlla totale 10, diniego ai partecipanti e widget inesistente.

Nell'anteprima doppia il partecipante può inviare domande simulate (5–2000 caratteri, massimo 10 invii), con aggiornamento immediato dei contatori in vista presentatore e Risultati. Tutto resta nello stato temporaneo del browser, azzerabile con «Ricomincia prova».

**Test locali:** TypeScript/Vite PASS; Node backend 468/468, frontend 50/50, Python 917/917 PASS; Chromium isolato desktop/mobile 1440/390 px PASS per geometria e tooltip. Le nuove funzioni richiedono ancora Full CI autenticata/PostgreSQL reale; i test non sono collaudo fisico.

**RC 53 → 56%:** formula di score invariata. Scomposizione delle parti automatiche di A3, B2, B4 (peso 2 ciascuna) già superate in Full CI 40638652838; gate residui A3/B2/B4 restano parziali e obbligatori. 21 gate, 4 accettati, 17 parziali. Release candidate NON pronta. Non attribuire credito alle nuove statistiche finché non passano CI.

**Commit/push/tag/release/Docker:** non effettuati.
