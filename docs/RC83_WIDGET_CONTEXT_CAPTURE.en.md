# RC83 native widget context ownership

The extended CI run 41232865276 observed `canvas_background_menu_open=True` after a browser-native right click on a visible widget, although Playwright verified hit-tested coordinates. This is **not** merely a locator failure; right click must be routed correctly by the production editor.

In RC83, `.widget-canvas` owns native context-menu dispatch at the **capture phase**. A widget target is recognized by DOM ancestry or, in the presence of retargeting, a hit against actual widget client rectangles. The code validates the widget identifier against current page widgets before opening `Azioni widget`. A genuinely blank point retains the page-background menu. No forced/synthetic click, no keyboard fallback, no release gate promotion.

Coverage: 3 Node geometry/selection unit cases and Python source/regression checks. Full native Chromium/Firefox/WebKit behavior and TypeScript Vite build require a new GitHub Actions run. The previous failure proves the old behavior was broken, but not yet that RC83 resolves it in production.
