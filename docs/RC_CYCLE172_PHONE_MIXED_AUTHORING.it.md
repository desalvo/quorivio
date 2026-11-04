# RC172 — Personalizzazioni smartphone e disposizione automatica senza sovrapposizioni

Partenza dal cumulativo RC171, senza perdere le personalizzazioni esistenti.

## Correzioni effettive

1. Il calcolo delle posizioni automatiche riserva preventivamente le aree verticali dei widget con coordinate smartphone esplicite. Gli altri widget evitano quelle aree e la pagina cresce solamente quando serve realmente altro spazio; la posizione dello schema desktop e quella personalizzata smartphone restano immutate.
2. La stessa altezza calcolata con la configurazione smartphone viene usata nel canvas di modifica e nel layout pubblico/anteprima partecipante. In precedenza l'editor e il pubblico chiamavano il calcolo dell'altezza **senza** passare le posizioni smartphone, potendo generare tagli o sovrapposizioni.
3. «Ricompatta automaticamente» azzera solo gli override di posizione. Le preferenze di carattere e colore smartphone rimangono intatte, come indicato dalla descrizione del comando.
4. Nei casi estremi in cui una posizione manuale occupa l'intera altezza, non esiste una soluzione senza sovrapposizioni: la ricerca è limitata e non entra in un ciclo infinito. Serve correggere l'override nell'editor.

## Verifiche ed esclusioni

Nuovi test Node per riserva manuale, footer, crescita della pagina, coerenza editor/partecipante e assenza di persistenza delle posizioni automatiche; preflight Python prima delle dipendenze e test di regressione storici aggiornati senza modificare i vecchi inventari. **296/296 test Node Web** superati localmente, inclusi cinque RC172; compilazione Vite completa e accettazione browser autenticato / su dispositivo reale **non ancora confermate** per questo cumulativo perché l'installazione npm non è riuscita in questa sessione.

**Completamento certificato: 85,25%** (43 gate accettati, 17 parziali). Mantieni `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag, pubblicazione Docker o deploy.
