#!/usr/bin/env bash
# RC302: one explicit consent publishes app and converter with matching labels.
# Both repos and native architecture digests are preflighted before ANY tag
# is mutated. Docker Hub has no cross-repository atomic transaction.
set -euo pipefail

[[ "${GITHUB_REPOSITORY:-}" == desalvo/quorivio ]] ||
  { echo 'Unexpected publisher repository' >&2; exit 2; }
[[ "${GITHUB_EVENT_NAME:-}" == workflow_dispatch || "${GITHUB_EVENT_NAME:-}" == push ]] ||
  { echo 'Unsupported publication event' >&2; exit 2; }
[[ -n "${QUORIVIO_IMAGE_TAGS:-}" ]] ||
  { echo 'No approved publication labels' >&2; exit 2; }

app_dir="${QUORIVIO_DIGEST_DIR:-digests}"
converter_dir="${QUORIVIO_CONVERTER_DIGEST_DIR:-converter-digests}"
app_tags=()
converter_tags=()
while IFS= read -r tag; do
  [[ "$tag" =~ ^desalvo/quorivio:([A-Za-z0-9_][A-Za-z0-9_.-]{0,127})$ ]] ||
    { echo 'Unapproved Docker tag' >&2; exit 2; }
  label="${BASH_REMATCH[1]}"
  for existing in "${app_tags[@]}"; do
    [[ "$existing" != "$tag" ]] || { echo 'Duplicate Docker tag' >&2; exit 2; }
  done
  app_tags+=("$tag")
  converter_tags+=("desalvo/quorivio-converter:$label")
done <<< "$QUORIVIO_IMAGE_TAGS"
(("${#app_tags[@]}" >= 1 && "${#app_tags[@]}" <= 2)) ||
  { echo 'Expected one or two matching tags per repository' >&2; exit 2; }

for kind in app converter; do
  if [[ "$kind" == app ]]; then
    repo=desalvo/quorivio
    source_dir="$app_dir"
  else
    repo=desalvo/quorivio-converter
    source_dir="$converter_dir"
  fi
  [[ -d "$source_dir" && ! -L "$source_dir" ]] ||
    { echo "Missing or unsafe digest directory for $kind" >&2; exit 2; }
  first=''
  for arch in amd64 arm64; do
    file="$source_dir/$arch.digest"
    [[ -f "$file" && ! -L "$file" ]] ||
      { echo "Missing or unsafe digest file for $kind/$arch" >&2; exit 2; }
    digest="$(cat "$file")"
    [[ "$digest" =~ ^sha256:[a-f0-9]{64}$ ]] ||
      { echo "Invalid native digest for $kind/$arch" >&2; exit 2; }
    [[ "$digest" != "$first" ]] ||
      { echo "Duplicate architecture digest for $kind" >&2; exit 2; }
    first="$digest"
    docker buildx imagetools inspect --raw "$repo@$digest" |
      python3 -c 'import json,sys
arch=sys.argv[1]
obj=json.load(sys.stdin)
entries=obj.get("manifests") or [obj]
platforms=[e.get("platform",{}) for e in entries]
if not any(p.get("os")=="linux" and p.get("architecture")==arch for p in platforms):
    sys.exit("Native OCI digest does not contain linux/"+arch)
' "$arch"
  done
done

# The existing publisher revalidates each individual manifest and its tags.
app_labels="$(printf '%s\n' "${app_tags[@]}")"
converter_labels="$(printf '%s\n' "${converter_tags[@]}")"
QUORIVIO_IMAGE_REPOSITORY=desalvo/quorivio \
 QUORIVIO_IMAGE_TAGS="$app_labels" QUORIVIO_DIGEST_DIR="$app_dir" \
 bash tools/publish_multiarch_manifest.sh
QUORIVIO_IMAGE_REPOSITORY=desalvo/quorivio-converter \
 QUORIVIO_IMAGE_TAGS="$converter_labels" QUORIVIO_DIGEST_DIR="$converter_dir" \
 bash tools/publish_multiarch_manifest.sh

printf 'Validated both multiarch repositories and matching labels:\n'
printf '  %s\n' "${app_tags[@]}" "${converter_tags[@]}"
