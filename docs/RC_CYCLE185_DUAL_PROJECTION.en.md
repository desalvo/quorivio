# RC185 — Independent presenter/audience live pages and cross-page results

## Baseline

RC184 was confirmed green in GitHub Actions [41993094578](https://github.com/desalvo/quorivio/actions/runs/41993094578) (commit `45f76e57b4c9e7a2acd3687893040d2d6d6658e6`): 14 successful jobs, 3 intentionally skipped image-publication jobs, zero failures. Preserve the green non-publishing, non-strict build as the release baseline. No assistant commit, push, tag, Docker Hub publication or release.

## Product behaviour delivered

- **Separate projection pointers**: `sessions.current_activity_id` continues to mean the only active audience page, while new nullable `sessions.presenter_activity_id` identifies the page projected by the authenticated presenter. The public snapshot contains only the audience activity; never the private presenter pointer or another page's results. Legacy sessions without the new value retain the previous same-page presentation behaviour.
- **Canvas right-click**: each page can choose the audience page to show while it is on the presenter screen (default: itself). It may also be excluded from the presenter navigation (`presenterHidden`) without deleting it or preventing that page from being an audience target. Controls are also in “Impostazioni pagina e risultati”. The arrows and keyboard navigation skip hidden pages and the displayed page counter counts presenter-visible slides only.
- **Atomic navigation**: the authorized server validates the chosen presenter page, checks the optional compare-and-swap presenter and audience pointers, resolves its audience mapping inside the same session and updates both pointers in one PostgreSQL transaction. All other audience pages close; the target audience page remains open, preserving `opened_at` when revisited. Only that target may receive votes, ratings, questions, reactions, uploads and other participant writes.
- **Cross-page Results widget**: in the widget inspector select the source *page*, the source *widget*, and optionally an individual question. Presenter-only live statistics are queried using the source's `activity_id` and widget ID, including independent questions, timed quizzes, ratings, reactions and topic questions. Updates follow owner live snapshots and polling. A missing source renders as unconfigured rather than reading another session.
- **Saving/collaboration**: new page controls and result links are part of autosave, downloaded local drafts and three-way conflict merge. The authenticated design endpoint checks the target audience page and result source in the same session before persisting. Deleting a page referenced by another page is rejected until links are cleared.
- **Import/export**: portable sessions carry source page identities only inside the private archive, then remap `audiencePageId` and `targetActivityId` to newly generated page IDs on import. Old independent sessions remain supported. Malformed or cross-session links are rejected.

## Example

1. Page A contains a question widget Q, and `presenterHidden=true`.
2. Page B contains a Results widget; select source page A and source widget Q. On B, set the audience destination to page A.
3. During a live session, the presenter displays B and sees Q's live answers, while the audience is still shown A and can answer Q. Advancing to another presenter-visible page changes the audience destination according to that page's configuration. A is skipped by the presenter's arrows but remains an active audience source.

## Security and validation

- Only presenter-authenticated APIs expose cross-page result details; participant snapshots are activity-scoped and public assets stay bound to the current audience page. No unrestricted read endpoint or direct client-defined page switching was introduced.
- Server accepts only legitimate same-session page and widget references; malformed UUIDs, forbidden widget kinds, nonexistent sources or nested question IDs are rejected.
- RC185 regressions: pure routing, backward compatibility, cross-page chart selection, portable identity remapping, private audience snapshot, transactional CAS and editor controls. Early preflight runs before npm, PostgreSQL and Docker.
- Local tests: API and frontend Node suites, Python contracts, TypeScript syntax and immutable package inventory; their exact counts are stored in the new local acceptance receipt. **Compiled Vite build, real PostgreSQL/Chromium dual-projection acceptance and the full GitHub campaign still require a new commit and CI run.** They are not claimed complete by local unit tests.

## Gate

Continue the previously certified **85.25%**, 43 accepted and 17 partial gates, until independent reviews and corresponding acceptance evidence permit promotion. Strict release and publication remain disabled by default.
