/** Bound queued bytes per client to prevent one slow consumer from retaining
 * unbounded snapshot data during a large live presentation. */
export const MAX_LIVE_SOCKET_BUFFER_BYTES=2*1024*1024;
export function shouldDropSlowSocket(bufferedAmount:number, nextMessageBytes:number):boolean {
 return !Number.isSafeInteger(bufferedAmount)||bufferedAmount<0||!Number.isSafeInteger(nextMessageBytes)||nextMessageBytes<0||bufferedAmount+nextMessageBytes>MAX_LIVE_SOCKET_BUFFER_BYTES;
}
