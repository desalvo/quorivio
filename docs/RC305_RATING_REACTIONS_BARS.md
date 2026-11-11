# RC305 — Rating privacy, reaction-bar geometry and sorting

2026-11-11. Baseline RC304 commit `29d573ad2c1826e4a3ce5663807b04cc1df4273b`.

## Changes

- Presenter's read-only rating widget explicitly suppresses any participant-selected score or comment, in live and rehearsal modes. Participant state remains local to the participant.
- The owner-only rating statistics route now includes the 0–9 histogram per session/page/source widget. It never emits individual participant votes or comments.
- All bar charts use the maximum **visible** count as 100% width; a zero-only series renders empty bars without division errors. Gradient normalization uses the same denominator.
- Overridden obsolete `max-content` sizing in scale-mode result widgets: each row and track occupies the actual widget width, removing the empty right gutter.
- Reactions and rating labels use widget-relative `cqw` sizing so resizing the widget rescales labels rather than preserving fixed icons.
- New `resultSortOrder` persisted on results-button: `index-asc`, `index-desc`, `count-asc`, `count-desc` (default count descending), configurable in Format widget.
- Node regression suite validates sort stability, scaling, source isolation, format persistence, API ownership contract and privacy.

## Acceptance

Verify in author editor, interactive preview, presenter projection and real participant device; cross-browser and PostgreSQL integration run through the main full CI before the paired native AMD64/ARM64 Docker images are updated. Certified RC progress remains **85.25% (43 accepted, 17 partial)** until independent external evidence is recorded.
