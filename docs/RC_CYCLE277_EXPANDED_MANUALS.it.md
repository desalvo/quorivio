# Quorivio 0.1.0-dev — RC277 | Manuali IT/EN completamente riscritti

## Ambito

Riscritti i sei manuali PDF in italiano e inglese per partecipante, presentatore e amministratore, usando sorgenti Markdown editabili in `docs/manuals-src/` e un generatore riproducibile `tools/generate_manuals.py` (Mistune/WeasyPrint). Le copie in `docs/manuals/` e `apps/web/public/docs/manuals/` sono identiche byte per byte. Versione/build in copertina: `0.1.0-dev / RC277 / 9 novembre 2026`.

- Partecipante: QR/link/codice, sessione, domande singole/multiple/libere/file, quiz a tempo, gradimento 0–9, reazioni, moderazione, feedback ✓/✕ solo dopo la conferma, privacy e troubleshooting.
- Presentatore: workflow completo, editor/schemi, catalogo delle **21 tipologie di widget**, formattazione indipendente, sfondi desktop/smartphone, interazioni live, risultati bars/pie/table/cloud, toggle R, importazione PDF/PPTX, Q&A, media, collaborazione, esportazione, prove d'accettazione.
- Amministratore: Compose/Helm/wizard Kubernetes, PostgreSQL 18, ingress, PVC/RWX, backup POSIX/NFS/S3/WebDAV, schedule e restore manuale, LDAP/LDAPS/autoregistrazione/approvazione, SMTP/OIDC/MFA, audit e retention, converter, antivirus, monitoring, security/GDPR, runbook e matrice di accettazione.
- Immagini: copertina fotografica illustrativa già presente nel progetto, 6 esempi di UI realizzati come schermate browser di una **ricostruzione statica**, 2 grafici con dati inventati e 2 diagrammi procedurali. Tutti gli esempi sono contrassegnati: **non sono screenshot live**, non costituiscono collaudo e dovranno essere sostituiti da veri screenshot verificati durante la revisione indipendente D5.

## Stato e verifiche

Nessuna modifica al comportamento applicativo RC276; nessuna certificazione GDPR/AgID. La pubblicazione non prova la compatibilità con dispositivi reali o infrastrutture LDAP/SMTP/storage. I PDF sono controllati per struttura, pagine, parole chiave e copie web identiche; file sorgente e immagini sono incluse nel cumulativo. La validazione editoriale da parte di utenti indipendenti, le screenshot live e la full CI rimangono da completare.

La baseline certificata resta **85,25%** (43 gate accettati/17 parziali); `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag effettuato dall'assistente.
