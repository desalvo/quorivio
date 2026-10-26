# Quorivio 0.1.0-dev — batch RC di recupero cancellazioni dopo il commit

Data: 26/10/2026. **Baseline ufficiale già committata dall'utente:** `quorivio-0.1.0-dev-rc-acceleration-retention-erasure-preflight-cumulative.zip`; Actions `40322399238`, quality `121570698068` e container `121572390069` **SUCCESS**; pubblicazione **SKIPPED** volutamente. Questo nuovo batch contiene **solo modifiche successive**, non è committato.

## 22 interventi tecnici/operativi effettivi in tre macroaree

**A. Ciclo di vita degli allegati privati (10)**
1. DELETE dei metadati dell'allegato e accodamento cancellazione fisica in **un'unica istruzione SQL atomica**.
2. Nessuna coda creata per file inesistenti o appartenenti ad altra sessione.
3. Conservati i controlli che impediscono l'eliminazione di media usati da widget o slide.
4. Nuova tabella durevole `session_asset_file_cleanup_jobs`, chiave composta e indice di scadenza.
5. Acquisizione concorrenziale PostgreSQL `FOR UPDATE SKIP LOCKED`, massimo 50 job per worker.
6. Lease di cinque minuti e conferma condizionata al lease ancora valido.
7. Retry con backoff esponenziale limitato a un'ora dopo errori filesystem.
8. Controllo UUID canonici e rifiuto delle cartelle di sessione simboliche.
9. File mancanti equivalgono a cancellazione riuscita; `unlink` non rimuove gli altri media della cartella.
10. Worker ripetuto ogni minuto, con tentativo immediato dopo il DELETE.

**B. Foto profilo e cancellazione account (7)**
11. Coda durevole e indipendente `profile_photo_cleanup_jobs`, senza FK sull'utente eliminabile.
12. Sostituzione/rimozione foto: l'URL viene aggiornato e la vecchia foto viene accodata **nella stessa transazione con blocco utente**.
13. Eliminazione amministrativa dell'account con enqueue foto prima del commit, mantenendo protezioni su utente corrente, amministratore principale e dati dipendenti.
14. Chiusura delle connessioni WebSocket dell'utente effettivamente eliminato.
15. Worker foto separato, con lease per replica, limite di 50 elementi e retry massimo di un'ora.
16. UUID stretti, divieto di seguire cartelle simboliche, nessuna cancellazione per enumerazione indiscriminata.
17. Avvio e ripetizione automatica del worker; una transazione foto fallita non perde il nuovo file.

**C. Osservabilità, privacy e preflight (5)**
18. Anche la precedente coda cancellazione delle cartelle di sessione riprova ogni minuto (non più soltanto alla purga oraria).
19. Errori della coda sessioni registrati solo come codice OS, senza percorso filesystem; ID sessioni validati in modo stretto.
20. Endpoint riservato al platform admin `GET /api/admin/privacy/erasure-status` con soli conteggi, quantità esigibili, età massima, header `private, no-store`, senza identificativi individuali.
21. Integrazione PostgreSQL CI estesa a cancellazione fisica su directory temporanee, isolamento sessioni, avatar, quote lavoro dovuto e recupero lease scaduti.
22. Preflight RC fail-closed, documentazione IT/EN, GDPR, inventario e matrice aggiornati.

**Prove:** 44 nuovi test Node e 10 nuovi contratti Python (54 casi di verifica distinti, **non 54 funzionalità né 54 esecuzioni CI**). Node **430/430 PASS**, Python **707/707 PASS**; verifica sintattica Node 22 dei file TypeScript modificati e dello script CI. **Build TypeScript completa e Vite non verificati qui** perché `node_modules` non è incluso e l'installazione delle dipendenze non si completa. **Test PostgreSQL reale, Chromium e acceptance esterna pendenti**.

## Prontezza RC e procedure operative

**Score prudenziale 45,5%, invariato**. Il verde GitHub vale per la precedente baseline già committata, non certifica queste nuove modifiche. D1 resta accettato solo per quella baseline, C4 parziale e D6 aperto.

Dopo il prossimo commit, eseguire CI standard e controllare in particolare il nuovo passo PostgreSQL erasure, seguito dal container gate. CI completa opt-in dopo 2–3 batch importanti, prima della RC o anticipata per nuove modifiche critiche all'autenticazione. Il solo operatore platform admin può consultare l'endpoint dei contatori; allarmi per code persistentemente non vuote devono ancora essere configurati. Verificare realmente cancellazioni su volumi RWX condivisi tra repliche e permessi del servizio.

**I media cancellati dal filesystem live NON sono automaticamente eliminati da backup, dump, export, snapshot, log e fornitori esterni.** Restano l'approvazione delle politiche di backup/retention e i collaudi indipendenti di GDPR, AGID, accessibilità, SSO, disaster recovery, Podman rootless e ARM64. Non dichiarare conformità GDPR né RC pronta.

Prossime priorità: CI PostgreSQL/Chromium per foto e allegati, collaudo funzionale presentatore/sondaggi/quiz, accessibilità dispositivi reali, ripristino produzione e portabilità. Nessun commit/push/tag/release effettuato.
