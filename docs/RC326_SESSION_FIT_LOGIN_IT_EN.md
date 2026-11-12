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

## RC327 — Adattamento proporzionale senza fuoriuscite / Overflow-safe proportional fitting

**IT:** Corretto il caso limite in cui testi e risultati molto lunghi superavano il riquadro perché una scala minima rigida impediva di ridurli ulteriormente. Ora la scala non supera mai il rapporto consentito da larghezza e altezza, compreso lo spazio previsto per tutti i risultati; quando lo spazio è maggiore non esiste un tetto di ingrandimento predefinito. Un eventuale limite massimo esplicito resta rispettato. L'aumento del contenuto applica immediatamente una riduzione della scala, senza toccare la geometria salvata del widget. Le opzioni manuali con adattamento disabilitato restano inalterate.

**EN:** Fixed a boundary case where very long text or results could escape a widget because an unconditional minimum scale prevented further shrinkage. Proportional sizing now honors both dimensions, including predicted result rows, and uses available space without a default enlargement ceiling; a specifically requested maximum is still supported. Growing content forces an immediate downscale, while authored widget geometry and explicit scroll mode remain unchanged.

**Validazione / Verification:** Node/TypeScript regressions for extreme text, predicted rows, optional caps and live-size changes; full PR CI must pass before merge or Docker publication. The official RC sign-off remains **85.25% (43 accepted, 17 partial)** pending external checks.

## RC328 — Righe su più linee, Formato widget e spazio verticale / Multiline results and balanced use of widget height

**IT:** In «Formato widget → Contenuti» è disponibile la stessa opzione persistente «Adatta automaticamente il contenuto alla dimensione del widget», già presente nelle proprietà del widget risultati (e per gli altri widget di contenuto idonei). Il risultato non forza più la larghezza di ogni risposta al testo completo: le etichette lunghe vanno a capo all'interno della larghezza disponibile, mantenendo insieme l'ultima parola e il conteggio. Il grafico a torta resta leggibile e limitato, mentre le righe si distribuiscono nell'altezza residua. L'algoritmo anticipa solo le righe selezionate per la visualizzazione, senza riservare righe invisibili o ricontare quelle già renderizzate. Lo scaling proporzionale del gruppo resta applicato soltanto quando necessario e non cambia la geometria salvata. Modalità manuale con scroll invariata.

**EN:** «Widget formatting → Content» exposes the very same persisted automatic-fit option as the results inspector (and other eligible content widgets). Long answers wrap within the available width instead of forcing a full-line max-content width; the last word and its count remain together. Pie charts stay readable and bounded while answer rows distribute across unused widget height. Predictive measurement considers only selected visible rows and avoids double-counting those already rendered. The authored widget rectangle is unchanged, and explicit scroll mode remains available.

**Acceptance:** compare exact long-option fixture in editor, rehearsal/preview, live presenter and mobile; verify no tiny corner layout, clipping or unwanted nested scroll. The official RC readiness remains **85.25%** until independent sign-off.

## RC329 — Visibilità dei tab delle impostazioni server / Server settings tab visibility

**IT:** Nella pagina **Impostazioni server** (amministratore di piattaforma), i sette tab **Generale, Autenticazione, Posta elettronica, Spazio disco, Convertitore, Backup, Audit** ricevono ora colori di sfondo/testo espliciti e un bordo visibile. La barra usa una tinta blu scuro, ogni tab inattivo un blu contrastato e quello selezionato un verde petrolio con testo bianco. Hover, focus tastiera e selezione rimangono distinguibili; altezza minima 44px e scorrimento orizzontale su smartphone. La correzione è limitata a questi tab e non modifica configurazioni, permessi o salvataggi.

**EN:** All seven platform server-settings tabs now have explicit visible backgrounds, borders and WCAG-AA text contrast in unselected, hovered and selected states. The dark tab rail harmonizes with the dashboard, the selected tab is teal, the keyboard focus ring remains visible and mobile users can scroll horizontally to access every tab. No authentication, permission or settings persistence logic changed.

**Verifica / Validation:** Node tests check the tab/panel contracts and contrast values; an opt-in Chromium fixture uses the actual production CSS at narrow and desktop widths to inspect rendered button visibility, text contrast and horizontal scrolling. RC acceptance score unchanged pending sign-off.
