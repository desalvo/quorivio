# Quorivio 0.1.0-dev — RC221: vero/falso nei risultati e PDF parzialmente modificabili

## Baseline e ambito
Ultima campagna GitHub integralmente verde: **RC219**, [run 42197607753](https://github.com/desalvo/quorivio/actions/runs/42197607753), 14 job riusciti. RC220 non ha ancora una full CI verificata. RC221 mantiene `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Avanzamento certificato **85,25% (43 gate accettati, 17 parziali)** sino ai test integrati e all'accettazione. Nessun commit/push/tag/pubblicazione automatici.

## Widget risultati
- Se la sorgente è una domanda a scelta singola/multipla o un quiz a tempo con chiave di valutazione, compare lo switch **Evidenzia le risposte vere** sotto la widget nell'editor, nelle proprietà e sullo schermo privato del presentatore. Default disattivato. Sullo schermo del presentatore l'attivazione è temporanea; nell'editor la preferenza può essere salvata. Le opzioni vere ricevono evidenziazione verde e `✓ Vero`, senza cambiare le risposte registrate.
- In **Formato widget** ogni titolo, testo della domanda, opzione e riga statistica può avere carattere, dimensione, colore, grassetto, corsivo, sottolineato e barrato propri. Identificativi separati per sottodomande con stesse opzioni; stili persistenti e validati. La formattazione originale della sorgente rimane dove non esistono override. Le domande sono blu per default; le opzioni sono in grassetto per default.
- Le chiavi corrette non sono inviate agli snapshot dei partecipanti; le widget risultati sono escluse dalla vista partecipante. Il server accetta i nuovi campi soltanto in widget risultati e rifiuta stili CSS arbitrari.

## Modalità di importazione PDF/PPTX
- Scegli la modalità **prima della conversione**: **Come immagini** conserva la fedeltà visiva e importa le pagine nella sessione corrente; **Elementi modificabili** crea una nuova sessione con elementi supportati, in modo parziale.
- PDF editabile: il worker isolato usa Poppler (`pdftohtml -xml`) per ricostruire caselle di testo native e immagini raster estraibili come widget indipendenti. Limiti: PDF massimo 50 MiB, 200 pagine, 16 widget per pagina, 200 immagini, massimo 50 MiB di asset. Grafica vettoriale complessa, tabelle, grafici, font non supportati, annotazioni e testo di scansioni senza layer testuale **non** diventano editabili; nessun OCR. Le immagini possono essere spostate e ridimensionate, non modificate al livello dei pixel.
- Restano obbligatori autenticazione, autorizzazione, abilitazione amministrativa, token interno, worker isolato, verifica sorgente, antivirus e limiti delle risorse.

## Verifiche e passi aperti
- Preflight RC221 prima di npm: scelta modalità, isolamento, validazione testo, chiavi private, regressioni storiche. Le suite Node API/frontend, gli inventari e l'archivio ZIP con SHA-256 sono validati localmente.
- Da confermare: full CI GitHub RC221; import PDF/PPTX su worker realmente distribuito con documenti di testo, immagini, vettoriali e scansioni; controllo visivo browser con sorgenti su altre pagine; revisione delle risorse di conversione.
