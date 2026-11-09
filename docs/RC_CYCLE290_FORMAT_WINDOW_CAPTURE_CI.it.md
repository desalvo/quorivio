# RC290 — Collaudo screenshot della finestra Formato dopo un vero ridimensionamento

## Evidenza

La [full CI 42670034364](https://github.com/desalvo/quorivio/actions/runs/42670034364) ha superato la precedente mancanza di PyMuPDF ed è arrivata alla raccolta di immagini reali su PostgreSQL e Chromium. Sono state acquisite dieci schermate. Il test è terminato con `Widget Formatting changed outer size when switching tabs` perché confrontava le dimensioni **automatiche** del tab Testo e del tab Contenuti, senza prima ridimensionare la finestra. Il requisito richiesto è mantenere le dimensioni **impostate dopo un ridimensionamento**.

## Correzione

L'acquisitore usa ora il vero comando accessibile «Ridimensiona Formattazione rapida widget selezionato»: aumenta larghezza e altezza con Maiusc+freccia, controlla che entrambe cambino davvero, seleziona «Contenuti» e verifica che le dimensioni esplicite rimangano stabili (tolleranza 2 px). Viene acquisita anche la nuova schermata `editor-widget-format-resized`. Test negativi impediscono di saltare il resize o confrontare le misure nell'ordine sbagliato. Restano invariati React, il CSS applicativo e le protezioni delle schermate reali.

## Collaudo e limiti

La verifica end-to-end con l'app reale, i vari tipi di preview e le sessioni live resta affidata alla prossima full CI. Nessuna modifica runtime e nessun avanzamento percentuale arbitrario: **85,25%** (43 accettati, 17 parziali), `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag.
