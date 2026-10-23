/** Strict comparison prevents cross-scheme Origin bypass on state-changing API calls. */
export function allowedWriteOrigin(origin:string|undefined,publicBaseUrl:string):boolean{
  if (!origin) return true; // non-browser/API clients; session cookies remain SameSite=Strict
  try {
    const received = new URL(origin);
    const expected = new URL(publicBaseUrl);
    return received.origin === expected.origin && received.username === '' && received.password === '';
  } catch {return false;}
}

/** WebSocket handshakes from browsers must supply an exact trusted Origin.
 * Non-browser clients without Origin remain permitted only after authentication. */
export function allowedLiveOrigin(origin:string|undefined,publicBaseUrl:string):boolean{
  return allowedWriteOrigin(origin,publicBaseUrl);
}
