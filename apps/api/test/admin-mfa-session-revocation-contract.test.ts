import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
const schema=readFileSync(new URL('../src/schema.sql',import.meta.url),'utf8');
test('admin MFA recovery invalidates prior authentication cookies',()=>{
 assert.match(schema,/ADD COLUMN IF NOT EXISTS auth_revoked_at timestamptz/);
 assert.match(server,/totp_enabled=false,auth_revoked_at=now\(\)/);
 assert.match(server,/SELECT approved,must_change_password,password_changed_at,auth_revoked_at FROM users/);
 assert.match(server,/error:'session_revoked'/);
});
test('presenter WebSocket authentication honors session revocation',()=>{
 assert.match(server,/auth_revoked_at IS NULL OR auth_revoked_at <= to_timestamp/);
 assert.match(server,/password_changed_at IS NULL OR password_changed_at <= to_timestamp/);
});
