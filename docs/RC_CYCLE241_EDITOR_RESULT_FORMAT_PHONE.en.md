# RC241 — Editor/results/phone parity and numeric controls

Based on RC240 cumulative, with full CI RC239 green as the latest acknowledged integrated baseline.

- Results answer labels share inherited font through their final word, while preserving count badges; a separate style record for each result/option supports family, size, colour, bold, italic, underline and strikethrough. The formerly collapsed result format controls are shown in the Text tab.
- Automatic mobile question height no longer adds a redundant 40px of reserved heading space on top of answer rows. Editor and rehearsal use the same 390 logical pixel stage padding and font-size conventions. The presenter single and side-by-side views use the same fixed 1280x720 logical stage with uniform scaling.
- Toolbar icon buttons for cut, copy, paste, info, undo and redo wire into editor selection/history; clipboard remains session-scoped.
- Every numeric control in Format Widget, including each independent result option, now supports a draft input that can be cleared and retyped without resetting and explicit step arrows usable independently of browser spinner rendering. Enter and blur commit once, Escape discards; keyboard ArrowUp/ArrowDown step within bounds.
- Mandatory early CI tests and release inventory checks. Previous RC240 receipt is preserved byte-for-byte. Integrated browser/TypeScript CI must run before RC241 sign-off.

Release flags remain `rc_strict=false`, `publish_image=false`, `publish_latest=false`. Certified 85.25% (43 accepted, 17 partial external gate sign-offs) unchanged. No commit/push/tag.
