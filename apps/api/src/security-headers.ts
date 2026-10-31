/** Production CSP policy for the same-origin React app and presenter views.
 * Keep the Vite development server outside this policy: its HMR needs eval/inline
 * development scripts, which must never be whitelisted in production.
 *
 * A deliberately narrow exception for inline CSS is necessary for React's
 * per-widget geometry, user-selected fills and live animation properties.
 * Scripts, workers and cross-origin connections remain restricted.
 */
export function productionCspDirectives(publicBaseUrl:string){
 const base=new URL(publicBaseUrl);
 if(!['http:','https:'].includes(base.protocol)||base.username||base.password||base.hash||base.search)
  throw new Error('invalid_public_base_url');
 const socketOrigin=`${base.protocol==='https:'?'wss':'ws'}://${base.host}`;
 return {
  defaultSrc:["'self'"],
  baseUri:["'none'"],
  objectSrc:["'none'"],
  formAction:["'self'"],
  frameAncestors:["'self'"], // editor and presenter use same-origin iframe previews
  scriptSrc:["'self'"], // never allow inline script or eval
  scriptSrcAttr:["'none'"],
  styleSrc:["'self'","'unsafe-inline'"], // React editor's per-widget inline geometry
  imgSrc:["'self'",'data:','blob:','https:'], // uploaded, QR and opted-in remote artwork
  fontSrc:["'self'",'data:'],
  mediaSrc:["'self'",'blob:','https:'],
  frameSrc:["'self'",'blob:','https:'], // same-origin PDF and selected external slide media
  connectSrc:["'self'",socketOrigin],
  workerSrc:["'self'",'blob:'],
  manifestSrc:["'self'"],
  ...(base.protocol==='https:'?{upgradeInsecureRequests:[]}:{}),
 };
}

/** Browser features not needed for Quorivio's web-based presenter and audience.
 * Do not forbid fullscreen; it is required by presenter and rehearsal modes.
 */
export const quorivioPermissionsPolicy='camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=()';
