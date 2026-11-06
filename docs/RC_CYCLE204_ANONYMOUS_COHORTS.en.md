# RC204 — Privacy-first statistical exports and small-cohort suppression

**Source:** RC203 was committed and its complete GitHub Actions RC campaign succeeded ([42110429701](https://github.com/desalvo/quorivio/actions/runs/42110429701)), including native OCI AMD64/ARM64 and verified Docker Hub multiarch publishing. Source version remains `0.1.0-dev`.

## Functional change

- Anonymous CSV and XLSX statistical exports now **suppress each answer/score/reaction bucket with fewer than five DISTINCT participant IDs**. Repeated submissions by a single participant never unlock a bucket. Counts represent distinct respondents, not repeat events. Suppression is per answer, question/widget, page and kind. This can result in header-only exports for small sessions, by design.
- Rows with missing participant IDs cannot satisfy a cohort threshold. Anonymous free-text, rating comments and file responses are replaced with a fixed placeholder only when their cohort independently meets the threshold. Names, IDs, precise timestamps and raw private answers are never included in the anonymized cells.
- Anonymous download filenames no longer reveal active session join codes. Default UI anonymization remains enabled. Only the primary owner can explicitly request identifiable/raw CSV or XLSX; existing authorization and `private, no-store` delivery headers remain in place.
- The dashboard export description explains the five-respondent suppression rule. The downloadable OOXML worksheet retains inline-string cells (no formula evaluation), and CSV formula-prefix escaping remains active.

## Limits and acceptance

This is a pragmatic disclosure safeguard, **not a guarantee of anonymity**: repeated exports, tiny populations, unique question labels and auxiliary information may still allow inferences. Review and legal/operational GDPR sign-off remain open. Suppressed cells are omitted, not rounded or filled with misleading zeros. This is not the same as differential privacy.

**Local verification:** API Node 615/615, frontend Node 352/352 (before final additional XLSX regression), RC204 Node cohort tests, RC204 early preflight, API owner check and real XLSX worksheet decoding PASS. Complete CI of RC204 is not yet verified. Certified release readiness is **85.25%** (43 accepted and 17 partial independent gates). `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No commit, push or tag by the assistant.
