"""Expanded bilingual operating content for the three Quorivio roles.
The procedures are intentionally capability-scoped to 0.1.0-dev.
"""

def section(name, *items):
    return (name, list(items))

def item(heading, text):
    return (heading, text)

EXTRA = {
'it': {
'user': [
section('Percorso guidato completo: dalla schermata iniziale alla conferma',
 item('Scenario di esercitazione','Prerequisiti: URL o QR fornito dal presentatore, browser con cookie funzionali abilitati, sessione attiva e una domanda aperta. Passo 1: apri il collegamento. Passo 2: controlla che il nome della sessione sia quello atteso. Passo 3: se richiesto inserisci uno pseudonimo riconoscibile solo per te. Passo 4: conferma l’uso dei cookie tecnici necessari. Passo 5: invia una risposta una sola volta. Passo 6: verifica la conferma prima di chiudere la scheda.'),
 item('Se il browser è stato chiuso','Riapri il medesimo browser e lo stesso indirizzo; mantieni i cookie della sessione. Se i dati locali sono stati cancellati, se cambi dispositivo o usi navigazione privata, il sistema potrebbe non riconoscerti. Non è garantito un voto unico per persona non autenticata.'),
 item('Quando il presentatore cambia domanda','Non è necessario eseguire operazioni sul materiale PowerPoint esterno. Il link Quorivio indirizza all’attività aperta. Se l’interfaccia non si aggiorna, verifica la rete, ricarica una sola volta e chiedi al presentatore se la raccolta è stata chiusa.'),
 item('Risposte e risultati live','I risultati aggregati possono essere visibili oppure nascosti secondo la scelta del presentatore. Una pagina senza risultati non significa che il tuo invio sia stato perso: fai riferimento al messaggio di conferma della risposta.')
),
section('Guida a situazioni particolari',
 item('QR code non riconosciuto','Prova il collegamento testuale o digita il codice mostrato a schermo. Evita app non attendibili per la scansione e non condividere codici privati fuori dall’evento. Se la sessione è stata revocata, soltanto il presentatore può fornire un nuovo invito.'),
 item('Domanda assente o non selezionabile','L’attività potrebbe essere in bozza, chiusa o ancora non aperta. Non tentare di aggirare la chiusura ricaricando ripetutamente la pagina. Chiedi al presentatore quale domanda sia attiva.'),
 item('Il voto sembra duplicato','Non premere ripetutamente Invia. Il backend applica controlli sui ritentativi, ma la ripresa di una sessione anonima non equivale all’identificazione certa della persona. Segnala l’anomalia al presentatore.'),
 item('Accessibilità','Usa zoom del browser, comandi da tastiera e strumenti assistivi. Le informazioni principali non dovrebbero dipendere soltanto dal colore. Se un contenuto multimediale non è accessibile richiedi al presentatore una versione testuale.')
),
section('Protezione dei dati e assistenza',
 item('Cookie tecnici e pseudonimo','Il cookie tecnico serve a riconoscere il browser durante la partecipazione ed evitare invii duplicati; lo pseudonimo è un dato fornito dall’utente. Accettare cookie necessari non costituisce consenso generale a profilazione o marketing. L’informativa effettiva dipende dall’operatore dell’istanza.'),
 item('Cosa non inviare','Evita password, identificativi personali, dati sanitari e informazioni riservate nelle risposte aperte, a meno che l’organizzatore ne abbia documentato la necessità. Quorivio è in fase di sviluppo e alcuni controlli GDPR sono ancora incompleti.'),
 item('Richieste sui dati','Rivolgiti all’amministratore o al titolare indicato nell’informativa dell’installazione. Specifica sessione, data e pseudonimo senza divulgare password. I tempi e le modalità di risposta dipendono dalle procedure organizzative del titolare.')
)],
'presenter': [
section('Checklist prima dell’evento',
 item('Almeno un giorno prima','Verifica che il tuo account sia approvato come presentatore. Crea la sessione con titolo riconoscibile e data di riferimento. Controlla le attività e i testi; apri il link pubblico da uno smartphone non autenticato. Verifica anche il collegamento a Internet e la disponibilità del proiettore.'),
 item('Accesso e informativa','Decidi se ammettere anonimi e se rendere pubblici i risultati. Spiega ai partecipanti se devono usare uno pseudonimo e che i cookie tecnici sono necessari al funzionamento. Non promettere anonimato assoluto né un voto unico per persona anonima.'),
 item('Grafica della sessione','Inserisci URL HTTPS di logo e sfondo dalla sezione tema preliminare, dove disponibile. Il supporto agli allegati remoti è limitato; l’upload e l’editor visuale completo sono ancora da implementare. Controlla leggibilità e contrasto sullo schermo reale.'),
 item('Prova generale','Usa un secondo dispositivo per simulare un voto, controlla il risultato pubblico e l’export CSV. Per test non definitivi crea una sessione di prova separata oppure duplica una definizione; non contaminare i risultati dell’evento.')
),
section('Conduzione live: cronologia operativa',
 item('Prima dell’apertura','Dal workspace seleziona la sessione. Scarica QR in PNG o SVG e incorporalo in qualunque presentazione esterna. Mantieni la pagina presentatore aperta sul tuo computer e usa la pagina Schermo pubblico separata per proiezione.'),
 item('Avvio','Premi Avvia, poi Apri sulla prima attività. Annuncia il codice e verifica che almeno un dispositivo di prova possa rispondere. Non proiettare il pannello amministrativo o credenziali. Mantieni controllata la visibilità dei risultati.'),
 item('Durante il sondaggio','Osserva l’andamento delle risposte; evita modifiche strutturali improvvise. In caso di modifica di opzioni già utilizzate, preserva gli identificatori originari. Le API di modifica live esistono, ma la UI di editing avanzato e i test multiutente non sono ancora completi.'),
 item('Chiusura, esportazione e controllo','Chiudi ogni attività prima di passare alla successiva. Termina la sessione quando l’evento è concluso. Verifica che lo storico sia accessibile e scarica il CSV; conserva i file secondo le regole dell’organizzazione. Le sessioni chiuse hanno retention globale iniziale di 60 giorni, configurabile dall’amministratore.')
),
section('Collaborazione e versioni dei contenuti',
 item('Assegnare co-presentatori','Puoi aggiungere presentatori approvati della stessa organizzazione tramite API della sessione. Prima di usarla per eventi reali verifica autorizzazioni, titolarità e accesso concorrente: una UI completa di invito, ruoli e revisione simultanea non è ancora disponibile.'),
 item('Duplicare una sessione','L’API duplicate crea una nuova bozza con nuovi inviti e senza risposte. Assegna nome e data adeguati, verifica domande e contenuti, poi distribuisci soltanto il QR della sessione nuova. Non riutilizzare il vecchio QR per una nuova edizione.'),
 item('Importare o esportare definizioni','L’export JSON attuale riguarda definizioni, attività e tema. Non comprende risultati, allegati o backup completo. Prima dell’importazione controlla il file e usa un’istanza di prova: i controlli di portabilità completa sono ancora in sviluppo.'),
 item('Invalidazione dei risultati','La funzione API di invalidazione marca le risposte di una domanda e ne esclude il contributo dagli aggregati, conservando tracce di audit. È un’operazione rilevante: comunica l’effetto ai partecipanti. Il reinvio dopo invalidazione non è ancora supportato end-to-end.')
),
section('Diagnostica rapida per il presentatore',
 item('Non compare alcun partecipante','Verifica indirizzo pubblico, codice, scadenza, accesso anonimo abilitato, HTTPS e stato attivo. Controlla se il QR è stato generato prima di modificare la URL esterna dell’istanza.'),
 item('Il risultato proiettato non cambia','Controlla che l’attività sia aperta e che le risposte siano state confermate. Prova a riaprire lo schermo pubblico; le notifiche multi-replica non sono ancora validate.'),
 item('Una risposta appare incoerente','Controlla se la domanda è stata modificata durante la raccolta. Non cancellare o rinominare indiscriminatamente opzioni votate. Usa l’invalidazione solo quando indispensabile e documenta la decisione.'),
 item('Errore di esportazione','Verifica permessi del presentatore e presenza dei risultati. CSV è il formato operativo disponibile; l’export Excel completo resta pianificato. Conserva copia del file e verifica la codifica all’apertura in foglio elettronico.')
)],
'admin': [
section('Checklist di prima installazione',
 item('Sicurezza prima dell’avvio','Prepara DNS pubblico e certificato TLS valido. Configura credenziali robuste, database PostgreSQL, segreti fuori dal repository, storage persistente e accessi amministrativi limitati. La password demo 000000 richiede opt-in non produzione; non esporla in Internet.'),
 item('Configurazione indirizzo esterno','Nell’area Amministrazione imposta la URL HTTPS effettiva del servizio. Questa URL viene impiegata nella generazione degli inviti di sessione. Dopo una modifica, richiedi ai presentatori di rigenerare e sostituire i QR già scaricati.'),
 item('Registro delle approvazioni','L’autoregistrazione non equivale ad autorizzazione. Controlla identità e necessità del ruolo prima di approvare utenti o presentatori. Revoca prontamente gli accessi non più necessari e documenta chi ha autorizzato l’account.'),
 item('Verifica di disponibilità','Controlla /api/health/live e /api/health/ready, PostgreSQL e certificati; fai un test con presentatore e browser anonimo. La CI è stata confermata verde su un cumulativo precedente, non sull’ultima modifica.')
),
section('PostgreSQL, migrazioni e protezione dei dati',
 item('Installazione interna','Il wizard può generare StatefulSet e PVC PostgreSQL 18.6. Per dati reali pianifica ridondanza, storage affidabile, backup e processi di aggiornamento. Un singolo StatefulSet non costituisce alta disponibilità.'),
 item('Database esterno','Imposta postgres_mode=external e configura host, porta, SSL verify-full, credenziali in Kubernetes Secret. Valida la catena CA e l’identità del server prima del go-live. Non includere stringhe DATABASE_URL nei manifest versionati.'),
 item('Migrazioni','Esegui le migrazioni del database in una finestra controllata e su copia di prova con dataset realistico. Prima di passare da PostgreSQL 17 a 18 effettua una migrazione maggiore compatibile: cambiare l’immagine container non migra automaticamente i dati.'),
 item('Backup e ripristino','Il backup integrale e il restore via UI non sono implementati. Fino ad allora usa strumenti PostgreSQL supportati e backup sincronizzati di eventuali file esterni; verifica il ripristino completo in ambiente isolato. Documenta RPO, RTO, cifratura e accesso ai backup.')
),
section('Kubernetes: configurazione riproducibile',
 item('Generazione standard','Esegui python3 tools/k8s_wizard.py --unattended --output ./k8s-generated --set host=quorivio.example.org --set max_upload_mb=100. Conserva solo i valori custom rispetto ai default; non inserire password. Valida le risorse prima di applicarle.'),
 item('Ingress NGINX e HAProxy','Seleziona il controller effettivamente installato. ingressClassName e annotazioni legacy HAProxy differiscono tra controller: controlla manualmente i manifest generati. L’annotazione NGINX proxy-body-size limita la dimensione del body; il backend deve applicare limiti equivalenti.'),
 item('Post-installazione','Usa kubectl kustomize per ispezionare la generazione e kubectl apply -k soltanto dopo convalida. Verifica DNS, TLS, limiti CPU/memoria, Secret esistenti, mount dei volumi e log di readiness. Multi-replica WebSocket resta da collaudare.'),
 item('Gestione delle modifiche','Rigenera i manifest dopo aggiornamenti a URL, classe ingress o dimensione upload. Cambiare un valore nel pannello amministrativo non modifica automaticamente il controller Kubernetes. Conserva il diff dei manifest e predispone rollback.')
),
section('Sicurezza e GDPR: attività amministrative',
 item('Data protection by default','Decidi basi giuridiche e ruoli di titolare/responsabile del trattamento, documenta informative, categorie di dati, fornitori esterni e tempi di conservazione. La piattaforma offre controlli tecnici parziali e non può da sola certificare la conformità.'),
 item('Conservazione','La retention globale iniziale delle sessioni chiuse è 60 giorni. Verifica le regole locali prima di modificarla: audit e backup potrebbero richiedere policy separate. Controlla periodicamente che la pulizia schedulata operi sui dati previsti.'),
 item('Cookie e identità','I partecipanti anonimi usano un cookie tecnico e uno pseudonimo. La finestra di conferma dei cookie necessari va distinta da un consenso per usi opzionali. Le registrazioni locali richiedono approvazione; SSO e MFA sono disponibili; SMTP/SMTPS può essere configurato nelle impostazioni server. Le integrazioni esterne richiedono credenziali e verifica operativa.'),
 item('Accesso ai log e incidenti','Proteggi log e audit evitando password, token e risposte sensibili. Predisponi escalation incidenti, rotazione delle credenziali, revoca delle sessioni e notifiche richieste dal GDPR quando applicabili. Esegui test di ripristino e tabletop exercise.')
),
section('CI/CD e problemi ricorrenti',
 item('GitHub e Docker Hub','Il workflow include gate di qualità, build container e Trivy HIGH/CRITICAL. Pubblica desalvo/quorivio:latest dai push main e il tag versionato dai tag, solo dopo gate e protezioni di production. I secret Docker Hub sono nell’ambiente production.'),
 item('La build fallisce per npm','Controlla che package-lock.json sia presente e coerente se usi npm ci. Il workflow precedente ha disabilitato la cache perché mancava il lockfile; non disabilitare controlli per ottenere un esito verde.'),
 item('Trivy segnala CVE','Leggi il percorso di origine della vulnerabilità e aggiorna/elimina il componente interessato. Il runtime non dovrebbe includere gli strumenti npm di compilazione; non escludere HIGH/CRITICAL senza motivazione e approvazione.'),
 item('Funzioni ancora mancanti','I servizi esterni di login e posta, la convalida del cluster multi-replica e i collaudi browser end-to-end richiedono ancora verifica. La CI non sostituisce il collaudo operativo.')
)]
},
'en': {}
}
# English version mirrors the Italian structure with actionable native instructions.
EXTRA['en']['user']=[
section('Guided walkthrough: from invitation to confirmed vote',
 item('Practice scenario','Requirements: presenter QR code or URL, modern browser with required functional cookies, an active session and an open question. Step 1: open the link. Step 2: verify the session title. Step 3: enter your chosen pseudonym if requested. Step 4: acknowledge necessary cookies. Step 5: submit one answer. Step 6: confirm the success message before leaving.'),
 item('Reopening the browser','Return using the same browser and link; do not erase session cookies. Private browsing, changing devices or clearing site data may prevent recognition. Anonymous access cannot guarantee one vote per natural person.'),
 item('When questions change','Keep the external slide deck in its own app. The Quorivio link follows the current activity. If it does not update, check the connection, refresh once and ask the presenter whether submissions are closed.'),
 item('Live feedback','Aggregate results may be visible or hidden according to presenter settings. No chart on your device does not mean a confirmed response was lost; rely on the response confirmation.')
),
section('Troubleshooting common participation problems',
 item('The QR is not recognized','Use the presenter-provided text URL or session code. Do not disclose nonpublic links outside the event. If the link was revoked, ask the presenter for a new one.'),
 item('No question appears','The activity may not yet be open, or it may have been closed. Do not attempt to bypass an activity window; ask the presenter which question is active.'),
 item('A duplicate vote is suspected','Avoid repeated clicks on Submit. The backend attempts to protect retries; an anonymous pseudonym cannot guarantee real-person uniqueness. Report inconsistencies to the event organizer.'),
 item('Accessibility','Use browser zoom, keyboard navigation and assistive technologies. Request text alternatives for inaccessible images, videos or PDFs; color alone should not determine meaning.')
),
section('Privacy and support',
 item('Necessary cookies','Functional cookies associate a browser with its participant session and help reduce duplicate submissions; the pseudonym is provided by the visitor. Acceptance of necessary cookies is not consent to profiling or advertising.'),
 item('Do not submit sensitive data','Avoid passwords, identity numbers, health information and confidential data in text answers unless the organizer has established a lawful, documented purpose. Some GDPR functions remain incomplete in this development build.'),
 item('Data-subject requests','Contact the instance operator or controller identified in its privacy notice. Provide the event date and pseudonym, but never your password. Organizational procedures determine how requests are handled.')
)]
EXTRA['en']['presenter']=[
section('Pre-event checklist',
 item('One day before','Confirm administrator approval for presenter role. Create the session with a recognizable name and reference date. Review questions, answer choices, QR and public address. Test participation using a second nonauthenticated device.'),
 item('Admission and notice','Choose whether anonymous attendees are allowed and whether they can view aggregates. Explain the pseudonym and necessary cookie flow. Do not claim strong anonymous one-person-one-vote guarantees.'),
 item('Appearance setup','Where available, enter HTTPS logo and background addresses using the basic theme controls. Remote media and the page editor are incomplete. Check readability, image contrast and projection quality on actual hardware.'),
 item('Dry run','Submit a test answer from another device and verify the public results and CSV export. Use a separate session or definition-only duplicate for rehearsals; never pollute production event results.')
),
section('Conducting an event, step by step',
 item('Before opening','Choose your session in the presenter workspace. Download QR as PNG or SVG and insert it in an external PDF/PowerPoint. Keep presenter controls on your private display and public screen in a second tab or device.'),
 item('Start','Start the session, then open the first activity. Present the code and confirm that a phone can submit. Avoid projecting secrets or administrative controls. Configure result visibility deliberately.'),
 item('During voting','Watch submitted counts and avoid unexpected structural edits. Keep existing option identifiers when changing answered questions. Live edit APIs exist, but a complete visual authoring experience is not validated.'),
 item('Close and export','Close each activity before proceeding. End the event session when done, then export CSV and verify access to history. Closed-session retention defaults to a global 60 days, adjustable by administrators.')
),
section('Collaboration, portability and revision control',
 item('Co-presenters','The owner can grant access to approved presenters within the organization using the session API. The complete invite UI, concurrent editing and permissions integration tests are unfinished.'),
 item('Duplicate a session','The duplicate API creates a fresh draft with new invitation credentials and no audience responses. Set an appropriate name and reference date, review contents and circulate only the new QR.'),
 item('Definition import and export','JSON export/import covers questions and layout definitions but not participant responses, uploaded files or complete backups. Review input data and trial imports in a nonproduction environment.'),
 item('Invalidate responses','The API can mark responses to one activity as invalid, excluding them from active aggregates while retaining an audit record. Tell the audience when this changes results. Reanswering after invalidation is not fully supported.')
),
section('Presenter troubleshooting',
 item('Audience cannot connect','Check PUBLIC_BASE_URL, HTTPS, session state, expiration and anonymous admission. QR codes downloaded before a public URL change must be regenerated.'),
 item('Projected results freeze','Check that the question is open and responses were confirmed. Reload the public screen carefully; cross-replica WebSocket synchronization has not been validated.'),
 item('Results do not match the question','Review whether choices changed after submissions started. Do not destroy identifiers linked to responses. Invalidate only with an explicit decision and retain an explanation.'),
 item('CSV cannot be exported','Verify presenter authorization and that the session has results. CSV is available; complete Excel export remains planned. Check encoding and preserve files in access-controlled storage.')
)]
EXTRA['en']['admin']=[
section('First-installation checklist',
 item('Before exposing the instance','Prepare public DNS and valid TLS, strong secrets, PostgreSQL, persistent storage, least-privilege admin access and tested backups. The known demo password 000000 is restricted to explicitly opted-in nonproduction installations.'),
 item('External URL','Set the real HTTPS public address in Administration. Session invitations use it. When it changes, ask presenters to regenerate previously downloaded QR codes and replace old slide assets.'),
 item('Approval workflow','Registration is not approval. Check identity and role need before approving a user or presenter; remove unnecessary access promptly and document approvals.'),
 item('Availability checks','Check /api/health/live, /api/health/ready, database health, and TLS. Reproduce an actual presenter-and-participant workflow. Green CI reported for an earlier revision does not validate every later change.')
),
section('PostgreSQL and recoverability',
 item('Internal deployment','The wizard can generate a PostgreSQL 18.6 StatefulSet and PVC. Plan durable storage, backups, version upgrades and operational monitoring; a single StatefulSet does not provide database high availability.'),
 item('External database','Choose postgres_mode=external and configure host, port, TLS verify-full and Secret references. Validate server identity and CA trust. Never commit DATABASE_URL credentials.'),
 item('Schema migrations','Test migrations on a realistic database snapshot before production. Moving from PostgreSQL 17 to 18 requires a supported major upgrade; changing the container tag alone is insufficient.'),
 item('Backup and restore','Full admin UI export/import is pending. Use supported PostgreSQL tools and consistent backups of external assets, then perform isolated restore drills and document RPO, RTO, encryption and ownership.')
),
section('Repeatable Kubernetes deployment',
 item('Generate manifests','Run python3 tools/k8s_wizard.py --unattended --output ./k8s-generated --set host=quorivio.example.org --set max_upload_mb=100. Review saved custom overrides and ensure credentials never enter the generated configuration.'),
 item('Ingress controllers','Choose NGINX or the actually deployed HAProxy variant. Ingress class and legacy annotation conventions differ. Confirm that upload body-size restrictions align with backend application limits.'),
 item('Apply safely','Review kubectl kustomize output and run kubectl apply -k only after validation. Verify namespace, TLS, Secrets, volumes, resource limits and readiness checks. Cross-replica WebSocket operation is not validated.'),
 item('Changing configuration','Regenerate and diff manifests after public URL, Ingress class or upload size changes. The admin settings UI cannot directly patch a live Kubernetes Ingress; document a rollback procedure.')
),
section('Security and GDPR operating controls',
 item('Privacy governance','Assign controller and processor roles; record legal basis, notices, recipients, subprocessors and retention periods. Current technical controls are partial and cannot themselves establish GDPR compliance.'),
 item('Retention','The initial global period for closed sessions is 60 days. Verify applicable retention duties, backup policy and deletion jobs before changing it. Audit evidence and backup retention may be separate.'),
 item('Cookies and account approval','Anonymous access uses a functional cookie and chosen pseudonym. Necessary cookies are not the same as optional tracking consent. Registered accounts require approval; SSO and MFA are available in the application; SMTP/SMTPS is configurable in server settings. External providers require real-world verification.'),
 item('Logs and incidents','Limit access to audit logs and exclude passwords, tokens and unnecessary response content. Document incident escalation, credential rotation, access revocation and breach reporting rules where applicable.')
),
section('CI/CD and operational troubleshooting',
 item('Publication flow','GitHub Actions runs quality, container build and blocking Trivy HIGH/CRITICAL security gates before production publication to desalvo/quorivio. Protect main and the production environment.'),
 item('npm errors','Use a committed reproducible lockfile with npm ci when available. A previous workflow disabled caching because package-lock.json was absent; avoid weakening quality gates.'),
 item('Trivy findings','Inspect the vulnerable runtime path and update or remove the relevant dependency. Build-only npm tooling should not remain in the runtime; do not silently ignore HIGH or CRITICAL vulnerabilities.'),
 item('Known production blockers','Real provider credentials, SMTP delivery, browser workflows, Kubernetes multi-replica deployment, GDPR evidence and load/security acceptance remain pending.')
)]

