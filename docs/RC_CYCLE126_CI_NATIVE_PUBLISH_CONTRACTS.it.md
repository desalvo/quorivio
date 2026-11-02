# RC126 — Aggiornamento contratti CI storici per Docker nativo multiarch

## Errore osservato (GitHub Actions 41371521619)

Il job `Production quality gate` supera TypeScript, Vite, PostgreSQL, Chromium e controlli vulnerabilità; nella suite finale `Kubernetes wizard and worker integration tests` falliscono 8 controlli statici su 1.656. Le asserzioni cercavano nomi e struttura della vecchia pipeline Docker in job unici, non più validi dopo RC125. Il riepilogo RC è fallito a valle, mentre le build OCI native e la pubblicazione Docker Hub sono state saltate: non si tratta di un nuovo blocco QEMU osservato.

## Correzioni

Aggiornati sette file di test storici (otto test): analisi YAML strutturata per confinare correttamente ogni job, requisiti manuali di consenso, pubblicazione da push soltanto col marcatore `[publish-docker]` e successo dell'intera campagna RC, `image-build` e scansioni prima delle build native, verifica delle due architetture e del successivo manifest, ambiente protetto e permessi GitHub sola lettura. Il test Podman senza privilegi non deve contenere autenticazione Docker Hub o pubblicazione. I test sostanziali non sono stati eliminati né resi opzionali.

Un nuovo preflight anticipato esegue le suite corrette prima di installare npm; la suite Python finale completa resta obbligatoria. La verifica esterna dei runner ARM64 nativi e della pubblicazione Docker effettiva è ancora pendente.

**Completamento certificato:** 85,25% (43 gate accettati / 17 parziali su 60). Stima locale provvisoria 85,75%, non promossa. **Commit suggerito:** `Align legacy CI contracts with native multiarch publication and gate both digest builds [full-ci]`.

Verifica locale: 57 test mirati eseguiti (56 superati, uno saltato per condizioni ambientali); la suite Python completa locale ha superato il limite di esecuzione e va ripetuta tramite CI GitHub.
