/** Strict OIDC authorization code + PKCE primitives; no implicit flow. */
import {randomBytes,createHash,createPublicKey,verify as verifySignature} from 'node:crypto';
export type OidcProvider={id:string;issuer:string;clientId:string;clientSecret:string;redirectUri:string;label?:string};
export type OidcDiscovery={issuer:string;authorization_endpoint:string;token_endpoint:string;jwks_uri:string};
/** Additional identity providers are configured through OIDC_PROVIDERS_JSON.
 * Each JSON item has id, label, issuer, clientId, clientSecret, redirectUri.
 * No identities or credentials are embedded in the source tree. */
export function providersFromEnv(env:NodeJS.ProcessEnv=process.env):OidcProvider[]{
 const ids=['google','custom'];
 const legacy=ids.flatMap(id=>{const prefix='OIDC_'+id.toUpperCase()+'_';const issuer=env[prefix+'ISSUER'],clientId=env[prefix+'CLIENT_ID'],clientSecret=env[prefix+'CLIENT_SECRET'],redirectUri=env[prefix+'REDIRECT_URI'];if(!issuer||!clientId||!clientSecret||!redirectUri)return [];const provider={id,issuer,clientId,clientSecret,redirectUri,label:id==='google'?'Google':'Custom OIDC'};return validProvider(provider)?[provider]:[]});
 let extra:unknown=[];
 if(env.OIDC_PROVIDERS_JSON){try{extra=JSON.parse(env.OIDC_PROVIDERS_JSON)}catch{throw new Error('invalid_oidc_providers_json')}}
 if(!Array.isArray(extra)||extra.length>32)throw new Error('invalid_oidc_providers_json');
 const used=new Set(legacy.map(x=>x.id));
 const list=[...legacy];
 for(const value of extra){
  if(!value||typeof value!=='object')throw new Error('invalid_oidc_provider');
  const v=value as Record<string,unknown>;
  if(['id','issuer','clientId','clientSecret','redirectUri','label'].some(k=>v[k]!==undefined&&typeof v[k]!=='string'))throw new Error('invalid_oidc_provider');
  const id=v.id as string;
  if(!/^[a-z][a-z0-9_-]{1,31}$/.test(id||'')||['github','facebook'].includes(id)||used.has(id))throw new Error('invalid_oidc_provider_id');
  const label=typeof v.label==='string'?v.label.trim():id;
  if(!label||label.length>80||/[<>\r\n]/.test(label))throw new Error('invalid_oidc_provider_label');
  const provider={id,issuer:v.issuer as string,clientId:v.clientId as string,clientSecret:v.clientSecret as string,redirectUri:v.redirectUri as string,label};
  if(!validProvider(provider))throw new Error('invalid_oidc_provider');
  const callback=new URL(provider.redirectUri);
  if(callback.pathname!==`/api/auth/oidc/${id}/callback`||callback.search||callback.hash)throw new Error('invalid_oidc_provider_callback');
  used.add(id);list.push(provider);
 }
 return list;
}
export function validProvider(p:OidcProvider){try{const issuer=new URL(p.issuer),callback=new URL(p.redirectUri);return issuer.protocol==='https:'&&callback.protocol==='https:'&&Boolean(p.clientId&&p.clientSecret)&&!issuer.username&&!issuer.password&&!callback.username&&!callback.password&&!p.issuer.includes('#')}catch{return false}}
export const nonce=()=>randomBytes(32).toString('base64url');
export const pkceChallenge=(verifier:string)=>createHash('sha256').update(verifier).digest('base64url');
export function authorizationUrl(p:OidcProvider,d:OidcDiscovery,state:string,challenge:string,nonceValue:string){const u=new URL(d.authorization_endpoint);if(u.protocol!=='https:')throw new Error('insecure_authorization_endpoint');u.searchParams.set('response_type','code');u.searchParams.set('client_id',p.clientId);u.searchParams.set('redirect_uri',p.redirectUri);u.searchParams.set('scope','openid email profile');u.searchParams.set('state',state);u.searchParams.set('nonce',nonceValue);u.searchParams.set('code_challenge',challenge);u.searchParams.set('code_challenge_method','S256');return u.toString()}
export function validateDiscovery(p:OidcProvider,d:OidcDiscovery){if(d.issuer!==p.issuer.replace(/\/$/,'')||!['authorization_endpoint','token_endpoint','jwks_uri'].every(k=>{try{return new URL(d[k as keyof OidcDiscovery]).protocol==='https:'}catch{return false}}))throw new Error('invalid_oidc_discovery');return d}
export function validateClaims(payload:Record<string,unknown>,p:OidcProvider,expectedNonce:string,now=Math.floor(Date.now()/1000)){if(payload.iss!==p.issuer.replace(/\/$/,'')||!(payload.aud===p.clientId||(Array.isArray(payload.aud)&&payload.aud.includes(p.clientId)))||typeof payload.exp!=='number'||payload.exp<=now||typeof payload.iat!=='number'||!Number.isFinite(payload.iat)||payload.iat>now+60||payload.iat<now-86400||!Number.isFinite(payload.exp)||payload.exp-payload.iat>86400||payload.nonce!==expectedNonce||typeof expectedNonce!=='string'||expectedNonce.length<16||typeof payload.sub!=='string'||!payload.sub||typeof payload.email!=='string'||payload.email_verified!==true)throw new Error('invalid_oidc_claims');if(Array.isArray(payload.aud)&&payload.aud.length>1&&payload.azp!==p.clientId)throw new Error('invalid_authorized_party');const email=payload.email.trim().toLowerCase();if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)||email.length>254)throw new Error('invalid_verified_email');return {subject:payload.sub,email}}
export async function verifyIdToken(token:string,p:OidcProvider,expectedNonce:string,jwks:Record<string,unknown>,now=Math.floor(Date.now()/1000)){const segments=token.split('.');if(segments.length!==3)throw new Error('invalid_id_token');let header:Record<string,unknown>,payload:Record<string,unknown>;try{header=JSON.parse(Buffer.from(segments[0],'base64url').toString('utf8'));payload=JSON.parse(Buffer.from(segments[1],'base64url').toString('utf8'))}catch{throw new Error('invalid_id_token')}if(header.alg!=='RS256'||typeof header.kid!=='string')throw new Error('unsupported_id_token_algorithm');const key=(Array.isArray(jwks.keys)?jwks.keys:[]).find((k:Record<string,unknown>)=>k.kid===header.kid&&k.kty==='RSA'&&(k.use===undefined||k.use==='sig')&&k.alg!== 'HS256');if(!key)throw new Error('oidc_key_not_found');let valid=false;try{const publicKey=createPublicKey({key,format:'jwk'} as Parameters<typeof createPublicKey>[0]);valid=verifySignature('RSA-SHA256',Buffer.from(segments[0]+'.'+segments[1]),publicKey,Buffer.from(segments[2],'base64url'))}catch{throw new Error('invalid_id_token_signature')}if(!valid)throw new Error('invalid_id_token_signature');return validateClaims(payload,p,expectedNonce,now)}
export async function fetchOidcJson(url:string):Promise<any>{const u=new URL(url);if(u.protocol!=='https:')throw new Error('insecure_oidc_url');const response=await fetch(url,{signal:AbortSignal.timeout(8000),headers:{accept:'application/json'}});if(!response.ok)throw new Error('oidc_provider_unavailable');const body=await response.text();if(body.length>262144)throw new Error('oidc_payload_too_large');return JSON.parse(body)}