# Audience tools: available in development code; full browser/DB integration pending.
for language in ('it','en'):
    if language == 'it':
        EXTRA['it']['user'].append(section('Nuvola di parole e domande moderate (nuovo)',
            item('Proporre una parola','Apri la sessione dal QR, registrati con lo pseudonimo e attendi che il presentatore apra una domanda. Nella sezione Strumenti interattivi scrivi una parola o una breve espressione (massimo 48 caratteri) e seleziona Invia parola. È ammesso un solo contributo per partecipante e domanda.'),
            item('Inviare una domanda Q&A','Nella stessa sezione scrivi una domanda di 5–500 caratteri e premi Invia per moderazione. Si possono inviare al massimo tre domande per attività. La domanda non appare al pubblico finché un presentatore non la approva.'),
            item('Votare una domanda approvata','Premi Aggiorna domande approvate per vedere gli interventi pubblicati. Usa Vota accanto a una domanda interessante: è consentito un voto per domanda e partecipante. Non puoi vedere le domande ancora da moderare.'),
            item('Limitazioni di verifica','Queste funzioni sono state introdotte nella build di sviluppo, ma richiedono ancora un collaudo con PostgreSQL reale, più smartphone e verifica WebSocket.')))
        EXTRA['it']['presenter'].append(section('Moderazione Q&A e nuvola di parole (nuovo)',
            item('Raccogliere parole','Apri una attività della sessione. Nell’area Moderazione Q&A e nuvola di parole seleziona Aggiorna. L’elenco mostra i termini normalizzati e il loro numero di occorrenze, in ordine decrescente; il contributo resta legato alla singola attività.'),
            item('Approvare domande','Le domande arrivano inizialmente con stato pending. Leggi il testo nella stessa area e seleziona Approva per mostrarlo ai partecipanti, oppure Rifiuta per escluderlo dalla vista pubblica. Le domande rimangono persistenti per l’audit della sessione.'),
            item('Consultare i voti','Premi Aggiorna per ricalcolare il totale dei voti di ogni domanda. Il conteggio viene mostrato insieme al testo e allo stato di moderazione. Non divulgare dati identificativi dei partecipanti sullo schermo pubblico.'),
            item('Limiti operativi','La moderazione richiede aggiornamento manuale e non include ancora una coda push per i moderatori. Sono necessari test multiutente, anti-spam e accessibilità prima dell’uso produttivo.')))
        EXTRA['it']['admin'].append(section('Q&A e parole: sicurezza e manutenzione',
            item('Persistenza','Lo schema PostgreSQL contiene audience_words, audience_questions e audience_question_votes. Le tabelle sono legate alle sessioni e vengono rimosse insieme alla sessione via CASCADE. Applicare lo schema prima di avviare il backend aggiornato.'),
            item('Autorizzazioni','L’invio è ammesso solo con cookie partecipante valido nella sessione attiva e attività aperta. Approvazione, rifiuto e statistiche complete richiedono l’autenticazione di un presentatore autorizzato.'),
            item('GDPR e conservazione','Le parole e le domande sono contenuti generati dal pubblico: predisporre informativa, moderazione e retention, evitando raccolte non necessarie di dati personali. Restano necessari test di concorrenza e abuso.')))
    else:
        EXTRA['en']['user'].append(section('Word cloud and moderated Q&A (new)',
            item('Contribute a word','Join using the QR code and your pseudonym. When the presenter opens an activity, type one word or short phrase of up to 48 characters under Interactive tools and press Submit word. One contribution is allowed per participant per activity.'),
            item('Ask a question','Type 5–500 characters and select Submit for moderation. Up to three questions are allowed per activity. Your question remains private until approved by an authorized presenter.'),
            item('Upvote a question','Choose Refresh approved questions and use Upvote. Each participant can upvote a given approved question once.'),
            item('Verification limits','These functions exist in the development build but still require real PostgreSQL, smartphone and WebSocket integration testing.')))
        EXTRA['en']['presenter'].append(section('Moderate Q&A and word cloud (new)',
            item('Collect words','Open an activity and select Refresh in the Q&A and word cloud panel. The list contains normalized words and their frequency, ordered by contribution count.'),
            item('Moderate questions','New questions start as pending. Select Approve to publish or Reject to withhold a question. The moderation state is persistent.'),
            item('Review upvotes','Refresh the panel to read vote totals alongside each question and its status. Do not expose participant identifiers on the public display.'),
            item('Operational limits','Moderator push updates, concurrency and anti-abuse testing are not finished. Do not treat the feature as production validated.')))
        EXTRA['en']['admin'].append(section('Q&A and word cloud operations',
            item('Persistence','The audience_words, audience_questions and audience_question_votes PostgreSQL tables belong to sessions, with cascading deletion. Apply the schema before starting the upgraded backend.'),
            item('Authorization','Posting requires a valid participant cookie and an open activity in an active session. Moderation and private analytics require authenticated presenter access.'),
            item('GDPR and retention','Audience questions and words may contain personal data. Configure appropriate notices, moderation and retention, and test concurrency and abuse controls before production.')))

