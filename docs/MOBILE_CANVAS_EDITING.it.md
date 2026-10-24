# Editor grafico su smartphone — coordinate e accessibilità

L'editor mantiene il sistema di coordinate 16:9 usato per la persistenza e per
l'import/export PowerPoint anche sotto 480 px di viewport. In precedenza la
regola mobile forzava i widget a `position:relative`, dimensioni 100% e
rotazione nulla, mentre il motore pointer continuava a scrivere coordinate
assolute: trascinamenti e ridimensionamenti non erano quindi fedeli.

Adesso, su schermi piccoli, il canvas editor resta un artboard largo almeno 600
px, scorrevole orizzontalmente. Widget, coordinate e rotazioni rimangono
inalterati. È disponibile anche l'elenco di controlli accessibili per spostare,
duplicare e cambiare i livelli dei widget senza trascinamento. **Non** è un
collaudo su dispositivo fisico. La visualizzazione dei partecipanti può invece
riorganizzare le risposte in colonna per la leggibilità.

## Verifiche residue

- Su iPhone/Android, provare scroll del canvas, drag, resize e rotazione;
  confrontare la geometria salvata prima e dopo la modifica.
- Provare tastiera virtuale, zoom del browser e screen reader.
- Eseguire build TypeScript/Vite pulita; nel workspace locale manca una
  dipendenza npm in cache (`@types/bcryptjs`) e non è stato generato un lockfile.
