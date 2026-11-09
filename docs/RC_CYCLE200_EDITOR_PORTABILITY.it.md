# RC200 — Portabilità editor, PDF/PPTX ed esportazioni con privacy

## Baseline
Full CI RC199 verde: https://github.com/desalvo/quorivio/actions/runs/42096705867 (14 job verdi, pubblicazione Docker Hub opzionale saltata). Versione invariata `0.1.0-dev`; flag di release/pubblicazione disattivati.

## Editor
- Pulsanti di navigazione nella prima riga e nome presentazione/proprietario primario in formato ridotto sotto i comandi.
- Rimossa la seconda voce «Modifica schemi» dalla sidebar miniature, conservata nella barra orizzontale.
- Menu contestuale miniature «Importa PDF/PPTX»: importa da file locale con convertitore isolato e inserisce le nuove pagine dopo quella selezionata. Necessario attivare il convertitore.

## Sessione portatile
- Il file standalone `.quo` include asset binari con checksum e immagini raster delle slide convertite. Reimportazione su altro account crea sessione, pagine, asset, link d’accesso e proprietà nuovi; non importa partecipanti, risposte, statistiche o segreti della vecchia sessione.
- Esportazioni PDF/PPTX tramite worker isolato; le immagini di slide importate vengono conservate e sotto i widget Quorivio. La fedeltà native PowerPoint resta parziale per alcuni widget avanzati.

## Privacy GDPR e statistiche
- Selezione esplicita «Anonimizza», abilitata per default. CSV/XLSX anonimi aggregano scelte, voti di gradimento e reazioni ed escludono pseudonimi, ID, timestamp individuali, testi liberi e asset upload. Non è una garanzia assoluta contro reidentificazione se gruppi sono piccoli o le domande sono sensibili: controllare prima della diffusione.
- Solo il proprietario primario può scegliere l’esportazione nominativa. CSV protetto da formule eseguibili; XLSX memorizza i testi come dati, non formule; massimo 50.000 record.

## Verifiche e limiti
- Suite Node locali complete: 609 API e 348 frontend superati; test Python mirati e smoke PDF con LibreOffice superati. La suite Python estesa (2.039 test) ha evidenziato due incompatibilità nei controlli storici (alias SQL qualificato per export portatile e tipi TypeScript ambientali mancanti nel test isolato); entrambi i controlli sono stati corretti e i 10 test mirati successivi sono verdi. La suite Python globale non è stata rieseguita dopo le correzioni. Typecheck/build completo, browser/PostgreSQL e full CI RC200 richiedono conferma GitHub dopo commit.
- `rc_strict=false`; `publish_image=false`; `publish_latest=false`. Completamento certificato **85,25%** (43 gate accettati, 17 parziali). Nessun commit/push/tag senza richiesta.
