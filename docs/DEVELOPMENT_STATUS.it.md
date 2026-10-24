## 2026-10-24 — Identità widget live e integrità risultati
- Rifiutati identificativi widget duplicati o assenti prima del confronto delle definizioni di quiz temporizzati aperti: in precedenza la mappa poteva sovrascrivere un widget senza segnalare l'ambiguità.
- La proiezione delle word cloud scarta etichette vuote o troppo lunghe provenienti da dati storici malformati.
- Verifiche: build produzione API e frontend PASS, 154/154 Node PASS, 252/252 Python PASS (più 10 sottotest). Due test Node aggiunti.
- Mancano prove reali PostgreSQL/browser/500 partecipanti; gate B1–B4 parziali, punteggio RC 40,0%. NON è una release candidate.

## 2026-10-24 — Scadenze quiz uniformate all’orologio PostgreSQL
- Quiz temporizzati tradizionali e widget temporizzati usano entrambi `clock_timestamp()` di PostgreSQL; eliminata la dipendenza dall’orologio del nodo API per scadenze e tempi della classifica. La policy condivisa verifica apertura, durata e limite esatto.
- Build backend e frontend/Vite PASS; 146/146 test Node PASS. Test Python verificati dopo l’aggiornamento dei controlli di contratto.
- Non eseguiti collaudi HTTP PostgreSQL, browser, multi-replica e 500 partecipanti. B2 parziale, RC 40,0%; nessun nuovo gate accettato.

## 2026-10-24 — Portable archive defensive validation follow-up (after RC load audit)
- Strict canonical UUID-shape validation now rejects malformed asset identifiers both on manifest export/import and during fresh-ID remapping.
- Manifest is limited to 2 MiB **before compression on export** and before ZIP deflate inflation on import; this prevents a disproportionate allocation from a forged central directory uncompressed-length field. Existing ZIP archive and total-media quotas remain unchanged.
- Added three Node.js regressions: malformed asset UUID, oversized manifest during encode, and forged ZIP central-directory manifest length.
- Verification: 129/129 Node.js tests PASS, 232/232 Python tests PASS. Backend TypeScript compilation PASS; frontend TypeScript checking PASS. The full Vite bundling in this cycle is BLOCKED by mismatched esbuild binary versions/platform in the reused npm dependency archive (nested esbuild JS 0.25.12, root available native binary 0.28.2); this is an environment blocker, not a verified product build failure. Earlier CI-green baseline is not invalidated by this local issue.
- No real PostgreSQL, SMTP/SSO, browser/mobile, 500-client load or Kubernetes tests were run. RC gate statuses and weighted progress remain 40.0%. The product is NOT release-candidate complete.

## 2026-10-24 — 500-user shard validation follow-up (after previous local cycle)
- Aggiunta la riconciliazione offline dei report del carico da 500 utenti con otto test e controlli rigorosi della topologia. Nessun carico reale eseguito; D4 resta aperto.
- Verifica locale: build backend/frontend PASS (esbuild Vite 0.25.12), Node 126/126 PASS, Python 232/232 PASS. Punteggio RC invariato al 40,0%; non eseguiti test PostgreSQL, carico reale, browser o cluster.

## 2026-10-24 — Ciclo integrato portabilità, MFA email verificata e amministrazione (post baseline CI confermata)
- Nuovi UUID e copia effettiva dei media nelle importazioni e duplicazioni; verifiche MIME/hash/AV e rollback; iscrizione email MFA verificata e indipendente da TOTP; configurazione amministrativa atomica e foto private senza condizioni di gara.
- Build API/frontend PASS, 126 test Node e 224 test Python PASS. Aggiunto smoke HTTP PostgreSQL CI **non ancora eseguito**; rigenerati sei manuali PDF IT/EN.
- RC 40,0% ponderato (C2 solo parziale), test browser/database reali/cluster aperti; **non è RC**. Dettagli: `docs/RC_CYCLE_2026-10-24.it.md`, `docs/RC_GATE_MATRIX.json`.

## 2026-10-24 — Correzione CI dopo commit confermato (verifica locale)
- Il log GitHub Actions `logs_108675600015.zip` fallisce in `apps/web/src/main.tsx:394` con TS2657 (pulsanti JSX adiacenti senza elemento genitore). Corretto racchiudendoli in un fragment React; nessuna modifica ad API o funzionalità.
- Usando le dipendenze complete Node 22 fornite dall’utente: `npm run build` OK (API TypeScript e web TypeScript/Vite); `npm test` OK (121 test); unittest Python OK (224 test).
- La CI con PostgreSQL, i test di integrazione, Kubernetes, browser, deploy e audit sicurezza non sono stati eseguiti su questa revisione. Stato gate RC: 37,5%; il package non è una release candidate.
- L’utente ha confermato il commit del cumulativo precedente: il nuovo commit suggerito riguarda soltanto la correzione JSX e le note di verifica.

## 2026-10-24 — Ciclo unificato: recupero modificabile delle celle delle tabelle PPTX (verifiche locali)
- Le tabelle PowerPoint importano ora il testo delle celle come widget indipendenti modificabili, mantenendo le coordinate proporzionali e il limite di 16 widget per pagina.
- La diagnostica conta celle importate e celle scartate; la struttura tabellare nativa (bordi, stili, fusioni e OOXML) rimane esplicitamente **non conservata**.
- Test locali: **220/220 Python, 120/120 Node.js**. Build completa tentata ma bloccata dalle tipizzazioni npm non installate nell'ambiente; nessuna nuova certificazione CI.
- **Rimangono sviluppi software**, non soltanto collaudi: PowerPoint complesso, MFA/SSO, flussi live, integrazione browser, portabilità tra istanze, build pulita, sicurezza e GDPR. Matrice RC invariata al 37,5%; non è una RC.

## 2026-10-24 — Verifica media PPTX e coerenza del rapporto di fedeltà (locale)
- L'importazione PPTX controlla anche la firma effettiva di PNG/JPEG, oltre al MIME dichiarato e alla dimensione; un media con tipo dichiarato non corrispondente non viene registrato come immagine modificabile.
- Il rapporto di fedeltà applica lo stesso ordine degli oggetti, il limite di 16 widget per pagina, il limite di 200 asset, il budget dei file e la deduplicazione dell'importatore.
- Test di regressione su firme non coerenti e su 18 caselle di testo. Verifiche locali: 218 test Python e 116 Node.js superati. La precedente CI era verde secondo l'utente, ma questa revisione non ha subito build completa o deployment.
- **NON COMPLETO:** restano gruppi/grafici/SmartArt/temi PPTX complessi, conclusione MFA e accettazione browser mobile. Avanzamento RC ponderato invariato al 37,5%.

## 2026-10-24 — Consolidamento accessibilità e descrizioni PowerPoint (verifica locale)
- Migliorati focus da tastiera, movimento ridotto, alto contrasto, target touch mobile e descrizione import PPTX. Python 216/216, Node 116/116. Build completa/browser/Kubernetes non verificati; RC 37,5%. Vedi docs/LOCAL_COMPLETION_AUDIT.it.md.

## 2026-10-24 — Gesti touch del canvas mobile (verifica locale)
- Corretto un conflitto CSS: sui telefoni `touch-action: manipulation` prevaleva sulla cattura dei Pointer Events durante trascinamento, ridimensionamento e rotazione. L’override è limitato all’editor e non altera i moduli dei partecipanti.
- Rimossi dal canvas mobile un’altezza minima e uno scorrimento interno in conflitto con la geometria 16:9 e lo scorrimento del contenitore esterno.
- Test: 213 Python e 116 Node superati. Build completa, test su dispositivi touch e Kubernetes da verificare. RC invariata al 37,5%.
- Aperti: accettazione editor/mobile, oggetti PPTX complessi, rifiniture MFA, workflow live, build riproducibile e audit sicurezza.

## 2026-10-24 — Isolamento dell’editor tra pagine (verifica locale)
- Il canvas ora è identificato dalla sessione e dalla pagina selezionata: selezione, editing e menu contestuali non persistono erroneamente passando a un’altra pagina. Pulizia dei riferimenti ai widget rimossi.
- Test: 211 Python unittest e 116 Node.js superati. Build completa e browser non certificati; RC invariata al 37,5%.

## 2026-10-24 — Accessibilità tastiera e cancellazione widget
- Aggiunti Canc/Backspace sul widget selezionato e Esc per deselezionare; campi di testo e controlli interni non vengono intercettati. La rimozione ripulisce il pannello proprietà e il menu contestuale.
- Test locali: 207/207 Python, 116/116 Node.js. Build completa e collaudi end-to-end non verificati; RC invariata al 37,5%. Le altre macroaree restano aperte.

## 2026-10-24 — Duplicazione indipendente widget e correzione risposte quiz
- La duplicazione dei widget copia indipendentemente opzioni e geometria, seleziona la copia e mantiene coordinate non negative ai bordi del canvas.
- Il pannello quiz interpreta il vecchio campo correctOptionId quando correctOptionIds è vuoto, coerentemente con il punteggio backend.
- Aggiunti tre controlli di regressione. Build TypeScript/Vite e collaudi browser/Kubernetes non certificati; RC invariata al 37,5%.

## 2026-10-24 — Persistenza selezione canvas e pannello attività
- Corretta la selezione che veniva annullata al rilascio del puntatore: il pannello di configurazione domanda/quiz scompariva. Ora la selezione persiste dopo il rilascio, supporta clic e focus da tastiera e si azzera eliminando il widget.
- Test locali: 198/198 Python e 116/116 Node.js. Build di produzione e collaudi browser/Kubernetes ancora necessari; RC 37,5% invariata.

## 2026-10-24 — Stabilizzazione geometria editor mobile (verifica locale)
- Eliminata la regola CSS sotto 480px che sovrascriveva posizione, dimensioni e rotazione dei widget mentre il motore pointer continuava a utilizzare coordinate assolute.
- L'editor mobile mantiene il canvas 16:9, scorrevole orizzontalmente e largo almeno 600px, senza alterare la geometria salvata; la vista partecipante può invece adattarsi verticalmente.
- Aggiunti due test di regressione: **195/195 Python** e **116/116 Node.js** superati.
- Tentata installazione npm offline: **bloccata** da `@types/bcryptjs` non disponibile nella cache. Non dichiarare riuscite build TypeScript/Vite o verifiche browser.
- **Ancora aperti**: collaudi mobile/accessibilità, PowerPoint complesso, widget live, MFA, lockfile, benchmark e accettazione Kubernetes. Matrice RC invariata al 37,5%; sviluppo globale non concluso.

## 2026-10-24 — Coerenza del salvataggio asincrono dell'editor (verifica locale)
- Impediti salvataggi sovrapposti e cambi di pagina mentre è in corso un salvataggio.
- La versione segnata come salvata corrisponde esattamente ai dati inviati al server, non alle modifiche effettuate successivamente. Le modifiche ulteriori restano indicate come non salvate.
- Aggiunta la scorciatoia Ctrl/Cmd+S nell'editor e disabilitato il pulsante Salva durante la richiesta.
- Test: 190/190 Python unittest e 113/113 Node.js. Build TypeScript/Vite completa e collaudi browser/Kubernetes non eseguiti. RC invariata al 37,5%.
- **Ancora aperti:** fedeltà agli oggetti PowerPoint complessi, formato portabile con asset, prove mobile end-to-end, installazione npm riproducibile, benchmark 500 utenti e accettazione dei gate RC. Nessuna dichiarazione di completamento del software.

## 2026-10-23 — Selezione pagine editor e comandi per sessioni chiuse
- Dopo la duplicazione viene selezionata automaticamente la nuova pagina confrontando gli ID degli snapshot; le miniature supportano frecce e Home/Fine; i comandi di modifica pagine sono disabilitati per sessioni chiuse.
- Tre test di regressione aggiunti. Build completa, collaudi browser e Kubernetes pendenti. RC invariata al 37,5%.

## 2026-10-23 — Editor pagine dedicato e correzione ciclo di vita
- Corretto `internal_error` durante la creazione di una pagina vuota: la query SQL aveva cinque parametri ma riceveva solo quattro valori.
- Aggiunto endpoint DELETE autorizzato e transazionale: azzeramento della pagina corrente quando necessario, compattazione degli ordinamenti e notifica ai client. **La cancellazione elimina anche le risposte associate**.
- Nuovo workspace editor a schermo intero con miniature verticali, riordino drag-and-drop o tramite pulsanti, creazione, duplicazione e cancellazione pagine e barra widget orizzontale. Il pulsante principale apre ora l'editor.
- Test locali: 177 Python e 113 Node superati; build completa e collaudi browser/Kubernetes non rieseguiti. RC invariata al 37,5%.

## 2026-10-23 — Forme decorative PPTX native modificabili
- Rettangoli, rettangoli arrotondati, ellissi e triangoli senza testo sono importati come widget `postit` modificabili, conservando colori RGB supportati, geometria e rotazione. In esportazione sono nuovamente forme native PowerPoint. Il rapporto di fedeltà conteggia separatamente le forme decorative.
- Test locali: 174/174 Python e 113/113 Node.js; collaudi browser/Kubernetes non effettuati. Restano aperte altre forme vettoriali, grafici e temi. RC al 37,5%.


## Hotfix CI — 23/10/2026

Run GitHub Actions 108461560295: build backend/frontend superata; suite Python fallita per dipendenze CI mancanti python-pptx e aiohttp (16 errori import, 3 fallimenti CLI). Il workflow installa e verifica tali dipendenze prima dei test; il simulatore valida gli argomenti prima di importare aiohttp. Suite Python locale: 171/171 superati. Riesecuzione GitHub Actions ancora da effettuare; RC invariata al 37,5%.

## 2026-10-23 — Conversione nativa delle forme rettangolari PowerPoint (test locali)
- I rettangoli e rettangoli arrotondati PowerPoint con testo sono importati come widget Quorivio `postit` modificabili; le normali caselle di testo restano widget `text`.
- L'esportazione dei widget `postit` produce un rettangolo PPTX nativo modificabile. Testo, geometria, stile testuale e rotazione usano il percorso di conversione esistente.
- Limiti di fedeltà: riempimenti, bordi, raggio degli angoli, gruppi e forme vettoriali senza testo non sono conservati. I rettangoli arrotondati vengono esportati come rettangoli normali. Supporto alle forme ancora parziale.
- Test locali: **171/171 Python**, **113/113 Node.js**, compreso un nuovo test di round-trip delle forme. Build TypeScript/Vite completa e collaudi browser/Kubernetes non verificati. RC ponderata invariata al **37,5%**.

