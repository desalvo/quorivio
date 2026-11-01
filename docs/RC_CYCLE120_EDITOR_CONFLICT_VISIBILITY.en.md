# RC120 — Visible conflict status

CI run 41338170505 passes the Chromium editor and audience stages, but the real PostgreSQL autosave/concurrency acceptance detects an invisible status due to flex shrink in the busy toolbar. The correction is visual and keeps optimistic revision checks, conflict resolution and server-side persistence untouched. The new Chromium gate uses the actual production CSS at desktop and mobile widths.
