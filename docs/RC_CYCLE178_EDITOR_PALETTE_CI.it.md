# Quorivio 0.1.0-dev — RC178: sblocco CI Chromium e palette editor responsiva

**Run analizzata:** https://github.com/desalvo/quorivio/actions/runs/41871700136/job/126720219254, 4 novembre 2026. `Production quality gate` fallisce esclusivamente durante `Chromium editor UI acceptance (opt-in)` nello script `tools/ci_editor_mock_layout_chromium.py`, alla vecchia asserzione `getComputedStyle(...).overflowX == "auto"`. Installazione npm, test unitari e compilazione backend/frontend avevano già superato la CI.

**Problema reale sottostante:** RC171 ha cambiato la palette da una barra a scorrimento orizzontale a un catalogo a righe con scorrimento verticale. La riga CSS RC101 rimaneva vincolata a 80px sul desktop: con almeno due righe di pulsanti, una parte della palette era tagliata. Inoltre, con la maggiore altezza effettiva della palette, il canvas 16:9 poteva superare leggermente la regione visibile.

**Interventi RC178:** track centrale della griglia a dimensione automatica e limitata, per desktop e finestre strette; ridimensionamento del canvas 16:9 nel desktop per non uscire dal viewport; verifica Chromium RC101 aggiornata a `overflow-y:auto`, `flex-wrap:wrap`, assenza di scorrimento orizzontale, limite d'altezza e raggiungibilità dell'ultimo widget; nuovo preflight Python con controllo negativo contro il ritorno alle regole fisse; controllo anticipato in CI; conservazione delle prove storiche.

**Verifiche locali già completate prima della generazione dell'inventario:** Chromium editor RC178 1440/390 px; Chromium RC171 palette 1440/960/620 px; Chromium RC105, hit target canvas, overlay header, menu portal, geometria widget, editor schemi e dual preview; test mirati RC101/RC178. Non confondere queste prove di fixture con un collaudo completo su React/PostgreSQL o dispositivo fisico.

**Gate e sicurezza:** 85,25% certificato (43 accettati / 17 parziali); questo ciclo non promuove gate senza accettazione indipendente. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push, tag o deploy eseguito dall'assistente.

**Regressione CI preflight finale:** 584 test Python eseguiti con zero errori (un test saltato), più 6 test mirati RC101/RC178 verdi. L’inventario RC178 è verificato sui sorgenti; il successivo commit e la nuova CI non sono ancora avvenuti.
