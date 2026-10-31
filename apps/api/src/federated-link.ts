/** OAuth callbacks arrive via cross-site navigation: a SameSite=Strict login
 * cookie is intentionally absent. Store the already authenticated session's
 * original issue time in the single-use DB state, and enforce revocation at
 * both initiation and redemption, including after password reset/admin MFA
 * revocation. An anonymous login does not store a linking principal.
 */
export const FEDERATED_LINK_ELIGIBLE_SQL = `SELECT id FROM users WHERE id=$1
 AND approved=true AND must_change_password=false
 AND (auth_revoked_at IS NULL OR auth_revoked_at<=to_timestamp($2::double precision/1000))
 AND (password_changed_at IS NULL OR password_changed_at<=to_timestamp($2::double precision/1000))`;

/** The account eligibility and link creation are ONE SQL statement, not a
 * separate stale SELECT followed by an unrestricted INSERT. Unique conflicts
 * are reported as HTTP 409 without exposing database details. */
export const FEDERATED_LINK_INSERT_SQL = `INSERT INTO oidc_identities(provider,subject,user_id)
 SELECT $1,$2,u.id FROM users u WHERE u.id=$3 AND $4::bigint>0
 AND u.approved=true AND u.must_change_password=false
 AND (u.auth_revoked_at IS NULL OR u.auth_revoked_at<=to_timestamp($4::double precision/1000))
 AND (u.password_changed_at IS NULL OR u.password_changed_at<=to_timestamp($4::double precision/1000))
 ON CONFLICT DO NOTHING RETURNING user_id`;

/** pg returns BIGINT as a string, and legacy rows have NULL. Fail closed. */
export function validFederatedLinkIssuedAt(value: unknown, now=Date.now()): number|null {
 if(typeof value!=='number' && (typeof value!=='string'||!/^[0-9]+$/.test(value)))return null;
 const issued=Number(value);
 if(!Number.isSafeInteger(issued)||issued<=0||issued>now+1000||now-issued>8*3600*1000)return null;
 return issued;
}
