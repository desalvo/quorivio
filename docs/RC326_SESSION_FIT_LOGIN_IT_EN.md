# Quorivio RC326 — Session viewer, responsive widgets, manual-cover login

## Italiano

- **Chiudi sessione** nella barra laterale chiude solo la sessione nell'editor/dashboard: non cambia lo stato server, non termina la presentazione, non disconnette i partecipanti. **Termina** resta un comando esplicito nella dashboard live.
- **Apertura sessioni:** il client anticipa il caricamento di uno snapshot autorizzato quando “Apri sessione” riceve hover/focus/touch. Il click riusa la richiesta pendente anziché duplicare lo stesso endpoint per ricavare i permessi. Una copia in sola memoria, vincolata all'identità dell'utente, permette la vista immediata per pochi secondi mentre il server riconferma i permessi; gli snapshot non vengono salvati nel browser storage. In caso di revoca, la verifica server invalida il dato. La schermata di caricamento appare solo oltre 550 ms.
- **Formato widget — Adatta automaticamente il contenuto alla dimensione del widget** è abilitato in modo predefinito e scala come gruppo testi, grafici, legende, opzioni, conteggi e simboli vero/falso. Vengono misurate le dimensioni naturali, inclusi tutti i risultati configurati e gli spazi per percentuali e contrassegni; ResizeObserver e MutationObserver ricalcolano il rapporto dopo modifiche del contenuto o delle dimensioni. La disattivazione esplicita consente ancora lo scroll. Ridimensionare il rettangolo o cambiare il font non disattiva più l'adattamento. Rimossa l'operazione separata “Adatta automaticamente l'altezza al contenuto”: la geometria dell'elemento non varia automaticamente.
- **Login:** lo sfondo usa /docs/assets/quorivio-manual-cover.png, già distribuito come copertina nei manuali Quorivio, con sovrapposizione scura per contrasto e layout responsive; nessuna risorsa esterna.
- **Verifica:** test TypeScript di regressione e controllo visivo Chromium; merge solo dopo CI verde. Completamento RC ufficiale invariato: 85,25%, 43 gate accettati, 17 parziali.

## English

- **Close session** in the sidebar leaves the current dashboard only. It never posts a closed state or interrupts the live presentation/participants. **End** remains a separate explicit action.
- **Fast opening:** authenticated prefetch starts on hover/focus/touch, shares the pending request with selection and offers a short-lived per-user in-memory preview. The server revalidates access; no session snapshot is written to disk. The loading panel only appears after 550 ms.
- **Widget formatting:** proportional automatic fitting is enabled by default and scales text, charts, legends, counts and truth badges as a group. Natural and anticipated content geometry is remeasured on resize and live data changes. Editing widget bounds/fonts does not disable fitting. Remove the redundant auto-height checkbox; leave widget geometry untouched.
- **Login background:** reuse the original manual cover asset, dark contrast overlay, responsive mobile layout, and no third-party resources.
- **Validation:** TypeScript regressions and Chromium CI, followed by gated multiarch Docker images once green. Official RC readiness unchanged.