## 2026-10-23 — Esportazione immagini PPTX (solo validazione locale)
- Completato il percorso di esportazione PPTX per widget immagine/logo: il backend autenticato prepara solamente gli asset PNG/JPEG della sessione effettivamente referenziati, verificando proprietà, numero massimo 200, 10 MiB per immagine, 50 MiB complessivi, dimensioni e SHA-256.
- Il convertitore isolato ripristina le immagini con geometria e rotazione nel PowerPoint. Riferimenti mancanti o non autorizzati provocano un errore esplicito. Rimane la rappresentazione statica delle attività interattive nel PPTX.
- Test locali: 165/165 Python, 112/112 Node. Build completa TypeScript/Vite e collaudi browser/PostgreSQL/Kubernetes NON verificati. RC invariata al 37,5%; aperti SmartArt, grafici, animazioni, temi e formati vettoriali.

## 2026-10-23 — PPTX embedded pictures as session image widgets (local validation)
- Editable PPTX browser imports now extract supported embedded PNG/JPEG pictures in the isolated worker as separate widget images, with original editable geometry and rotation. Media is placed in conversion scratch space, never exposed through portable JSON as binary data.
- During new-session creation the API checks declared asset IDs, MIME types, per-file and aggregate size bounds, count, SHA-256 and widget references; stores files under the new session and registers corresponding session_assets in the same PostgreSQL transaction. Failed imports roll back the database and remove the new session directory.
- The worker limit is 200 imported images / 50 MiB in total, each image <=10 MiB. Unsupported formats, images beyond the supported widget cap, grouped graphics, SmartArt and PPTX image export remain open. JSON Quorivio export still needs an asset-inclusive portable bundle for full media portability; static PPTX export currently omits image widgets.
- Local tests: 158 Python unittest and 111 Node.js tests passed, including new embedded picture extraction and updated fidelity report regression. Production TypeScript build and browser/PostgreSQL/Kubernetes integration NOT validated. RC 37.5% unchanged pending acceptance.

## 23 ottobre 2026 — Aggregazione difensiva delle statistiche widget (verifica locale)
- Rafforzati i risultati per revisione contro revisioni storiche non valide e payload di risposta malformati. Sono esposte soltanto revisioni intere positive sicure; ogni opzione valida viene conteggiata una sola volta tramite proprietà JavaScript proprie e sicure (anche per nomi riservati). Valori non testuali di risposta e allegato ignorati. Nessuna modifica allo schema o al contratto API.
- Aggiunto test Node di regressione per revisioni non valide, identificativi non ammessi e payload incompleti. Verifiche locali: **147/147 Python unittest**, **111/111 Node.js** superati.
- **Blocco build chiarito:** il package non include `package-lock.json` né shrinkwrap, quindi `npm ci --offline` non è eseguibile; nell'ambiente non sono installate le dipendenze di build. Build di produzione e test E2E browser/PostgreSQL/Kubernetes **non verificati**. Generare e versionare il lockfile in un ambiente fidato con accesso alle dipendenze, quindi `npm ci && npm run build`.
- Percentuale RC ponderata **37,5% invariata** finché non vengono validati i gate. Residui: E2E widget, live multi-replica, MFA/foto profilo e documenti non PDF.

## 2026-10-23 — Aggregazione sicura delle risposte widget (test locali)
- Corretti i conteggi per identificativi speciali (`__proto__`, `constructor`) e per identificativi ripetuti nelle risposte storiche. Ogni opzione viene conteggiata al massimo una volta per risposta; nessuna modifica API o migrazione.
- Verifiche: 147 test Python superati; 110 test Node.js superati (nuovo test di regressione). Installazione npm non completata nell'ambiente; build completa, PostgreSQL reale, browser e Kubernetes **non collaudati**.
- Avanzamento RC ponderato invariato al **37,5%**, in attesa dei gate di accettazione.

## 2026-10-23 — Controllo finale scadenza risposte dei quiz a tempo (test locali)
- Corretto il controllo della scadenza con una lettura aggiornata di `clock_timestamp()` PostgreSQL subito prima dell'inserimento della risposta, dopo le verifiche dell'allegato e della revisione. Lo stesso riferimento temporale calcola il tempo per le classifiche. API e schema invariati.
- Verifiche: **147/147 test Python** e **109/109 test Node.js** superati. Installazione delle dipendenze npm non completata (timeout), quindi build TypeScript/Vite **non validata**. Mancano i collaudi reali PostgreSQL, browser e Kubernetes.
- Avanzamento RC ponderato **37,5% invariato**. Residui: test temporali e multi-replica reali e gli altri gate di accettazione.

## 2026-10-23 — Compatibilità delle risposte corrette dei widget quiz (verifica locale)
- Risolta una divergenza tra validazione e punteggio: i widget quiz a risposta singola con il precedente `correctOptionId` e `correctOptionIds` vuoto utilizzano ora coerentemente la chiave precedente. La risposta multipla richiede `correctOptionIds`; vengono rifiutate chiavi duplicate prima della registrazione.
- Unica logica di risoluzione per convalida e punteggio, senza migrazioni DB/API. Aggiunti test di regressione.
- Verifiche locali: pytest Python **160 superati + 7 subtest**, Node.js **107 superati**. Build di produzione tentata, bloccata dalle tipizzazioni Node assenti (TS2580). Collaudi browser, PostgreSQL e Kubernetes non eseguiti. **RC ponderata invariata al 37,5%.**
- Residui: E2E browser dell'editor e delle risposte, live multi-replica, MFA, foto profilo e altri gate RC.

## 2026-10-23 — Creazione pagine dalla dashboard tramite widget
- Unificata la creazione delle pagine nei comandi della sezione Pagine, eliminando il modulo di creazione duplicato dall’interfaccia. API e modifica dei dati legacy conservate per compatibilità. Aggiornati messaggi e test; collaudo browser ancora necessario.
- Verifica: 158 test pytest superati (+7 subtest), 107 test Node superati; build bloccata dai tipi Node non disponibili (TS2580). Nessun collaudo browser/PostgreSQL/Kubernetes.
- RC: 37.5% unchanged pending production and Kubernetes acceptance.

## 2026-10-23 — Controllo transazionale invio risposte dei widget (verifica locale)
- Corretta la condizione di concorrenza tra controllo iniziale del partecipante e inserimento della risposta. La transazione blocca e ricontrolla sessione attiva e non scaduta, pagina corrente, permessi di partecipazione anonima e attività aperta prima di registrare la risposta.
- Lock sulla sessione prima del lock sull'attività, coerentemente con le transizioni del presentatore. Nessuna migrazione o nuova API; le risposte storiche restano intatte.
- Verifiche: pytest 156 superati (+7 subtest), Node 107 superati. Build tentata ma bloccata dalle tipizzazioni @types/node non installate (TS2580 Buffer). Collaudi browser, PostgreSQL reale, Kubernetes e multi-replica non eseguiti. RC invariata al 37,5%.
- Residui: completamento attività esclusivamente tramite widget, prove live nel browser, MFA/foto profilo, documenti non PDF e altri gate RC.

## 2026-10-23 — Rendering dei widget multimediali nella proiezione (verifica locale)
- Sostituiti i segnaposto con sole etichette nello schermo del presentatore: immagini, loghi, video e PDF utilizzano ora gli asset della sessione (immagine, video controllabile, visualizzatore/link PDF). In assenza di asset compare un messaggio non ambiguo. Geometria, timer e stati live mantenuti; nessuna migrazione o modifica API.
- Aggiunti CSS per il contenimento dei media e test di regressione su URL codificati, formati supportati e link sicuri.
- Verifiche: **142 test Python**, **107 test Node** superati; `npm run build` **bloccata** per tipizzazioni Node non installate (`TS2580 Buffer`). Collaudi browser, PostgreSQL, Kubernetes **non eseguiti**. RC ponderata **37,5%** invariata.
- Residui: collaudo autorizzazioni e visibilità degli asset in browser, attività esclusivamente tramite widget, documenti non PDF, sincronizzazione su più repliche, MFA e foto profilo.

## 23 ottobre 2026 — Creazione pagine vuote direttamente nel canvas (verifica locale)
- Aggiunto `POST /api/sessions/:id/pages` autenticato per creare una slide vuota nella sequenza, con validazione titolo, permessi presentatore, blocco sessioni chiuse, transazione e ordinamento. Riutilizza il layout JSONB esistente, senza migrazioni.
- Nella sezione Pagine è presente **Nuova pagina vuota · Editor widget**: la pagina viene selezionata e si apre direttamente l'editor canvas. Il modulo quiz/sondaggio preesistente resta disponibile per compatibilità; creazione completamente basata su widget NON ancora terminata.
- Test: Python **144 superati** (+7 subtest), Node.js **107 superati**. Collaudi E2E browser/PostgreSQL/Kubernetes ancora pendenti. RC ponderata **37,5%** invariata.
- Residui: quiz/sondaggi interamente configurabili nei widget, build completa, verifica live, MFA/foto profilo e documenti oltre PDF.

## 2026-10-23 — Apertura diretta editor dopo la creazione di una pagina (verifica locale)
- Dopo la creazione di una pagina interattiva, l'interfaccia conserva l'identificativo restituito dall'API, ricarica la sessione, seleziona la scheda Pagine e carica la pagina appena creata nell'editor dei widget. Non è più necessaria una selezione manuale aggiuntiva.
- L'API di creazione attività rimane compatibile. Il modulo iniziale di sondaggio/quiz **non è ancora interamente sostituito** dalla creazione esclusiva tramite widget: questa macroarea rimane aperta. Nessuna migrazione.
- Verifiche: **141 test pytest** superati (più 7 subtest), **107/107 test Node**. Build completa **bloccata** da dipendenze e definizioni Node TypeScript mancanti; nessun collaudo E2E browser, PostgreSQL o Kubernetes. RC ponderata ancora **37,5%**.
- Da completare: flusso di creazione esclusivamente tramite widget, sincronizzazione reale presentatore/partecipanti e ulteriori gate di accettazione.

## 2026-10-23 — Chiusura pagina live e sicurezza snapshot partecipanti (verifica locale)
- La chiusura di una pagina pubblicata azzera `sessions.current_activity_id` nella stessa transazione, con lock sulla sessione, e notifica i client. Si evita così che una pagina chiusa rimanga selezionata sullo schermo pubblico.
- Gli snapshot WebSocket dei partecipanti includono pagina/risultati solo con sessione attiva e attività effettivamente aperta. In pausa, chiusura o assenza di pagina restituiscono liste vuote; gli snapshot del proprietario restano completi. Nessuna migrazione database.
- Verifica: pytest Python **139 superati** (più 7 subtest), Node **107/107**, con tre controlli di regressione nuovi. Build e collaudi E2E Kubernetes/browser/PostgreSQL ancora non verificati. RC invariata **37,5%**.
- Restano: collaudi reali apertura/chiusura/ripresa con due browser e broadcast multi-replica Kubernetes; attività solo widget, documenti extra PDF, MFA e foto profilo.

## 2026-10-23 — Stati della proiezione e comandi sessione (verifica locale)
- Corretto lo schermo presentatore per distinguere sessione **non avviata**, **attiva senza pagina pubblicata**, **in pausa** e **terminata**. Prima una sessione attiva senza pagina poteva mostrare un'area vuota, mentre la pausa continuava a mostrare l'ultima pagina senza indicazione.
- Aggiunta spiegazione nella dashboard: Avvia non pubblica automaticamente una pagina, che deve essere aperta nella sezione Pagine e contenuti. I comandi in pausa indicano che le nuove risposte sono bloccate dalle API. Endpoint e schema invariati.
- Verifiche: **136/136 Python**, **107/107 Node.js** superati, inclusi tre test di regressione sul ciclo di vita della proiezione. Non certificati build completa, browser, PostgreSQL o Kubernetes end-to-end.
- Restano aperti collaudi live e ripresa dei partecipanti, menu contestuali posizionati al puntatore, altri documenti e attivita' basate soltanto sui widget. RC **37,5%** invariata.

## 23 ottobre 2026 — Menu contestuale nativo per sfondi del canvas vuoto (verifica locale)
- Aggiunto clic destro sullo **spazio vuoto del canvas** per scegliere immagini dalla libreria, caricare con autenticazione o rimuovere uno sfondo caricato; il salvataggio del layout resta esplicito. I menu contestuali dei widget sono indipendenti; i controlli espandibili per pagina e risultati rimangono accessibili da tastiera.
- Riutilizzati stato `questionBackgroundAsset`, upload e PATCH del layout: nessuna nuova API o migrazione. Il menu è posizionato nel canvas e non ancora alle coordinate esatte del puntatore.
- Verifiche: Python 133/133 e Node.js 107/107 superati. Build di produzione tentata, BLOCCATA dall'assenza di tipi Node/dipendenze workspace. Nessun collaudo browser, PostgreSQL o Kubernetes. RC **37,5%** invariata.
- Aperti: menu contestuale specifico dei risultati, altri documenti, attività solo tramite widget, sincronizzazione live e verifiche browser.

## 2026-10-23 — Controlli contestuali per sfondi pagina/risultati (verifica locale)
- Introdotti menu espandibili accessibili da tastiera per selezionare asset, caricare immagini con autenticazione e rimuovere separatamente gli sfondi delle pagine e dei risultati. Conservati i controlli precedenti.
- Corretto un difetto di persistenza: l'URL svuotato viene ora rimosso esplicitamente dal layout, senza mantenere quello precedente nel merge PATCH. Il salvataggio resta esplicito.
- Test: Python 130/130 e Node.js 107/107 superati. Build di produzione tentata ma bloccata dalle dipendenze/tipizzazioni Node non installate. Nessun collaudo reale browser, PostgreSQL o Kubernetes; RC sempre al 37,5%.
- DA FARE: clic destro sullo sfondo vuoto del canvas (i nuovi menu sono espandibili, non menu al puntatore), altri documenti, sincronizzazione presentazione live e attività soltanto tramite widget. Nessuna migrazione DB.

