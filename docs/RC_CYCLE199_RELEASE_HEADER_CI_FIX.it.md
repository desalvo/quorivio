# RC199 — Correzione CI intestazioni release e verifica del package

## Causa riprodotta

La RC198 committata dall’utente (`0375877`) ha fallito nella [run 42094437419](https://github.com/desalvo/quorivio/actions/runs/42094437419), job Production quality gate `127480690817`, al passo **Validate active RC release headers against the current inventory**. Errore riprodotto localmente:

```text
ValueError: DEVELOPMENT_STATUS.md: missing one or more explicit release flags
```

Le sezioni correnti RC198 di `docs/DEVELOPMENT_STATUS.md` e `.it.md` non riportavano esplicitamente i tre flag obbligatori prima di `---`. I file di handoff erano invece completi. I documenti storici non devono soddisfare la verifica corrente. Il job si è arrestato prima di TypeScript, browser e PostgreSQL: non certifica un difetto della nuova formattazione.

## Interventi

- Quattro intestazioni RC199 allineate e complete dei flag invariati: `rc_strict=false`, `publish_image=false`, `publish_latest=false`, con percentuali **85.25%** in inglese e **85,25%** in italiano.
- RC198/RC197 preservate nello storico; inventario e verificatore RC198 immutati, richiamati da CI in modalità `--historical`, nuova RC199 corrente.
- Test negativo che riproduce l’omissione di un singolo flag nel sommario corrente anche se gli altri documenti sono corretti.
- Verifica delle quattro intestazioni contenute **all’interno dello ZIP** della RC199, non soltanto nei file locali, prima della consegna.

## Verifiche e politica

Eseguire preflight anticipato, test mirati e hash di sorgenti e ZIP. La full CI GitHub resta da verificare indipendentemente. Nessuna modifica ai flag di pubblicazione, alla versione o al runtime; nessuna promozione di gate: **85,25%** certificato (43 accettati, 17 parziali). Nessun commit/push/tag da parte dell’assistente.

Commit monoriga suggerito dopo RC198: `Fix RC199 active release headers and validate packaged CI metadata`.
