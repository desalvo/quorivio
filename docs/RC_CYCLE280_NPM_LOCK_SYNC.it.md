# RC280 — Correzione deterministica del lockfile npm

La CI #42605580476 è fallita nella fase `npm ci` perché `apps/api/package.json` richiedeva `ldapts@^9.2.0`, ma il lockfile non includeva il pacchetto né la dipendenza `strict-event-emitter-types@2.0.0`.

Sono stati aggiunti i pacchetti al `package-lock.json` di workspace e le relative entry `packages` e `dependencies` v2, con gli hash SRI SHA-512 verificati. `npm ci` rimane obbligatorio; non tornare a `npm install` durante il workflow, perché può alterare l'inventario SHA-256.

Il controllo `tools/tests/test_rc280_npm_lock.py` verifica le dipendenze dirette e transitive, la sincronizzazione dei manifest, gli hash e la presenza del gate prima di `npm ci` in tutti i job pertinenti. Vanno conservati gli inventari storici RC279 e precedenti.

Validazione locale: verifica statica dei metadati, `npm ci --dry-run --offline` senza errore EUSAGE, test Python. L'installazione effettiva, la build API/web e le schermate reali richiedono la successiva full CI; non sono ancora certificate.
