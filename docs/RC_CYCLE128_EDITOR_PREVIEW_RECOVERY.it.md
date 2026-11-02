# RC128 — Uniformità editor e anteprime, ripristino pagina e arresto alle collisioni

**Verifiche locali dell’hotfix:** suite Python completa: 1.666 test, 1.665 superati, 1 saltato e nessun errore; frontend Node: 185/185 superati. Corretti i contratti storici RC89, RC91 e RC124; invariati logica applicativa, pubblicazione Docker e punteggio RC. Serve una nuova CI GitHub verde. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.


**Hotfix CI RC128 guide magnetiche (run GitHub `41387175909`, commit `3c01b88f994cd28d88c43330170dc21a737e4109`):** il preflight delle intestazioni RC è passato, ma 2/4 asserzioni storiche RC124 richiedevano ancora il ritorno all'origine in caso di collisione e la vecchia espressione per le guide. RC128 arresta invece correttamente la widget al primo ostacolo e mostra le guide magnetiche soltanto se la posizione proposta è raggiungibile. Aggiornato `tools/tests/test_rc124_smart_guides.py` per verificare arresto al contatto, anti-attraversamento, visibilità delle guide sulla posizione accettata e presenza dei test Node RC128 nella CI. La suite completa ha evidenziato anche asserzioni obsolete RC91 sui font del numero pagina e RC89 sull’etichetta della risposta libera: ora verificano le unità tipografiche aggiornate e l’invio disabilitato nel presentatore. Nessuna modifica al codice di geometria dei widget o alle condizioni di sicurezza del rilascio. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. La CI GitHub completa e la verifica visuale nel browser vanno ripetute sul nuovo commit.


Data: 2 novembre 2026. Base: cumulativo RC127. Correzioni nate dalle tre schermate dell'utente; nessuna accettazione esterna inventata.

## Problemi corretti nel sorgente

- **Testo errato sotto la risposta nell'anteprima presentatore:** il precedente ramo dedicato al presentatore sovrapponeva risposte simulate al widget domanda. Le anteprime usano ora la stessa struttura della domanda (testo, risposta e tasto di invio); il presentatore vede il tasto ma non può inviare. Le statistiche rimangono nel widget collegato «Risultati».
- **Anteprime affiancate e stili:** conservate le coordinate e dimensioni percentuali definite nell'editor, incluse formattazione, font, titolo e footer. Dimensioni dei controlli e del testo espresse nella scala del canvas da 1280 unità (`cqw`), anche nella vista affiancata.
- **Casella per risposte libere:** introdotta nell'editor una maniglia indipendente che ridimensiona l'altezza della textarea (48–400 unità logiche), senza cambiare il riquadro del widget. L'altezza salvata vale anche per anteprima e partecipanti.
- **Righello superiore:** corrette griglia e overflow del contenitore per non tagliare il righello orizzontale.
- **Reload browser:** memorizzazione per scheda della sessione, sezione, scheda dashboard e pagina; ripristino solo dopo autenticazione e conferma dal server. Nessuna credenziale, risposta o bozza non salvata memorizzata. Sessioni cancellate/non autorizzate riportano alla dashboard; il logout esplicito azzera la posizione.
- **Collisioni:** spostamento fino al primo limite disponibile, senza rimbalzi o attraversamento di ostacoli sottili. Selezioni multiple restano rigide; forme decorative conservano la possibilità di sovrapporsi; le regole precedenti di ridimensionamento restano attive.

## Evidenza locale

- Suite completa test frontend Node: **185/185 superati** (`node --experimental-strip-types --test apps/web/test/*.test.ts`).
- Contratti Python RC128: **5/5 superati** (`python3 -m unittest tools.tests.test_rc128_rehearsal_parity_contract -q`).
- Copertura di collisioni, passaggio attraverso ostacoli, selezione multipla, normalizzazione dello stato locale e unità tipografiche; test storico presentatore aggiornato per il markup condiviso con invio disabilitato.
- Parsing TypeScript effettuato; **build Vite/npm completa non verificabile localmente** perché l'installazione delle dipendenze npm non si è conclusa. Mancano anche prove visive Chromium e CI GitHub RC128.

## Prontezza RC

RC128 conserva le innovazioni RC127 sul runtime ARM64 nativo e il piano dei 17 gate esterni. Certificazione **85,25%** (43 accettati, 17 parziali, 60 totali); stima ingegneristica **85,75%** provvisoria. RC stretta non approvata. Prossimo commit con `[full-ci]`, non `[publish-docker]`: `publish_image=false`, `publish_latest=false`, `rc_strict=false`. Nessun commit/push/rilascio da parte dell'assistente.

Messaggio di commit cumulativo dal commit RC126 confermato: `Add native OCI runtime gates and fix editor-preview parity, reload recovery and collision boundaries [full-ci]`.