## 23 ottobre 2026 — Selezione contestuale dei media del canvas (solo verifica locale)
- I menu contestuali dei widget Immagine, Logo, Video e PDF consentono selezione di asset già caricati e upload autenticato. La scelta aggiorna `assetId` nello stesso layout, da salvare esplicitamente; nessuna nuova API pubblica.
- Filtro MIME per tipo widget, riuso di `uploadWidgetMedia`, input disabilitato durante gli upload. Proprietà esistenti e comandi di livello conservati.
- Test Python 127/127 e Node.js 107/107 PASS. Build completa tentata ma BLOCCATA per dipendenze e tipi Node non presenti; nessun collaudo browser/Kubernetes. RC ponderata invariata al 37,5%.
- APERTI: documenti oltre PDF, sfondo tramite menu contestuale, rendering e sincronizzazione live, attività solo tramite widget, E2E editor/UI; convalidare upload e selettori nel deployment.

## 2026-10-23 — Azioni contestuali widget canvas (verifica locale; RC in sospeso)
- Aggiunti menu da clic destro e pulsante accessibile anche a touch/tastiera: duplicazione, livelli, modifica titolo ed eliminazione. Schema dei widget invariato.
- Test Python 126/126 e Node.js 107/107 superati. Build frontend bloccata dalle dipendenze `vite/client` assenti. Da verificare in browser/Kubernetes e da completare il selettore media contestuale. RC invariata al 37,5%.

## 2026-10-23 — Estensione widget multimediali (test locali, collaudo Kubernetes pendente)
- Aggiunti alla palette dell'editor i widget separati Logo e PDF oltre a Immagine e Video; riutilizzate libreria file e API di caricamento private. Associazione di immagini ai loghi e PDF ai documenti con selezione o upload diretto.
- Rafforzata la convalida dei layout: ogni widget multimediale richiede un asset UUID; al salvataggio il server verifica appartenenza alla sessione, origine del file dal presentatore e corrispondenza del MIME. Accesso pubblico limitato alla pagina corrente di una sessione attiva. PDF esposto come collegamento; altri formati documentali non ancora supportati.
- Test locali: Python 124/124 e Node 107/107; build TypeScript/Vite completa non disponibile (mancano le definizioni vite/client). Restano i collaudi reali browser/PostgreSQL/Kubernetes.
- Aperti: sfondi caricati per pagina con consegna pubblica sicura, documenti oltre PDF, menu contestuale sul canvas, rendering media completo sullo schermo presentatore. Nessuna nuova macroarea/gate RC validata; avanzamento ponderato invariato 37,5%.

## 2026-10-23 — Consolidamento UI delle date sessione (collaudo locale)
- Le date della sessione hanno ora data, ora iniziale, durata e fuso IANA esplicito; controlli per timezone, duplicati e ordinamento. Importazione opzionale delle vecchie date prive di orario; API e dati legacy conservati, editor parallelo eliminato.
- Test contrattuali in `tools/tests/test_session_dates_consolidation.py`. Collaudo browser/PostgreSQL/Kubernetes ancora aperto. RC ponderata invariata: 37,5%.

## 23 ottobre 2026 — Navigazione sessioni a pagina intera e layout dashboard (accettazione parziale)
- Vista Nuova sessione, Apri sessione e Calendario separate; dashboard sostituisce il selettore dopo la scelta. Accesso esplicito alle pagine, etichette date sessione e risultati più chiare, adattamento responsive e fix pulsante Termina.
- Test locali Python 118/118 e Node 107/107 PASS; build completa/browser/K8s non verificati. Widget multimediali avanzati e dati legacy ancora da completare. RC 37,5% invariata. Dettagli: `SESSION_NAVIGATION_REWORK.it.md`.

## 23 ottobre 2026 — Ciclo MFA multi-metodo, calendario e volume asset Kubernetes (locale, non committato)
- Dopo la verifica delle credenziali primarie, il login restituisce una sfida MFA PostgreSQL di cinque minuti. TOTP oppure email sono alternativi; il codice email viene inviato solo a scelta esplicita, e TOTP o codice di recupero consumano la sfida monouso con lock e limite tentativi.
- Interfaccia separata per il secondo fattore. Rimossi i campi TOTP/recupero dal login iniziale. La configurazione email non richiede un codice TOTP già attivo.
- Salvataggio nickname/ruolo/approvazione accorpato (rimane un controllo rapido separato per lo stato di approvazione). Nuovo calendario giorno/settimana/mese con dati e API esistenti.
- Aggiunti fsGroup=1000 e OnRootMismatch ai pod applicativi Kubernetes/Helm per consentire l'accesso al volume degli asset da utente non privilegiato: causa possibile ma NON ancora confermata del bug foto. Sostituzione foto elimina il vecchio file privato.
- SSO: provider OIDC letti dalla configurazione ambientale. Un elenco vuoto non dimostra un bug; servono parametri OAuth/OIDC reali per il test.
- Test: Python 115/115 PASS; Node 107/107 PASS con stripping TypeScript sperimentale. Build completa BLOCCATA dall'installazione npm (idealTree/timeout); verifica sintattica con compilatore globale priva di errori TS1xxx, ma dipendenze React/Node non installate. Nessun E2E PostgreSQL/browser/K8s; RC resta 37,5%.
- APERTI: controllo MFA generale, validazione del possesso dell'indirizzo email, prova upload foto sul cluster e antivirus, test visuali responsive, atomicità del salvataggio admin e accettazione end-to-end. Non dichiarare RC.


## 23 ottobre 2026 — Correzione CI per generazione credenziali Kubernetes (non committata)
- Run CI 108303599236: 115 test Python e conversione PDF superati; fallimento nel vecchio confronto `diff -ru /tmp/q-a /tmp/q-b`, perché due nuove installazioni devono generare password differenti.
- Il nuovo `tools/check_k8s_generation.py` rigenera nella medesima directory e confronta le impronte SHA-256 dei file; verifica credenziali diverse tra installazioni indipendenti, permessi riservati e assenza di segreti nell'output CI.
- Verifiche locali: controllo dedicato PASS, suite Python 115/115 PASS. La CI GitHub va rieseguita; non si dichiarano verificati i job successivi al gate fallito.
- Baseline: commit del cumulativo credenziali Kubernetes confermato dall'utente. Il prossimo commit comprende soltanto questa correzione. Versione 0.1.0-dev invariata.

## K8s wizard credentials — 2026-10-23
2026-10-23: il wizard Kubernetes genera credenziali PostgreSQL interne, admin e AUTH_SECRET riutilizzabili, salva override/Secret con permessi 0600 e richiede una password nota per DB esterno. Vedi K8S_SECRETS.it.md. Collaudo reale ancora aperto.

## 2026-10-23 — Kubernetes test deployment and image correction (uncommitted after latest confirmed green CI)
- Default application image corrected to `desalvo/quorivio:latest` in Compose/Kustomize/Helm/CI; Helm converter image reference renamed to `desalvo/quorivio-converter:0.1.0-dev` (registry availability not confirmed).
- Wizard supports TLS termination without a named ingress TLS secret (controller default certificate required), explicit TLS disable, and independent app/PostgreSQL pod node selectors. Helm supports optional TLS secret and shared pod nodeSelector.
- Verifiche: 111/111 Python, 107/107 Node.js, build di produzione backend/frontend PASS e parsing YAML Kustomize. Helm non disponibile; cluster Kubernetes reale e pubblicazione registry non verificati. See `K8S_TEST_DEPLOYMENT.en.md` / `.it.md`. GitHub not changed; new maintainer commit and CI required before deploying. Version unchanged 0.1.0-dev.


## 2026-10-23 — Verifica editor con Chromium: blocco di accesso al server locale
- Chromium 144 e Python Playwright disponibili e avviabili; il browser gestito dall'ambiente blocca le navigazioni verso il server Vite su 127.0.0.1 (`ERR_BLOCKED_BY_ADMINISTRATOR`). Non è stato eseguito alcun E2E browser né PostgreSQL (server non disponibile).
- Correzione: i campi input dentro i widget non avviano più trascinamenti accidentali; la perdita della cattura del puntatore annulla il gesto e ripristina la geometria precedente. Aggiornati i test di regressione.
- Build backend/frontend superate; Node 107/107, Python 104/104. I gate RC rimangono al 37,5% secondo matrice, senza promuovere test sorgente ad accettazione browser.

## 2026-10-23 — Stabilizzazione gesti editor (ciclo 3, parziale)
Rotazione incrementale con orientamento preservato, rollback della geometria su pointercancel, cleanup su perdita pointer capture, touch-action dei widget. Build backend/frontend superate; Node suite e 102 test Python superati. Collaudi browser, touch, PostgreSQL e accessibilità assistiva non eseguiti. RC 37,5% invariato secondo matrice; editor non ancora validato E2E. Vedi EDITOR_STABILIZATION.it.md.


## 2026-10-23 — Editor responsive e controlli accessibili (ciclo 2)
- Aggiunto pannello alternativo ai gesti del canvas per ogni widget: spostamento del 5% sui due assi, duplicazione e gestione dei livelli con controlli touch da almeno 44px e nomi accessibili.
- Layout adattivo e focus visibile. Persistenza tramite i metodi widget già esistenti, senza modifiche al database.
- Build backend e frontend superate, 107 test Node e 99 Python superati. Non verificati: dispositivi fisici, screen reader, PostgreSQL E2E. Il gate RC resta 37,5% e l'editor non è ancora accettato end-to-end.

## 23/10/2026 — Ciclo accorpato composizione editor (non committato)
- Aggiunti griglia opzionale 5%, duplicazione widget con nuovo ID e gestione livelli avanti/dietro nel canvas 16:9; salvataggio e tastiera esistenti preservati.
- Node 107/107, Python 99/99 con tre test statici, build TypeScript/Vite PASS; browser/DB E2E non eseguiti. Nessun gate RC chiuso: matrice ponderata **37,5%** invariata. Vedere `EDITOR_COMPOSITION.it.md`.
- Ultimo commit confermato: baseline CI verde prima dei risultati configurabili. Nessuna operazione git.

## 2026-10-23 — Correzione sincronizzazione slide partecipanti (parziale)
La pagina attiva ricevuta via WebSocket viene scelta usando `current_activity_id` dal server e lo stato open, non più la prima attività. Build di produzione PASS, Node 107/107 e Python 96/96. E2E browser/PostgreSQL ancora aperti; RC invariata al 37,5%. Vedere `AUDIENCE_PAGE_SYNC.it.md`.

## 2026-10-23 — Nuvola dei risultati per widget (parziale)

Aggiunta vista Nuvola per le frequenze delle opzioni di ogni widget domanda, con conteggi espliciti e revisioni distinte. Non è una nuvola delle parole delle risposte libere. Build backend/frontend e test Node PASS. Collaudi browser/PostgreSQL non eseguiti. Gate RC **37,5%** invariati; vedere `RESULT_WORD_CLOUD.it.md`.

## 2026-10-23 — Fondamenta per MFA email (NON ATTIVA)

Codici casuali a sei cifre, digest HMAC separati per utente/sfida, controllo a tempo costante, helper invio SMTP TLS e tre test. Il login non cambia: restano necessari challenge PostgreSQL monouso, scadenza, limitazione tentativi e interfaccia. **MFA email ancora APERTA**, punteggio RC invariato. Vedere `EMAIL_MFA_FOUNDATION.it.md`.

## 2026-10-23 — Verifica rigorosa Origin in scrittura

Confronto completo schema/host/porta per le API che modificano dati; compatibilità con i client senza Origin invariata. 97/97 test Node e 95/95 Python PASS; build backend TypeScript e frontend Vite PASS. E2E con browser/reverse proxy non eseguito. Vedere `docs/ORIGIN_POLICY_HARDENING.it.md`. Punteggio ponderato di accettazione RC **37,5%**, vedere `docs/RC_GATE_MATRIX.json`.

## 2026-10-23 — Ricalcolo dei gate RC (autorevole)

**RC 37,5% su evidenze ponderate, non 67%.** Vedere `docs/RC_GATE_AUDIT.it.md` e `docs/RC_GATE_MATRIX.json`. I valori precedenti del 67% sotto sono soltanto cronologia, superati da questo ricalcolo. Nessuna nuova validazione end-to-end dichiarata.

## 2026-10-23 — Verifica revoche WebSocket dei presentatori già connessi

Implementata verifica PostgreSQL ogni dieci secondi per i WebSocket già aperti dei presentatori, con chiusura per revoca, account non approvato e indisponibilità del database (fail-closed). Build API + Vite PASS, test Node 95/95, Python 93/93. E2E PostgreSQL/multi-replica NON eseguiti; MFA email e restanti gate RC aperti. Baseline gate RC invariata al 67%. Vedere `docs/LIVE_WEBSOCKET_REVOCATION.it.md`.

## 23 ottobre 2026 — Protezione quiz a tempo attivi (parziale)
- Bloccate con HTTP 409 le modifiche a risposte, durata e rimozione mentre la pagina è aperta; la geometria resta modificabile. Le modifiche successive creano una revisione. 91/91 test Node superati. Build Vite avviata ma non confermata (timeout ambiente). PostgreSQL/browser E2E da verificare. RC invariata 67%. Vedi `TIMED_WIDGET_LIVE_LOCK.it.md`.

## 23 ottobre 2026 — Quiz a tempo indipendenti per widget (parziale)
- Risposte e classifiche separate per widget, configurazione e paginazione presentatore. Build locali superate; test PostgreSQL/browser E2E mancanti. RC **67%** invariato. Vedi `TIMED_WIDGET_INDEPENDENCE.it.md`.

## 23/10/2026 — Risultati per widget domanda (parziale)
- Pannello Risultati del presentatore: aggregazioni autonome per ogni widget domanda, separate per revisione e visualizzazione scelta nell’editor (barre, torta, tabella). Build TypeScript/Vite e 90 test Node superati. Quiz a tempo multipli indipendenti ancora mancanti. Gate RC **67% invariati**. Vedere `WIDGET_RESULTS_PER_WIDGET.it.md`.

## 23/10/2026 — Quiz a tempo e Risultati per il presentatore (parziale)
- Vedi `TIMED_QUIZ_RESULTS.it.md`: attività separata e cronometro dal server, classifica protetta, nuovi widget palette e pulsante Risultati del presentatore, build frontend/backend e 90 test Node superati. **Macroarea non conclusa.** 67% invariato. Le funzioni precedenti non committate rimangono incluse nel cumulativo.

