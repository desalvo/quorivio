# RC269 — Autenticazione LDAP/LDAPS, pulizia, ownership e sidebar

## Funzioni incluse

- Una richiesta API autenticata che restituisce `authentication_required` o `session_revoked` (401) porta direttamente alla pagina di login tramite reload; il flusso pubblico dei partecipanti e i tentativi di login non vengono reindirizzati. La stessa protezione vale per upload/importazione che utilizzano `fetch` binario.
- Un processo ogni **12 ore** e uno iniziale recuperano spazio dai workspace di conversione inutilizzati, solo se più vecchi di 12 ore e non attivi, e dagli allegati persistenti **non registrati** in `session_assets`. File registrati, immagini della libreria sfondi, Gravatar/foto profilo e percorsi sconosciuti vengono conservati. In caso di errore PostgreSQL la cancellazione degli allegati fallisce in sicurezza.
- Il proprietario primario può trasferire una sessione a un altro presentatore approvato della medesima organizzazione; il nuovo proprietario eredita attività e contenuti, l'operazione è atomica e auditata. Opzione per rimanere collaboratore oppure perdere l'accesso.
- LDAP/LDAPS opzionale con service bind, ricerca filtrata, bind delle credenziali dell'utente, STARTTLS o LDAPS con validazione TLS, mapping gruppi → ruolo, MFA Quorivio esistente. Le identità esterne non vengono abbinate automaticamente per email a utenti locali. Collegamento esplicito nell'interfaccia Profilo con password LDAP. Provisioning automatico disattivato per default.
- Le miniature aprono il menu contestuale sullo spazio vuoto **solo** con clic destro o pressione prolungata mobile (650 ms), mai con clic sinistro; drag/drop invariato.
- Nelle risposte dell'editor smartphone viene applicato un minimo leggibile di 17 px senza alterare QR e numerazione pagina.

## Configurazione LDAP nel wizard Kubernetes

`python3 tools/k8s_wizard.py --no-self-update --unattended --output /PERCORSO/NUOVO-MANIFEST --set ldap_enabled=true --set ldap_url=ldaps://ldap.example.org:636 --set ldap_bind_dn='cn=quorivio,ou=svc,dc=example,dc=org' --set ldap_base_dn='dc=example,dc=org'`

Impostare **`ldap_bind_password` tramite file JSON di override riservato (permessi 0600)**, non come argomento CLI nella shell history. Il wizard genera la password nel Secret Kubernetes `05-app-secret.yaml`, non nella ConfigMap. Valori: `ldap_starttls=true` solo con `ldap://`; `ldap_user_filter=(uid={login})`, `ldap_id_attribute=entryUUID` (per Active Directory spesso `objectGUID`), `ldap_email_attribute=mail`, `ldap_group_attribute=memberOf`, `ldap_admin_group_dn`, `ldap_presenter_group_dn`, `ldap_auto_provision=false`, e `ldap_organization_id` se auto-provisioning è desiderato. Un certificato CA privato richiede `ldap_tls_ca_file` e un file montato nel container Quorivio; il solo percorso non monta il file.

Per cluster esistente **non rigenerare/applicare manifest alla cieca**: preservare patch del converter e della sonda Postgres, incorporare le chiavi LDAP nei manifest effettivi, verificare gli output con `kubectl kustomize`, prima di applicare. Il wizard per nuovi deployment a replica singola e PVC `ReadWriteOnce` usa `Recreate` e per `:latest` `imagePullPolicy: Always`.

## Verifica e limiti

Controlli automatici inclusi per URL e TLS, LDAP filter injection, conservazione libreria, cleanup orfani, route ownership, UI e generazione manifest. L'accesso con una directory LDAP reale, SMTP, Kubernetes e la full CI GitHub richiedono collaudo successivo; non simulare queste prove come effettuate. Il pacchetto usa `ldapts` 9.2.x (Node 22+) installato durante la build del container tramite `npm install`.

**Avanzamento complessivo invariato: 85,25%.** `rc_strict=false`, `publish_image=false`, `publish_latest=false`; nessun commit/push/tag eseguito dall'assistente.
