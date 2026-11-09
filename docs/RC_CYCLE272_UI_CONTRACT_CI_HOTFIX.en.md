# RC272 — Restore RC241 result-row style contract after RC270 composition

## Verified CI failure

Full CI [42537006971](https://github.com/desalvo/quorivio/actions/runs/42537006971) stopped at the **Production quality gate**, RC241 result/widget UI preflight, with `RC241 UI contract missing: per-row-result-style`. RC270 keeps the per-option `resultTextCss(widget.resultTextStyles,resultElementKey('row',...))` but composes it with pie chart palette colors using `style={{...resultTextCss(...),...(chart==='pie'?...}}`. The historical test matched only the earlier direct `style={resultTextCss(...)}` spelling; no functionality regression was observed in the result-row source.

## Fix and validation

* The RC241 guard matches direct or composed style on the same `linked-result-pair` JSX element, remaining fail-closed if the actual row-level style is removed.
* Add a negative removal test and an original-direct-style compatibility regression.
* Keep RC271 checksum receipts frozen as historical, promote current RC272 checksum source/ZIP inventory. Generalize the RC271 promotion regression so a new active version does not trigger the same release guard again.
* No API/web runtime behavior changes; RC270 backup, LDAP approval, audit and chart functionality retained.

GitHub full CI, skipped dependent jobs, actual PostgreSQL/NFS/S3/WebDAV restore, LDAP/SMTP and browser matrix remain pending. Ledger baseline **85.25%**. Flags `rc_strict=false`, `publish_image=false`, `publish_latest=false`. No assistant commit, push or tag.
