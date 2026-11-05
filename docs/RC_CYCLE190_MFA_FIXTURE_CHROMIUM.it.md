# RC190 — Fixture di login MFA su Chromium compilato

## Run e causa

GitHub Actions run `42023471301`, job `127231773092`, falliva nel passo «Chromium editor UI acceptance» durante `ci_rc186_mfa_enter_chromium.py`, prima di testare il tasto Enter. Il primo elemento atteso («Informativa cookie funzionali») non compariva. Il codice MFA e il consenso ai cookie non erano la causa: il test caricava l’app compilata dentro `about:blank`, dove `localStorage`/`sessionStorage` possono sollevare `SecurityError` per l'origine opaca. La fixture RC186 non simulava queste API, a differenza delle fixture Chromium precedenti già verdi.

## Correzione

- Cookie funzionali in memoria, inizialmente assenti; il dialogo reale viene atteso e confermato tramite «Ho capito».
- `localStorage` e `sessionStorage` indipendenti, con `getItem/setItem/removeItem/clear/key/length`, definiti **prima** dell’iniezione del bundle Vite.
- Preflight dello stato browser, diagnostica dei `pageerror` quando il montaggio React fallisce, e browser-smoke dedicato a 1440/390 px.
- Preflight Python prima di npm e smoke Chromium nello stesso blocco E2E esistente, **prima** del test MFA con React compilato.
- Invariati i test della verifica reale via Enter per TOTP/email/recovery, doppio invio e ritentativo dopo codice errato. Nessun dato di produzione, nessuna modifica all’API e nessuna rinuncia alla verifica GDPR del consenso.

## Evidenze locali e limiti

`python3 -m unittest tools.tests.test_rc190_mfa_fixture_reconciliation tools.tests.test_rc186_totp_keyboard -q`: **9/9**.

`python3 tools/ci_rc190_mfa_fixture_chromium.py`: **2/2**, 1440x900 e 390x844.

Il bundle React compilato non è stato riprodotto localmente per assenza della rete npm (EAI_AGAIN). Solo la prossima GitHub CI potrà confermare l'intero flusso e gli ulteriori collaudi. Completamento certificato invariato: **85,25%** (43 accettati, 17 parziali). Nessun commit/push/tag o rilascio automatico.
