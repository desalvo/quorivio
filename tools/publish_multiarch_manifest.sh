#!/usr/bin/env bash
# Atomic native AMD64 + ARM64 manifest publication; caller must authorize tags.
set -euo pipefail
[[ "${GITHUB_REPOSITORY:-}" == desalvo/quorivio ]] || { echo 'Wrong publishing repository' >&2; exit 2; }
image_repo="${QUORIVIO_IMAGE_REPOSITORY:-desalvo/quorivio}"
[[ "$image_repo" == desalvo/quorivio || "$image_repo" == desalvo/quorivio-converter ]] || { echo 'Unapproved image repository' >&2; exit 2; }
[[ "${GITHUB_EVENT_NAME:-}" == workflow_dispatch || "${GITHUB_EVENT_NAME:-}" == push ]] || { echo 'Unsupported publication event' >&2; exit 2; }
[[ -n "${QUORIVIO_IMAGE_TAGS:-}" ]] || { echo 'Missing approved image tags' >&2; exit 2; }
source_dir="${QUORIVIO_DIGEST_DIR:-digests}"
[[ -d "$source_dir" ]] || { echo 'Missing native build digests' >&2; exit 2; }
for arch in amd64 arm64; do
    digest_file="$source_dir/$arch.digest"
    [[ -f "$digest_file" && ! -L "$digest_file" ]] || { echo "Missing $arch digest" >&2; exit 2; }
    digest="$(cat "$digest_file")"
    [[ "$digest" =~ ^sha256:[a-f0-9]{64}$ ]] || { echo "Invalid $arch digest" >&2; exit 2; }
    if [[ "$arch" == amd64 ]]; then amd64="$digest"; else arm64="$digest"; fi
done
[[ "$amd64" != "$arm64" ]] || { echo 'Duplicate digest for different platforms' >&2; exit 2; }
tags=()
while IFS= read -r tag; do
    [[ -n "$tag" ]] || { echo 'Empty Docker image tag' >&2; exit 2; }
    [[ "$tag" =~ ^desalvo/quorivio(-converter)?:[a-zA-Z0-9_][a-zA-Z0-9_.-]{0,127}$ && "$tag" == "$image_repo:"* ]] || { echo 'Invalid publisher tag' >&2; exit 2; }
    tags+=("$tag")
done <<< "$QUORIVIO_IMAGE_TAGS"
((${#tags[@]} >= 1 && ${#tags[@]} <= 2)) || { echo 'Invalid tag count' >&2; exit 2; }
[[ "${tags[0]}" != "${tags[-1]}" || ${#tags[@]} == 1 ]] || { echo 'Duplicate tag' >&2; exit 2; }
# Abort on missing images, bad manifests, or a wrong platform BEFORE making
# mutable tags visible. The native runner name is not evidence by itself.
for pair in "amd64:$amd64" "arm64:$arm64"; do
    expected="${pair%%:*}"
    sha="${pair#*:}"
    docker buildx imagetools inspect --raw "$image_repo@$sha" |
      python3 -c 'import json,sys
arch=sys.argv[1]
obj=json.load(sys.stdin)
entries=obj.get("manifests") or [obj]
platforms=[e.get("platform",{}) for e in entries]
if not any(p.get("os")=="linux" and p.get("architecture")==arch for p in platforms):
    sys.exit("Native OCI digest does not contain linux/"+arch)
' "$expected"
done
args=()
for tag in "${tags[@]}"; do args+=(--tag "$tag"); done
docker buildx imagetools create "${args[@]}" "$image_repo@$amd64" "$image_repo@$arm64"
for tag in "${tags[@]}"; do
    docker buildx imagetools inspect --raw "$tag" |
      python3 -c 'import json,sys
obj=json.load(sys.stdin)
platforms={(p.get("os"),p.get("architecture")) for e in obj.get("manifests",[]) for p in [e.get("platform",{})]}
required={("linux","amd64"),("linux","arm64")}
if not required.issubset(platforms):
    sys.exit("Published manifest missing: "+str(sorted(required-platforms)))
'
done
printf 'Validated published multiarch tags: %s\n' "${tags[*]}"
