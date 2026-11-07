# RC245 — Riconciliazione Chromium delle domande smartphone compatte

- **Evidenza:** full CI [42380437684](https://github.com/desalvo/quorivio/actions/runs/42380437684), commit `9af6cb4c99f8347c386b59f58ec1eced903928d3`. Fallimento nel browser reale partecipante/PostgreSQL su `questionHeight>=278-1` obsoleto.
- **Causa:** la RC241 ha ridotto il margine fisso non interattivo delle domande da 190 a 150px, eliminando spazio vuoto e scroll inutile. Con due risposte brevi da **44px** la domanda occupa **238px**, non 278. Rimangono obbligatorie leggibilità e invarianti RC207/RC217.
- **Correzione:** il test Chromium reale ora richiede due opzioni, altezza touch >=44px ciascuna, font calcolato >=17,5px (18 nominali), budget compatto, altezza e spaziatura coerenti, footer corretto e nessun widget privato del presentatore. Aggiornate le mutazioni negative RC217. Non modificato il pianificatore di produzione.
- **Test aggiunti:** regressioni Python prima di npm, Node con testi brevi/lunghi e override manuali, browser Chromium a 320/390/760px; conservati PostgreSQL/React reali e RC207.
- **Stato:** RC244 storica immutata, RC245 corrente. `rc_strict=false`, `publish_image=false`, `publish_latest=false`; completamento **85,25%** (43 accettati/17 parziali). Full CI RC245 da verificare; nessun commit/push/tag.
