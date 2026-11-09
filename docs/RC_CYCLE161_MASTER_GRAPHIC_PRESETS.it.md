# RC161 — Editor degli schemi, font Arial e grafica senza titoli

## Funzioni

- Arial è il font effettivo predefinito per testo, titolo e footer nello schema e nell'editor pagina, indipendentemente dal dispositivo; le scelte esplicite dei presentatori non vengono sovrascritte.
- In **Modifica schemi**, selezionare **Carica immagine** nello sfondo globale, oppure scegliere un'immagine della libreria. Dopo **Salva schema**, le pagine desktop senza immagine propria ereditano quella dello schema. Le immagini della pagina hanno precedenza; gli sfondi smartphone esplicitamente gestiti restano indipendenti.
- Gli allegati dello schema sono autorizzati per la sola pagina live, protetti dalla cancellazione finché utilizzati e inclusi/rimappati negli archivi portabili `.quo`.
- **Linee** e **Forme** non mostrano mai titolo e descrizione sul canvas o nella presentazione. La palette consente il click standard per la versione base, il tasto destro, la pressione prolungata di 560 ms o il tasto Menu contestuale/Shift+F10 per scegliere un preset. Disponibili linee continue/tratteggiate/punteggiate, frecce a uno/due terminali, spessori e colori; per le forme anche tipi comuni e riempimento personalizzabile o trasparente.
- I widget grafici inseriti restano completamente modificabili tramite le normali proprietà; il backend valida ogni opzione.

## Verifiche e limiti

Eseguire `node --experimental-strip-types --test apps/web/test/*.test.ts apps/api/test/*.test.ts` e `python3 -m unittest tools.tests.test_rc161_master_background_graphics -q`. Il controllo reale richiede due account, una pagina con background proprio e una senza, visualizzazione presentatore/partecipante e immagine dello schema; verificare anche il layout telefono indipendente. **Non ancora certificato** in una nuova CI o sessione autentica.

**Stato certificato:** 85,25%, 43 gate accettati e 17 parziali; mantenere `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