# New operator instructions incorporated in the next bilingual manual refresh.
for language in ('it','en'):
    chapter = ('Upload in streaming e controlli', [('Caricamento file','Il caricamento usa scrittura progressiva su volume privato e verifica firma, lunghezza e limite di 100 MB; non lasciare il browser prima della conferma. La scansione antivirus è inclusa nel deployment Compose/Helm, ma lo storage condiviso resta da integrare.')] ) if language=='it' else ('Streaming uploads and checks', [('Uploading files','Uploads are progressively written to private storage; type signature, length and default 100 MB limit are checked. Keep the browser open until confirmation. The Compose/Helm deployment bundles antivirus scanning; shared storage is still pending.')])
    for role in ('user','presenter','admin'):
        EXTRA[language][role].append(chapter)

# Newly delivered, explicitly scoped authentication service procedures.
EXTRA['it']['presenter'].append(section('MFA TOTP per il presentatore',
 item('Attivare un autenticatore','Eseguire accesso locale, scegliere Configura MFA, importare il segreto o il link otpauth in una app di autenticazione e confermare il primo codice valido. Dal login successivo inserire email, password e le sei cifre correnti.'),
 item('Disattivazione e recupero','La disattivazione richiede password e codice TOTP. Sono disponibili codici di recupero monouso, mostrati una sola volta: conservarli offline in modo protetto.')))
