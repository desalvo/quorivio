/** RC325: client-only IT/EN copy for legacy menus and administrator panels.
 * No external translation service or user content is sent anywhere.
 * Text nodes are translated without replacing DOM elements, preserving React
 * event handlers and input values. Use explicit keyed copy for new components.
 */
export type UiLanguage='it'|'en';
export const UI_LANGUAGE_STORAGE='quorivio:ui-language';
const englishLabels:Record<string,string>={
  "Sezioni": "Sections",
  "Nuova sessione": "New session",
  "Apri sessione": "Open session",
  "Calendario": "Calendar",
  "Profilo presentatore": "Presenter profile",
  "Sicurezza / MFA": "Security / MFA",
  "SSO / Identità": "SSO / Identity",
  "Gestione utenti": "User management",
  "Impostazioni server": "Server settings",
  "Autenticazione a due fattori": "Two-factor authentication",
  "Identità federate": "Federated identities",
  "Gestisci questa funzionalità dal pannello dedicato a sinistra.": "Manage this feature from the dedicated panel on the left.",
  "Le idee prendono vita.": "Bring ideas to life.",
  "Seleziona una sessione o creane una nuova.": "Select a session or create a new one.",
  "Logout": "Sign out",
  "Accedi": "Sign in",
  "Registrati": "Register",
  "Torna al login": "Back to sign in",
  "Password dimenticata? / Forgot password?": "Forgot password?",
  "Accesso locale · Configurazione amministratore": "Local sign-in · Administrator settings",
  "Nuovi account soggetti all'approvazione dell'amministratore.": "New accounts require administrator approval.",
  "Accedi con": "Sign in with",
  "PRESENTER CONTROL ROOM": "PRESENTER CONTROL ROOM",
  "Sessione": "Session",
  "Sessioni": "Sessions",
  "Pagine e contenuti": "Pages and content",
  "Partecipanti": "Participants",
  "Risultati": "Results",
  "Statistiche": "Statistics",
  "Impostazioni": "Settings",
  "Opzioni": "Options",
  "Aggiungi": "Add",
  "Salva": "Save",
  "Annulla": "Cancel",
  "Rimuovi": "Remove",
  "Elimina": "Delete",
  "Chiudi": "Close",
  "Indietro": "Back",
  "Avanti": "Next",
  "Precedente": "Previous",
  "Successiva": "Next",
  "← Precedente": "← Previous",
  "Successiva →": "Next →",
  "Riprova": "Retry",
  "Aggiorna": "Refresh",
  "Aggiorna ora": "Refresh now",
  "Caricamento…": "Loading…",
  "Crea": "Create",
  "Duplica": "Duplicate",
  "Rinomina": "Rename",
  "Apri pagina": "Open page",
  "Rinomina pagina": "Rename page",
  "Duplica pagina": "Duplicate page",
  "Rinomina pagine selezionate": "Rename selected pages",
  "Duplica pagine selezionate": "Duplicate selected pages",
  "pagina": "page",
  "pagine selezionate": "selected pages",
  "Crea e importa pagine": "Create and import pages",
  "Nuova pagina prima": "New page before",
  "Nuova pagina dopo": "New page after",
  "Importa PDF/PPTX…": "Import PDF/PPTX…",
  "Importa layout JSON": "Import JSON layout",
  "Ordina pagine": "Reorder pages",
  "Menu della pagina": "Page menu",
  "Menu pagina": "Page menu",
  "Proprietà widget": "Widget properties",
  "Formato widget": "Widget formatting",
  "Formato": "Formatting",
  "Pagina": "Page",
  "Pagine": "Pages",
  "Widget": "Widget",
  "Risposte": "Answers",
  "Risposta": "Answer",
  "Domanda": "Question",
  "Domande": "Questions",
  "Testo": "Text",
  "Titolo": "Title",
  "Descrizione": "Description",
  "Data": "Date",
  "Dimensione": "Size",
  "Colore": "Color",
  "Animazione": "Animation",
  "Nessuno": "None",
  "Nessuna": "None",
  "Tutte": "All",
  "Disattivato": "Disabled",
  "Attivato": "Enabled",
  "Abilitato": "Enabled",
  "Disabilitato": "Disabled",
  "Conferma": "Confirm",
  "Modifica": "Edit",
  "Continua": "Continue",
  "Nuovo": "New",
  "Invia": "Send",
  "Copia": "Copy",
  "Taglia": "Cut",
  "Incolla": "Paste",
  "Scarica": "Download",
  "Carica": "Upload",
  "Importa": "Import",
  "Esporta": "Export",
  "Prova": "Test",
  "Prova presentazione": "Rehearse presentation",
  "Anteprima": "Preview",
  "Visualizza": "View",
  "Presenta": "Present",
  "Presentatore": "Presenter",
  "Partecipante": "Participant",
  "Desktop": "Desktop",
  "Smartphone": "Smartphone",
  "Affiancate": "Side by side",
  "Torna alle sessioni": "Back to sessions",
  "Duplica sessione": "Duplicate session",
  "Elimina sessione": "Delete session",
  "Apri": "Open",
  "Avvia": "Start",
  "Pausa": "Pause",
  "Riprendi": "Resume",
  "Riavvia countdown": "Restart countdown",
  "Riavvia timer": "Restart timer",
  "Torna alla dashboard": "Back to dashboard",
  "Impostazioni pagina e risultati": "Page and results settings",
  "Proiezioni indipendenti": "Independent projections",
  "Pagina per i partecipanti": "Audience page",
  "Questa stessa pagina": "This page",
  "Salta sullo schermo presentatore": "Skip on presenter display",
  "Impostazioni pagina": "Page settings",
  "Testo personalizzato": "Custom text",
  "Modifica titolo": "Edit title",
  "Aggiungi opzione": "Add option",
  "Aggiungi domanda indipendente": "Add independent question",
  "Aggiungi opzione di risposta": "Add answer option",
  "Risposta obbligatoria": "Answer required",
  "Tipo di risposta": "Answer type",
  "Scelta singola": "Single choice",
  "Scelta multipla": "Multiple choice",
  "Testo libero": "Free text",
  "Allegato": "Attachment",
  "Allegati": "Attachments",
  "Carica nuovo file": "Upload new file",
  "Sostituisci file": "Replace file",
  "Nessun file": "No file",
  "Elimina selezione": "Delete selection",
  "Duplica selezione": "Duplicate selection",
  "Taglia selezione": "Cut selection",
  "Copia selezione": "Copy selection",
  "Incolla selezione": "Paste selection",
  "Porta selezione davanti": "Bring selection to front",
  "Porta selezione dietro": "Send selection to back",
  "Un livello avanti": "Bring forward one layer",
  "Un livello indietro": "Send backward one layer",
  "Porta avanti": "Bring forward",
  "Porta indietro": "Send backward",
  "Strumenti di selezione e allineamento": "Selection and alignment tools",
  "Allineamento orizzontale e verticale": "Horizontal and vertical alignment",
  "Carattere": "Font",
  "Grassetto": "Bold",
  "Corsivo": "Italic",
  "Sottolineato": "Underline",
  "Barrato": "Strikethrough",
  "Paragrafo": "Paragraph",
  "Centro": "Center",
  "Destra": "Right",
  "Sinistra": "Left",
  "Sfondo": "Background",
  "Riempimento": "Fill",
  "Tinta unita": "Solid",
  "Colore di sfondo": "Background color",
  "Colore riempimento": "Fill color",
  "Nessun riempimento": "No fill",
  "Senza riempimento": "No fill",
  "Riempimento trasparente": "Transparent fill",
  "Colore bordo": "Border color",
  "Tipo di bordo": "Border type",
  "Stile bordo": "Border style",
  "Bordo visibile": "Visible border",
  "Nessun bordo": "No border",
  "Continuo": "Solid",
  "Tratteggiato": "Dashed",
  "Puntinato": "Dotted",
  "Spessore bordo (pt)": "Border width (pt)",
  "Spessore (pt)": "Width (pt)",
  "Gradiente": "Gradient",
  "Secondo colore": "Second color",
  "Secondo colore del gradiente": "Second gradient color",
  "Tema": "Theme",
  "Tema visivo": "Visual theme",
  "Effetto": "Effect",
  "Effetto speciale": "Special effect",
  "Dissolvenza": "Fade",
  "Scorrimento": "Slide",
  "Fluttuante": "Floating",
  "Inclinazione": "Tilt",
  "Studio": "Studio",
  "Vetro": "Glass",
  "Vivace": "Vivid",
  "Minimale": "Minimal",
  "Studio · elegante": "Studio · elegant",
  "Vetro · luminoso": "Glass · bright",
  "Pop · creativo": "Pop · creative",
  "Essenziale · sobrio": "Essential · understated",
  "Fluttuazione delicata": "Gentle float",
  "Bagliore": "Glow",
  "Profondità 3D": "3D depth",
  "Quadrante timer": "Timer dial",
  "Clessidra": "Hourglass",
  "Orologio circolare": "Circular clock",
  "Digitale": "Digital",
  "Forma": "Shape",
  "Forma del widget": "Widget shape",
  "Direzione della linea": "Line direction",
  "Orizzontale": "Horizontal",
  "Verticale": "Vertical",
  "Frecce della linea": "Line arrows",
  "Senza frecce": "No arrows",
  "Freccia iniziale": "Start arrow",
  "Freccia finale": "End arrow",
  "Entrambe le frecce": "Both arrows",
  "Preset di forma": "Shape preset",
  "Tipo riempimento": "Fill type",
  "Solido": "Solid",
  "Immagine della libreria": "Library image",
  "Immagine già associata": "Image already linked",
  "Ritaglio immagine": "Crop image",
  "Ripristina immagine intera": "Restore full image",
  "Spessore contorno (pt)": "Outline width (pt)",
  "Colore contorno": "Outline color",
  "Nessun contorno": "No outline",
  "Tratteggio contorno": "Outline dash",
  "Visualizzazione risultati": "Results display",
  "Barre": "Bars",
  "Torta": "Pie",
  "Tabella": "Table",
  "Nuvola": "Cloud",
  "Nuvola animata": "Animated cloud",
  "Gauge semicircolare": "Semicircular gauge",
  "Bolle emoji (reazioni)": "Emoji bubbles (reactions)",
  "Domanda principale": "Main question",
  "Titolo widget": "Widget title",
  "Widget intero": "Entire widget",
  "Pulsante di invio": "Submit button",
  "Numero pagina": "Page number",
  "Ambito": "Scope",
  "Manuale": "Manual",
  "Minimo": "Minimum",
  "Massimo": "Maximum",
  "Media": "Average",
  "Ordinamento": "Sort order",
  "Risposte in tempo reale": "Live answers",
  "Risultati in tempo reale": "Live results",
  "Domande del pubblico": "Audience questions",
  "Parole più frequenti": "Most frequent words",
  "Moderazione Q&A e nuvola di parole": "Q&A and word cloud moderation",
  "Seleziona pagina": "Select page",
  "Deseleziona": "Deselect",
  "Filtro domande": "Filter questions",
  "In attesa": "Pending",
  "Approvate": "Approved",
  "Rifiutate": "Rejected",
  "Approva": "Approve",
  "Rifiuta": "Reject",
  "Invia risposta": "Submit answer",
  "Invia domanda": "Submit question",
  "La tua domanda": "Your question",
  "Invia per moderazione": "Send for moderation",
  "Invia parola": "Submit word",
  "Invia domanda di prova": "Submit test question",
  "Riprova grafico": "Retry chart",
  "Nessuna risposta per questo widget.": "No answers for this widget.",
  "Nessuna reazione ancora registrata.": "No reactions recorded yet.",
  "Nessuna risposta ancora registrata per questa sorgente.": "No answers recorded for this source yet.",
  "Ancora nessuna parola.": "No words yet.",
  "Nessuna domanda approvata.": "No approved questions.",
  "Nessuna domanda in questa categoria.": "No questions in this category.",
  "Dati di simulazione": "Simulated data",
  "Ricomincia prova": "Restart rehearsal",
  "× Chiudi": "× Close",
  "✕ Esci": "✕ Exit",
  "Generale": "General",
  "Autenticazione": "Authentication",
  "Posta elettronica": "Email",
  "Spazio disco": "Disk space",
  "Spazio disco e allarmi": "Disk space and alerts",
  "Convertitore": "Converter",
  "Backup": "Backup",
  "Audit": "Audit",
  "Audit amministrativo": "Administrative audit",
  "Audit delle operazioni": "Operations audit",
  "Configurazione server": "Server configuration",
  "Server SMTP": "SMTP server",
  "Porta SMTP": "SMTP port",
  "Utente SMTP": "SMTP user",
  "Password SMTP (lasciare vuota per conservare quella precedente)": "SMTP password (leave blank to keep existing)",
  "Email mittente (indirizzo email valido)": "Sender email (valid email address)",
  "Trasporto": "Transport",
  "Nome del mittente": "Sender name",
  "SMTP - STARTTLS obbligatorio": "SMTP - STARTTLS required",
  "SMTPS - TLS implicito": "SMTPS - implicit TLS",
  "Configurazione SMTP cifrata. Scegli TLS implicito (di norma porta 465) oppure STARTTLS obbligatorio (di norma porta 587): la password è cifrata nel database e non viene mai restituita dal server.": "Encrypted SMTP settings. Select implicit TLS (usually port 465) or mandatory STARTTLS (usually port 587). Passwords are encrypted in the database and never returned by the server.",
  "Occupazione disco e allarmi": "Disk usage and alerts",
  "Caricamento metriche disco…": "Loading disk metrics…",
  "Misura non disponibile": "Measurement unavailable",
  "Non disponibile": "Unavailable",
  "Attivo e pronto": "Active and ready",
  "Abilitato, worker non raggiungibile": "Enabled, worker unreachable",
  "Convertitore PDF / PowerPoint (worker isolato)": "PDF / PowerPoint converter (isolated worker)",
  "Abilita importazione PDF/PPTX": "Enable PDF/PPTX imports",
  "Disabilita importazione PDF/PPTX": "Disable PDF/PPTX imports",
  "Verifica stato worker": "Check worker status",
  "Caricamento stato convertitore…": "Loading converter status…",
  "Salva impostazioni": "Save settings",
  "URL esterna HTTPS": "External HTTPS URL",
  "Giorni conservazione sessioni chiuse": "Closed session retention (days)",
  "Limite upload (MB, 1–1024)": "Upload limit (MB, 1–1024)",
  "Dopo una modifica del limite rigenera e applica i manifest Ingress Kubernetes.": "After changing the limit, regenerate and apply the Kubernetes Ingress manifests.",
  "Account": "Account",
  "Utente": "User",
  "Utenti": "Users",
  "Ruolo": "Role",
  "Amministratore": "Administrator",
  "Ricerca": "Search",
  "Salva utente": "Save user",
  "Utente salvato": "User saved",
  "Elimina account": "Delete account",
  "Profilo utente e presentatore": "User and presenter profile",
  "Nome visualizzato": "Display name",
  "Nickname (univoco)": "Nickname (unique)",
  "Salva profilo": "Save profile",
  "Elimina foto": "Delete photo",
  "Foto profilo": "Profile photo",
  "Aggiornamento foto in corso…": "Updating photo…",
  "Foto aggiornata": "Photo updated",
  "Foto rimossa": "Photo removed",
  "Profilo salvato": "Profile saved",
  "Usa Gravatar per la foto del mio account": "Use Gravatar for my profile photo",
  "Importa / aggiorna Gravatar": "Import / refresh Gravatar",
  "Aggiungi o modifica una foto su Gravatar": "Add or change a photo on Gravatar",
  "Collegamento LDAP": "LDAP account linking",
  "Collega identità LDAP": "Link LDAP identity",
  "Utente LDAP": "LDAP user",
  "Password LDAP": "LDAP password",
  "Password corrente": "Current password",
  "Disattiva MFA": "Disable MFA",
  "Attiva MFA": "Enable MFA",
  "Codice MFA per disattivare": "MFA code to disable",
  "Copia codici": "Copy codes",
  "Li ho salvati": "I saved them",
  "Password": "Password",
  "Email": "Email",
  "Verifica": "Check",
  "Salvataggio…": "Saving…",
  "Salvataggio in corso…": "Saving…",
  "Stato": "Status",
  "Sì": "Yes",
  "No": "No",
  "Pronto": "Ready",
  "Non pronto": "Not ready",
  "Completa": "Complete",
  "Incompleta": "Incomplete",
  "Disabilita": "Disable",
  "Abilita": "Enable",
  "Non approvato": "Not approved",
  "Approvato": "Approved"
};
export function translateUiText(value:string,language:UiLanguage):string{
 if(language==='it'||!value)return value;
 const match=/^(\s*)([\s\S]*?)(\s*)$/.exec(value);
 if(!match)return value;
 const source=match[2];
 const found=englishLabels[source]??(
  /^Rinomina (pagina|pagine selezionate) \(R\)$/.test(source)?source.replace('Rinomina','Rename').replace('pagina','page').replace('pagine selezionate','selected pages'):
  /^Duplica (pagina|pagine selezionate) \(D\)$/.test(source)?source.replace('Duplica','Duplicate').replace('pagina','page').replace('pagine selezionate','selected pages'):
  undefined
 );
 return match[1]+(found??source)+match[3];
}
export function preferredUiLanguage():UiLanguage{
 try{return globalThis.localStorage?.getItem(UI_LANGUAGE_STORAGE)==='en'?'en':'it'}catch{return 'it'}
}
type TextCopy={original:string;rendered:string};
type AttrCopy={original:string;rendered:string};
/** Install on the app body: includes menus portalled outside #root.
 * Never rewrite inputs, editable widget text or saved slide contents.
 * Disconnect and restore old labels before switching back to Italian.
 */
