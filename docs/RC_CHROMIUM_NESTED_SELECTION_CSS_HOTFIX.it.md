# Hotfix CSS dei controlli annidati Chromium — 26 ottobre 2026

- Baseline committata `b8b08fd1fd61fcf15ff49c98ed530df7693c7e38`.
- Run fallita https://github.com/desalvo/quorivio/actions/runs/40392423273/job/121816969728. Il gruppo allineamento era presente; le azioni annidate livelli/spostamenti erano assenti dall'albero di accessibilità.
- Causa: `display:none!important` su tutti i `.canvas-editor-tools`, con riattivazione condizionale solo del figlio diretto.
- Correzione: il gruppo annidato riceve `display:flex!important` **soltanto** quando il menu canvas è aperto. Nessuna toolbar permanente ripristinata.
- Test: `tools/ci_nested_context_css_chromium.py` controlla il CSS reale in Chromium desktop e touch (chiuso, aperto, clic, richiuso), anche prima dell'accettazione completa dell'editor; helper e test principale verificano la visibilità delle azioni livelli.
- CI standard e poi Full CI manuale con `browser_test=true`, `publish_image=false`, `publish_latest=false`. RC invariata 48,0% fino a conferma.
- Nessun commit, push, tag o pubblicazione effettuati.
