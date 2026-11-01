# Quorivio 0.1.0-dev — RC109 — risposte, adattamento widget e Footer monoriga (1 novembre 2026)

**Baseline:** full CI RC107 `41309042012` SUCCESS, commit `99a801ab7623347ba776b8214d054aa872ddb5c6`, immagine Docker Hub pubblicata. Gli sviluppi RC108 e RC109 sono cumulativi locali e **non ancora certificati dalla CI GitHub**.

**Editor:** per Domanda, Quiz a tempo e Domande del pubblico appare già nel canvas il pulsante di invio (anteprima non interattiva), anche nelle domande annidate. Testo delle risposte e opzioni possono avere carattere, dimensione, colore, grassetto e corsivo indipendenti; la dimensione del pulsante (12–40 px) è modificabile dalla palette flottante o dalle proprietà. Le stesse proprietà sono usate nella vista partecipante e nella simulazione. Tutti i nuovi campi sono validati dal backend.

**Adattamento automatico:** i widget testuali e interattivi crescono per far entrare i contenuti dopo le modifiche, senza oltrepassare il canvas 16:9 o spostare altre widget. Un resize manuale disattiva il comportamento solo per quella widget; nelle Proprietà si può riattivarlo. In presenza di collisioni o spazio insufficiente il ridimensionamento viene rifiutato: è necessario intervenire sul layout.

**Footer:** i nuovi Footer sono una sola fascia alta 7% da y=93%, con titolo della sessione centrato, sfondo trasparente, separatore superiore sottile e numerazione indipendente ancorata a 10 px dagli angoli inferiori. Posizioni personalizzate già salvate non sono alterate e la normalizzazione legacy rimane supportata.

**Cumulativo:** incluso anche RC108 con esportazione PowerPoint di gruppi di domande e relativo testo formattato senza chiavi di risposta.

**Verifiche locali:** 565/565 API Node, 154/154 frontend Node, test Python mirati RC109 e regressioni storiche Footer superati. Browser completo e full CI GitHub ancora da confermare.

**Completamento certificato invariato:** 85,25% (43 gate accettati, 17 parziali su 60). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag/pubblicazione dell'assistente. Commit cumulativo da RC107: `Export grouped questions to PPTX and improve editor answers, auto-fit and slide footers [full-ci]`.
