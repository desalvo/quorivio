# RC108 — esportazione PowerPoint dei quiz a domande multiple

L'esportazione nativa scrive ora tutti i testi delle domande del widget, incluse fino a cinque domande indipendenti, le descrizioni e le opzioni. Gli intervalli di stile rimangono editabili per ciascun campo, con gestione degli indici UTF-16. Il contenuto può essere modificato in PowerPoint come testo nativo.

**Limite funzionale deliberato:** il PPTX rimane una **presentazione statica**. Non contiene informazioni sulle risposte corrette, voti, dati dei partecipanti o credenziali; importarlo in Quorivio recupera testo editabile, ma non la logica del quiz. Conservare una definizione di sessione privata per eventuale ripristino interattivo.

Le domande malformate, i riferimenti ai campi di stile non presenti e i contenuti oltre quota sono respinti senza troncare silenziosamente il documento. Verificare la leggibilità su Office reale, la stampa e i dispositivi prima della RC definitiva. Nove regressioni PowerPoint sono inserite nella CI dopo l'installazione delle dipendenze. Baseline RC107: full CI `41309042012` verde, nuova RC108 ancora da verificare in GitHub. Completamento certificato 85,25% invariato; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
