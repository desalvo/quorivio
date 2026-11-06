# RC227 — Master background gallery and adaptive participant mode

## Implementation

- The slide-master ribbon presents an icon-above-caption **Backgrounds** tool with a complete tooltip, beside Upload and Remove; choosing an image opens a bounded named-thumbnail gallery rather than overflowing the master toolbar.
- The modal exposes accessible dialog labelling, Escape/backdrop close, Tab/Shift+Tab containment, focus restoration and aria-pressed for the selected image.
- A participant's auto-selected phone layout responds to viewport/pointer changes (including orientation) until one of the 16:9, smartphone or accessible-reading choices is explicitly activated; user choice is never overwritten.
- Existing attachment filenames, presentation permissions, session storage, widget and appearance behavior are unchanged; no DB/API migrations.

## Evidence and remaining gates

- All **398/398** web Node tests, **34/34** focused Python tests, TypeScript TSX syntax parsing and real Chromium representative CSS/modal viewport checks at 320, 390, 760 and 1440px pass; RC173 expectations updated for the new manual override behavior.
- Integrated compiled React/browser interactions, PostgreSQL and the full GitHub CI are still unverified. `npm ci` could not reach npm registry due to DNS `EAI_AGAIN`; this is not a build failure.
- Last fully green CI RC219 run `42197607753`; certified **85.25%** (43 accepted, 17 partial). `rc_strict=false`, `publish_image=false`, `publish_latest=false`; no commit, push, tag or image publication.

- The full Python test discovery did not complete within the local 45-second limit; no green global-suite claim is made.