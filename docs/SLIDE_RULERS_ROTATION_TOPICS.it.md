# Editor slide, anteprima e domande per argomento — 0.1.0-dev

## Canvas e rotazione

La dashboard della sessione permette di aprire l'editor delle pagine. Ogni pagina usa una superficie bianca 16:9 con righelli percentuali sopra e a sinistra. Il widget si sposta trascinandolo dal corpo, si ridimensiona dai bordi e si ruota con la maniglia circolare sopra il bordo superiore. Posizione, dimensioni e rotazione (da -360 a +360 gradi) sono salvate nel layout. La vista a schermo intero è disponibile dall'editor. Le pagine possono essere riordinate nella barra delle slide.

## Schermi mobili

La pagina live usa coordinate percentuali sui browser ampi; fino a 700 pixel di larghezza, i widget si dispongono verticalmente per preservare leggibilità e interazioni. La rotazione viene rimossa nella vista mobile, ma i valori salvati rimangono disponibili su desktop. Da verificare con browser e dispositivi reali, soprattutto video e sovrapposizioni.

## Anteprima del presentatore

La dashboard espone un'anteprima incorporata e un collegamento separato allo schermo pubblico con le statistiche della pagina attiva. Questa anteprima utilizza lo stato reale della sessione; la precedente prova partecipante rimane invece isolata, senza inviare risposte.

## Widget «Domande sul tema»

Dalla toolbox aggiungi `topic-question` più volte sulla stessa slide. Ogni widget mantiene la propria lista di domande, indipendente dai quiz. Ogni partecipante può inviare fino a dieci domande per widget, ciascuna di 5–2000 caratteri. Dalla pagina del presentatore le domande sono elencate per widget e paginabili a **10 per pagina**, con aggiornamento periodico. L'opzione «Mostra nickname al presentatore» è facoltativa, disabilitata per impostazione predefinita. L'indirizzo email non viene mostrato.

## Limitazioni aperte

Il browser, la migrazione PostgreSQL su istanza esistente e l'accessibilità mediante tecnologia assistiva richiedono ancora test integrati. La lista argomenti si aggiorna ogni 5 secondi; non sono ancora implementati moderazione e archiviazione per singola domanda tematica né un'anteprima delle statistiche storiche indipendente dalla pagina attiva. Il modello mobile è reflow e non mantiene la geometria esatta delle slide desktop.
