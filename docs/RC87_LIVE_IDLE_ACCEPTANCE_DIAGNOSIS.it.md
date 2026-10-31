# Quorivio RC87 — collaudo idle live a fase indipendente

**Origine:** `logs_111783956906.zip`, CI estesa RC86. Il test `ci_live_idle_snapshots.py` ha fallito dopo 70 s per il presentatore. Il precedente collaudo Chromium della palette e il test PostgreSQL WebSocket A↔B erano invece verdi.

## Problema verificato

L'API usa una scansione globale con periodo 20 s a partire dall'avvio del processo. Il test precedente richiedeva uno snapshot dopo 35 e uno dopo 55 secondi *dall'apertura del socket*, senza sincronizzare la fase con il timer del server. Ad esempio un flusso valido a 0/14/34/54 s supera il vincolo di massimo 25 s fra consegne, ma fallisce la soglia artificiale di 55 s. Il test simulato RC87 riproduce esattamente il falso negativo.

## Correzione e garanzie mantenute

La prova di 70 s richiede almeno 3 snapshot autoritativi, almeno uno nell'intervallo finale di 40 s e almeno uno nell'intervallo finale di 20 s; resta **obbligatoria** la ricezione di snapshot validi entro 25 s, il controllo ID sessione e l'assenza di dati privati nel flusso partecipante. Il test non modifica il trasporto, non simula messaggi nella prova reale e non rende verde alcun gate senza CI. In caso di fallimento la diagnostica indica soltanto i tempi relativi di ricezione, mai cookie, URL o dati di sessione.

Regressioni: fase 14/34/54, fase 19/39/59 e rifiuto di un flusso senza aggiornamenti finali. La suite è eseguita nel workflow prima della prova reale dopo l'installazione di aiohttp. Inventari precedenti preservati, RC87 corrente; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**Completamento certificato invariato: 84,75%** (42 gate accettati, 17 parziali). RC strict non certificata; nessuna pubblicazione automatica.
