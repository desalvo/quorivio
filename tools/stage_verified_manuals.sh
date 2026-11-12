#!/usr/bin/env bash
# Stage current IT/EN PDF guides into the app image; fail closed on missing data.
set -euo pipefail
source_root="$1"
test -d "$source_root"
destination="apps/web/public/docs/manuals"
mkdir -p "$destination"
for role in user presenter admin; do
  for lang in it en; do
    name="$role-guide.$lang.pdf"
    candidates="$(find "$source_root" -type f -name "$name" -print)"
    test "$(printf '%s\n' "$candidates" | sed '/^$/d' | wc -l)" -eq 1 || { echo "Missing/duplicated PDF: $name" >&2; exit 1; }
    source_file="$candidates"
    test -s "$source_file"
    test "$(head -c 5 "$source_file")" = '%PDF-'
    test "$(wc -c < "$source_file")" -gt 10240
    cp "$source_file" "$destination/$name"
    cmp "$source_file" "$destination/$name"
    sha256sum "$destination/$name"
  done
done
echo "Verified all six build-matched manuals in the Docker app context."
