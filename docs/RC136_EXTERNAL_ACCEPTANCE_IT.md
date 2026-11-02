# RC136 — Collaudo indipendente e raccolta verificabile delle evidenze

**Baseline:** RC135, GitHub Actions `41437489546`, commit `6c1118e93076c5d2eb8d60e96a43f8c663178053`, CI completa verde e pubblicazione multiarch riuscita. RC136 introduce uno **strumento di verifica delle evidenze esterne**, ma **non certifica né chiude automaticamente alcuno dei 17 gate parziali**. Completamento certificato **85,25%**, 43 gate accettati / 17 parziali. `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Uso pratico

1. Impostare il **commit esatto a 40 caratteri** della versione da collaudare. Creare un fascicolo **fuori dal repository**:

   ```bash
   python3 tools/rc_external_evidence.py --init ../quorivio-operator-evidence --commit <sha-del-commit-esaminato>
   ```

2. In `reviews.json` ci sono 17 schede non approvate, con le prove obbligatorie per ognuna. Il catalogo ufficiale di ciò che serve è `docs/validation/RC136_OPERATOR_EVIDENCE_REQUIREMENTS_20261102.json`. Eseguire i collaudi reali previsti dal piano esterno RC127: dispositivi mobili reali, NVDA/VoiceOver/TalkBack, provider SMTP/OAuth, infrastruttura fisica, offsite, Microsoft Office e valutazioni indipendenti di sicurezza, GDPR e documentazione.
3. **Prima** di importare i file eliminare dati personali, token, password, email, immagini private e chiavi. Importare una prova distinta per ogni categoria, ad esempio:

   ```bash
   python3 tools/rc_external_evidence.py --attach ../quorivio-operator-evidence --gate A4 --facet nvda --file /percorso/rapporto-nvda-oscurato.pdf
   ```

   Il programma copia il documento e ne registra lo SHA-256. Accetta PDF, TXT, MD, JSON, CSV, PNG, JPEG, WebP, MP4, WebM e LOG, non file `.env` o chiavi. Non sovrascrive allegati già registrati. **Non effettua automaticamente la rimozione dei dati personali.**
4. Il revisore indipendente compila `operator`, `independent_reviewer`, `reviewed_at` con fuso orario, `environment`, `review_scope`, `notes`. Solo in caso di esito favorevole reale imposta `outcome="pass"` e `independent_approval=true`. Operatore e revisore devono essere persone distinte; lo strumento non è in grado di verificarne autonomamente l'identità.
5. Verificare la completezza:

   ```bash
   python3 tools/rc_external_evidence.py --report ../quorivio-operator-evidence
   python3 tools/rc_external_evidence.py --check ../quorivio-operator-evidence --expected-commit <sha-del-commit-esaminato>
   ```

   L'assenza di una prova, una firma dichiarata ma non compilata, un checksum errato, un allegato simbolico/esterno o un commit diverso producono errore. **La validazione tecnica non autentica l'approvazione umana e non equivale a una certificazione.**
6. Il responsabile RC verifica indipendentemente il contenuto e promuove manualmente i gate nel registro solo dopo l'accettazione reale. Per il controllo finale rigoroso:

   ```bash
   python3 tools/rc_release_preflight.py --strict --evidence-dir ../quorivio-operator-evidence --commit <sha-del-commit-esaminato>
   ```

   La verifica richiede sia tutti i 60 gate accettati sia il fascicolo esterno coerente. In CI autorizzata si possono utilizzare `QUORIVIO_RC_EVIDENCE_DIR` e `GITHUB_SHA`. Senza prove esterne reali, l'RC ufficiale resta bloccata.

## Stato e limitazioni

La CI verde di RC135 conferma gli automatismi già eseguiti; non dimostra in autonomia accessibilità con screen reader reali, compatibilità di tutti i PPTX, ripristino offsite con RPO/RTO misurati, provider esterni, conformità GDPR/AGID o esito del penetration test. Il pacchetto RC136 è uno strumento che rende verificabile e più rapida la raccolta delle evidenze; **non rilascia il prodotto, non effettua commit, non attribuisce nuovi punti**, e non autorizza la pubblicazione. Conservare prove e identità dei revisori in un archivio privato con accessi controllati, mai nei ZIP pubblici.
