## 2026-10-23 — Estensione widget multimediali (test locali, collaudo Kubernetes pendente)
- Aggiunti alla palette dell'editor i widget separati Logo e PDF oltre a Immagine e Video; riutilizzate libreria file e API di caricamento private. Associazione di immagini ai loghi e PDF ai documenti con selezione o upload diretto.
- Rafforzata la convalida dei layout: ogni widget multimediale richiede un asset UUID; al salvataggio il server verifica appartenenza alla sessione, origine del file dal presentatore e corrispondenza del MIME. Accesso pubblico limitato alla pagina corrente di una sessione attiva. PDF esposto come collegamento; altri formati documentali non ancora supportati.
- Test locali: Python 124/124 e Node 107/107; build TypeScript/Vite completa non disponibile (mancano le definizioni vite/client). Restano i collaudi reali browser/PostgreSQL/Kubernetes.
- Aperti: sfondi caricati per pagina con consegna pubblica sicura, documenti oltre PDF, menu contestuale sul canvas, rendering media completo sullo schermo presentatore. Nessuna nuova macroarea/gate RC validata; avanzamento ponderato invariato 37,5%.

### Collaudi richiesti
1. Aggiungere widget immagine/logo/video/PDF e allegare il formato corrispondente.
2. Salvare e riaprire verificando la persistenza.
3. Verificare il rifiuto di asset di altre sessioni e formati errati.
4. Avviare la sessione, aprire la pagina e verificare che i media non siano accessibili su altre pagine.
5. Verificare popup PDF e restrizioni sugli allegati privati.
