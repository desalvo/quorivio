/** A single authoritative snapshot has exactly two trust domains. Serialize
 * once per view, never once per recipient (especially at 500 clients). */
export interface LiveBroadcastSocket {
 readyState: number;
 bufferedAmount: number;
 send(payload: string): void;
 close(code: number, reason: string): void;
}

export interface LiveBroadcastResult {
 serialized: number;
 delivered: number;
 droppedSlow: number;
 transportErrors: number;
}

export function deliverLiveSnapshot<T extends LiveBroadcastSocket>(
 clients: Iterable<T>,
 data: unknown,
 audienceView: (snapshot: any) => unknown,
 isPresenter: (client: T) => boolean,
 shouldDropSlowSocket: (bufferedAmount: number, nextMessageBytes: number) => boolean,
 onTransportError: (error: unknown) => void = () => {},
): LiveBroadcastResult {
 const presenter: T[] = [], audience: T[] = [];
 // Take a stable view of the session. Newly connected clients explicitly
 // enqueue their own refresh and do not depend on joining this iteration.
 for (const client of clients) {
  if (client.readyState !== 1 /* WebSocket.OPEN */) continue;
  (isPresenter(client) ? presenter : audience).push(client);
 }
 const result: LiveBroadcastResult = {serialized: 0, delivered: 0, droppedSlow: 0, transportErrors: 0};
 // Prepare both payloads before sending any. A failed public projection must
 // never result in a partially distributed owner-only snapshot.
 const ownerPayload = presenter.length ? JSON.stringify({type: 'snapshot', data}) : undefined;
 const audiencePayload = audience.length ? JSON.stringify({type: 'snapshot', data: audienceView(data)}) : undefined;
 if (ownerPayload !== undefined) result.serialized++;
 if (audiencePayload !== undefined) result.serialized++;
 for (const [group, payload] of [[presenter, ownerPayload], [audience, audiencePayload]] as const) {
  if (payload === undefined) continue;
  const size = Buffer.byteLength(payload, 'utf8');
  for (const client of group) {
   // An asynchronous close can occur while the snapshot is being serialized.
   if (client.readyState !== 1) continue;
   if (shouldDropSlowSocket(client.bufferedAmount, size)) {
    result.droppedSlow++;
    try { client.close(1013, 'slow_consumer'); }
    catch (error) { result.transportErrors++; onTransportError(error); }
    continue;
   }
   try { client.send(payload); result.delivered++; }
   catch (error) {
    result.transportErrors++;
    onTransportError(error);
    try { client.close(1011, 'transport_error'); }
    catch (closeError) { result.transportErrors++; onTransportError(closeError); }
   }
  }
 }
 return result;
}
