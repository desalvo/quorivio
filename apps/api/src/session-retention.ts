/** Session-specific storage limitation, evaluated using PostgreSQL time.
 * Platform setting is a DEFAULT for new sessions, never an override of an
 * existing owner-selected retention window.
 */
export const SESSION_RETENTION_DEFAULT_SQL = `(SELECT value::integer FROM platform_settings WHERE key='closed_session_retention_days')`;

/** Purge only closed or expired sessions after their own retention period.
 * An expired but not closed session is anchored to expires_at. A closed session
 * with a closed_at timestamp is anchored to the actual closure. Legacy closed
 * rows without closed_at conservatively use expires_at.
 */
export const SESSION_RETENTION_PURGE_SQL = `
WITH deleted AS (
 DELETE FROM sessions
 WHERE (status='closed' OR expires_at < now())
   AND COALESCE(closed_at, expires_at) + retention_days * interval '1 day' < now()
 RETURNING id
), queued AS (
 INSERT INTO session_asset_cleanup_jobs(session_id)
 SELECT id FROM deleted
 ON CONFLICT (session_id) DO UPDATE SET claimed_until=NULL
 RETURNING session_id
) SELECT session_id AS id FROM queued`;

/** Durable cleanup outbox: session and enqueue are one atomic SQL statement. */
export const SESSION_DELETE_WITH_CLEANUP_SQL = `
WITH deleted AS (
 DELETE FROM sessions WHERE id=$1 AND owner_id=$2 RETURNING id
), queued AS (
 INSERT INTO session_asset_cleanup_jobs(session_id)
 SELECT id FROM deleted
 ON CONFLICT (session_id) DO UPDATE SET claimed_until=NULL
 RETURNING session_id
) SELECT session_id AS id FROM queued`;

/** Workers claim batches without racing other replicas; a crash expires the lease.
 * Truncate to JavaScript Date milliseconds so equality-fenced ACKs can match.
 */
export const SESSION_CLEANUP_CLAIM_SQL = `
UPDATE session_asset_cleanup_jobs
SET claimed_until=date_trunc('milliseconds', now()+interval '5 minutes'), attempts=attempts+1
WHERE session_id IN (
 SELECT session_id FROM session_asset_cleanup_jobs
 WHERE claimed_until IS NULL OR claimed_until < now()
 ORDER BY queued_at ASC LIMIT 50 FOR UPDATE SKIP LOCKED
) RETURNING session_id,claimed_until`;


export function retentionDeadline(status: string, expiresAt: Date, closedAt: Date | null, days: number): Date | null {
 if (!Number.isInteger(days) || days < 1 || days > 3650 || !Number.isFinite(expiresAt.getTime()) || (closedAt && !Number.isFinite(closedAt.getTime()))) return null;
 if (status !== 'closed' && status !== 'expired') return null;
 const start = closedAt ?? expiresAt;
 return new Date(start.getTime() + days * 86400000);
}
