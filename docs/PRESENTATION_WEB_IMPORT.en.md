# Browser presentation import

Experimental presenter-only PDF/PPTX upload. The server validates the session and file type, runs a bounded Python converter, checks its manifest and per-page SHA-256 hashes, and inserts all slide pages transactionally. An error rolls back database changes and removes newly written assets. Max 100 MiB and 200 pages.

**Security gate:** QUORIVIO_ENABLE_CONVERTER defaults to disabled. Running a subprocess is not a complete security boundary; separate sandboxed conversion workers, CPU/memory caps, malware scanning, and PostgreSQL/browser integration tests are still required before production.
