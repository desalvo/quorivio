# Release Candidate batch — Rich widget styling and terminated-session duplication

Date: 2026-10-27. Based on the last **uncommitted** dashboard/widget appearance ZIP, which already contains the prior uncommitted editor/autosave improvements; last confirmed committed baseline `67a7be939a5930e2f9a49ce3932a4b7f29a682ac`.

## Functional changes

- Session duplicator is discoverable in the **Open sessions** directory for owners and collaborators, including closed sessions. The existing authorized API clones the portable session definition (pages, activity definitions, widgets, themes and referenced media), gives the requesting presenter ownership, a **draft** status, new activity/asset UUIDs and fresh joining credentials. It does **not** copy responses, participant identities, votes, statistics, moderation queues, or live state. User confirmation discloses precisely what is and is not copied.
- PostgreSQL mandatory portable acceptance now closes a session before duplicating it and verifies the new draft status, access credentials and distinct page/media IDs. Existing integrity and malware checks for imported media remain enabled.
- Strict API-validated widget styles: rectangle, rounded rectangle, circle, ellipse, triangle, diamond, cloud, speech bubble and hexagon; transparent or semi-transparent solid, gradient or private image fills; independent color, alpha, gradient end color, line dash/color/width for each widget. Image references are checked against the source session and must be real presenter-uploaded images, including result layout widgets. Private image fills are included in portable asset remapping and only exposed on the active audience page.
- A separate image can be selected from the presenter media library **or uploaded directly** for each widget. Editor, presenter, participant and rehearsal reuse one appearance renderer.
- Selecting a widget reveals a compact icon-based quick-format palette **below** the canvas; deselecting on blank canvas hides it. Includes fill/border colors, transparency, layer-independent horizontal/vertical canvas centering, typography and properties. Full rich style controls remain in the sole widget inspector.
- Confirm before deletion via canvas `×`, widget context menu, selection Delete/Backspace, selection cut and bulk deletion. Magnetic edge snap (1.5% tolerance), conservative axis-aligned collision rejection on move/resize/keyboard/arrange, collision-free insertion and single duplication, group copy placement rejection when overlap remains. For rotated/nonrectangular shapes this conservative rectangle rule is a limitation; cross-browser device validation pending.
- Default rating 0–10 buttons with explicit min/max labels; optional dropdown; reaction emojis available in audience and rehearsal; preview counter shows zero, timer runs from preview mount, presenter profile widget already available, rehearsal now shows QR and example result controls; results control stays presenter-only in the live audience.
- Canvas align-to-page left/right/top/bottom/center actions, subject to existing no-overlap restrictions.

## Evidence and status

- Node API + web tests and Python contract suites are locally executable, including new rich-style, media remapping, collision and closed-session privacy regressions.
- **Not yet externally accepted:** GitHub full quality/build, real Chromium+PostgreSQL with stored image fills, actual owner and collaborator closed-session duplication, browser/multidevice visual comparison, upload malware scanning on deployment, rotated-shape collision studies and assistive technology assessment. The new GitHub CI portable HTTP test is mandatory and has not run on this batch.
- RC gate ledger remains **53.0%**, **release_candidate_ready=false**. Do not promote A1/A3/B1 or claim production readiness on local results alone.
- No commit, push, tag or publication performed by the assistant.
