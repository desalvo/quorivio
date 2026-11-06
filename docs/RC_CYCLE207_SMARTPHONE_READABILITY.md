# RC207 — readable phone questions and response widgets

Base: RC206 cumulative; application version remains `0.1.0-dev`.

## Problem and root cause
The smartphone editor, rehearsal and real participant display use a separate 390 logical-pixel portrait stage, but answer, free-text and submit-control inline styles were still expressed in `cqw` relative to the 1280px desktop stage. A 16px desktop answer would therefore appear around 4.9px on a 390px phone. Explicit rich-text font-size spans suffered the same scaling. Separately, automatic widget heights reserved only 29px per choice despite long answers and touch controls.

## Fix
- Default smartphone question title inherits 22px Arial/bold, answer labels/fields and submit buttons are 18px. Choice and submit tap targets occupy at least 44px; the free-text field stays at least 76px. Desktop cqw styling remains unchanged.
- The same phone-specific pixel custom properties are consumed in editor, smartphone rehearsal and participant phone, with the widget's explicit answer/submit typography and phone overrides taking precedence over defaults.
- Character-specific rich-text sizes use a second phone-only CSS custom property; non-font formatting and desktop sizes are unchanged.
- The automatic portrait layout reserves space for wrapped answer text up to 255 characters and subquestions instead of shrinking it. Authored smartphone positions are not changed by the planner.
- The shared regression checks run as dependency-free Python/Node preflight and a real Chromium computed-geometry test once the browser is installed. No new API migration or permission change.

## Local evidence and remaining acceptance
Node API `616/616`, web `360/360`, focused Python regression `40/40`, and real Chromium CSS fixture passed across editor/rehearsal/public phone, including custom 26/27px runs. The complete React/Vite typecheck cannot run locally without the `vite/client` dependency; PostgreSQL/live interactive smoke and full GitHub RC207 CI remain pending. Certified product completion **85.25%**, 43 accepted and 17 partial gates. `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or tag. Most recent confirmed full-green baseline: RC203 `42110429701`.
