#!/usr/bin/env bash
# Explicit push-to-main publication after the COMPLETE automatic RC acceptance.
# Independent of manual workflow_dispatch image publication; fail closed.
set -euo pipefail
[[ "${GITHUB_EVENT_NAME:-}" == push ]] || { echo 'Commit publication requires a push event' >&2; exit 2; }
[[ "${GITHUB_REF:-}" == refs/heads/main ]] || { echo 'Commit publication requires main' >&2; exit 2; }
[[ "${GITHUB_REPOSITORY:-}" == desalvo/quorivio ]] || { echo 'Unexpected publisher repository' >&2; exit 2; }
[[ "${GITHUB_SHA:-}" =~ ^[0-9a-fA-F]{40}$ ]] || { echo 'Invalid commit SHA' >&2; exit 2; }
[[ "${QUORIVIO_CAMPAIGN_CONCLUSION:-}" == success ]] || { echo 'Full RC campaign must succeed before publishing' >&2; exit 2; }
[[ "${QUORIVIO_COMMIT_MESSAGE:-}" == *'[publish-docker]'* ]] || { echo 'Explicit [publish-docker] marker missing' >&2; exit 2; }
[[ -n "${GITHUB_OUTPUT:-}" ]] || { echo 'Missing GitHub output file' >&2; exit 2; }
# The single explicit marker opts in to updating both the immutable SHA tag
# and latest, but no untrusted user-supplied Docker tag is ever interpolated.
{
  printf 'tags<<QUORIVIO_IMAGE_TAGS_EOF\n'
  printf 'desalvo/quorivio:sha-%s\n' "${GITHUB_SHA:0:12}"
  printf 'desalvo/quorivio:latest\n'
  printf 'QUORIVIO_IMAGE_TAGS_EOF\n'
} >> "$GITHUB_OUTPUT"
echo 'Verified commit publication after successful complete RC campaign'
