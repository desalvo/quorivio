# RC131 — Collisioni continue e fedeltà tipografica dei partecipanti (2 novembre 2026)

## Baseline verificata

RC130 è stata committata e la run GitHub Actions [41420021082](https://github.com/desalvo/quorivio/actions/runs/41420021082), commit `d3e89fb2f27cee0cb6aa87d57a61927cef2c874d`, è verde: gate produzione, Chromium/PostgreSQL reale, ClamAV, runtime e build OCI nativi AMD64/ARM64, Kubernetes NGINX/HAProxy, Podman e campagna RC. Docker Hub è stato pubblicato con autorizzazione esplicita nel commit. Questa prova riguarda RC130, non ancora RC131.

## Modifiche RC131

1. Il trascinamento non campiona più al massimo 400 posizioni: una verifica **geometrica continua** calcola il primo contatto con ogni widget fisso e arresta il gruppo sul bordo, anche con ostacoli dello 0,05% e movimenti rapidi. Restano validi spostamenti diagonali, limiti canvas, rigidità del gruppo, controlli sui numeri non finiti e sovrapposizioni delle forme. Una disposizione iniziale irregolare non viene riparata di nascosto.
2. Nella **pagina 16:9 del partecipante** le precedenti dimensioni font con `!important`, anche in modalità mobile, sovrascrivevano quelle stabilite dall'autore. Ora viene usato `--authored-widget-font-size` con la stessa tipografia di editor e anteprima. La modalità **lettura accessibile** resta indipendente e usa 1rem.
3. Aggiunti sette test Node per geometria e collisioni e un test Chromium CSS reale per coordinate/dimensioni e titolo/footer (famiglia, dimensione, peso, colore) nelle superfici editor, anteprima presentatore/partecipante, proiezione presentatore e pagina partecipante, a 1440 e 390 px. I test browser applicativi rimangono necessari.
4. Allineati i contratti RC124, aggiunto preflight RC131 e test Chromium nel workflow; conservati inventari storici e restrizioni di pubblicazione.

## Confini di accettazione

**Completamento certificato invariato all'85,25%:** 43 gate accettati e 17 parziali. Le migliorie interessano A1/A3, ma non sostituiscono le prove fisiche iOS/accessibilità, provider reali, storage/HA indipendente, sicurezza/GDPR o la firma dei manuali. Il gate RC rigoroso rimane bloccato. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

**RC131 richiede ancora una nuova CI GitHub verde** e la verifica del comportamento applicativo. Nessuna autorizzazione di pubblicazione Docker è stata aggiunta.

## Verifiche locali RC131

- Suite Python completa: **1.677 test eseguiti, uno saltato, zero fallimenti**. Un test negativo stampa intenzionalmente un errore CLI; l'esito globale è OK.
- Suite frontend Node: **192/192 superati**, inclusi sette nuovi test del trascinamento.
- Chromium locale: **PASS a 1440 e 390 px** su editor, prova, proiezione e pagina partecipante.
- Parser TSX: **zero errori sintattici**; compilazione npm/Vite e accettazione React/PostgreSQL reale da confermare nella prossima CI GitHub.
- Inventario e intestazioni coerenti; nessuna approvazione esterna dichiarata.