## 2026-10-23 — Recupero MFA amministrativo per utente
- Introdotto reset MFA TOTP per utente con verifica password/TOTP amministratore, protezione account principale e reset proprio, cancellazione transazionale dei segreti/codici, chiusura WebSocket, indicatore MFA e controllo UI. Il cookie di login preesistente **non è revocato**: gate sicurezza produzione aperto.
- Build sorgenti, TypeScript e Vite eseguite; 87 verifiche Node e 91 Python. Nessun test E2E PostgreSQL/browser. Vedere `ADMIN_MFA_RESET.it.md`. Gate RC ancora al **67%**.

## Stato dei gate aggiornato — 23 ottobre 2026 (ultimo cumulativo)
- **Gate RC chiusi: 67% (invariato).** La nuova anteprima geometrica e il riordino via tastiera non hanno ancora superato build/collaudo browser; la stima non è percentuale di test né idoneità alla produzione.
- Implementate miniature con fino a 24 widget, posizioni e rotazioni salvate, sfondo facoltativo; riordino Alt+frecce tramite API transazionale già esistente. Media rappresentati con simboli e non con veri fotogrammi.
- Verifiche locali: 85/85 test Node.js e 88/88 Python, inclusi 2 nuovi test statici. `npm install --offline` non riesce per assenza di `@types/bcryptjs` nella cache: build TypeScript/Vite **non eseguita** e CI recente non confermata.
- Restano aperti i gate PostgreSQL/browser/container/Kubernetes/SSO/MFA via email e amministrativa/accessibilità/sicurezza/HA. I manuali PDF sono edizioni precedenti e **non** descrivono integralmente l'interfaccia attuale. Dettagli in `SLIDE_THUMBNAILS_KEYBOARD.it.md`.
- Nessuna modifica del repository remoto; gli sviluppi successivi all'ultima CI confermata sono cumulativamente non committati.


## RC editor grouped cycle 2026-10-23 — see docs/RC_EDITOR_BATCH.en.md and .it.md
## 2026-10-23 — Phase 2 field-validation follow-up

See `docs/VALIDATION_PHASE2_ISSUES.it.md` / `.en.md` for completed work, unverified UI, and pending calendar/editor work.

# Stato sviluppo (IT) — 2026-10-22
Versione `0.1.0-dev`. Realizzati nei sorgenti: backend/frontend, sessioni, sondaggi/quiz iniziali, QR code, risultati WebSocket, CSV, documentazione bilingue, wizard Kubernetes con output Kustomize, workflow GitHub CI/Docker Hub. I PDF e gli asset grafici sono inclusi e consultabili nell'interfaccia. Non sono ancora verificate build npm, runtime Docker/Podman/Kubernetes, provider social/generic OIDC, cluster reali e test end-to-end. I gate di produzione sono **configurati**, non ancora eseguiti con successo sulla CI reale. Evitare di dichiarare il prodotto pronto per il traffico pubblico prima di risolvere i blocchi e verificare sicurezza, disaster recovery e carico. Si veda il file `DEVELOPMENT_STATUS.md` per il dettaglio tecnico.

**Aggiornamento:** quattro test wizard superati; generati i quattro PDF, logo, grafica copertina e relativi link applicativi. Bloccata la generazione lockfile npm nell'ambiente offline. CI di produzione configurata ma non eseguita. Testo integrale ufficiale EUPL-1.2 da incorporare prima del rilascio pubblico.

## Terzo ciclo — PostgreSQL, Ingress e GDPR (22/10/2026)

- Compose aggiornato a PostgreSQL 18.6 con percorso dati `/var/lib/postgresql`; gli upgrade major richiedono migrazione reale.
- Wizard: database interno StatefulSet/PVC o esterno senza risorse DB; cambio modalità idempotente, annotazioni ingress NGINX/HAProxy per varianti community/haproxytech.
- Deployment con Secret DATABASE_URL; credenziali e certificati devono essere forniti dall'amministratore.
- Creati registri tecnici GDPR IT/EN con lacune aperte; nessuna dichiarazione di conformità.
- Test Python wizard ampliati; build npm, test reali PostgreSQL/Kubernetes e deployment non verificati. PDF precedenti non rigenerati in questo ciclo.

## Ciclo gestione dati e partecipanti (22 ottobre 2026)

- L'utente conferma CI precedente completamente verde e commit del cumulativo precedente; queste modifiche **non sono state committate**.
- Implementati cancellazione della sessione autorizzata al proprietario, revoca con rotazione dei link e chiusura WebSocket, retention configurabile (1–3650 giorni, predefinita a 90).
- Aggiunto cleanup orario delle sessioni chiuse/scadute oltre la retention, con cancellazione PostgreSQL a cascata; riconnessione del partecipante con cookie valido senza crearne uno nuovo.
- Esportazione CSV protetta contro formula injection e nuovi test dedicati.
- Verifiche: **6/6 test Node superati**, **11/11 test wizard Kubernetes superati**. API/database reali, migrazioni, CI, Docker e conformità GDPR ancora **non verificati** in questo ciclo.
- Prossimi passi: test API PostgreSQL, sicurezza sessioni/CSRF/TLS, policy backup, eventi multi-replica, SSO e nuove attività.
- Verifica libreria: presenti 6 ZIP Quorivio, inferiori al limite di 10; nessun archivio da eliminare.

## Avanzamento — stime basate sulle evidenze (2026-10-22)

These are **engineering estimates**, NOT CI pass percentages or certifications. Each category counts toward a fixed equal-weight functional rubric (10 items) or operational-readiness rubric (10 items). Recalculate every cycle from verified functionality; do not silently promote source implementation to tested release capability.

**Completamento funzionale: 34%** (scores / 10). Rubric: core architecture 80, session lifecycle 65, participant UX 40, polls/quizzes 30, results and exports 25, advanced activity types 0, integrated presentations 0, IAM/SSO/tenancy 45, documentation 35, operations tooling 20 = 340 / 10. Documentation 35 refers to completeness across all required deliverables, not quality of the new manuals alone.

**Prontezza alla produzione: 36%** (355 / 10, rounded). Rubric: baseline CI 80, basic Docker runtime 70, database integration 30, Kubernetes deployment 40, auth hardening 30, GDPR controls 20, multi-replica 0, operational docs 55, disaster-recovery verification 10, production E2E/load/security verification 20. CI success was reported by the user for the **previous** cumulative archive; this new artifact has not run in GitHub Actions.

Progress bars (10 blocks):

- Features: **34%** `███░░░░░░░`
- Prontezza alla produzione: **36%** `████░░░░░░`

## Consegna corrente — UI GDPR e manuali illustrati

- Added presenter UI for editing session retention (on blur), revoking access and deleting a session with confirmation. The backend handlers already existed. UI/browser integration **not tested**.
- Added third documentation navigation link for the dedicated presenter manual (IT/EN).
- Added reproducible `tools/generate_manuals.py` PDF generator: six role-specific PDF manuals (participant, presenter, administrator × IT/EN), cover imagery, navigable table of contents, total page numbering, illustrated UI/workflow diagrams, results chart, procedures, troubleshooting, and appendices. Contents distinguish implemented vs planned features.
- Copied manuals to `apps/web/public/docs/manuals/` for delivery by web UI; frontend build not run locally (npm packages unavailable).
- Local automated regressions: 6/6 Node domain tests and 11/11 Kubernetes wizard tests passed. PDF generation and PDF page geometry inspected. User-reported previous CI green remains separate.
- Next priorities: executable CI for current package, PostgreSQL integration and frontend E2E, GDPR audit/rights workflows, SSO, activity breadth, load and Kubernetes cluster verification.


## Ciclo identità, contenuti e governance (22 ottobre 2026)

Aggiunte migrazioni additive per approvazioni, cambio password obbligatorio, pseudonimi, accesso anonimo per sessione, temi pagine, impostazioni amministrative e retention predefinita di 60 giorni dalla chiusura. Realizzati API e controlli UI preliminari per approvazione utenti, impostazioni admin e risorse media HTTPS. Ingresso autenticato, MFA, SMTP, SSO, upload asset, editor visivo e risultati personalizzati restano aperti. Credenziali admin demo 000000 solo con opt-in in sviluppo e cambio obbligatorio; non consentite in produzione. Test locali: 8/8 dominio, 11/11 wizard. Build integrale/CI/PostgreSQL reale non verificati. **Funzionalità 39%, readiness 34%** (stime; CI verde solo per commit precedente).

Ulteriori sviluppi: registrazione web, creazione/eliminazione utenti da UI admin, verifica ruolo owner WebSocket, pubblicazione opzionale dei risultati aggregati e sfondi/loghi delle sessioni. Servono test reali PostgreSQL/API/browser.

## 2026-10-22 — Collaboration, portable sessions and ingress sizes
Implementazione parziale API: collaboratori, import/export delle sole definizioni JSON, duplicazione in bozza, invalidazione con audit, modifica live e limiti ingress. 8/8 test Node, 14/14 test wizard. Backup completo DB, upload e UI ancora pendenti. CI non verificata. Stima funzionalità 43%; readiness 33%.

## 2026-10-22 — Backup offline e storage Kubernetes

- Introdotto `tools/instance_backup.py`: dump PostgreSQL + file, manifest con SHA-256, verifica e ripristino su destinazioni vuote con conferma esplicita.
- Guide operative bilingui `INSTANCE_BACKUP.it.md` e `.en.md`.
- Wizard Kubernetes: PVC asset, montaggio `/app/assets`, dimensione/access mode/StorageClass configurabili.
- Test locali: 11/11 Node, 19/19 Python. **Non eseguiti**: backup/ripristino PostgreSQL reale, build CI, browser e cluster Kubernetes.
- **Aperti**: backup da interfaccia admin, pianificazione e cifratura integrata, test disaster recovery reale, storage condiviso e validazioni di produzione.
- Le precedenti percentuali 53% e 33% restano stime storiche. Questo ciclo non dimostra un aumento verificato di almeno 10 punti percentuali.

## 22 ottobre 2026 — Immagini, layout e risposte invalidate
- Default Compose/Podman/Kubernetes: `desalvo/quorivio:latest`; pubblicazione Docker Hub aggiornata, mantenendo GitHub `desalvo/quorivio`.
- Data di riferimento persistita e modifica dei metadati durante la sessione.
- Editor dei layout specifici domanda e risultati; ancora da verificare il rendering completo in browser.
- Risposte invalidate mantenute per audit; indice univoco parziale sulle sole risposte attive per consentire un nuovo voto. Applicare prima la migrazione.
- Manuali PDF rigenerati. Test locali: 11 Node, 23 Python; verifiche PostgreSQL reali/CI/browser ancora aperte.
- Copertura funzionale precedente 55%, readiness 35%; incremento di 10 punti non verificato.


## Quiz e reazioni (22 ottobre 2026)
Modalità risposte e obbligatorietà, reazioni uniche e statistiche, controlli web iniziali. Test locali: 17 Node, 23 Python superati. PostgreSQL e browser E2E non verificati. Funzionalità 63%, readiness 35%.

2026-10-22: widget composer question-page ordering, rating 0–10 endpoints, PostgreSQL uniqueness and aggregate stats; no full browser/DB CI yet. Timer/QR placeholders. Docs build dev-20261022.

## Widget runtime e portabilità quiz — 22 ottobre 2026
- Definizioni sessione: modalità, obbligatorietà e risposte corrette multiple conservate in export/import/duplicazione.
- Widget timer con countdown e QR SVG pubblico senza privilegi.
- Test locali: 20/20 Node e 23/23 Python. Build browser e PostgreSQL reali non verificati. L'incremento richiesto del 10% non è attestabile.

### 2026-10-22 — Widget domanda indipendenti
Aggiunti endpoint di risposta per widget, tabella `widget_answers`, statistiche aggregate per il presentatore e UI partecipante con risposte singole/multiple/testo/allegato. Mancano test integrati PostgreSQL/browser, caricamento file anonimo e versionamento delle domande modificate. Funzionalità stimate 83% (da 80%); readiness invariata 35%.

## 22 ottobre 2026 — Preparazione importazione presentazioni offline
- Aggiunto `tools/import_presentation.py`: conversione PDF/PPTX in PNG con limiti e manifest SHA-256.
- Corretto un errore di quoting TypeScript nella query per l'elenco delle sessioni.
- Verifiche: 46 test Node e 27 test Python superati. Build completa e conversione PPTX reale non verificate.
- Aperti: importazione via browser, associazione alle sessioni, worker isolato, migrazioni, collaudi end-to-end.
- Copertura funzionale stimata: 89% (+1 punto); readiness produzione: 35%.


## Ciclo pagine slide — 2026-10-22

Pagine slide integrate: aggiunta di singole immagini o più PNG/JPEG/WebP dalla UI come pagine della sessione; accesso pubblico limitato alla slide corrente. Conversione PDF/PPTX ancora offline, worker isolato da realizzare. Collaudi PostgreSQL/browser pendenti. Stima funzionalità 90% (prima 89%); readiness 35%.

## 22 ottobre 2026 — Base per MFA TOTP e SMTPS
- Implementati: attivazione e conferma MFA con autenticatore, verifica al login, disattivazione con due fattori, cifratura AES-256-GCM dei segreti e interfaccia web.
- Implementati: validazione SMTP su variabili d'ambiente, controllo configurazione senza password ed email di prova su TLS con verifica del certificato.
- Test locali aggiunti su TOTP RFC 6238, finestre temporali, cifratura e configurazione email. Build npm completa, server SMTP reale, PostgreSQL e browser da verificare.
- Aperti: SSO social/generic OIDC, codici di recupero MFA, protezione contro replay e tentativi di accesso distribuiti, integrazioni produttive.

## 22/10/2026 — Recupero password
Implementati token monouso con hash SHA-256 e scadenza 20 minuti, risposta generica anti-enumerazione, invio SMTPS, limitazione richieste per IP/account, UI di recupero e revoca dei cookie preesistenti nel middleware API. TOTP rimane obbligatorio. Test superati: 57/57 Node e 27/27 Python. Mancano prove con SMTP/PostgreSQL/browser reali e sistemi multinodo. SSO ancora aperto.

