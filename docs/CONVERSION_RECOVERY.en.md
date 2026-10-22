# Recovering a conversion reservation

If the isolated PDF/PPTX conversion worker exits unexpectedly, its `.conversion-lock` directory remains intentionally in place. This prevents a new worker from modifying output possibly left by an interrupted operation.

1. Stop **every** converter worker that mounts the same conversion storage. Do not rely only on a single pod restart.
2. Identify the affected opaque 32-hex-character job ID. Verify no converter is operating on that volume.
3. Inspect in read-only mode: `python3 tools/recover_conversion_lock.py JOBID --root /conversions`.
4. Check operational logs and failed job output; preserve any needed forensic evidence.
5. If the job has one valid source, no `pages` output, and the lock is empty, explicitly recover using `python3 tools/recover_conversion_lock.py JOBID --root /conversions --recover --workers-stopped`.
6. Restart the worker and retry the authorized conversion.

The tool refuses unknown IDs, symlinked paths, nonempty locks, missing/ambiguous sources, and existing output. It cannot prove workers are stopped; `--workers-stopped` is an explicit operator assertion. Never run recovery during concurrent conversion. Do not expose this tool as an unauthenticated HTTP endpoint.
