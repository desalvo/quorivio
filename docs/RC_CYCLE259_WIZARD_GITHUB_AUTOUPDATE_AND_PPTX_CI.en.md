# RC259 — Self-updating standalone Kubernetes wizard and PPTX CI reconciliation

**CI source:** RC258 full CI [42480854048](https://github.com/desalvo/quorivio/actions/runs/42480854048), commit `64744e1bb3aec55ba7de4482ed9a05640b4a5376`. The "Kubernetes wizard and worker integration tests" job ran 2,325 Python tests and failed exactly one obsolete PPTX projection test requiring `const textStyle={fontFamily:widget.style?.fontFamily`. The renderer correctly uses `explicitWidgetFontFamily(...)` to preserve supported custom fonts and omit literal `undefined`. Updated the test, not the production renderer, and added an early RC259 CI gate.

## One-file release, version and automatic update

`tools/k8s_wizard.py` is a standalone Python 3 stdlib script; `kubectl` is needed only for cluster operations. Embedded version: `0.1.0-dev-rc259`.

On **every operational CLI start** the script checks `https://raw.githubusercontent.com/desalvo/quorivio/main/tools/k8s_wizard.py` over HTTPS (only official upstream). The download is capped at 2 MiB and validated for UTF-8, Python syntax, explicit `0.1.0-dev-rcN` release number, standalone embedded helpers, and HTTPS origin. It never downgrades. If a newer release or changed content is available, it writes atomically alongside the existing script preserving permissions, then re-executes Python **with the exact original arguments**, using a one-shot restart guard. The cluster is never touched before the update gate.

```bash
python3 ./k8s_wizard.py --version          # local version; offline
python3 ./k8s_wizard.py --self-update-only # update and exit; no Kubernetes changes
python3 ./k8s_wizard.py --inspect-cluster \
  --set namespace=quorivio --set name=quorivio --output ./cluster-inventory
python3 ./k8s_wizard.py --no-self-update --unattended \
  --set host=quorivio.example.org --output ./new-install # explicit offline mode
```

**Operational safety:** inability to check GitHub or atomically update blocks cluster-changing commands (fail closed). `--no-self-update` is an explicit opt-out for air-gapped maintenance, and then the operator is responsible for version freshness. `--version`/`--help` require no network. Old unversioned code on GitHub or a lower version is not allowed to overwrite a newer local wizard. There are no configurable third-party update URLs. The converter still requires a reviewed plan and explicit apply; the updater alone never applies Kubernetes resources.

**Validation:** hermetic tests cover version reporting, atomic update and permissions, bounded download, old/unversioned sources, UTF-8 and syntax errors, untrusted redirects, symlinks, write failure, restart with unchanged CLI args and no external Python modules; legacy wizard cluster workflow tests remain. Historical RC258 inventory is immutable; RC259 has a separate inventory. GitHub full CI pending after commit. **85.25%** (43 accepted/17 partial), `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
