# Consolidamento editor RC — 23 ottobre 2026

Tre macroaree accorpate nei sorgenti: **widget media caricati**, **barra visuale delle pagine**, **toggle dei controlli principali sì/no**. Dettagli in `RC_EDITOR_BATCH.en.md`.

- Media: caricamento diretto nell'editor, selezione file allegato, validazione e lettura pubblica soltanto sulla pagina corrente attiva, protezione contro la cancellazione di media collegati.
- Pagine: nuova barra di navigazione con tipo/titolo; le operazioni di duplicazione, spostamento e riordino restano disponibili nell'elenco.
- Privacy sessione: pulsanti verde/rosso accessibili per anonimato e pubblicazione risultati.

**Test focalizzati:** 5 nuovi controlli superati; gli 82 test Node e gli 81 Python preesistenti superati una volta durante la modifica. Build npm/browser, esecuzione Docker e collaudi reali **non verificati**.

**Chiusura stimata dei gate RC: 63%**, rispetto al precedente 60%, stima ingegneristica e non certificazione. Restano: vere miniature delle slide, MFA amministrativa e email opzionale, configurazione SSO completa via web, rifiniture tastiera/accessibilità, integrazione con client reali.
