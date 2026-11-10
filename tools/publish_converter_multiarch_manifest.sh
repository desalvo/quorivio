#!/usr/bin/env bash
# RC302: converter gets matching authorized tags, native AMD64/ARM64 only.
set -euo pipefail
fail(){ echo "$1" >&2; exit 2; }
[[ "${GITHUB_REPOSITORY:-}" == desalvo/quorivio ]] || fail 'Wrong repository'
[[ "${GITHUB_REF:-}" == refs/heads/main || "${GITHUB_REF:-}" == refs/tags/v* ]] || fail 'Wrong ref'
[[ "${GITHUB_SHA:-}" =~ ^[0-9a-fA-F]{40}$ ]] || fail 'Invalid commit'
case "${GITHUB_EVENT_NAME:-}" in
  push)
    [[ "$GITHUB_REF" == refs/heads/main ]] || fail 'Push must be main'
    [[ "${QUORIVIO_COMMIT_MESSAGE:-}" == *'[publish-docker]'* ]] || fail 'Explicit marker missing'
    [[ "${QUORIVIO_CAMPAIGN_CONCLUSION:-}" == success ]] || fail 'Full RC must pass'
    ;;
  workflow_dispatch)
    [[ "${QUORIVIO_PUBLISH_IMAGE:-}" == true ]] || fail 'No manual publish permission'
    [[ "${QUORIVIO_RC_ACCEPTANCE_SUITE:-}" != true ]] || fail 'RC campaign cannot authorize publishing'
    ;;
  *) fail 'Unsupported event';;
esac
mode="${1:---publish}"
[[ "$mode" == --publish || "$mode" == --verify-only ]] || fail 'Unknown mode'
source_dir="${QUORIVIO_DIGEST_DIR:-digests}"
[[ -d "$source_dir" && -n "${QUORIVIO_IMAGE_TAGS:-}" ]] || fail 'Missing digests/tags'
tags=()
while IFS= read -r tag; do
  [[ "$tag" =~ ^desalvo/quorivio:[A-Za-z0-9_][A-Za-z0-9_.-]{0,127}$ ]] || fail 'Invalid app tag'
  tags+=("desalvo/quorivio-converter:${tag#desalvo/quorivio:}")
done <<< "$QUORIVIO_IMAGE_TAGS"
(( ${#tags[@]} >= 1 && ${#tags[@]} <= 2 )) || fail 'Unexpected tag count'
if (( ${#tags[@]} == 2 )); then [[ "${tags[0]}" != "${tags[1]}" ]] || fail 'Duplicate tags'; fi
digests=()
for arch in amd64 arm64; do
  f="$source_dir/converter-$arch.digest"
  [[ -f "$f" && ! -L "$f" ]] || fail "Missing $arch converter digest"
  digest="$(cat "$f")"
  [[ "$digest" =~ ^sha256:[0-9a-f]{64}$ ]] || fail "Invalid $arch converter digest"
  digests+=("$digest")
done
[[ "${digests[0]}" != "${digests[1]}" ]] || fail 'Duplicate architecture digests'
for i in 0 1; do
  expected="$( [ "$i" = 0 ] && echo amd64 || echo arm64 )"
  docker buildx imagetools inspect --raw "desalvo/quorivio-converter@${digests[i]}" |
    python3 -c 'import json,sys
arch=sys.argv[1]; obj=json.load(sys.stdin)
items=obj.get("manifests") or [obj]
if not any(x.get("platform",{}).get("os")=="linux" and x.get("platform",{}).get("architecture")==arch for x in items):
    sys.exit("Wrong native converter architecture: "+arch)
' "$expected"
done
if [[ "$mode" == --verify-only ]]; then
  echo 'Verified native converter digests; no mutable tags written'
  exit 0
fi
args=()
for tag in "${tags[@]}"; do args+=(--tag "$tag"); done
docker buildx imagetools create "${args[@]}" \
  "desalvo/quorivio-converter@${digests[0]}" \
  "desalvo/quorivio-converter@${digests[1]}"
for tag in "${tags[@]}"; do
  docker buildx imagetools inspect --raw "$tag" |
    python3 -c 'import json,sys
obj=json.load(sys.stdin)
arches={(p.get("os"),p.get("architecture")) for x in obj.get("manifests",[]) for p in [x.get("platform",{})]}
if not {("linux","amd64"),("linux","arm64")}.issubset(arches):sys.exit("Incomplete converter multiarch manifest")
'
done
printf 'Verified published converter multiarch tags: %s\n' "${tags[*]}"
