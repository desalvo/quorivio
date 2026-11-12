# Quorivio RC325 — Server settings tabs and interface language / Schede impostazioni e lingua

## Italiano

- La pagina **Impostazioni server** ha sette tab: Generale, Autenticazione, Posta elettronica, Spazio disco, Convertitore, Backup e Audit. Un solo pannello è visibile per volta; tab accessibili via click/tocco e frecce sinistra/destra, Home e Fine. I pannelli inattivi sono nascosti anche al focus, ma restano montati per non perdere le bozze LDAP/OIDC/social, SMTP e backup.
- Il selettore lingua nell'intestazione permette di passare fra **italiano e inglese**; la preferenza viene memorizzata localmente sul dispositivo. È aggiornata anche la lingua del documento HTML.
- Oltre ai componenti già bilingui, un catalogo locale IT/EN copre navigazione, comandi editor, menu contestuali, opzioni a tendina, etichette, attributi ARIA, placeholder, pagine di gestione, impostazioni e molti messaggi. Non vengono usati servizi di traduzione di terze parti e i contenuti privati non vengono inviati a provider esterni.
- L'adattamento dei componenti legacy interviene solo sui nodi di testo e sugli attributi UI: preserva campi editabili e valori inseriti, senza sostituire componenti React o ricaricare la pagina. Le etichette non presenti nel catalogo mantengono l'originale italiano fino al completamento della localizzazione. Le eventuali stringhe composte dinamicamente vanno aggiunte esplicitamente al catalogo o ai componenti nuovi, senza tradurre il contenuto degli utenti.
- Controlli di regressione: node --experimental-strip-types --test apps/web/test/rc325-*.test.ts; build web e full CI prima della release.

## English

- **Server settings** now uses seven tabs: General, Authentication, Email, Disk Space, Converter, Backup and Audit. One panel is visible at a time, with pointer/touch and Left/Right/Home/End keyboard navigation. Inactive panels remain mounted to retain unsaved LDAP/OIDC/social, SMTP and backup drafts, but are not keyboard-focusable.
- The header language toggle switches between **Italian and English**, persists its preference locally, and updates the document language.
- A local IT/EN translation catalogue supplements existing bilingual components and covers navigation, editor/context menus, dropdown options, ARIA labels, form placeholders, administration pages and many interface messages. No third-party translation or transfer of user content is involved.
- Legacy UI localization updates text nodes and UI attributes without replacing React DOM subtrees, editable fields, or user-entered values. Unmapped messages retain their original Italian text until explicitly localized; dynamic strings should be handled by explicit copy keys.
- Regression checks: Node TS tests, web build and gated full CI.
