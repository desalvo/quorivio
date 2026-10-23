# Presenter-only Results control on a slide

The `results-button` widget is edited using the same pointer/keyboard geometry controls as other slide widgets. In the projection screen it is positioned using its persisted `x`, `y`, `width`, `height` and `rotation` percent coordinates, rather than the former horizontal margin. It toggles a private presenter results region outside the slide canvas. If a legacy slide lacks the control widget, a fallback Results button is shown beneath the slide.

The region contains aggregate results for the current activity, the timed-quiz leaderboard (when applicable), and every topic-question widget's dedicated list, fetched through presenter-authenticated routes with up to 10 questions per page. Participant screens do not render this control. This is an implementation-level validation, not a claim of multi-browser synchronization or database E2E tests.

Still open: per-widget chart-type selection, in-page interactive widget-scoped timed quizzes, true independent widget statistics, and live/browser/accessibility E2E testing.
