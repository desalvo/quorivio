/**
 * Serialize database schema upgrade and first-account provisioning across API
 * processes. PostgreSQL session advisory locks are released on connection loss;
 * use one dedicated pool client throughout bootstrap (never pool.query inside
 * the protected section, which could consume another connection).
 */
import type {Pool, PoolClient} from 'pg';

// Private two-key advisory lock namespace; neither key is user controlled.
export const BOOTSTRAP_LOCK_KEYS = [1726825682, 1903521631] as const;
const LOCK_SQL = 'SELECT pg_advisory_lock($1::integer,$2::integer)';
const UNLOCK_SQL = 'SELECT pg_advisory_unlock($1::integer,$2::integer) AS released';

export async function withBootstrapLock<T>(pool: Pick<Pool, 'connect'>,
    action: (client: PoolClient) => Promise<T>): Promise<T> {
  const client = await pool.connect();
  let locked = false;
  let sessionReset = false;
  let destroy = false;
  try {
    // A blocked follower must eventually fail readiness rather than hang forever.
    await client.query("SET lock_timeout = '120s'");
    await client.query(LOCK_SQL, [...BOOTSTRAP_LOCK_KEYS]);
    locked = true;
    await client.query('SET lock_timeout = DEFAULT');
    sessionReset = true;
    return await action(client);
  } finally {
    // If lock acquisition failed, even SET lock_timeout may have changed the
    // session. Never return that connection to the normal application pool.
    // On an interrupted lock acquisition PostgreSQL could also have an
    // uncertain session state. Destroying the lease fails closed.
    if (!locked || !sessionReset) destroy = true;
    if (locked) {
      try {
        const result = await client.query(UNLOCK_SQL, [...BOOTSTRAP_LOCK_KEYS]);
        if (result.rows[0]?.released !== true) destroy = true;
      } catch {
        // Never return a connection with an uncertain lock to the pool.
        destroy = true;
      }
    }
    client.release(destroy);
  }
}
