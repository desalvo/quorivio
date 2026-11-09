# Quorivio RC275 — Shared linked result rendering CI fix

GitHub Actions run [42551661125](https://github.com/desalvo/quorivio/actions/runs/42551661125) failed in the RC220 pre-npm step: historical RC192 asserted a literal `result={widget}` call, but RC274 deliberately passes `result={viewWidget}` into `LinkedResultSourceQuestion` so the R toggle controls source-answer highlighting. RC196 had the same outdated expectation in a later gate.

Both contracts now verify the active bridge. New RC275 negative tests detect accidental return to plain `widget` or removal of `hasKey&&truthVisible`; public answer keys remain protected. No runtime API/UI changes. Historical RC274 checksums are immutable, RC275 is the current source inventory. Local checks, release metadata and ZIP integrity are validated, while full CI and live/browser acceptance remain pending. **85.25%**; `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag.
