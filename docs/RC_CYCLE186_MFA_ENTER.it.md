# Quorivio 0.1.0-dev — RC186 — Conferma TOTP con Invio

## Modifica

La sfida di autenticazione a due fattori ora è un vero modulo HTML con `onSubmit` React. Quando il cursore è nel campo **Codice autenticatore** e il TOTP è valido per lunghezza (sei cifre), **Invio/Enter** attiva esattamente la stessa verifica del pulsante **Verifica**. Non occorre spostare il mouse o toccare il pulsante.

Il modulo condiviso conserva Email MFA e codici di recupero: anche questi possono essere confermati con Invio. I pulsanti per scegliere il metodo, mostrare il recupero e annullare rimangono esplicitamente `type="button"`, per evitare invii involontari. Il pulsante Verifica è il solo `type="submit"` del modulo.

Una guardia `useRef` e lo stato di caricamento bloccano richieste concorrenti quando l'utente preme Invio ripetutamente o alterna Invio e clic. Il codice non viene spedito se incompleto; se il server rifiuta la verifica, il modulo resta disponibile e si può riprovare, da tastiera o con il pulsante. Gli endpoint e la logica crittografica del TOTP non cambiano.

## Verifiche

- Test Python anticipati sulla struttura del form, validazione, protezione invii ripetuti e mutazioni negative.
- Test Playwright **sul React compilato**, eseguito nella CI dopo la build: a 1440 e 390 px, TOTP con Invio, codice incompleto, doppia pressione, errore e nuovo tentativo; Email MFA e codice di recupero con Invio; pulsante di verifica tradizionale.
- Il test del browser sostituisce soltanto le risposte HTTP con fixture temporanee senza account e credenziali reali. Non certifica l'integrazione TOTP con dispositivi reali o SMTP.

## Baseline e stato

RC185 cumulativa (sviluppo doppia proiezione, CI ancora da verificare); l'ultima campagna GitHub completamente verde verificata è **RC184**, run `41993094578`. RC186 non modifica il database o la logica delle presentazioni. Nessun commit, push, tag o deploy automatico. Avanzamento certificato **85,25%** (43 gate accettati, 17 parziali). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
