import {test} from 'node:test';
import assert from 'node:assert/strict';
import {SESSION_RETENTION_DEFAULT_SQL, SESSION_RETENTION_PURGE_SQL, SESSION_DELETE_WITH_CLEANUP_SQL, SESSION_CLEANUP_CLAIM_SQL, retentionDeadline} from '../src/session-retention.ts';
const date=(s:string)=>new Date(s);
test('retention: closed session uses closure timestamp and own days',()=>{
 assert.equal(retentionDeadline('closed',date('2026-11-01'),date('2026-10-01'),7)?.toISOString(),'2026-10-08T00:00:00.000Z');
 assert.equal(retentionDeadline('closed',date('2026-11-01'),date('2026-10-01'),60)?.toISOString(),'2026-11-30T00:00:00.000Z');
});
test('retention: expired session anchors to expiry, not creation',()=>{
 assert.equal(retentionDeadline('expired',date('2026-10-01'),null,1)?.toISOString(),'2026-10-02T00:00:00.000Z');
});
test('retention: active, paused, ready, draft cannot purge',()=>{
 for(const status of ['active','paused','ready','draft']) assert.equal(retentionDeadline(status,date('2026-01-01'),null,1),null);
});
test('retention: closed legacy row without closure time waits for expiry',()=>{
 assert.equal(retentionDeadline('closed',date('2026-11-01'),null,1)?.toISOString(),'2026-11-02T00:00:00.000Z');
});
test('retention: invalid policy cannot create deadline',()=>{
 for(const days of [-1,0,1.5,NaN,Infinity,3651]) assert.equal(retentionDeadline('closed',date('2026-01-01'),null,days),null);
 assert.equal(retentionDeadline('closed',new Date('invalid'),null,1),null);
});
test('retention: boundary values 1 and 3650 accepted',()=>{
 assert.ok(retentionDeadline('closed',date('2026-01-01'),null,1));
 assert.ok(retentionDeadline('closed',date('2026-01-01'),null,3650));
});
test('retention: SQL uses per-session retention and guards live status',()=>{
 assert.match(SESSION_RETENTION_PURGE_SQL,/retention_days\s*\*\s*interval '1 day'/);
 assert.match(SESSION_RETENTION_PURGE_SQL,/status='closed' OR expires_at < now\(\)/);
 assert.doesNotMatch(SESSION_RETENTION_PURGE_SQL,/platform_settings/);
 assert.match(SESSION_RETENTION_PURGE_SQL,/RETURNING id/);
});
test('retention: platform setting applies only when creating new sessions',()=>{
 assert.match(SESSION_RETENTION_DEFAULT_SQL,/closed_session_retention_days/);
 assert.doesNotMatch(SESSION_RETENTION_DEFAULT_SQL,/UPDATE|DELETE/i);
});

test('retention: manual deletion atomically enqueues filesystem erasure',()=>{
 assert.match(SESSION_DELETE_WITH_CLEANUP_SQL,/WITH deleted AS/);
 assert.match(SESSION_DELETE_WITH_CLEANUP_SQL,/owner_id=\$2/);
 assert.match(SESSION_DELETE_WITH_CLEANUP_SQL,/INSERT INTO session_asset_cleanup_jobs/);
 assert.match(SESSION_DELETE_WITH_CLEANUP_SQL,/SELECT id FROM deleted/);
 assert.match(SESSION_DELETE_WITH_CLEANUP_SQL,/ON CONFLICT/);
});
test('retention: automated purge atomically enqueues filesystem erasure',()=>{
 assert.match(SESSION_RETENTION_PURGE_SQL,/INSERT INTO session_asset_cleanup_jobs/);
 assert.match(SESSION_RETENTION_PURGE_SQL,/SELECT id FROM deleted/);
 assert.match(SESSION_RETENTION_PURGE_SQL,/COALESCE\(closed_at, expires_at\)/);
});
test('session directory lease round-trips through millisecond-resolution JavaScript Dates',()=>{
 assert.match(SESSION_CLEANUP_CLAIM_SQL,/claimed_until=date_trunc\('milliseconds', now\(\)\+interval '5 minutes'\)/);
});
test('retention: cleanup workers lease work without colliding across replicas',()=>{
 assert.match(SESSION_CLEANUP_CLAIM_SQL,/FOR UPDATE SKIP LOCKED/);
 assert.match(SESSION_CLEANUP_CLAIM_SQL,/claimed_until < now\(\)/);
 assert.match(SESSION_CLEANUP_CLAIM_SQL,/LIMIT 50/);
 assert.match(SESSION_CLEANUP_CLAIM_SQL,/attempts=attempts\+1/);
});
