# RC197 — Riconciliazione dei controlli Python Kubernetes

**Versione:** Quorivio 0.1.0-dev (invariata)  
**Data:** 5 novembre 2026  
**Origine:** cumulativo RC196 / commit della run #297 (`42085779348`, `1a5e9cd9c6b3a0ace506514ea57a0dfe07d31234`).

## Diagnosi GitHub

La run #297 è fallita nel `Production Quality Gate` dopo avere superato i preflight, `603` test Node API, `345` test Node frontend e i typecheck TypeScript strict. Il passo `Kubernetes wizard and worker integration tests` ha eseguito `2.024` casi Python, con sei asserzioni obsolete. I controlli cercavano nomi e comportamenti antecedenti alle anteprime indipendenti RC185 e alla tipografia comune RC194. ClamAV verde; job successivi saltati.

## Correzioni RC197

Sei moduli Python storici verificano ora il percorso corrente, senza ripristinare quello obsoleto:

- `test_page_rename_preview_contract_20261027`: titolo e widget della pagina effettiva del presentatore/pubblico, navigazione limitata alle pagine del presentatore.
- `test_rc143_phone_result_ribbon`: layout autonomo smartphone basato su `viewActivity`/`viewWidgets` e non su un'unica pagina.
- `test_rc75_typescript_ci`: tipi delle sottodomande con `description` opzionale, conservando `answerMode`, risposte e collegamenti dei risultati.
- `test_rc_presenter_linked_preview_20261028` e `test_rehearsal_send_parity_20261028`: le reazioni di prova sono associate a `audienceActivity.id`.
- `test_visual_parity_rehearsal_20261028`: i font sono risolti da `widgetTextDefaults` e `widgetTypographyStyle`, rispettando gli stili personalizzati.

Un nuovo controllo RC197 verifica routing indipendente, stato delle reazioni, tipo della domanda sorgente e posizione dell'esecuzione nella CI. Tutti e sei i moduli vengono eseguiti **anche prima di npm**, oltre che nella suite integrata originale. Nessuna modifica al runtime applicativo, al database o alle API.

## Validazione

- `35/35` test Python dei moduli interessati e del nuovo controllo: superati.
- Node API `603/603`, frontend `345/345`: superati.
- Ripetuta la suite globale Python con il manifesto RC197: **2.027 test eseguiti: 2.026 superati, 0 errori/fallimenti e 1 saltato** (82,078 secondi). Il primo tentativo senza manifesto era uno stato intermedio, non il risultato di rilascio.
- La nuova campagna CI completa con PostgreSQL, Chromium e Kubernetes deve ancora confermare l'integrazione.

**Governance:** `0.1.0-dev` invariata; **85,25%** certificato, 43 gate accettati e 17 parziali; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Ultima baseline verde/pubblicata RC190 (`42027634427`, `42032833536`). Nessun commit, push o tag.
