# RC225 — Attachments, filenames and visual background pickers

## Implemented

- Session assets and background library uploads retain original filenames as `display_name` metadata; physical files remain stored under opaque UUIDs, not user-provided paths.
- Case-insensitive duplicate detection returns HTTP 409 and proposes numbered filenames (`image (2).png`, `image (3).png`). The UI asks for explicit confirmation before retrying; DB uniqueness prevents concurrent overwrites.
- Session attachment rename/delete is available, with server validation, HTTP 204 handling, optimistic removal and inventory refresh. Background rename/delete maintains authorization and in-use checks.
- Thumbnail galleries show each preview with its filename beneath it, on the canvas context picker, page and results backgrounds, phone editor and slide master editor. Responsive internal scrolling ensures access on small screens.
- The slide master canvas now displays the selected global background immediately, matching inherited page backgrounds.
- Library background copies retain human-readable names and remain safe after their source library entry is deleted; old duplicate labels are migrated. Export/import bundles preserve names of referenced media, while remaining compatible with prior archives.
- Participant attachments retain sanitized filenames without colliding with presenter's library entries.

## Evidence and remaining gates

- Local Node API 628/628, frontend 390/390, seven focused Python contracts, and Chromium CSS at 320×240, 390×844 and 1440×900 green.
- Early RC225 preflight and browser CSS acceptance added to GitHub CI. Full TypeScript, integrated PostgreSQL, compiled React, Kubernetes and GitHub RC225 CI not yet executed.
- Last certified all-green CI remains RC219 run `42197607753`. Completion unchanged: **85.25%**, 43 accepted, 17 partial; version 0.1.0-dev, `rc_strict=false`, `publish_image=false`, `publish_latest=false`.
- No assistant commit, push or tag. Cumulative inventory preserves historical receipts.