EXTRA['en']['presenter'].append(section('Presenter TOTP MFA',
 item('Enable an authenticator','Log in locally, choose Configure MFA, import the secret or otpauth link and confirm a valid code. Subsequent logins require password plus the current six-digit code.'),
 item('Disable and recovery','Deactivation requires the password and a valid TOTP code. One-time recovery codes are generated and shown once: store them securely offline.')))
EXTRA['it']['admin'].append(section('Controllo SMTPS e sicurezza degli account',
 item('Configurazione SMTP','Aprire Impostazioni server e compilare host, porta SMTPS, account, password e mittente. Le credenziali sono cifrate nel database; la password non viene restituita al browser. Verificare la configurazione e inviare una mail di prova.'),
 item('Test e limitazioni','SMTPS richiede TLS con certificato valido. STARTTLS non è abilitato in questa configurazione. Reset password via email e codici di recupero MFA sono implementati, ma la consegna effettiva deve essere collaudata. Il servizio non è certificato AgID o GDPR.'),
 item('Chiave AUTH_SECRET','Conservare una chiave segreta stabile: il suo cambiamento rende illeggibili i segreti MFA cifrati. Valutare una migrazione protetta prima della rotazione.')))
EXTRA['en']['admin'].append(section('SMTPS and account security',
 item('SMTP configuration','Open Server Settings to configure SMTP host, implicit-TLS port, account, password and sender. Credentials are encrypted at rest; the password is never returned to the browser. Send a test message to verify delivery.'),
 item('Tests and restrictions','SMTPS uses certificate-validated TLS; actual mail delivery still needs acceptance testing; email reset and one-time MFA recovery codes are implemented. STARTTLS is not enabled.'),
 item('AUTH_SECRET retention','Keep a stable protected AUTH_SECRET. Changing it without migration prevents decryption of stored MFA secrets.')))

