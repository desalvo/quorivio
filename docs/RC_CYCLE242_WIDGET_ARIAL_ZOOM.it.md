# Quorivio RC242 — Arial predefinito, schemi compatti e zoom globale

## Modifiche
- Ogni elemento di testo delle widget su canvas pagine e schemi eredita Arial: titoli, etichette, campi di testo, risposte, pulsanti e contenuti annidati. Le famiglie carattere personalizzate dall'utente non vengono sovrascritte.
- La barra dell'editor schemi non va a capo: pulsanti più piccoli; **Salva schema** e indicatore delle modifiche su un'unica riga e sempre raggiungibili. Le altre sezioni scorrono orizzontalmente se la finestra è stretta.
- Controllo di zoom generale visibile su tutte le pagine: −, percentuale corrente, + e ripristino al 100%. Intervallo 70–150% con passi 10%; impostazione salvata esclusivamente tra le preferenze locali del browser. Lo zoom interessa anche finestre e dialoghi fuori dal canvas.

## Accettazione
- Test Node: `node --experimental-strip-types --test apps/web/test/rc242-global-zoom.test.ts`.
- Test Python: `python3 -m unittest tools.tests.test_rc242_arial_master_zoom -q`.
- Chromium reale: `python3 tools/ci_rc242_arial_zoom_chromium.py` a 390/760/1440px per tutti i 20 tipi di widget in entrambi gli editor.
- Restano obbligatori i test Node completi, la discovery Python e la full CI GitHub.

## Sicurezza e stato
- Nessuna migrazione dei contenuti salvati o modifica alle API; i font esplicitamente scelti sono preservati.
- RC241 storica e immutata, RC242 corrente; nessun controllo CI disabilitato.
- Completamento certificato **85,25%** in attesa dei gate indipendenti; `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
