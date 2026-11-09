# RC285 — Sessioni portabili dalla sidebar

## Workflow presentatore

1. Aprire una sessione. Nella sidebar, **Sessione aperta → Esporta in locale (.quo)**. Il download genera un file nella cartella configurata dal browser; eventuali errori JSON non vengono salvati come archivi.
2. Nella sidebar scegliere **Importa da locale (.quo)**, disponibile anche dalla dashboard senza sessione aperta, e selezionare il file.
3. Il server verifica archivio, dimensioni, contenuto, hash SHA-256 e antivirus. Una riuscita importazione genera una **nuova sessione bozza** con identificativi univoci e nuovo codice di accesso. La sorgente resta intatta.
4. Verificare pagine, schemi, allegati e collegamenti alle domande di altre pagine prima di presentare.

## Confini di portabilità e privacy

L’archivio include *tutta la libreria privata della sessione*, anche asset non referenziati in pagine o schemi. Non include file caricati dai partecipanti, risposte, voti, dati personali, statistiche, codici di accesso e segreti. Non è un backup completo dell'istanza o un export statistico. Restrizioni: massimo 300 file multimediali, 80 MiB media e 100 MiB archivio. Backup amministrativi necessari per DR. Il workflow non usa storage locale persistente del browser, ma un normale download e un file picker.

**CI:** test regressione prima di npm e prova PostgreSQL HTTP che importa in due copie differenti anche un asset non usato, assicurandone rimappatura e conservazione. I precedenti check RC284 e i controlli del formato ZIP rimangono attivi.
