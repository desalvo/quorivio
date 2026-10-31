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

/** A browser hosted at the current application Host may establish a live socket
 * even when the stored public URL has not been updated after a proxy move.
 * Never use X-Forwarded-Host, which a client may spoof. Authentication and
 * session membership are still verified after this same-host Origin check. */
export function allowedSameHostBrowserOrigin(origin:string|undefined,host:string|undefined):boolean{
 if(!origin||!host)return false;
 try{
  const supplied=new URL(origin);
  return (supplied.protocol==='https:'||supplied.protocol==='http:')&&
   supplied.username===''&&supplied.password===''&&supplied.pathname==='/'&&
   supplied.search===''&&supplied.hash===''&&supplied.host.toLowerCase()===host.toLowerCase();
 }catch{return false}
}
/** A QR displayed within the authenticated dashboard must point to the exact
 * same origin as that dashboard, not an outdated configured localhost URL.
 * Explicit Sec-Fetch-Site makes this a browser-only same-origin exception.
 * All other requests keep the trusted configured URL. */
export function qrBrowserOrigin(configured:string,referrer:string|undefined,host:string|undefined,fetchSite:string|undefined):string{
 if(fetchSite!=='same-origin'||!referrer)return configured;
 try{
  const ref=new URL(referrer);
  if(allowedSameHostBrowserOrigin(ref.origin,host))return ref.origin;
 }catch{ /* preserve configured canonical address */ }
 return configured;
}
