# Quorivio RC273 — Hotfix typecheck API

## Diagnosi verificata

La full CI [42547239843](https://github.com/desalvo/quorivio/actions/runs/42547239843) è arrivata fino a `./node_modules/.bin/tsc --noEmit -p apps/api/tsconfig.json`. Il controllo RC189 ha segnalato quattro errori: TS2352 su upload WebDAV, TS2769 sul body S3 e due TS2339 sull'ID dell'audit HTTP. Le fasi pre-npm hanno superato il blocco precedente RC241; la campagna successiva è stata saltata dopo il fallimento della validazione.

## Correzioni

- `apps/api/src/full-backup.ts`: mantenuto il body stream di Node per WebDAV, l'header Content-Length e `duplex:'half'`; il cast è limitato al confine con le typings standard di `RequestInit`, che non rappresentano le estensioni Node.
- `apps/api/src/s3-backup.ts`: trasformazione esplicita del Buffer in `Uint8Array` web-compatible, con stessi byte del payload firmato SHA-256 per AWS SigV4.
- `apps/api/src/server.ts`: lettura tipizzata e validazione UUID del parametro `id`, mantenendo la scrittura audit asincrona senza bloccare le risposte.
- Inventario RC272 passato a storico `--historical`; RC273 corrente con manifesto SHA-256 completo e intestazioni allineate.

## Validazione e rischio residuo

I test Node RC270 backup, S3 e WebDAV passano. I tre moduli di backup passano anche `tsc --noEmit` con TypeScript 5.8 e dichiarazioni Node, utilizzando una configurazione equivalente per i moduli isolati. Il typecheck completo di `apps/api` e la CI estesa richiedono dipendenze npm installate: non sono certificati in questo ambiente. Test di integrazione reali (LDAP, storage, ripristino PostgreSQL 18) ancora aperti. La baseline rimane 85,25%, senza promuovere gate.

Non eseguire commit/push/tag dell'assistente.
