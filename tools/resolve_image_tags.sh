#!/usr/bin/env bash
# Manual publisher safety policy. Used exclusively by workflow_dispatch after quality and image gates.
set -euo pipefail
[[ "${GITHUB_EVENT_NAME:-}" == workflow_dispatch ]] || { echo 'Only workflow_dispatch may publish images' >&2; exit 2; }
[[ "${QUORIVIO_PUBLISH_IMAGE:-}" == true ]] || { echo 'Explicit publish_image consent is required' >&2; exit 2; }
[[ "${GITHUB_REPOSITORY:-}" == desalvo/quorivio ]] || { echo 'Unexpected image publisher repository' >&2; exit 2; }
[[ "${GITHUB_SHA:-}" =~ ^[0-9a-fA-F]{40}$ ]] || { echo 'Invalid checked-out commit SHA' >&2; exit 2; }
ref="${GITHUB_REF:-}"
case "$ref" in
  refs/heads/main) default_tag="sha-${GITHUB_SHA:0:12}" ;;
  refs/tags/v*)
    version="${ref#refs/tags/}"
    [[ "$version" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]] || { echo 'Only semver release tags may be published' >&2; exit 2; }
    default_tag="$version" ;;
  *) echo 'Only main or semver release tags may be published' >&2; exit 2 ;;
esac
custom="${QUORIVIO_PUBLISH_TAG:-}"
label="${custom:-$default_tag}"
# Restrict to a safe subset of Docker tags, never permit a second tag hidden in input.
[[ "$label" =~ ^[a-zA-Z0-9_][a-zA-Z0-9_.-]{0,127}$ ]] || { echo 'Invalid Docker image tag' >&2; exit 2; }
[[ "$label" != latest ]] || { echo 'latest requires the separate publish_latest checkbox' >&2; exit 2; }
extra="${QUORIVIO_PUBLISH_LATEST:-false}"
[[ "$extra" == false || "$extra" == true ]] || { echo 'Invalid publish_latest boolean' >&2; exit 2; }
if [[ "$extra" == true && "$ref" != refs/heads/main ]]; then
  echo 'latest can only be published from the main branch' >&2; exit 2
fi
[[ -n "${GITHUB_OUTPUT:-}" ]] || { echo 'GITHUB_OUTPUT is required' >&2; exit 2; }
{
  printf 'tags<<QUORIVIO_IMAGE_TAGS_EOF\n'
  printf 'desalvo/quorivio:%s\n' "$label"
  if [[ "$extra" == true ]]; then printf 'desalvo/quorivio:latest\n'; fi
  printf 'QUORIVIO_IMAGE_TAGS_EOF\n'
} >> "$GITHUB_OUTPUT"
printf 'Verified manual publication: %s (latest=%s)\n' "$label" "$extra"
