# Quorivio RC cycle 41 — Configurable artistic widget themes

Four per-widget `style.artTheme` values: `studio` (default), `glass`, `playful`, `minimal`. Four independent `style.artEffect` values: `none` (default), `float`, `glow`, `tilt` (depth shadow without changing stage rotation or placement). The editor exposes both selectors in the appearance fieldset.

The server validates a strict enum allowlist; values are saved with each page widget and retained across JSON export/import. The renderer uses the same theme data across editor, interactive rehearsal, presenter and participant surfaces. Explicit transparency, image fills, gradients, and authored colors take precedence over the decorative style. This feature accepts no arbitrary CSS URL or remote resources.

Timers combine a semantic hourglass, circular progress ring, and readable numerical count, with a static editor mini-preview and live rehearsal/presentation timing. Motion honours `prefers-reduced-motion`. Decorative layers do not become interactive or change the screen-reader reading order.

**Limit:** new built-in themes use CSS illustrations/textures rather than a built-in stock photo library. Presenters can use their own uploaded images as independent fills. Full browser/build acceptance of the changes is still pending after the maintainer's commit.
