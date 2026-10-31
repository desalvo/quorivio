/** A bounded application-level heartbeat made of fresh, authoritative snapshots.
 * Database reads are bounded across independent active sessions, not merely
 * deduplicated among sockets within one session. Overlapping timer ticks do
 * not start a second sweep, avoiding a PostgreSQL connection stampede.
 * The entire sweep still visits every live session, including sessions
 * queued behind a slow read; errors do not starve neighboring sessions.
 * No NOTIFY is published: replicas update their own connected sockets.
 */
export const MAX_LIVE_REFRESH_CONCURRENCY = 32;
export const DEFAULT_LIVE_REFRESH_CONCURRENCY = 8;

export function validLiveRefreshConcurrency(value: number): number {
 if (!Number.isSafeInteger(value) || value < 1 || value > MAX_LIVE_REFRESH_CONCURRENCY) {
  throw new RangeError(`live refresh concurrency must be an integer in [1, ${MAX_LIVE_REFRESH_CONCURRENCY}]`);
 }
 return value;
}

export function createLivePeriodicRefresh(options: {
 activeSessions: () => Iterable<string>;
 isSessionActive?: (sessionId: string) => boolean;
 readAndSend: (sessionId: string) => Promise<void>;
 onError?: (error: unknown, sessionId: string) => void;
 maxConcurrent?: number;
}) {
 const maxConcurrent = validLiveRefreshConcurrency(options.maxConcurrent ?? DEFAULT_LIVE_REFRESH_CONCURRENCY);
 const inFlight = new Set<string>();
 let running = false;
 const tick = async (): Promise<void> => {
  // Return immediately to the interval callback while the current sweep is
  // running; pending sessions are already covered by the original sweep.
  if (running) return;
  running = true;
  try {
   const ids = [...new Set(options.activeSessions())].filter(Boolean);
   let cursor = 0;
   const workers = Array.from({length: Math.min(maxConcurrent, ids.length)}, async () => {
    while (cursor < ids.length) {
     const sessionId = ids[cursor++];
     // Avoid needless database reads for sessions whose last client left
     // while this bounded sweep was waiting for an available worker.
     if (options.isSessionActive && !options.isSessionActive(sessionId)) continue;
     inFlight.add(sessionId);
     try { await options.readAndSend(sessionId); }
     catch (error) {
      try { options.onError?.(error, sessionId); }
      catch { /* An exception in reporting must not halt the sweep. */ }
     }
     finally { inFlight.delete(sessionId); }
    }
   });
   await Promise.all(workers);
  } finally { running = false; }
 };
 return {tick, pendingCount: () => inFlight.size, isRunning: () => running};
}