## Codici di recupero MFA — 2026-10-22
Implementati dieci codici monouso con hash HMAC, consumo atomico al login, rigenerazione protetta, interfaccia web e revoca in caso di disattivazione MFA. Test locali: 60/60 Node, 27/27 Python. Da verificare: migrazione PostgreSQL, browser, SSO e sicurezza in produzione.

## 2026-10-22 — Prima integrazione SSO OpenID Connect
- Implementati OIDC configurabile Google/generic OIDC/custom, Authorization Code con PKCE, state/nonce, JWKS RS256, associazione esplicita all'account e nuovi controlli UI.
- Non si associano utenti per semplice coincidenza dell'email; l'MFA TOTP locale non viene aggirato da OIDC.
- Verifica: 64/64 test Node e 27/27 test Python. Non verificati login con provider reali, migrazioni PostgreSQL e browser.
- Aperti: GitHub e Facebook OAuth, broker OIDC/SAML, stato distribuito e step-up MFA per OIDC. Non abilitare per produzione senza collaudi.
- Stima completamento funzionale 96% (+1); production readiness 35% invariata.

## 2026-10-22 — GitHub/Facebook OAuth2
**Implementato:** avvio/callback OAuth2, cookie di stato, recupero ID immutabile, collegamento esplicito, prevenzione bypass TOTP, link UI e cinque test. **Verificato:** 69 test Node, 27 Python. **Aperto:** provider reali, stato multi-replica, PostgreSQL, build frontend e test end-to-end.

## 2026-10-22 — Riordino grafico delle pagine
- Introdotto drag-and-drop HTML5 delle pagine con API transazionale esistente; gli ID e le risposte storiche restano invariati, e rimangono i pulsanti Su/Giù da tastiera.
- Quattro nuovi test automatici sul riordino, guide `PAGE_STORYBOARD.it.md` e `.en.md` e manuali bilingui aggiornati.
- Corretto il testo obsoleto sull'importazione PDF/PPTX diretta, sperimentale e subordinata alla configurazione.
- Da collaudare: build npm, browser, PostgreSQL, concorrenza, provider OAuth reali e worker di conversione isolato.
- Stima di copertura funzionale 98% (prima 97%), readiness 35%; non equivalgono a certificazione.


## 2026-10-22 — Canvas libero dei widget (sperimentale)
- Realizzato il posizionamento percentuale, trascinamento, editing del titolo nel blocco, larghezza modificabile e rimozione individuale, con salvataggio nel layout.
- Validazione server delle coordinate e due nuovi test; regressione 71/71 Node e 27/27 Python. Parsing TS/TSX senza errori.
- Non verificati build completa, browser e PostgreSQL; assenti rilevazione collisioni, storage distribuito e worker isolato.
- Stima copertura funzionale 98% invariata, readiness 35% invariata; non dichiarare completamento totale.

## Scansione antivirus — 22 ottobre 2026
Nuovo client ClamAV INSTREAM con esito fail-closed configurabile per upload e importazioni. Test locali: 75/75 Node e 27/27 Python; scanner reale non ancora installato né collaudato. Copertura funzionale stimata 98%, prontezza produzione 35%, invariate. Per l’attivazione è necessario predisporre ClamAV e impostare QUORIVIO_AV_REQUIRED=true, CLAMAV_HOST; vedere docs/ANTIVIRUS_UPLOADS.it.md. Restano worker conversione isolato, coordinamento multi-replica, storage condiviso e collaudi integrati.

## Configurazione OIDC generica (2026-10-22)
Rimossi il precedente preset istituzionale e ogni riferimento al suo nome. Nuovi provider OIDC configurabili tramite OIDC_PROVIDERS_JSON, fino a 32, con controlli stretti e due test dedicati. Nessun provider esterno collaudato. Restano aperti worker documentale isolato, WebSocket/stato autenticazione distribuiti, storage condiviso e collaudi end-to-end. Non dichiarare completo il prodotto o pronto per la produzione.


## Managed antivirus and SSO defaults (2026-10-22)

Docker/Podman Compose now bundles a private ClamAV service and persists its signatures. Helm includes a ClamAV sidecar with fail-closed scanning. Public provider endpoints are documented for Google, GitHub and Facebook; client registrations and secrets remain operator tasks. Offline source-level tests do not constitute deployment validation. Multi-replica synchronization and isolated document conversion are still outstanding.

## 2026-10-22 — Sincronizzazione WebSocket multi-replica e persistenza asset Helm

**Implementato:** PostgreSQL LISTEN/NOTIFY per distribuire gli aggiornamenti delle sessioni, listener con riconnessione, payload UUID, PVC Helm persistente con opzione di claim esterno e wizard Kustomize con 2–20 repliche solo in presenza di storage RWX. Guide `MULTI_REPLICA_SYNC.it.md` ed `.en.md`.

**Verificato localmente:** 79 test Node, 33 test Python e controlli statici Helm. **Non verificato:** PostgreSQL reale, cluster Kubernetes, browser, build frontend completa e accesso concorrente ai media. Lo stato OAuth/OIDC e il rate limiting sono ancora locali al processo, quindi l'autenticazione multi-replica non è pronta per la produzione. Completamento funzionale stimato **98%**, readiness **35%** invariati in mancanza di prove integrate.

**Ancora da sviluppare autonomamente:** worker isolato PDF/PPTX, stato OAuth condiviso, limitazione distribuita, test E2E e rifiniture canvas. **Richiede ambiente/credenziali dell'operatore:** SSO reali, consegna SMTP e prove Docker/Kubernetes.

## 22 ottobre 2026 — Autenticazione federata e limitazione richieste distribuite

**Implementato:** gli stati temporanei SSO OIDC/GitHub/Facebook sono ora conservati in PostgreSQL e consumati atomicamente con `DELETE ... RETURNING`; callback protetti da cookie, provider e scadenza. Il rate limiting API utilizza contatori a finestra temporale condivisi in PostgreSQL (UPSERT atomico), con errore 503 se il database non è disponibile. Pulizia periodica inclusa.

**Test:** 82/82 Node e 33/33 Python superati. **Non ancora verificati:** build npm completa, migrazioni PostgreSQL reali, login con provider esterni, cluster multi-replica e conversione isolata di presentazioni.

**Restano da sviluppare:** worker isolato delle conversioni, test end-to-end e rifiniture del canvas e della gestione degli upload. Per i test finali sarà necessario predisporre servizi e credenziali nell'ambiente dell'utente. Nessuna certificazione di production readiness.

## 2026-10-22 — Worker isolato per la conversione
- Introdotto servizio container dedicato non privilegiato, dispatch interno autenticato, volume temporaneo privato, stack Compose e sidecar Helm. L’API non esegue più direttamente il convertitore.
- Test: 82 Node, 37 Python. Da collaudare container reali, PostgreSQL, browser, build completa e sicurezza; altre attività software ancora aperte.

## 22 ottobre 2026 — Verifica CI su PostgreSQL e build convertitore
- Limite recupero password migrato da mappa in memoria a contatore PostgreSQL atomico, condiviso fra repliche.
- CI: servizio temporaneo PostgreSQL 18, avvio API compilata, verifica health e pagina web, account iniziale e tabelle, rifiuto dell'accesso non autenticato.
- Aggiunta build dell'immagine convertitore in CI; scansione Trivy bloccante presente sull'immagine principale, scansione dedicata del convertitore ancora da includere.
- Nuovi test di contratto e guide `CI_INTEGRATION.it.md` e `.en.md`.
- Mancano nell'ambiente corrente le dipendenze npm e Docker: compilazione completa, test Postgres reale e pipeline remota **non sono verificati**. Il proprietario può eseguire la CI e fornire il primo log di errore. Non dichiarare il 100% né la readiness per produzione.
- Stime invariate: **98% funzionale**, **35% readiness**.


## CI 107927415489: correzione dipendenza vulnerabile (22/10/2026)
- PASS confermati: test unitari (82), compilazione frontend/backend, avvio su PostgreSQL 18, endpoint di salute, bootstrap e autorizzazioni di base.
- FAIL confermato: `npm audit` sulle dipendenze di produzione; Nodemailer 6 vulnerabile HIGH.
- Modifica: `nodemailer: ^10.2.1` e rimozione di `@types/nodemailer`, non più necessario.
- PENDENTE: nuova installazione npm, compilazione/audit in GitHub Actions e build container. **Non dichiarare la CI verde prima della riesecuzione.**
- Baseline commit: l'utente ha confermato il commit precedente; il prossimo messaggio di commit riguarda solo questa correzione e documentazione.

## Segnalazione GitGuardian sul test TOTP (22/10/2026)
- Eliminata la stringa Base32 letterale del vettore pubblico RFC 6238 dal test; vettore ricostruito a runtime e altri segreti di test generati casualmente.
- Test locali superati: 82/82 Node, 40/40 Python.
- Altri errori CI non ancora analizzati in assenza dei relativi log.
- Nessun commit o push effettuato.


## Pulizia cache Python (2026-10-22)
- Aggiunte le regole .gitignore per __pycache__/, *.py[cod], .pytest_cache/, .mypy_cache/, .ruff_cache/.
- Escluse cache e bytecode Python dal pacchetto cumulativo, mantenendo sorgenti e test.
- Le cache già tracciate da Git richiedono la rimozione dall'indice da parte del manutentore (`git rm --cached`); non serve riscrivere la cronologia.
- Ultimo commit confermato: hotfix di sicurezza Nodemailer. Modifiche successive: fixture TOTP e pulizia cache Python. Nessun commit eseguito.
- Stime invariati: 98% funzionale e 35% readiness; CI reale ancora da verificare.

## Baseline CI verde e sicurezza delle conversioni (2026-10-22)
- L'utente ha confermato commit della pulizia delle cache Python e CI verde: questa è la nuova baseline dei futuri messaggi di commit; sostituisce gli esiti CI storici riportati sopra.
- Worker isolato: rifiuto di output preesistenti e symlink, protezione da conversioni simultanee dello stesso job nella singola istanza, rilascio della prenotazione anche in caso di errore; HTTP 413 per richieste eccessive.
- CI: aggiunta scansione Trivy HIGH/CRITICAL anche per l'immagine `quorivio-converter:gate`, senza indebolire gli altri controlli.
- 3 nuovi test di regressione. Verifiche locali: 82/82 Node, 43/43 Python, eseguiti senza scrittura bytecode Python.
- Ancora da verificare nella CI reale il nuovo gate Trivy; non eseguiti collaudi browser/conversione reale/multi-pod. Il blocco anti-duplicazione è locale al worker, non un lock distribuito.
- Nessun commit, push, tag o release eseguito.

## 2026-10-22 — Prenotazione delle conversioni fra processi (non committata)
- Aggiunta prenotazione atomica `.conversion-lock` per ogni lavoro sul volume temporaneo condiviso. Impedisce doppie conversioni simultanee anche su processi/worker differenti che usano lo stesso filesystem.
- In caso di arresto improvviso il blocco rimane: verificare il job prima della rimozione manuale, evitando recuperi automatici rischiosi.
- Test di regressione su prenotazione già presente, ciclo di vita e pulizia su errore. Esito locale: 82/82 Node e 46/46 Python.
- Baseline ultimo commit confermato con CI verde (pulizia cache Python); nel package rimangono cumulativamente hardening worker e scansione Trivy. Non effettuati commit o push.
- Da verificare: nuova CI, test multi-worker su volume reale e collaudi end-to-end/deployment.

## Recupero amministrativo delle conversioni interrotte (2026-10-22, non committato)

- Aggiunto `tools/recover_conversion_lock.py`: ispezione non distruttiva predefinita e recupero esplicito solo con `--recover --workers-stopped`, dopo l'arresto di tutti i worker che montano lo stesso volume.
- Rifiuta identificativi non validi, percorsi o blocchi simbolici, prenotazioni non vuote, sorgenti ambigue e output già esistenti. Non effettua mai recuperi automatici potenzialmente concorrenti.
- Aggiunte guide operative IT/EN e sette test. Verifiche locali: **82/82 Node** e **53/53 Python**; restano i collaudi end-to-end in container, multi-worker reale, database e browser.
- Versione `0.1.0-dev`, nessun commit. Il prossimo messaggio di commit deve includere tutte le modifiche dall'ultimo commit confermato: hardening converter, Trivy, locking distribuito e recupero manuale.

## 2026-10-22 — Integrità della pubblicazione e sorgenti ambigue (non committato)
- Reject ambiguous PDF/PPTX jobs with two valid sources; require exactly one.
- Generate page manifest in private staging before atomically renaming the completed page directory into place, avoiding partially published output.
- Unit tests: 82/82 Node, 55/55 Python pass. Real image builds, multi-worker NFS/PVC semantics and browser import remain to be confirmed in CI/deployment.
- Last confirmed commit: Python cache cleanup with green CI. All converter/Trivy/recovery changes since then remain uncommitted. Version unchanged: 0.1.0-dev.

## 2026-10-22 — Ciclo integrato per verifiche release candidate (non committato)
- Aggiunti test HTTP reali del worker privato: autenticazione, conversione, rifiuto richieste errate, limite 413, stato 503 e rilascio lock.
- Rafforzato l'import PDF/PPTX: l'API verifica formato/versione manifest, tipo e SHA-256 del sorgente, ordine e posizione delle pagine, firma PNG e checksum prima della registrazione.
- CI: prerequisiti Poppler/ReportLab espliciti, con rendering PDF obbligatorio anziché test opzionalmente saltato.
- Nuove checklist di consegna `docs/RELEASE_CANDIDATE_READINESS.{it,en}.md`.
- Test locali: 82/82 Node, 60/60 Python. Baseline ultimo commit utente: pulizia cache e CI verde. Rimangono cumulativamente non committati: hardening converter, Trivy, lock condivisi, recupero manuale, pubblicazione atomica e questo ciclo.
- **RC BLOCCATA** fino a nuova CI e collaudi reali Docker/Podman/browser/HA. Versione invariata 0.1.0-dev; nessun commit, tag o rilascio effettuato.

