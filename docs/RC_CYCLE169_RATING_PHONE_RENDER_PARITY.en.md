# Quorivio 0.1.0-dev — RC169 — Rating and phone typography fidelity

## Baseline and defects

RC168 already shares mobile widget placement, but the **Rating** body still diverged between the editor, rehearsal, projector, and actual participant page. The real audience route omitted authored button size and text marking; the preview omitted the description and 0–9 legend; and the editor could render a duplicate optional comment field. A smartphone title could also fall back to 16px instead of inheriting the master title font size.

## Changes

1. `RatingStageContent` now owns the optional title, rich description, white accessible comment input, 0–9 scale, and authored button size, and is shared by all surfaces. Editor/projector stay read-only; only a real joined participant can submit remotely.
2. Remove the duplicate rating comment preview in the editor canvas.
3. `stageWidgetTypography` resolves master-title style before mobile font sizing, shared by rehearsal and actual public stage, with existing per-phone overrides preserved.
4. Match phone-stage widget overflow behavior between real audience and rehearsal.
5. Extend the disposable real Chromium/PostgreSQL participant fixture with a saved rating widget and explicit checks for one comment, ten choices, contrast, custom button size, and correct 1174-logical-pixel mobile stage height.

## Verification boundaries

RC169 Node and Python regression tests, local Chromium CSS/DOM 390/1440 acceptance, a before-npm preflight, and Git/ZIP SHA-256 inventory checks are supplied. The full Vite TypeScript build, disposable authenticated Chromium/PostgreSQL acceptance, and independent physical-device pixel comparisons remain CI/manual verification gates; local fixtures do not prove production device parity. Conservative certified progress stays **85.25% (43 accepted / 17 partial)**. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit/push/tag/deploy by the assistant.