# Antivirus scanning: operator responsibilities and limits for this cumulative.
EXTRA['it']['admin'].append(section('Scansione antivirus degli allegati',
 item('Attivazione ClamAV','Avviare Quorivio via Compose/Helm: lo stack include automaticamente ClamAV su rete privata; conserva e aggiorna le firme, e imposta QUORIVIO_AV_REQUIRED=true. Senza scanner disponibile il backend deve rifiutare gli upload invece di considerarli sicuri.'),
 item('Verifica e operatività','Eseguire prove reali con un file di test innocuo e con il pattern di prova EICAR in un ambiente autorizzato. Verificare i log, l’eliminazione degli allegati rifiutati e l’assenza di record nel database. Questo controllo non è ancora collaudato su un servizio ClamAV reale.'),
 item('Limitazioni','La scansione antivirus non sostituisce la validazione MIME, le politiche GDPR o l’isolamento della conversione documenti. Lo scanner non è incluso nell’installazione di default. Consultare docs/ANTIVIRUS_UPLOADS.it.md.')
))
EXTRA['en']['admin'].append(section('Attachment antivirus scanning',
 item('Enable ClamAV','Start the managed Compose/Helm deployment: ClamAV is bundled on the private network with persistent signature updates and QUORIVIO_AV_REQUIRED=true. With mandatory scanning a missing scanner must block the upload, not silently accept it.'),
 item('Operational checks','In an authorized test environment, test benign files and the EICAR test pattern, examine the logs, and verify rejected assets leave no database record. This feature is not yet validated with a real ClamAV deployment.'),
 item('Limits','Malware scanning does not replace MIME checks, GDPR processes or isolated document conversion. ClamAV is bundled with Compose/Helm; real-runtime validation remains necessary. See docs/ANTIVIRUS_UPLOADS.en.md.')
))