export function activateUiLanguage(language:UiLanguage):()=>void{
 if(typeof document==='undefined')return ()=>{};
 document.documentElement.lang=language;
 try{localStorage.setItem(UI_LANGUAGE_STORAGE,language)}catch{/* private browsing */}
 if(language==='it')return ()=>{};
 const textCopies=new Map<Text,TextCopy>();
 const attrCopies=new Map<Element,Map<string,AttrCopy>>();
 const skip=(element:Element|null)=>!element||!!element.closest('script,style,code,pre,svg,canvas,[contenteditable],[data-ui-locale-ignore],.widget-fit-content,.page-editor-preview-title,.page-editor-preview-widget');
 const withinApp=(element:Element|null)=>!!element?.closest('#root,.page-editor-thumb-menu-floating,.editor-floating-scope,.editor-floating-panel,.rehearsal-dialog');
 function visitText(node:Text){
  const parent=node.parentElement;
  if(skip(parent)||!withinApp(parent))return;
  const current=node.nodeValue||'';
  const previous=textCopies.get(node);
  const original=previous&&(current===previous.rendered||current===previous.original)?previous.original:current;
  const rendered=translateUiText(original,language);
  if(rendered!==original)textCopies.set(node,{original,rendered});else textCopies.delete(node);
  if(current!==rendered)node.nodeValue=rendered;
 }
 const ATTRIBUTES=['aria-label','title','placeholder'];
 function visitAttributes(element:Element){
  if(skip(element)||!withinApp(element))return;
  for(const name of ATTRIBUTES){
   const current=element.getAttribute(name);if(current===null)continue;
   const previous=attrCopies.get(element)?.get(name);
   const original=previous&&(current===previous.rendered||current===previous.original)?previous.original:current;
   const rendered=translateUiText(original,language);
   if(rendered!==original){
    let record=attrCopies.get(element);if(!record){record=new Map();attrCopies.set(element,record)}
    record.set(name,{original,rendered});
   }else attrCopies.get(element)?.delete(name);
   if(current!==rendered)element.setAttribute(name,rendered);
  }
 }
 function visit(node:Node){
  if(node.nodeType===Node.TEXT_NODE){visitText(node as Text);return}
  if(node.nodeType!==Node.ELEMENT_NODE)return;
  const element=node as Element;
  if(skip(element))return;
  visitAttributes(element);
  const walker=document.createTreeWalker(element,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT);
  let descendant:Node|null;
  while((descendant=walker.nextNode())){
   if(descendant.nodeType===Node.TEXT_NODE)visitText(descendant as Text);
   else visitAttributes(descendant as Element);
  }
 }
 visit(document.body);
 const observer=new MutationObserver(mutations=>{
  for(const mutation of mutations){
   if(mutation.type==='characterData'){visit(mutation.target);continue}
   if(mutation.type==='attributes'){visitAttributes(mutation.target as Element);continue}
   for(const added of mutation.addedNodes)visit(added);
  }
 });
 observer.observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:ATTRIBUTES});
 return ()=>{
  observer.disconnect();
  for(const [node,copy] of textCopies)if(node.nodeValue===copy.rendered)node.nodeValue=copy.original;
  for(const [element,record] of attrCopies)for(const [name,copy] of record)if(element.getAttribute(name)===copy.rendered)element.setAttribute(name,copy.original);
 };
}
