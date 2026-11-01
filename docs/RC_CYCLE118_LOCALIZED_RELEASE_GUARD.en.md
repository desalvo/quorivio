# Quorivio RC118 — Localized release header verification

Run `41332909058` failed on four historical documentation assertions because active Italian RC117 headers reported `85.25%` instead of `85,25%`. The browser/Chromium gate never started; this run is not evidence that group Undo passes.

RC118 fixes current Italian and English headers, retains every immutable historic receipt, and adds a release guard that derives the exact localized score from the active gate ledger. Tests prove missing, stale, or wrongly localized scores fail before npm. No application logic, baseline acceptance score, or independent certification was changed. Full GitHub CI remains necessary.
