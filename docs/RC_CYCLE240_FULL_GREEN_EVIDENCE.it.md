# RC240 — Full CI verde e raccolta sicura delle prove indipendenti

## Baseline GitHub verificata

La RC239 è stata committata a `0594b72806a7b6bf27de07a5fb2856747c8fd68d`; la [run 42284582481](https://github.com/desalvo/quorivio/actions/runs/42284582481) si è conclusa con successo il 6 novembre 2026 alle 20:18:06 UTC. Passati quality gate, ClamAV, Firefox/WebKit, runtime OCI nativi amd64/arm64, HTTPS/ingress NGINX e HAProxy, failover KIND, PostgreSQL/Podman e build container. Il sommario finale conferma **11/11 job obbligatori**: 14 job riusciti e tre di pubblicazione saltati intenzionalmente. Non è stata certificata nessuna nuova pubblicazione Docker Hub.

La prova strutturata è `docs/validation/RC239_FULL_CI_ACCEPTANCE_20261107.json`. Aggiornato il riferimento `last_verified_full_ci` senza perdere lo snapshot del 31 ottobre, conservato nella chiave storica dedicata; nessuna modifica ai manifest SHA storici.

## Interventi RC240

- Rafforzato `tools/rc_external_evidence.py`: lettura dei documenti operatori con descrittore del file regolare fissato e opzioni `O_NOFOLLOW`/`O_NONBLOCK`; rifiuto di symlink sostituiti, modifiche in corso, inode cambiati, file speciali o troppo grandi.
- Hash sui byte realmente copiati, verifica dell'allegato di destinazione prima di aggiornare il manifest. In caso di errore pulizia del solo file nuovo e del proprio temporaneo, preservando un eventuale temporaneo preesistente.
- Test negativi contro sostituzione con link simbolico, FIFO, manomissione del file, interruzione del JSON e perdita di dati del revisore.
- Il protocollo già presente per le prove private degli operatori e il blocco fail-closed della RC restano attivi. Non includere prove private o dati personali nello ZIP.
- Nuovo preflight obbligatorio prima di npm, inventario sorgenti/ZIP RC240 con SHA-256 e documentazione bilingue.

## Limiti

**85,25% certificato**, 43 gate accettati e 17 parziali. Una full CI verde non certifica dispositivi fisici, NVDA/VoiceOver/TalkBack, privacy/GDPR, provider SMTP/SSO, CSI RWX reale, disaster recovery fuori sede o fedeltà di un corpus Office. La RC formale resta **bloccata**: `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit, push o tag dell'assistente.
