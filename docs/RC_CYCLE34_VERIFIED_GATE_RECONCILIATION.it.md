# Quorivio 0.1.0-dev — ciclo 34 — 30 ottobre 2026 — RC 80,25% (+1,00 pp)

**Baseline committata:** `f5ccf9a7545e7c17b4323d067db66aff5eca9b41`. Il workflow esteso https://github.com/desalvo/quorivio/actions/runs/41048187760 è verde (quality, container, ClamAV, Kubernetes multiworker NGINX), pubblicazione disattivata. **RC formale: 80,25%, 50 gate (33 accettati, 17 parziali). NON RC READY.**

**Riconciliazione basata esclusivamente su GitHub:** `C4-AV-INSTREAM` (peso 1 accettato) separato da C4 parziale (peso da 3 a 2); job `124037870523` verifica `PING/PONG`, scansione INSTREAM ClamAV effettiva, file pulito ed EICAR attraverso il client applicativo. `B4-KIND-INGRESS-RECOVERY` (peso 1 accettato) separato da B4 parziale (peso da 3 a 2); job `124038997005` verifica due worker KIND distinti, PostgreSQL 18, condivisione di file tramite bind temporaneo, NGINX reale con Host, recupero dopo sostituzione di un pod. Risultato 79,25 → 80,25, conservando il peso totale 100; i 17 gate residui non sono promossi.

**Nuovo sviluppo NON conteggiato nel punteggio:** scanner ClamAV con handle `O_NOFOLLOW | O_NONBLOCK`, solo file regolari, streaming dall'handle aperto, controllo `size/mtimeNs/ctimeNs` dopo scansione per rifiutare link simbolici e modifiche in-place prima del risultato pulito; nuovi test Node e regressioni Python. Non certificato da nuova CI sul codice del ciclo 34.

**Limiti espliciti:** non ancora verificati cluster multi-macchina con storage CSI/NFS RWX di produzione, HAProxy reale, TLS pubblico, macchine ARM64 fisiche, upload HTTP concorrenziali al ClamAV gestito, collaudo dispositivo fisico, revisione GDPR/AGID e sicurezza indipendente. Il test KIND è su singolo host, il test ClamAV su server temporaneo. Non attivare `rc_strict` o pubblicare immagini. Nessun commit/push/tag/release a cura dell'assistente.

**Commit suggerito (solo ciclo 34):** `feat(rc): reconcile verified ClamAV and ingress failover gates and harden antivirus file scanning`

**Verifiche locali ciclo 34:** 12/12 test scanner mirati, 492/492 backend Node, 65/65 frontend Node, 1.243 test Python eseguiti in otto gruppi disgiunti (1 saltato, 0 falliti). Inventario corrente SHA-256 e ZIP validati. Build TypeScript/Vite sul nuovo codice non verificata localmente (dipendenze npm mancanti); nuova Full CI dopo commit necessaria. I test ClamAV e multiworker reali che accreditano il punteggio sono quelli del commit precedente, non del codice modificato nel ciclo 34.

---

