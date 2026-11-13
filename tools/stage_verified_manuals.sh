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

# Ship the build-matched six-page A4 portrait brochures in the native app too.
brochure_dir="apps/web/public/docs/brochures"
mkdir -p "$brochure_dir"
for lang in it en; do
  name="quorivio-brochure-$lang.pdf"
  mapfile -t matches < <(find "$source_root" -type f -name "$name" -print)
  test "${#matches[@]}" -eq 1 || { echo "Missing/duplicate portrait brochure: $name" >&2; exit 1; }
  source_file="${matches[0]}"
  test -s "$source_file"
  test "$(head -c 5 "$source_file")" = '%PDF-'
  test "$(wc -c < "$source_file")" -gt 20000
  cp "$source_file" "$brochure_dir/$name"
  cmp "$source_file" "$brochure_dir/$name"
  sha256sum "$brochure_dir/$name"
done
echo "Verified both six-page portrait brochures in the Docker app context."