## 2026-10-22 — Field validation (phases 1–2) corrections, pending CI (uncommitted)
- ARM64 Compose: managed ClamAV default changed to `clamav/clamav:stable-debian` based on maintainer deployment feedback; image existence/build must still be validated in CI or real deployment.
- Authentication: the mandatory initial password change now signs out client-side and shows the login screen rather than attempting to reuse a revoked cookie. Login accepts either email or the optional globally unique, case-insensitive nickname. Primary administrator has the reserved, immutable nickname `admin` but may change email via a separate audited-by-API administration action. Existing databases migrate primary identity at startup when absent.
- User administration: principal administrator can never be demoted, unapproved or deleted; current-user self-demotion protection remains. User approval toggles immediately and visibly between red and green states. Admin account identity may change its email without changing the stable login identifier.
- Web UI: functional navigation routes to main-area panels for Users, Server Settings, SSO, MFA, Presenter Profile and Workspace. Workspace distinguishes owner/collaborator roles by color. Each session may have zero or several explicit schedule dates via new API and date-selection controls. Session creation still retains legacy reference_date defaults for compatibility.
- Server SMTP/SMTPS settings: admin configuration can now persist with AES-256-GCM encryption under `AUTH_SECRET` and never returns the password. Existing environment configuration remains as fallback. MFA enrollment requires a configured SMTP transport. MFA provides both otpauth URI and authenticated, no-store PNG QR code; actual notification/email fallback behavior is not yet implemented or validated.
- Added additive SQL migrations for primary admin identity, nickname uniqueness, session schedule dates, encrypted SMTP settings. For production, back up the database and test migrations on a clone; avoid changing `AUTH_SECRET` without migrating encrypted settings.
- Validation: Node and Python offline suites, TypeScript/TSX syntax checks; full npm CI, PostgreSQL migration, browser interactions and real SMTPS connectivity remain **unverified** for this cycle. Version remains `0.1.0-dev`, RC acceptance blocked.
- Last user-confirmed commit: RC-readiness-integration cumulative with green CI. All the changes above are subsequent, uncommitted work.
- Next priorities: operational end-to-end verification, UX polishing, MFA notification path, SSO configuration UI, full calendar presentation, and validation that the database migration works against existing installations.

## Correzione CI TypeScript navigazione (2026-10-23)
- **Errore osservato nella CI:** `apps/web/src/main.tsx`, TS2345 nella navigazione admin: le voci condizionali venivano inferite come `string[][]`, perdendo il tipo letterale accettato da `setDashboardPage`.
- **Correzione:** tuple letterali (`as const`) nelle sole voci riservate agli admin, preservando il controllo statico TypeScript senza cast del parametro o ampliamento del tipo dello stato.
- **Regressione:** aggiunto `tools/tests/test_dashboard_navigation_types.py`. Resta necessaria una nuova build npm completa tramite GitHub Actions per confermare la compilazione.
- Restano inclusi gli interventi del precedente collaudo; versione invariata, nessun commit effettuato.

## Ciclo 2026-10-23 — paginazione server, calendario e ciclo di vita (non ancora committato)
- Ricerca e paginazione server-side di utenti e sessioni (1–100 voci/pagina), rispettando i ruoli owner/collaboratore; mantenuta la compatibilità delle risposte legacy.
- Nuova tabella `session_appointments` con data, ora HH:MM, durata di 5–1440 minuti e fuso IANA, API del calendario globale filtrata per permessi e appuntamenti per singola sessione, vista mensile e editor appuntamenti.
- Stato sessione `paused`, con pausa e ripresa; l'invio delle risposte rimane limitato alle sessioni attive.
- Navigazione iniziale a tab per l'editor e adattamento responsive del calendario.
- Verifiche locali: 82 test Node e 75 test Python superati. Build TS completa, migrazione PostgreSQL con dati esistenti e collaudi reali browser/container ancora obbligatori.
- **Da completare**: MFA amministrativa completa, secondo fattore email, gestione completa SSO dalla UI, audit accessibilità/responsive, conversione globale dei controlli sì/no a toggle e test end-to-end. RC non ancora validata.

## Aggiornamento post-collaudo UI e profili (23 ottobre 2026)
- Foto profilo caricate direttamente con streaming privato (PNG/JPEG/WebP, massimo 5 MB), scansione antivirus, sostituzione ed eliminazione; accesso pubblico alle foto dei presentatori vincolato alla sessione.
- Nickname inizializzato dal profilo corrente; rimosso l'inserimento di URL esterni per la foto.
- Toolbox con drag & drop nel canvas esistente; widget spostabili e rimovibili.
- Notifiche chiudibili con clic, pulsante e tasto Escape; migliorata la sovrapposizione visiva.
- Test di regressione aggiunti. **Ancora aperti**: esperienza completa tipo PowerPoint (widget immagine/video dedicati, catalogo integrale, miniature pagine e navigazione), verifica responsive nel browser, compilazione completa in CI e test operativi.


### 2026-10-23: Prova sessione nel browser e widget post-it
Aggiunto alla dashboard un dialogo di prova come partecipante con risposte locali, navigazione pagine e reset: non invia risposte all’API e non equivale a un collaudo E2E con partecipanti veri. Aggiunto il post-it al canvas e alla validazione condivisa. Rimangono da completare widget media con accesso sicuro, rifiniture dell’editor, MFA amministrativa, SSO via web e prove browser/CI.

Widget media, navigazione pagine e toggle implementati nei sorgenti; chiusura stimata gate RC 63%, collaudi E2E aperti.

## 2026-10-23 — Canvas slide a tutto schermo e riordino visuale
- L'editor usa un canvas 16:9, spostamento trascinando il corpo del widget e ridimensionamento da otto bordi/angoli. Le dimensioni sono salvate in percentuale; `height` è opzionale per compatibilità con le vecchie pagine.
- Rimossi i pulsanti di larghezza `+`/`−`; mantenuto il piccolo controllo di rimozione sul bordo.
- Aggiunto il comando di editor a schermo intero e riordino drag & drop nella barra delle slide, tramite l'API transazionale esistente.
- La simulazione partecipante rispetta le altezze salvate; aggiunti test delle geometrie.
- Test locali Node e Python eseguiti. La build TypeScript completa, il comportamento browser e i collaudi E2E devono essere verificati in CI e su un'installazione reale; restano aperti i flussi SSO/MFA e altri gate RC.

## 2026-10-23 — Righelli, rotazione, reflow mobile, domande per argomento e anteprima presentatore

- Editor bianco 16:9 con righelli percentuali; movimento dal corpo del widget, ridimensionamento ai bordi e rotazione arbitraria da maniglia dedicata (angolo salvato). Restano modalità fullscreen e riordino delle slide.
- Layout live su mobile adattato in blocchi verticali per la leggibilità; la rotazione salvata viene ignorata solo sul piccolo schermo.
- La dashboard espone anteprima incorporata e collegamento alla schermata pubblica di presentazione/risultati.
- Nuovo widget `topic-question` ripetibile: invii indipendenti per argomento in PostgreSQL, elenco del presentatore paginato a 10 domande, pseudonimo facoltativo disattivato per impostazione predefinita, aggiornamento periodico; dieci invii per partecipante/widget.
- Test mirati completati. **Da validare in CI/browser/PostgreSQL reali:** compilazione integrale, trascinamenti, responsive e migrazione dati. Consulta `docs/SLIDE_RULERS_ROTATION_TOPICS.it.md`.
- Stima di chiusura gate RC **67%** (prima 65%); non equivale a certificazione production-ready.

## 2026-10-23 — Geometria dei widget accessibile da tastiera (non committato)
- I widget del canvas sono selezionabili con Tab: frecce per spostamento (1 punto percentuale), Maiusc+frecce per ridimensionamento, Alt+frecce per rotazione (5 gradi). Ctrl abilita regolazioni fini (0,1 punti percentuali o 1 grado). Le operazioni rispettano i limiti del canvas e sfruttano il normale percorso di persistenza della geometria. I controlli di inserimento testo e i pulsanti non sono intercettati. Aggiunti indicatori di focus e istruzioni accessibili.
- Verifiche del ciclo: compilazione backend TypeScript **SUPERATA** e frontend TypeScript/Vite **SUPERATA** (1.579 moduli); Node **85/85 SUPERATI**; Python **91/91 SUPERATI**, compresi tre nuovi controlli contrattuali. Mancano prove su browser reale e tecnologie assistive; il gate accessibilità non è chiuso.
- Stima gate RC invariata al **67%**; restano verifiche reali browser, database, CI, multi-replica e deployment. Nessun commit/push/tag/release effettuato. Le modifiche dopo l'ultimo commit con CI verde dichiarato dall'utente restano non committate.

## 2026-10-23 — Posizionamento dei Risultati e domande per argomento (non committato)
- Il pulsante `results-button` nella proiezione segue ora l'intero rettangolo e la rotazione salvati; resta un pulsante di riserva per le pagine precedenti. I risultati sono visibili soltanto al presentatore tramite un pannello espandibile accessibile.
- Il pannello mostra statistiche dell'attività, classifica quiz a tempo se applicabile ed elenchi paginati (10/pagina) per ciascun widget di domande per argomento.
- Verifiche locali: build backend TypeScript e frontend Vite PASS; Node 90/90 PASS; Python 93/93 PASS, inclusi due nuovi test contrattuali. Test E2E con browser e PostgreSQL non eseguiti.
- **Chiusura gate RC confermata al 67%**. Mancano grafici configurabili per singolo widget, quiz a tempo indipendenti e verifiche reali di sincronizzazione/deployment. Nessuna nuova CI confermata, commit o release.

## Current cycle (2026-10-23)
2026-10-23 — Scelta visualizzazione risultati sul widget `results-button`: barre, torta, tabella; persistenza tramite layout. Build backend/frontend e test 90 Node + 93 Python PASS. **Ancora aperti** configurazione per singolo widget, quiz a tempo multipli indipendenti, E2E browser/PostgreSQL, allineamento manuali PDF. CI verde precedente confermata dall’utente (baseline prima di questo ciclo); nessun commit eseguito in questo ciclo. Gate RC 67% invariati.

## 23 ottobre 2026 — Paginazione della classifica quiz a tempo (dopo il commit, CI utente da eseguire)
- L'utente ha confermato **commit e CI verde** per `quorivio-0.1.0-dev-presenter-results-canvas-cumulative.zip`: questo è il riferimento dell'ultimo commit. I cicli relativi ai grafici dei risultati e alla paginazione non sono ancora committati. Le annotazioni storiche precedenti rimangono tali.
- La classifica riservata ai presentatori è paginata a 20 risposte corrette per pagina; ordinamento stabile per tempo registrato dal server, timestamp di invio e ID. La posizione in classifica continua tra le pagine; navigazione nel pannello Risultati con aggiornamento ogni due secondi.
- Build di produzione backend/frontend **PASS**; test Node **90/90 PASS**, Python **93/93 PASS**. Non eseguiti collaudi E2E con browser e database per questa funzione.
- **Avanzamento RC invariato al 67%**. Ancora aperti quiz indipendenti multipli, grafici per singolo widget, MFA email, invalidazione cookie dopo reset MFA e collaudi infrastrutturali. La RC non è raggiunta.

## 2026-10-23 — Revoca delle sessioni dopo reset MFA (non committato)
- Il reset MFA amministrativo aggiorna transazionalmente `users.auth_revoked_at`: i cookie emessi in precedenza sono respinti dalle API protette e dalle nuove connessioni WebSocket del presentatore. Rimane la chiusura delle connessioni locali già presente.
- Aggiunti migrazione SQL incrementale, due regressioni e note tecniche IT/EN. **Restano aperti i collaudi PostgreSQL e la chiusura proattiva dei WebSocket sulle altre repliche.**
- Ultimo commit/CI verde confermato dall'utente: `presenter-results-canvas`. Gli interventi successivi non risultano committati. Chiusura gate RC invariata: **67%**.

## 23 ottobre 2026 — Interventi accorpati di sicurezza (successivi all'ultimo commit confermato)
- L'upgrade WebSocket verifica ora l'origine completa dell'URL pubblico (schema, host e porta), invece del solo host, coerentemente con la protezione delle API HTTP che modificano dati. Restano supportati i client non-browser autenticati senza header Origin.
- Entrambi gli endpoint delle classifiche rifiutano paginazioni ambigue, frazionarie o fuori limite con HTTP 400, senza più forzare silenziosamente il valore. Dimensione e ordinamento delle classifiche rimangono invariati.
- Verifiche: build backend TypeScript PASS; build produzione frontend Vite PASS (1579 moduli); 99/99 test Node.js PASS; 95/95 test Python PASS. Collaudi E2E PostgreSQL, browser, SSO reale e Kubernetes ancora mancanti.
- Audit RC **37,5%** (40,0/100), invariato in assenza di nuove evidenze di accettazione. Non è una percentuale di righe di codice implementate.
- Tutti gli interventi dal commit `presenter-results-canvas` restano non committati; nessun commit, push, tag o release.


## 2026-10-23 — Email MFA flow
MFA email: aggiunti challenge PostgreSQL monouso, verifica login, UI e impostazione; build e test di contratto superati; collaudi E2E ancora necessari.
RC weighted gate score unchanged at 37.5%; email MFA is partial until PostgreSQL/SMTP/browser integration passes.


### 2026-10-23 – Protezione emissione MFA email
Limite condiviso tra repliche (3/account/minuto), una sola sfida attiva atomica, pulizia migrazione e indice univoco. Dettagli in `docs/EMAIL_MFA_ISSUANCE_HARDENING.it.md`. Gate RC invariati in attesa di prove di integrazione.

### 2026-10-23 — sfondi caricati per pagina (ciclo multimediale parziale)
- Aggiunto `backgroundAssetId` per pagina/risultati; validazione server MIME immagine, titolarità e appartenenza alla sessione.
- Selezione/upload sfondi nell’editor, rendering sul presentatore e anteprima partecipante.
- Distribuzione pubblica limitata alla pagina correntemente aperta.
- Restano aperti: menu contestuali, parità grafica del pubblico live, build/browser e collaudo Kubernetes. Avanzamento RC invariato 37,5%.

## 2026-10-23 — Modelli di pagine interattive con accesso diretto al canvas
- Aggiunte azioni per creare pagine sondaggio, quiz e quiz a tempo tramite l'API autenticata esistente: opzioni iniziali, durata predefinita di 30 secondi per quiz a tempo, aggiornamento sessione e apertura automatica dell'editor widget.
- Il modulo storico resta disponibile; opzioni e risposte corrette si configurano ancora nell'editor attività. La creazione *esclusivamente* tramite widget **non è conclusa**.
- Verifiche: 146 test Python (+7 sottotest) e 107 Node superati; build tentata e bloccata da dipendenze/tipi Node non disponibili (`Buffer` TS2580). Collaudi browser/PostgreSQL/Kubernetes non effettuati. RC **37,5%** invariata.