# 2026-10-24 verified-source supplement; not a claim of browser/production acceptance.
EXTRA['it']['presenter'].append(section('Archivi portabili e duplicazione sicura',
 item('Esportazione completa della sessione','.quorivio include definizioni e asset referenziati, escludendo utenti, codici di accesso, risposte e dati dei partecipanti. Il formato JSON precedente non include i media.'),
 item('Importazione o duplicazione','L’importazione e la duplicazione interna producono una nuova bozza, nuove credenziali e nuovi identificativi globali per i file multimediali. I widget che condividono una foto continuano a condividere la nuova copia.'),
 item('Collaudi ancora necessari','Eseguire un ciclo di esportazione e reimportazione su un’altra istanza PostgreSQL con storage indipendente. Verificare immagini, sfondi, PDF e video, e che i dati dei partecipanti non compaiano nel nuovo archivio.')))
EXTRA['en']['presenter'].append(section('Portable archives and safe duplication',
 item('Self-contained session export','A .quorivio file embeds referenced media plus session definitions, but excludes identities, passwords, responses, join codes and audience data. Legacy JSON exports do not contain media.'),
 item('Import or duplicate','Importing or internally duplicating creates a new draft, new joining credentials and fresh global UUIDs for all media. Shared references within theme/page/results remain linked to the new copy.'),
 item('Acceptance outstanding','Perform cross-instance import with independent PostgreSQL and asset storage, check backgrounds, PDF and video media, and verify that the bundle contains no audience information.')))
