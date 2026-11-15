# RC341 — Verifica reale del rendering PDF e PPTX nel converter

## Italiano

L'errore di dashboard \`Rendering della presentazione non riuscito (HTTP 502)\` indica una risposta non riuscita al download autenticato. Può derivare dal worker (HTTP 422 trasformato dall'app in 502), dal proxy oppure da problemi del deployment. La RC340 ha reso l'errore gestibile ma non ha testato il percorso reale di cattura del browser **all'interno dell'immagine converter**.

La RC341 aggiunge nel job \`image-build\` una prova **obbligatoria e fail-closed** che:
1. estrae il bundle React compilato dalla **stessa immagine app** destinata alla pubblicazione;
2. avvia **la stessa immagine converter**, senza privilegi, con root filesystem in sola lettura, memoria e CPU limitate e directory isolata;
3. usa un server HTTP esclusivamente in loopback con uno snapshot sintetico di 3 pagine, tra cui una pagina partecipante nascosta al presentatore e mappata a una pagina visibile;
4. verifica il token di accesso alla definizione e il blocco delle altre richieste API;
5. richiede al worker le quattro combinazioni PPTX/PDF per presentatore/partecipante;
6. controlla i documenti generati dentro il container rispettando il permesso 0600, inclusi il numero di slide, le immagini OOXML, l'intestazione PDF e il trailer PDF;
7. pulisce i dati temporanei. Nessun account, sessione utente, accesso Internet o segreto di produzione.

Questo test **non sostituisce** un export autenticato completo contro PostgreSQL reale, né gli eventi/log del deployment \`quorivio.apps.desalvo.eu\`. Lo smoke RC339 su staging resta opt-in. L'esito delle build/CI verrà verificato prima di qualsiasi pubblicazione.

Per classificare il guasto reale, verificare dopo un tentativo i soli log tecnici (senza cookie/token/dati personali):

    kubectl -n <namespace> logs <nome-pod> -c converter --since=5m
    kubectl -n <namespace> logs <nome-pod> -c quorivio --since=5m
    kubectl -n <namespace> describe pod <nome-pod>

La percentuale di prontezza RC indipendente rimane 85,25%.

## English

RC341 introduces mandatory real converter-image Chromium/LibreOffice smoke using the actual compiled web bundle for presenter/participant PDF and PPTX exports. A synthetic local-only test fixture exercises both formats and both views, checks final document integrity, and preserves private per-job paths and token checks. The test is not a substitute for PostgreSQL-authenticated staging acceptance or production logs. The reported 502 remains unconfirmed as resolved on the live installation. Independent RC readiness stays 85.25%.

### Esito del primo collaudo RC341

La CI [43762696511](https://github.com/desalvo/quorivio/actions/runs/43762696511) ha correttamente bloccato il rilascio: Chromium nel converter reale si è chiuso in fase `launch` con eccezione `TargetClosedError`, generando HTTP 422. La causa compatibile è l'ambiente HOME/XDG non scrivibile in presenza di `readOnlyRootFilesystem`; la RC341 alloca quindi un HOME/profilo Chromium privato per job su `/tmp`, escludendo le credenziali del worker dalle variabili passate al browser. Anche il default HOME dell'immagine converter è ora `/tmp`, scrivibile mediante tmpfs. **È una correzione da ricollaudare:** non rappresenta ancora una prova di risoluzione sul sito reale.

English: The first mandatory image test failed at Chromium browser startup (`TargetClosedError`). RC341 now uses a per-job writable HOME/XDG environment with a credential-free browser environment and a writable converter HOME under the existing /tmp mount. These changes require rerunning the same fail-closed image test.
