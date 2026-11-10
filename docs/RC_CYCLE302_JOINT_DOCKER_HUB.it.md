# RC302 — Pubblicazione congiunta autorizzata su Docker Hub

**Baseline:** RC301 integrata in `main` al commit `d18b14129afe8850b5df549213e5d56ba03a47b3`, full CI `42901855073` verde. La precedente pubblicazione `42897981990` aveva aggiornato la sola immagine dell'applicazione.

## Una autorizzazione, due immagini verificate

Con la stessa autorizzazione vengono aggiornati tag identici nei due repository:

- `desalvo/quorivio:sha-<12>` e `desalvo/quorivio:latest`
- `desalvo/quorivio-converter:sha-<12>` e `desalvo/quorivio-converter:latest`

L'autorizzazione `[publish-docker]` sul commit `main` richiede tutta la campagna RC automatica verde; l'avvio esplicito `workflow_dispatch` con `publish_image=true` conserva i gate di qualità e container. PR, push normali, campagne RC e soli commit `[full-ci]` non pubblicano. Rimane disponibile il vecchio workflow manuale del converter per interventi straordinari.

Runner nativi AMD64 e ARM64 costruiscono **entrambe** le immagini e le inviano inizialmente solo tramite digest immutabile, con SBOM e provenance, senza QEMU di rilascio. I digest distinti vengono trasferiti insieme. Il publisher verifica preventivamente i digest nativi del converter, i tag e l'autorizzazione **prima** di modificare alcuna etichetta; pubblica poi e verifica entrambi i manifest multiarchitettura. La scansione Trivy delle due immagini resta obbligatoria.

**Limite del registry:** due repository Docker Hub non possono essere aggiornati in un'unica transazione atomica. Se il secondo aggiornamento fallisce, il job segnala l'errore anche se il primo è già stato pubblicato. Un errore nel preflight non aggiorna i tag.

**Limite RC:** miglioramento infrastrutturale, non accettazione esterna di sicurezza o accessibilità fisica. Punteggio ufficiale **85,25% (43 accepted, 17 partial)**; RC stretta ancora subordinata a verifiche indipendenti. Versione `0.1.0-dev`, nessun tag Git.

**Messaggio merge suggerito:** `ci: publish app and converter together after verified full CI [publish-docker]`
