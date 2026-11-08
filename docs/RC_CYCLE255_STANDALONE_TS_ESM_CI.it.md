# Quorivio 0.1.0-dev — RC255: compilazione TypeScript rigorosa e Node ESM

## Incidente e causa

- Full CI RC254: https://github.com/desalvo/quorivio/actions/runs/42476782314 (commit `45bf2bea9ed09c82684012ffcaa0925dbaf48dd2`).
- Errore: `Production quality gate` / `RC197 reconcile Kubernetes Python integration contracts before npm` / test `tools.tests.test_rc75_typescript_ci`.
- TS5097 in `apps/web/src/slide-master.ts:2`: il test standalone invoca `tsc --noEmit --strict --moduleResolution bundler` senza `--allowImportingTsExtensions`; RC254 aveva introdotto un import `.ts` verso la funzione condivisa di validazione dei font. La build reale accetta tale import, indispensabile nei test TypeScript eseguiti direttamente con Node.

## Intervento

- Aggiunto `--allowImportingTsExtensions` solo al comando standalone di compilazione senza emissione, senza indebolire `--strict`.
- Conservato l'import con estensione `.ts` nel codice di produzione, per non interrompere i test Node ESM.
- Aggiunto controllo preventivo RC255 in CI: verifica il contratto, ripete l'esatta compilazione rigorosa RC75 ed esegue i test Node effettivi dei font e degli schemi.
- Intatte le correzioni Arial RC254 e tutti gli inventari storici SHA-256.

## Verifica locale (dalla radice del progetto)

```bash
python3 -m unittest -q tools.tests.test_rc75_typescript_ci tools.tests.test_rc255_standalone_typescript_ci
node --experimental-strip-types --test apps/web/test/rc195-master-typography.test.ts apps/web/test/rc254-all-widget-schema-fonts.test.ts
npm run build -w @quorivio/web
python3 tools/verify_rc_cycle255_inventory.py
```

La nuova full CI su GitHub deve confermare la correzione dopo il commit. Nessun push Docker, tag o release.
