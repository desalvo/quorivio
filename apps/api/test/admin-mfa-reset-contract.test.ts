import { test } from 'node:test';
import { strict as assert } from 'node:assert';
import { readFileSync } from 'node:fs';
const server=readFileSync(new URL('../src/server.ts',import.meta.url),'utf8');
test('admin MFA reset requires administrator and step-up credentials',()=>{
 const route=server.slice(server.indexOf("app.post('/api/admin/users/:id/mfa/reset'"),server.indexOf("app.patch('/api/admin/users/:id/identity'"));
 assert.ok(route.includes('requireAuth,requireAdmin'));
 for(const safeguard of ['admin_password','bcrypt.compare','admin_totp_code','verifyTotp','confirm!==true','primary_admin_mfa_protected','use_self_service_mfa_disable','FOR UPDATE','DELETE FROM mfa_recovery_codes','ws.close','COMMIT'])assert.ok(route.includes(safeguard),`missing ${safeguard}`);
 assert.ok(!route.includes('res.json({recovery_codes'));
});
test('administrator directory reports MFA state without secrets',()=>{
 const route=server.slice(server.indexOf("app.get('/api/admin/users'"),server.indexOf("app.patch('/api/admin/users/:id'"));
 assert.ok(route.includes('totp_enabled'));
 assert.ok(!route.includes('totp_secret'));
});