## 23/10/2026 — configurazione delle attività tramite widget del canvas
- Aggiunti controlli nel canvas per domanda e quiz a tempo: modalità risposta, opzioni, risposte corrette, obbligatorietà, durata.
- Conservati API e percorsi legacy delle attività; versione invariata.
- Verifiche locali: 140 test Python e 107 test Node superati. Build frontend completa e collaudi browser/Kubernetes pendenti.
- Vedere `docs/CANVAS_WIDGET_ACTIVITY_EDITOR.it.md`.

## 2026-10-23 — Visualizzazione widget interattivi sul presentatore
- La proiezione dei widget `question` e `timed-quiz` mostra ora il testo della domanda, descrizione, opzioni, indicazioni della modalità di risposta e conto alla rovescia del quiz, anziché la sola etichetta. Le risposte corrette non vengono svelate nella proiezione.
- I widget testo e post-it mostrano anche la descrizione. Introdotti stili per contenere testi lunghi e 3 test statici di regressione.
- Verifiche locali: 145 test Python superati (il runner emette anche una diagnostica della CLI recover durante l'importazione), 107 test Node.js superati. Build tentata, bloccata dalle tipizzazioni Node mancanti (`Buffer`, TS2580). Non eseguiti collaudi browser, PostgreSQL o Kubernetes. Avanzamento RC fermo al 37,5%.
- Residui: test end-to-end presentatore/partecipante, editing esclusivamente via widget, build e collaudi Kubernetes.

## 2026-10-23 — Confronto canonico delle revisioni dei quiz a tempo
- Allineato il confronto delle chiavi di risposta al calcolo effettivo dei punteggi: per scelta singola prevale `correctOptionId` non vuoto; in sua assenza è equivalente `correctOptionIds` con un elemento. Per scelta multipla vale `correctOptionIds`. Default: scelta singola e 30 secondi.
- Evita revisioni superflue e blocchi delle modifiche live che cambiano soltanto la rappresentazione; rimangono protette le modifiche effettive alla chiave o alla durata.
- Due nuovi test Node: 109/109 superati; 145/145 test Python unittest superati. Build TypeScript completa e collaudi browser/PostgreSQL/Kubernetes non verificati nel ciclo. RC invariata al 37,5%.
- Da completare: flusso interamente basato sui widget, collaudo live, MFA/foto profilo, build di produzione e accettazione Kubernetes.

### 23 ottobre 2026 — Coerenza temporale dei widget a tempo
- La verifica della scadenza e il calcolo del tempo trascorso usano il medesimo `clock_timestamp()` PostgreSQL durante la lettura bloccata dell'attività, anziché gli orologi delle singole repliche Node.js.
- Test di regressione in `tools/tests/test_widget_database_clock.py`; 147 test Python e 109 test Node superati localmente.
- Restano pendenti build TypeScript di produzione e collaudi reali PostgreSQL/browser/Kubernetes multi-replica; RC invariata al 37,5%.

### 23/10/2026 — Base per portabilità PowerPoint modificabile
- Aggiunto `tools/pptx_portable.py` per convertire caselle di testo PPTX in widget testuali modificabili e definizioni Quorivio JSON in slide PPTX statiche (dipendenza opzionale `python-pptx`).
- Corretto l'import JSON proprietario per le pagine `slide`, prima esportabili ma non reimportabili.
- Rafforzato layout mobile, pulsanti touch e gestione overflow, mantenendo invariata la geometria salvata.
- Conversione fedele completa, integrazione browser e collaudo sui dispositivi ancora APERTI. Si veda `docs/POWERPOINT_PORTABILITY.md`.
- Percentuale RC invariata fino a build e collaudi end-to-end.

### 2026-10-23 — Editable PPTX text-style round-trip
- Extended the optional text-box converter to retain explicit font family, point size, bold, italic and fixed RGB color on PPTX import/export. Local styled PPTX round-trip passed. Mixed formatting, master/theme semantics, in-browser export, production build and device acceptance remain OPEN. RC gate score unchanged at 37.5%.

### Rafforzamento import PPTX modificabile (2026-10-23)
- CLI: verifiche preliminari su dimensioni ZIP, numero voci, macro/binari e filtro dei font ammessi dal formato portabile. Nuovi test di regressione Python.
- Aperti: import/export PPTX modificabile dal browser, grafica PowerPoint complessa, collaudi mobile end-to-end e gate di accettazione.

### 2026-10-23 — Miglioramenti incrementali PPTX modificabile e mobile
- Convertitore CLI: titolo pagina estratto dai testi della slide e rotazione delle caselle di testo preservata; aggiunto test di regressione.
- Mobile: controlli radio/checkbox più utilizzabili al tocco e aree per risposte testuali responsive, senza cambiare la geometria salvata.
- Test: 153 Python e 111 Node.js superati. Build frontend completa e collaudi browser/Kubernetes non verificati.
- Fedeltà PowerPoint, import/export PPTX dal browser, media incorporati e collaudi mobile ancora APERTI; RC 37,5%.

### 2026-10-23 — Import/export PPTX modificabile integrato nel browser
- Aggiunti `POST /api/presentations/import-editable` autenticato (crea una nuova sessione modificabile), `GET /api/sessions/:id/export.pptx` riservato ai presentatori autorizzati e relativi controlli nella dashboard.
- Conversione esclusivamente tramite il worker isolato, con ID di lavoro opachi, token, lock, limiti dimensionali, scansione antimalware in ingresso e pulizia dei file temporanei; immagine converter con python-pptx 1.0.2.
- Importazione modificabile di testi, posizione, rotazione e parte degli stili; esportazione PPTX limitata ai contenuti supportati, con attività interattive statiche. L'importazione grafica precedente resta disponibile per massimizzare la fedeltà visiva.
- Test: 155 Python e 111 Node.js superati; round-trip del worker riuscito. Build TypeScript completa BLOCCATA dai tipi Node non installati; nessun collaudo browser, PostgreSQL o Kubernetes reale. Fedeltà e integrazione non ancora accettate; RC invariata al 37,5%.

### 2026-10-23 — PPTX import fidelity reporting / Rapporto di fedeltà PPTX
- Extended editable PowerPoint conversion to round-trip explicit underline formatting; added metadata-only import fidelity counts for skipped pictures, charts, tables and unsupported shapes and page overflow, returned from worker to API without including slide text or media bytes. / Estesa la conversione PPTX alla sottolineatura; aggiunto resoconto delle forme non convertite restituito dall’API senza contenuti privati.
- 157 Python and 111 Node tests passed locally. Image/shape editability, frontend build and real browser/mobile/Kubernetes testing remain open. Weighted RC unchanged at 37.5%.


## 2026-10-23 — Demo, presenza e carico
Aggiunte sessioni dimostrative transazionali per ogni nuovo account (5 attività), widget live del numero di partecipanti distinti tra repliche, e simulatore autorizzato con 500 client. Accettazione Kubernetes pendente.

### 2026-10-23 — Carico anonimo QR per 500 partecipanti
- Aggiornato `tools/load_500.py` per il percorso anonimo via URL QR, sessioni cookie indipendenti, presentatore opzionale, suddivisione su generatori distinti, IP locali configurabili e metriche JSON.
- Aggiunti `docs/ARCHITECTURE_500.it.md`, versione inglese e profilo Helm staging opzionale; supporto configurabile alle annotazioni Ingress.
- **Gate RC aperto:** carico 500 utenti non misurato sul cluster; fan-out WebSocket tra pod e sincronizzazione, sizing e ingress da collaudare. Percentuale invariata (37,5%).


### 2026-10-23 — Fan-out reconnect hardening
Il listener PostgreSQL per le notifiche tra pod ora risincronizza le sessioni WebSocket locali dopo la riconnessione; aggiunto test di recupero. Collaudo multi-pod reale pendente.

### 2026-10-23 Ciclo geometria PPTX nativa
- Rimossi i minimi forzati del 12% di larghezza e 8% di altezza da importazione PPTX e validazione API per conservare oggetti piccoli. Aggiunti diagnostica delle forme fuori canvas e test round-trip.
- Avanzamento RC invariato al 37,5%; build frontend completa e collaudi browser/Kubernetes non verificati.

### 2026-10-23 — Deduplicazione media PPTX nativi e verifica OOXML
- Durante l'importazione PPTX modificabile le immagini PNG/JPEG identiche condividono un solo asset, pur mantenendo widget e geometrie indipendenti per ogni occorrenza.
- Il controllo preventivo rifiuta percorsi OOXML non sicuri, nomi duplicati e membri ZIP cifrati.
- Test di regressione: riutilizzo delle immagini ed esclusione di percorsi non sicuri. Superati localmente 169 test Python e 113 Node.js.
- Build TypeScript completa, browser, PostgreSQL e Kubernetes **non validati**. Avanzamento RC verificato invariato al **37,5%**.

### 2026-10-23 — Protezione media importati da PPTX nativi
- Corretta la precedenza logica del controllo MIME/dimensione rispetto alla quota disponibile in `tools/pptx_portable.py`: i formati non supportati non possono entrare nella cartella temporanea degli asset.
- Aggiunto test di regressione in `tools/tests/test_pptx_portability.py`.
- Verifiche locali: 170 test Python e 113 test Node superati; build frontend di produzione e collaudi browser/PostgreSQL/Kubernetes non certificati.
- Forme vettoriali PPTX modificabili e fedeltà completa ancora aperte; matrice RC invariata.


### 2026-10-23 forme PPTX colori
Sviluppo successivo al commit confermato: riempimenti, contorni e angoli arrotondati delle forme PPTX ora salvati nello stile dei widget e riprodotti in export e proiezione. Test locali superati; collaudi browser/Kubernetes pendenti.

#### 2026-10-23 — Native PPTX ellipse and triangle shape round-trip
- Added editable shapeType support for oval and isosceles-triangle PPTX text autoshapes, including validated API styles and presenter approximations; preserved rectangle compatibility.
- Round-trip regression added, 173 Python tests and 113 Node tests passed locally. Full production build/browser/Kubernetes acceptance not claimed.
- RC gate percentage remains 37.5%; no external changes or commits performed.

### 2026-10-24 — Modifiche non salvate nell’editor
Aggiunti confronto tra layout corrente e salvato, indicatore delle modifiche, conferme per cambio pagina/chiusura e protezione beforeunload. Resta il collaudo browser completo.

### 2026-10-24 — Anteprime miniature editor e sicurezza delle modifiche
- Le miniature verticali mostrano ora posizioni, dimensioni, titoli e sfondi URL dei widget del layout **salvato**, invece del solo titolo; anteprima non interattiva, limite di 24 widget per pagina.
- Il riordino (trascinamento e pulsanti) e il ritorno alla dashboard richiedono conferma in caso di modifiche al canvas non salvate.
- Verifiche locali: 186 test Python e 113 test Node superati. Build completa TypeScript/Vite e collaudi browser/Kubernetes **non verificati** in questo ciclo.
- RC invariata al **37,5%**; rimangono aperti i contenuti PPTX complessi, la fruizione mobile, la sincronizzazione multi-replica end-to-end e l'accessibilità.

## Ciclo formato Quorivio portabile (2026-10-24)
Implementati import/export ZIP `.quorivio` con manifest degli asset, verifica SHA-256, convalida rigorosa dell’archivio, nuovi codici di accesso e comandi dashboard. Il JSON legacy senza allegati resta compatibile. Verifiche locali: 190 test Python e 116 test Node superati. Mancano collaudo browser/database su istanze distinte e build completa TypeScript/Vite. Gate RC invariato al 37,5%.

### 2026-10-24 — Stabilizzazione geometria editor
- Allineati i limiti di ridimensionamento con mouse/touch e tastiera allo 0,01% già supportato da backend e convertitore PPTX. Conservati quattro decimali per non ingrandire involontariamente gli oggetti molto piccoli.
- Verificato che le scorciatoie geometriche non intercettino le frecce all'interno dei campi di modifica.
- Test locali: 193 Python e 116 Node.js superati. Build di produzione/browser e Kubernetes non collaudati in questo ciclo; RC invariata al 37,5%.

### 2026-10-24 — Stabilizzazione concorrenza riordino pagine (cumulativo successivo al commit)
- Serializzate le richieste di riordino preservando la conferma delle modifiche non salvate e la navigazione nell'editor a pagina intera.
- Aggiunto `aria-busy`, disabilitati trascinamento/riordino delle miniature durante il salvataggio dell'ordine e ignorati gli snapshot tardivi appartenenti a una sessione precedentemente selezionata.
- Aggiunti test di regressione Python. Nessuna migrazione DB, modifica API pubbliche, operazione GitHub o deployment Kubernetes.
- **Non** è completato l'intero backlog: restano la fedeltà OOXML complessa, MFA e mobile, build di produzione/integrata, sicurezza e accettazione Kubernetes. Gate RC invariato al **37,5%**.
- Verifiche di questo ciclo: 204 test Python e 116 Node superati; integrità ZIP superata. `npm run build` locale **non** superata (tipizzazioni Node assenti nel container, TS2580 in `totp.ts`); CI/browser/Kubernetes non rieseguiti.

## 2026-10-24 — Gestione dei puntatori multipli sul canvas
- Assegnata ogni operazione di trascinamento, ridimensionamento e rotazione all'identificativo del puntatore iniziale: un secondo dito non può sostituire il gesto e i suoi movimenti/rilasci/annullamenti vengono ignorati. Il mouse accetta soltanto il pulsante principale.
- Aggiornati i test dei gesti e aggiunti due test multipuntatore. Verifiche locali: 209 test Python e 116 Node superati.
- La build TypeScript/Vite non è stata convalidata: `npm install --offline` termina con ENOTCACHED per `@types/bcryptjs`. Collaudi browser/device/Kubernetes non eseguiti; il gate editor rimane aperto.
- RC verificata invariata: 37,5%. Nessun commit o modifica remota.

### 2026-10-24 — Verifica unificata: attivazione indipendente dell'autenticatore
- Eliminato il requisito SMTP erroneamente imposto all'attivazione TOTP. L'autenticatore funziona indipendentemente dalla posta; il secondo fattore email continua a richiedere SMTP.
- La risposta contenente il segreto TOTP usa `Cache-Control: no-store, private`, come già il QR.
- Aggiunti test Node specifici e corretto il precedente controllo Python che imponeva l'accoppiamento errato.
- Sul nuovo cumulativo: 218 test Python superati, 118 test Node superati. `npm run build` FALLISCE localmente perché mancano le definizioni Node in questo ambiente; non è una certificazione della build. Restano APERTI integrazione browser/PostgreSQL, multi-replica, OOXML avanzato, sicurezza e GDPR.
- Percentuale RC invariata all'ultima baseline verificata (37,5%). Non dichiarare concluso il software.

### 24/10/2026 — Consolidamento unificato / integrità degli archivi
- Rafforzati coerenza ZIP, intervalli senza sovrapposizioni, firme MIME e test avversari.
- Test: 218 Python e 120 Node superati; build completa e integrazione reale non certificate.
- Vedere `docs/UNIFIED_COMPLETION_PROGRESS_2026-10-24.it.md`. Gate RC invariato al 37,5%.

## 2026-10-24 — Recupero forme PowerPoint raggruppate
- Conversione di gruppi annidati in widget modificabili indipendenti con coordinate trasformate.
- Rapporto di fedeltà segnala i gruppi appiattiti come conversione con perdita.
- Verifiche locali: 223 Python, 120 Node.js API. Build bloccata dalle tipizzazioni Node non installate; non RC.
- Vedere `docs/UNIFIED_COMPLETION_PROGRESS_2026-10-24.it.md`.

## 2026-10-24 — Prosecuzione integrata delle macroaree: titoli grafici e controlli OIDC

- I titoli dei grafici PPTX nativi vengono importati come widget di testo modificabili, rispettando il limite esistente di 16 widget/pagina. Serie, assi, dati e formattazione dei grafici non sono conservati e sono dichiarati esplicitamente nel rapporto di fedeltà.
- I token ID OIDC vengono respinti se la data `iat` è troppo remota, la durata è superiore a 24 ore o i valori temporali non sono finiti, mantenendo le verifiche di firma, emittente, destinatario e nonce. Aggiunti test.
- Evidenze locali: 224 test Python OK e 121 test Node.js OK. La build npm completa è stata tentata ma interrotta perché mancano le definizioni TypeScript Node (`TS2580`). Non è quindi certificata per questa revisione.
- **Ancora aperti:** Release Candidate globale, grafici PowerPoint completi/SmartArt, MFA/SSO end-to-end, flussi live con PostgreSQL, trasferimento archivi tra istanze, verifica accessibilità su browser/dispositivi, capacità reale di 500 partecipanti, audit sicurezza/GDPR e CI riproducibile di questa revisione. Servono ulteriori sviluppi o verifiche esterne.
- Nessuna modifica a repository, server o Kubernetes.

## 24 ottobre 2026 — Consegna cumulativa del ciclo integrato
- Si veda `docs/CYCLE_DELIVERY_2026-10-24.it.md` per differenze dalla baseline, test, blocchi e prossimi collaudi.
- Compilazione locale PASS; Node 126/126 PASS; Python 224/224 PASS. Aggiunto test HTTP PostgreSQL in CI, non eseguito localmente.
- Matrice invariata a 40,0/100, nessuna dichiarazione RC, nessuna modifica ai servizi reali.

### 2026-10-24 ulteriore rafforzamento integrato
- Import `.quorivio`: controllo della quota complessiva dichiarata prima della decompressione e lettura UTF-8 rigorosa del manifest; export con limite sull'archivio ZIP risultante.
- Aggiunti test di rifiuto degli archivi anomali. PostgreSQL, browser/dispositivi reali, SSO e carico live di 500 partecipanti **non** collaudati qui.
- Compilazione TypeScript API e suite Node/Python eseguite; bundle Vite bloccato dal binario esbuild non compatibile nell'archivio dipendenze disponibile. Nessun gate RC promosso senza prove.

## Ciclo 2026-10-24 — riconciliazione gesture touch mobile
- Corretto il breakpoint a 700px che reimpostava `touch-action:manipulation` sui widget del canvas, rischiando di interrompere la cattura degli eventi durante trascinamento, ridimensionamento e rotazione. Mantenuta l'interazione touch dei controlli dei moduli.
- Aggiunti 3 test di regressione (`tools/tests/test_mobile_touch_capture_contract.py`).
- Verifiche locali: build API TypeScript PASS; frontend TypeScript noEmit PASS; Node 131/131 PASS; Python 235/235 PASS. Bundling Vite completo BLOCCATO dai binari nativi esbuild incompatibili nell'archivio offline; da ripetere in GitHub Actions. Nessun collaudo reale mobile/browser/database eseguito. Matrice RC invariata: 40,0%.

### 24 ottobre 2026 — Rafforzamento riordinamento pagine
- Validazione rigorosa di versione/variante UUID e rifiuto di identificativi preesistenti duplicati.
- Verifica della permutazione con insiemi, a complessità lineare.
- Tre nuove regressioni Node.js; suite mirata: 8/8 PASS.
- Gate RC A2 ancora parziale: servono prove browser e multidispositivo. Nessuna modifica a server reali.

### 24 ottobre 2026 — Accelerazione multi-gate: autorizzazioni live
- Strategia aggiornata per macroaree end-to-end: `docs/RC_ACCELERATION_PLAN.it.md` e `.en.md`.
- Audit WebSocket ogni 10 secondi esteso a sessioni, ruolo/delega presentatore e appartenenza dei partecipanti; chiusura fail-closed in caso di revoca, scadenza o indisponibilità DB. Nuovi test di regressione.
- Backend TypeScript PASS; frontend TypeScript/Vite PASS; Node 138/138 PASS; Python 235/235 PASS. Mancano prove E2E PostgreSQL/multi-replica; B1–B4 ancora parziali. Matrice 40,0%.

## 24 ottobre 2026 — Affidabilità live

- Aggiunta la coda di snapshot per sessione e la protezione da client WebSocket lenti (2 MiB), con cinque test Node. Build backend TypeScript e frontend Vite PASS, Node 143/143, Python 235/235. B1 resta parziale in attesa di prove PostgreSQL/multi-replica e browser. Vedere `LIVE_DELIVERY_RELIABILITY.it.md`.

### 2026-10-24 — Riconnessione del bus delle sessioni
- Il listener PostgreSQL LISTEN si riconnette se fallisce la risincronizzazione obbligatoria degli snapshot locali, evitando client browser silenziosamente non aggiornati.
- Aggiunte regressioni per errori LISTEN e di risincronizzazione.
- Il gate B1 resta parziale: non è stato eseguito un collaudo browser multi-replica PostgreSQL.

### 24 ottobre 2026 — Isolamento listener obsoleti e recupero errori bus
- Ignorate notifiche provenienti da listener PostgreSQL già disconnessi o dopo l’arresto del servizio, verificando identità e ciclo di vita della connessione.
- Se il gestore di una notifica rifiuta la Promise, viene registrato l’errore e forzata la riconnessione con risincronizzazione, anziché ignorarlo.
- Due nuovi test Node. Verifiche locali complete: backend TypeScript e frontend Vite PASS, Node 150/150 PASS, Python 252 superati (+10 subtest).
- Gate B1 ancora parziale: test su listener simulati, non collaudo multi-replica PostgreSQL. Nessuna modifica a infrastrutture reali.

## 2026-10-24 — Propagazione errori e completamento della coda live

La coda per sessione ora consente ai chiamanti concorrenti di attendere l’ultimo aggiornamento accorpato; gli errori delle letture vengono propagati dopo gli eventuali aggiornamenti pendenti e la coda viene liberata. La risincronizzazione del listener non ignora più gli errori. Aggiunti due test. Build locali PASS, Node 152/152, Python 252/252 (10 sottotest). B1 resta parziale fino ai collaudi multi-replica PostgreSQL e browser.

## 2026-10-24 — Collaudo HTTP live con PostgreSQL (gate B1–B4)

- Aggiunto `tools/ci_live_http.py` come passo obbligatorio della CI dopo il collaudo portabilità/profilo, utilizzando la password aggiornata dell'amministratore CI.
- Verifica sessione attiva, sondaggio, **24 partecipanti indipendenti** con cookie separati, risposte concorrenti, idempotenza, conteggi e riservatezza del report, chiusura e rifiuto delle risposte tardive.
- Verifica inoltre un quiz temporizzato di cinque secondi, accettazione iniziale, scadenza secondo PostgreSQL e conteggio esatto nel report.
- Due nuovi test statici garantiscono presenza e ordine del gate nel workflow.
- **Verificato localmente:** build backend e Vite PASS, Node 154/154 PASS, Python 239/239 PASS, compilazione script PASS. **Non eseguiti localmente:** collaudo HTTP su PostgreSQL, WebSocket multi-replica, browser/dispositivi e carico 500 utenti. Il nuovo passo sarà eseguito dalla prossima CI autorizzata, non è già stato collaudato.
- **Matrice RC invariata: 40,0%**. B1–B4 rimangono parziali in attesa delle prove reali.


## Hotfix CI successivo al commit 22daad0 (2026-10-24)

GitHub Actions run 40128742733, job 120975700188: il test HTTP del formato portabile su PostgreSQL è fallito alla prima importazione con `invalid_bundle_definition` (HTTP 400). Causa: `portableSession()` leggeva `reference_date` (DATE) senza cast; node-postgres lo trasformava in Date JavaScript e l’archivio serializzava un timestamp ISO anziché `YYYY-MM-DD`. Correzione: `reference_date::text AS reference_date`; aggiunta verifica HTTP di regressione sull’export JSON. Build TypeScript API PASS, 154/154 test Node PASS, 254 test Python PASS (10 sottotest). Occorre rieseguire la CI PostgreSQL dopo il commit; gate non ancora accettato.


### 2026-10-24 — CI concurrent live throttle hotfix
Hotfix CI: il test HTTP di portabilità PostgreSQL ora passa; il test concorrente live incontrava il rate limiter condiviso per IP (429). Aggiunto token di carico effimero solo CI per il bypass già presente e non disponibile in produzione. Necessaria nuova esecuzione CI.

## 2026-10-24 — Collaudo obbligatorio PostgreSQL WebSocket su due repliche (dopo baseline CI verde)

- Aggiunto `tools/ci_live_replicas.py`: prova HTTP/WebSocket reale con due processi API e database PostgreSQL 18 condiviso.
- La CI avvia una seconda API sulla porta 8081, verifica la disponibilità, esegue il collaudo e arresta entrambe le istanze anche in caso di errore, stampando i log.
- Verifica socket presentatore/partecipante su repliche opposte, propagazione di apertura, aggregazione risposte, chiusura attività e sessione e riservatezza dei risultati non pubblicati.
- Usa token di carico effimero, valido soltanto fuori produzione; i limiti di produzione rimangono attivi.
- L'utente ha confermato commit e CI verde per la baseline `ci-live-throttle-hotfix`; queste modifiche sono successive.
- Gate B1/B4 ancora **parziali** fino all'esecuzione del nuovo test CI e ai collaudi browser/500 utenti.
- Verifiche locali del ciclo: 154/154 test Node PASS, 242 test Python PASS (unittest discovery), build backend TypeScript e frontend Vite PASS. Il nuovo test runtime su due repliche non è eseguibile localmente (assenza PostgreSQL/container); in attesa della CI.

### Lotto consolidato di dieci interventi — capacità e repliche (24 ottobre 2026)

Un solo package cumulativo, senza ZIP intermedi. Gli interventi riguardano:
(1) cookie HTTP su IP locali; (2) validazione UUID e token QR; (3) privacy degli
snapshot WebSocket; (4) durata effettiva dei test; (5) percentili dei report;
(6) accesso ai report riservato al presentatore; (7) risultati non pubblicati
protetti all'apertura; (8) idempotenza risposte tra repliche; (9) privacy anche
dopo il voto; (10) collaudo opzionale di 500 partecipanti sulla stessa sessione
con PostgreSQL effimero, osservatore unico e pulizia finale.

**Avanzamento verificato: 43,0%** (prima 40,0%). Il gate D2 passa da `open` a
`partial` sulla base della CI PostgreSQL 18 confermata verde dal manutentore:
bootstrap dello schema e test HTTP portabilità/profilo. Si tratta di una
riclassificazione delle prove già ottenute, non di una nuova certificazione
backup/restore o migrazione. Nessun gate nuovo è `accepted`.

Verifiche locali: 154 test Node, 248 test Python, build TypeScript backend e Vite
frontend superate. I test WebSocket su due repliche e il carico reale di 500
partecipanti richiedono esecuzione CI: il carico è **solo su richiesta manuale**
con `workflow_dispatch` e `capacity_test`, mai su ogni commit. Non dichiarare RC.

## 24 ottobre 2026 — lotto funzionale consolidato: disaster recovery e replica live

**Dieci interventi, un solo package:** pubblicazione atomica dei backup, limiti di
quota, validazione rigorosa dei percorsi, verifica completa dei checksum prima della
pubblicazione, staging degli allegati prima del ripristino PostgreSQL, protezione contro
link simbolici e destinazioni non vuote, sette nuovi test avversariali, collaudo reale
PostgreSQL 18 su database nuovo, integrazione obbligatoria nella CI e rafforzamento del
test WebSocket contro notifiche obsolete dopo il voto.

**Verifiche locali:** 154/154 Node, 255/255 Python, build backend e frontend superate.
**Ancora da verificare in CI:** ripristino PostgreSQL 18 e sincronizzazione su due repliche.
Il gate D2 rimane `partial` e la percentuale complessiva rimane **43,0%**: nessun
incremento non giustificato da evidenze di accettazione. Nessun commit/push/tag/release.

### Hotfix client PostgreSQL 18 in CI (24/10/2026)
- La CI 40133452409 si è fermata nel backup DR: pg_dump 16.15 contro PostgreSQL 18.6.
- La CI installa ora esplicitamente il client PostgreSQL 18 e controlla le versioni di pg_dump/pg_restore prima dei test.
- I test HTTP live e WebSocket a due repliche erano verdi; DR rimane in attesa della nuova CI.
- Nessun gate RC viene chiuso automaticamente da questa correzione.
