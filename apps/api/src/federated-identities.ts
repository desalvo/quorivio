/** Explicit management of account-linked SSO identities.
 * Password confirmation is mandatory for unlink, even for a valid session.
 * Never reveal immutable provider subject identifiers in an account listing.
 */
export const FEDERATED_IDENTITY_LIST_SQL = `SELECT provider, linked_at FROM oidc_identities WHERE user_id=$1 ORDER BY provider`;
export const FEDERATED_IDENTITY_UNLINK_SQL = `DELETE FROM oidc_identities WHERE user_id=$1 AND provider=$2 RETURNING provider`;
export function validFederatedProviderId(value: unknown): value is string {
 return typeof value === 'string' && /^[a-z][a-z0-9_-]{1,31}$/.test(value);
}
export function validFederatedUnlinkPassword(value: unknown): value is string {
 return typeof value === 'string' && value.length >= 1 && value.length <= 256;
}
