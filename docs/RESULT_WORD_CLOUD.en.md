# Per-widget result word cloud (2026-10-23)

The presenter-only results panel supports a fourth **Cloud** visualization for question widgets. The editor stores `resultsView: "cloud"` on the individual widget alongside bars, pie and table. Labels derive from the widget's configured options and relative type sizes derive from the per-revision counts; every entry retains an explicit numeric count for accessibility. Revisions remain separate. The cloud is a frequency-based visualization of configured options, **not** extraction of words from free-text answers. Aggregate page Results retains its pre-existing bars/pie/table modes.

Local TypeScript/backend and Vite builds pass. Node unit regressions pass. Browser, screenreader, data correctness on PostgreSQL and end-to-end synchronization remain unverified; this does not close an RC gate.
