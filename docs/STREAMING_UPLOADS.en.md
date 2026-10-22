# Streaming binary uploads — 0.1.0-dev

Both `POST /api/sessions/:id/assets` and `POST /api/join/:code/activities/:aid/widgets/:wid/upload` now write incoming bytes progressively to private temporary files and enforce the limit while reading. SHA-256 and file-header sniffing no longer require buffering the whole upload in memory. Incorrect Content-Length, oversized transfers and mismatched signatures reject the upload and remove temporary files. Database metadata is committed only after successful file completion.

## Verification steps

1. Configure `QUORIVIO_ASSET_DIR` on private persistent storage and the upload limit (default 100 MB) in administration.
2. On an open session upload supported images, PDFs and videos. Test truncated bodies, falsified MIME and oversized payloads; verify error responses and absence of temporary files.
3. For participant uploads test the join cookie, open page, active file widget and ownership checks.
4. Verify checksum, authorized downloads, backups and restores, storage quotas and restarts.

## Known limitations

Malware scanning, multi-replica shared S3 storage and a durable orphan cleanup/reconciliation queue remain unavailable. Content-Length is required. Concurrent participant upload quotas require atomic enforcement. Basic signatures do not replace deep file inspection. PostgreSQL, proxy, browser and filesystem end-to-end verification are required before production approval.
