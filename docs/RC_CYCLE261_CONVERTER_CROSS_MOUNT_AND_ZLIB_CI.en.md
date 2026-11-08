# Quorivio 0.1.0-dev — RC261 — Kubernetes PDF/PPTX and converter security

**Status:** local fixes implemented and tested; **new RC261 full GitHub CI still pending**. Docker Hub publication remains explicitly manual. **Product completion 85.25%** (43 accepted / 17 partial gates). `rc_strict=false`, `publish_image=false`, `publish_latest=false`.

## Confirmed cause and CI failure

- Kubernetes uses distinct `emptyDir` mounts for `/tmp` and `/conversions`. RC260 rendered pages below `/tmp/quorivio-import-*` and then attempted an atomic `Path.rename` to `/conversions/<job>/pages`; that fails across devices with `OSError: [Errno 18] Invalid cross-device link` (`EXDEV`). The original RC260 was reproduced failing with errno 18; RC261 renders real PDF and PPTX on a separate `/dev/shm` volume and publishes them successfully.
- RC260 GitHub run [42486677344](https://github.com/desalvo/quorivio/actions/runs/42486677344), commit `d3f58e634d13900ea989aca7d68e82f38acd7e38`: **production quality gate succeeded**, converter **container build gate failed** at Trivy because of two HIGH issues, `CVE-2026-76844` and `CVE-2026-85091`, in Debian `zlib1g`; fixed baseline `1:1.3.dfsg+really1.3.1-1+deb13u1`.

## Fixes and validation

1. Render in a private temporary directory *inside the conversion job workspace*, preserving same-volume atomic publication, cleanup and no partial output.
2. Log only the safe numeric POSIX `errno` on worker I/O failures; no document paths or converter stderr.
3. Map an explicit worker HTTP 422 to a sanitized `conversion_failed` response/UI message instead of the generic `internal_error`.
4. Upgrade and verify fixed Debian `zlib1g` **before** Poppler/LibreOffice installation. Do not bypass Trivy `HIGH,CRITICAL` or compromise the earlier APT fix.
5. Standalone wizard RC261 permits `--sync-generated` to adopt a **converter-image-only** change previously rolled out to Kubernetes; all other drift remains denied and previous manifests receive private backups.
6. Mandatory RC261 CI preflight for cross-mount conversion, security fixes and live two-mount Poppler/LibreOffice PDF/PPTX integration following native dependency setup.

## Deploying the fix into an existing Kubernetes cluster

**Do not update until RC261 is committed, its full CI is green, and the converter image is published using the separate manual converter workflow.** Pushing to GitHub does not publish the converter automatically.

1. Dispatch **Publish Quorivio PDF/PPTX converter (manual only)** on `main`, explicitly authorize the publication, confirm multiarch completion, and copy its real published `sha256` digest from the job logs.
2. Confirm `kubectl config current-context` and `kubectl -n quorivio get deployment quorivio`.
3. Replace only the sidecar image with the **verified immutable digest** (placeholder below):

   ```bash
   kubectl -n quorivio set image deployment/quorivio \
     converter=desalvo/quorivio-converter@sha256:<VERIFIED_DIGEST>
   kubectl -n quorivio rollout status deployment/quorivio
   ```

   `<VERIFIED_DIGEST>` is a placeholder. Restarting unchanged `:latest` with `IfNotPresent` can reuse an old cached image.
4. Run the updated standalone wizard to synchronize original Kustomize manifests **without changing the cluster**:

   ```bash
   python3 k8s_wizard.py --sync-generated --generated-dir ./k8s-generated \
     --set namespace=quorivio --set name=quorivio
   kubectl kustomize ./k8s-generated > /dev/null
   ```

5. Perform actual PDF and PPTX flattened image imports and inspect the converter's sanitized error logs if necessary. New user-facing API errors require separately publishing an updated application image; the actual conversion is fixed in the dedicated converter image.

Database, Secrets, storage, TLS and other containers are not rewritten by local reconciliation. The production cluster was not changed during this development cycle.