EXTRA['it']['admin'].append(section('MFA email con conferma e impostazioni atomiche',
 item('Iscrizione MFA email','In Sicurezza / MFA, inserire la password e richiedere il codice di iscrizione. Il fattore email NON diventa attivo finché il codice di sei cifre ricevuto nella casella di posta non viene confermato entro dieci minuti. TOTP resta indipendente.'),
 item('Limiti e disattivazione','Il backend accetta al massimo cinque errori per codice e tre richieste d’iscrizione al minuto per account. La conferma o la disattivazione revoca le sessioni precedenti, richiedendo un nuovo accesso.'),
 item('Impostazioni server e foto','Le modifiche combinate a URL pubblico, retention e limite upload vengono validate integralmente e salvate in un’unica transazione. Le fotografie private vengono sostituite con blocco per utente e i file precedenti rimossi. I collaudi multi-replica e browser restano aperti.'),
 item('Procedura di accettazione','Provare SMTP reale, codice errato/scaduto, rinnovo dopo revoca, login TOTP/email indipendenti, aggiornamenti amministrativi con valori non validi e collisioni di importazione .quorivio. La CI aggiunge un test HTTP PostgreSQL, ma la prima esecuzione sulla nuova revisione è ancora da verificare.')))
EXTRA['en']['admin'].append(section('Email MFA confirmation and atomic settings',
 item('Email MFA enrollment','In Security/MFA, enter the current password to request an enrollment code. Email MFA is NOT enabled until the six-digit email code is confirmed within ten minutes. TOTP remains independently configurable.'),
 item('Limits and disable','Five invalid codes exhaust an enrollment. No more than three enrollments per account per minute may be issued. Confirmation or disabling revokes existing sessions, requiring sign-in again.'),
 item('Server settings and profile images','Public URL, retention and upload limit changes are validated together and written atomically. Private profile photos use per-user row locking for replace/delete and dispose of superseded files. Multi-replica and browser acceptance are still outstanding.'),
 item('Operator checks','Test a real SMTP server, expired and incorrect codes, login using each enabled factor, invalid combined settings updates and .quorivio UUID collisions. A PostgreSQL HTTP CI test has been added but has not been run on the new revision yet.')))
