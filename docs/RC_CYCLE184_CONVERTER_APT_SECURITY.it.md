# Quorivio 0.1.0-dev — RC184: aggiornamento sicurezza APT nel convertitore

## Evidenza CI

La run GitHub Actions [41988947593](https://github.com/desalvo/quorivio/actions/runs/41988947593) (commit `15fceb662007c86867d94461c77381fcbb746566`) ha completato con successo il **Production quality gate**, i collaudi ClamAV, Kubernetes, Podman, Firefox/WebKit e i runtime OCI AMD64/ARM64. La campagna RC è fallita **solo** perché il `Container build gate`, step `Scan converter image`, ha rilevato due finding HIGH nel convertitore Debian 13.7: `apt` e `libapt-pkg7.0` versione 3.0.3, CVE-2026-109518 (versione corretta 3.0.4). Il riepilogo finale ha propagato il fallimento.

Fonte: Debian Security Advisory DSA-6607-1 del 4 novembre 2026, https://lists.debian.org/debian-security-announce/2026/msg00526.html e tracker https://security-tracker.debian.org/tracker/CVE-2026-109518.

## Modifica RC184

- `Dockerfile.converter`: base `python:3.12-slim-trixie` (Debian 13 esplicita), indice APT aggiornato con `Acquire::Retries=0` per mitigare il client vulnerabile durante il bootstrap, upgrade esplicito di `apt` e `libapt-pkg7.0` **prima** di installare Poppler/LibreOffice, verifica **bloccante** `dpkg --compare-versions >= 3.0.4` per entrambi e cleanup dei file temporanei APT.
- Nessuna modifica a privilegi dell'utente finale (`USER converter`), dipendenze Python, worker o runtime Quorivio.
- `tools/ci_converter_apt_security.py` e test con mutazioni negative: preflight anticipato per evitare che un downgrade o un bypass Trivy passi inosservato.
- La scansione Trivy del convertitore mantiene `severity: CRITICAL,HIGH`, `exit-code: '1'` e `ignore-unfixed: true`. Nessuna whitelist CVE, nessun `continue-on-error`.
- Nuovo inventario RC184; gli inventari RC183 e anteriori restano immutati.

## Validazione e limiti

Verifiche locali: test unitari RC184, sintassi POSIX shell, contratti CSS/API e inventario (quando eseguiti). **Non è stata eseguita una build Docker locale né una nuova scansione Trivy dell'immagine**, perché in questo ambiente Docker/Podman non sono disponibili. La prossima CI deve provare effettivamente l'upgrade nel layer e la scansione Trivy, che devono continuare a fallire se i repository non offrono la versione sicura.

**Stato della RC:** 85,25% certificato (43 gate accettati, 17 parziali), salvo aggiornamenti del ledger di accettazione; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Nessun commit/push/tag/release.
