# Artistic timer faces and fill precedence — cycle 42

A presenter can select the **Timer face** in a Timer or Timed Quiz widget’s properties: **Hourglass**, **Circular clock**, or **Digital**. The choice persists in the page design and passes a strict server allowlist, and is rendered in the editor, rehearsal and public projections. Legacy widgets default to Hourglass. Real countdown state, not a simulated animation, drives the face. Urgent styling highlights the last seconds.

Explicit transparency, solid fills, gradients and image fills override artistic theme backgrounds. `fillOpacity=0` must not reveal a decorative theme gradient. Reduced-motion settings disable ornamental movement without stopping the live timer.

**Acceptance after commit:** check all faces in Chromium, Firefox and WebKit on all four surfaces; verify saved persistence, timer expiry, zero-opacity, gradient and private image fills, and unauthorised asset protection. Local tests do not advance the formal RC gate score.
