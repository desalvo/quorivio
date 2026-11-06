# RC228 — Historical gallery preflight CI recovery

## Verified GitHub failure

- User-committed RC227 run [42226572219](https://github.com/desalvo/quorivio/actions/runs/42226572219) on 6 November 2026, commit `ec9de12e8f7e39cbc90d573bc2758b7fdf034ce2`.
- Job `Production quality gate` (`127921466008`), step `RC225 asset filenames, delete recovery and schema background before npm`, failed in `AssetLibraryRegression.test_gallery_covers_all_background_flows` at line 30.
- The test demanded the exact inline prop `label="Immagine sfondo dello schema"`, which was removed from the source committed on GitHub when the schema gallery was moved into a portaled accessible dialog. The committed code instead uses `label="Scegli lo sfondo globale"` inside `SchemaBackgroundTool`.
- The RC campaign summary failed as a consequence, and dependent jobs were skipped. No runtime defect was established in that run, which stopped before most acceptance jobs.

## Fix

- Update the legacy RC225 regression to check the four remaining inline gallery labels and the new semantic schema dialog (`SchemaBackgroundTool`, `role="dialog"`, `aria-modal`, gallery selection with close, selected schema asset), not an obsolete literal.
- Add `test_rc228_ci_gallery_contract.py`: reproduce the committed label/call-site form, assert the legacy test still passes, then intentionally remove the modal and the close-on-select action and require the tests to fail. Run this early in GitHub CI, *before* npm and database/browser work.
- No authentication, personal information, API, database or image-publishing behavior was changed.

## Verification and gate policy

- Local focused Python suites and Node tests are recorded in the RC228 handoff; neither the complete GitHub CI nor the independent hardware/security gates have been certified by this change.
- Last complete GitHub CI success remains RC219 (`42197607753`). Certified 85.25% (43 accepted, 17 partial), unchanged.
- `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit/push/tag. The next commit message covers only this post-RC227 fix.
