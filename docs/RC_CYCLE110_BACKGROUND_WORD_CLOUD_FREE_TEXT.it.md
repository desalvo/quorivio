# Quorivio 0.1.0-dev — RC110 — Caricamento JPG sfondi, nuvola risultati e dimensioni risposta libera (1 novembre 2026)

**Baseline:** full CI RC107 `41309042012` SUCCESS; commit `99a801ab7623347ba776b8214d054aa872ddb5c6`, pubblicazione Docker Hub completata. Le RC108–RC110 sono un cumulativo locale **da certificare in GitHub CI**.

**Caricamento sfondi:** Dal menu contestuale del canvas si apre il selettore del sistema operativo per JPEG/JPG, PNG, GIF, WebP. Il server restituisce un asset della sessione e lo carica nella libreria personale; il suo ID è immediatamente assegnato alla pagina, poi l'autosalvataggio conserva il layout. Prima il menu si chiudeva anche quando l'upload falliva perché l'errore veniva intercettato dalla funzione; ora chiude soltanto se il server risponde con successo e mostra nell'interfaccia avanzamento e mancata riuscita. Il backend continua ad applicare autorizzazione, limiti di dimensione, firma immagini e scansione antivirus. Il percorso reale con JPG, browser e PostgreSQL va ancora verificato end-to-end.

**Nuvola:** i cinque risultati più frequenti hanno colori diversi, dal sesto tutti usano lo stesso colore neutro. Ordinamento per frequenza discendente, alfabetico in caso di parità; widget risultati, grafico risultati collegato e nuvola delle domande del pubblico. Gli altri grafici conservano l'ordine originario.

**Dimensioni della risposta libera:** `answerFieldWidth` tra 25 e 100% e `answerFieldHeight` tra 48 e 400px sono configurabili dalla palette flottante e dalla finestra Proprietà widget. Stessa visualizzazione in editor, simulazione e partecipanti; le proprietà vengono validate rigorosamente nel backend. Valori predefiniti 100% e 96px; nessun cambiamento ai widget già salvati se non modificati. Autofit rimane disponibile quando c'è spazio.

**Cumulativo:** incluse RC108 (PowerPoint domande raggruppate) e RC109 (invio risposte, auto-fit, Footer monoriga). Test Node API 565/565 e frontend 157/157 superati; regressioni mirate verdi. Suite Python completa non conclusa entro il timeout; test reale browser/upload ancora da certificare. Versione `0.1.0-dev`, completamento certificato **85,25%** (43/60 gate accettati, 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o pubblicazione effettuati.

Commit cumulativo suggerito da RC107: `Export grouped question PPTX, improve editor answers and footer, and fix JPG backgrounds, cloud colors and response field sizing [full-ci]`.
