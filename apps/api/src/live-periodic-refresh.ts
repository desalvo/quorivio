/** A bounded application-level heartbeat made of fresh, authoritative snapshots.
 * One database read/fanout per active session, never one read per connected
 * participant. A success path cannot be claimed until readAndSend resolves.
 * Does not publish PostgreSQL NOTIFY: other replicas refresh their own sockets.
 */
export function createLivePeriodicRefresh(options: {
 activeSessions: () => Iterable<string>;
 readAndSend: (sessionId: string) => Promise<void>;
 onError?: (error: unknown, sessionId: string) => void;
}) {
 const inFlight = new Set<string>();
 const tick = async (): Promise<void> => {
  const sessionIds = new Set(options.activeSessions());
  await Promise.all([...sessionIds].map(async sessionId => {
   if (!sessionId || inFlight.has(sessionId)) return;
   inFlight.add(sessionId);
   try { await options.readAndSend(sessionId); }
   catch (error) { try { options.onError?.(error, sessionId); } catch { /* failure reporting must not kill heartbeat */ } }
   finally { inFlight.delete(sessionId); }
  }));
 };
 return {tick, pendingCount: () => inFlight.size};
}
