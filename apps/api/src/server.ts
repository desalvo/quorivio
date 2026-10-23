import {SESSION_CHANNEL,startSessionBus} from './session-bus.js';
import {socialProviders,socialState,socialAuthorizationUrl,exchangeSocialCode,socialSubject} from './social-oauth.js';
import {providersFromEnv,nonce,pkceChallenge,authorizationUrl,validateDiscovery,verifyIdToken,fetchOidcJson} from './oidc.js';
import {generateRecoveryCodes,recoveryCodeDigest,validRecoveryCode} from './recovery-codes.js';
import {normalizeResetEmail,generateResetToken,resetTokenDigest,validResetToken,validNewPassword,resetLink} from './password-reset.js';
import {generateTotpSecret,makeTotp,verifyTotp,sealTotp,openTotp,totpAuthUrl,validTotpCode} from './totp.js';
import {smtpConfigFromEnv,sendTestEmail,sendPasswordResetEmail} from './smtp.js';
import {sealSmtpConfig,openSmtpConfig,validateSmtpInput,publicSmtpConfig} from './smtp-store.js';
import {widgetAnswerShapeChanged,aggregateWidgetAnswerRevisions} from './widget-revisions.js';
import {normalizeWord,validateQuestion,moderationStatus,safeFrequency} from './audience-tools.js';
import {validPageOrder} from './page-sequence.js';
import express from 'express';import helmet from 'helmet';import pg from 'pg';import bcrypt from 'bcryptjs';import QRCode from 'qrcode';import {WebSocketServer,WebSocket} from 'ws';import {createServer} from 'node:http';import {randomUUID,randomBytes,createHash,createHmac,timingSafeEqual} from 'node:crypto';import {readFileSync,existsSync} from 'node:fs';import {mkdir,writeFile,readFile,unlink,rm} from 'node:fs/promises';import {validAsset} from './asset-policy.js';import {receiveAssetStream} from './stream-upload.js';import {scanUploadedFile} from './malware-scan.js';import {readdir,stat} from 'node:fs/promises';import path from 'node:path';import {fileURLToPath} from 'node:url';import {validTransition,validateOptions,checkAnswer,publicActivity,escapeCsvCell,validRetentionDays,validPageDesign,validPseudonym,validAnswerMode,validateSubmittedAnswer,validReaction,type Activity,type SessionStatus} from './domain.js';
const db=new pg.Pool({connectionString:process.env.DATABASE_URL});const secret=process.env.AUTH_SECRET||'';if(secret.length<32)throw new Error('AUTH_SECRET must have >= 32 characters');
const base=process.env.PUBLIC_BASE_URL||'http://localhost:8080';let publicBase=base;const app=express();app.disable('x-powered-by');app.use(helmet({contentSecurityPolicy:false}));app.use(express.json({limit:'32kb'}));const server=createServer(app);const wss=new WebSocketServer({noServer:true});
const hash=(v:string)=>createHash('sha256').update(v).digest('hex');const sign=(s:string)=>createHmac('sha256',secret).update(s).digest('base64url');const cookies=(s:string='')=>Object.fromEntries(s.split(';').map(x=>x.trim().split('=')).filter(x=>x.length===2));
function auth(req:express.Request){const token=cookies(req.headers.cookie).q_auth;if(!token)return null;const parts=token.split('.');if(parts.length!==3||!/^\d+$/.test(parts[1]))return null;const body=parts.slice(0,2).join('.');const a=Buffer.from(sign(body));const b=Buffer.from(parts[2]);if(a.length!==b.length||!timingSafeEqual(a,b)||Number(parts[1])<Date.now())return null;return parts[0]}
async function requireAuth(req:express.Request,res:express.Response,next:express.NextFunction){const uid=auth(req);if(!uid){res.status(401).json({error:'authentication_required'});return}try{const r=await db.query('SELECT approved,must_change_password,password_changed_at FROM users WHERE id=$1',[uid]);if(r.rowCount&&r.rows[0].password_changed_at){const expires=Number(cookies(req.headers.cookie).q_auth?.split('.')[1]||0);if(expires-8*3600*1000<new Date(r.rows[0].password_changed_at).getTime()){res.status(401).json({error:'session_revoked'});return}}if(!r.rowCount||!r.rows[0].approved){res.status(403).json({error:'account_pending_approval'});return}if(r.rows[0].must_change_password&&!['/api/auth/change-password','/api/auth/me'].includes(req.path)){res.status(403).json({error:'password_change_required'});return}next()}catch{res.status(503).json({error:'auth_unavailable'})}}
const sendError=(res:express.Response,e:unknown)=>{console.error('request error',e instanceof Error?e.message:'unknown');res.status(500).json({error:'internal_error'})};
function originSafe(req:express.Request){if(!['POST','PUT','PATCH','DELETE'].includes(req.method))return true;const origin=req.headers.origin;if(!origin)return true;try{return new URL(origin).host===new URL(base).host}catch{return false}}
app.use('/api',(req,res,next)=>{if(!originSafe(req)){res.status(403).json({error:'invalid_origin'});return;}next()});
// Shared, database-backed fixed-window limiter: consistent across all API replicas.
async function throttle(req:express.Request,res:express.Response,next:express.NextFunction){try{
 const key=hash(req.ip||'unknown'),bucket=Math.floor(Date.now()/60000);
 const r=await db.query(`INSERT INTO api_rate_windows(client_hash,bucket,hits) VALUES($1,$2,1)
 ON CONFLICT(client_hash,bucket) DO UPDATE SET hits=api_rate_windows.hits+1 RETURNING hits`,[key,bucket]);
 if(Number(r.rows[0].hits)>100){res.setHeader('Retry-After',String(60-Math.floor(Date.now()/1000)%60));res.status(429).json({error:'rate_limited'});return}next();
 }catch(e){console.error('rate limiter unavailable',e instanceof Error?e.message:'unknown');res.status(503).json({error:'rate_limiter_unavailable'})}}
app.use('/api',throttle);
async function owner(id:string,uid:string){const r=await db.query('SELECT s.* FROM sessions s WHERE s.id=$1 AND (s.owner_id=$2 OR EXISTS (SELECT 1 FROM session_presenters sp WHERE sp.session_id=s.id AND sp.user_id=$2))',[id,uid]);return r.rows[0] as (Record<string,any>|undefined)}
const validDate=(x:string)=>/^\d{4}-\d{2}-\d{2}$/.test(x)&&!Number.isNaN(Date.parse(x));
const strip=(s:any)=>({access_role:s.access_role||'owner',id:s.id,title:s.title,reference_date:s.reference_date,join_code:s.join_code,status:s.status,expires_at:s.expires_at,current_activity_id:s.current_activity_id,allow_anonymous:s.allow_anonymous,show_results:s.show_results,theme:s.theme,retention_days:s.retention_days,join_url:`${publicBase}/join/${s.join_secret}`});
async function snapshot(sid:string){const s=(await db.query('SELECT * FROM sessions WHERE id=$1',[sid])).rows[0];if(!s)return null;const acts=(await db.query('SELECT * FROM activities WHERE session_id=$1 ORDER BY position',[sid])).rows as Activity[];const counts=(await db.query('SELECT a.id AS activity_id,r.option_id,count(*)::int AS count FROM activities a JOIN responses r ON r.activity_id=a.id AND r.invalidated_at IS NULL WHERE a.session_id=$1 GROUP BY a.id,r.option_id',[sid])).rows;const totals=(await db.query('SELECT activity_id,count(*)::int AS count FROM responses WHERE invalidated_at IS NULL AND activity_id IN (SELECT id FROM activities WHERE session_id=$1) GROUP BY activity_id',[sid])).rows;const reactions=(await db.query('SELECT activity_id,emoji,count(*)::int AS count FROM page_reactions WHERE session_id=$1 GROUP BY activity_id,emoji',[sid])).rows;return {session:strip(s),activities:acts,results:counts,totals,reactions};}
const sockets=new Map<string,Set<WebSocket>>();
async function broadcastLocal(sid:string){if(!sockets.get(sid)?.size)return;const data=await snapshot(sid);for(const ws of sockets.get(sid)||[])if(ws.readyState===WebSocket.OPEN)ws.send(JSON.stringify({type:'snapshot',data:(ws as any).view==='owner'?data:participantSnapshot(data)}))}
async function broadcast(sid:string){await broadcastLocal(sid);await db.query('SELECT pg_notify($1,$2)',[SESSION_CHANNEL,sid]);}


// Audience interactions are session-scoped, use an existing anonymous participant cookie,
// and may only be submitted while the selected activity is open.
async function audienceIdentity(req:express.Request,code:string,activityId:string){
 const s=await publicSession(code);
 if(!s||s.status!=='active'||s.current_activity_id!==activityId||!s.allow_anonymous)return null;
 const token=cookies(req.headers.cookie)[`q_part_${s.id}`];if(!token)return null;
 const p=await db.query('SELECT id FROM participants WHERE session_id=$1 AND token_hash=$2',[s.id,hash(token)]);
 const a=await db.query("SELECT id FROM activities WHERE id=$1 AND session_id=$2 AND status='open'",[activityId,s.id]);
 return p.rowCount&&a.rowCount?{sessionId:s.id,participantId:p.rows[0].id}:null;
}
app.post('/api/join/:code/activities/:aid/words',async(req,res)=>{try{
 const word=normalizeWord(req.body?.word);if(!word){res.status(400).json({error:'invalid_word'});return}
 const who=await audienceIdentity(req,req.params.code,req.params.aid);
 if(!who){res.status(403).json({error:'join_or_open_activity_required'});return}
 await db.query('INSERT INTO audience_words(session_id,activity_id,participant_id,word) VALUES($1,$2,$3,$4) ON CONFLICT (activity_id,participant_id) DO NOTHING',[who.sessionId,req.params.aid,who.participantId,word]);
 await broadcast(who.sessionId);res.status(202).json({ok:true});
 }catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/activities/:aid/words',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const rows=await db.query('SELECT word,count(*)::int AS count FROM audience_words WHERE session_id=$1 AND activity_id=$2 GROUP BY word ORDER BY count DESC,word LIMIT 100',[s.id,req.params.aid]);
 res.json(safeFrequency(rows.rows));
 }catch(e){sendError(res,e)}});
app.post('/api/join/:code/activities/:aid/questions',async(req,res)=>{try{
 const body=validateQuestion(req.body?.body);if(!body){res.status(400).json({error:'invalid_question'});return}
 const who=await audienceIdentity(req,req.params.code,req.params.aid);
 if(!who){res.status(403).json({error:'join_or_open_activity_required'});return}
 const n=await db.query('SELECT count(*)::int AS n FROM audience_questions WHERE activity_id=$1 AND participant_id=$2',[req.params.aid,who.participantId]);
 if(n.rows[0].n>=3){res.status(429).json({error:'question_limit_reached'});return}
 await db.query('INSERT INTO audience_questions(id,session_id,activity_id,participant_id,body) VALUES($1,$2,$3,$4,$5)',[randomUUID(),who.sessionId,req.params.aid,who.participantId,body]);
 res.status(202).json({status:'pending_moderation'});
 }catch(e){sendError(res,e)}});
app.get('/api/join/:code/activities/:aid/questions',async(req,res)=>{try{
 const s=await publicSession(req.params.code);if(!s||s.current_activity_id!==req.params.aid){res.status(404).end();return}
 const r=await db.query("SELECT q.id,q.body,count(v.participant_id)::int AS votes FROM audience_questions q LEFT JOIN audience_question_votes v ON v.question_id=q.id WHERE q.session_id=$1 AND q.activity_id=$2 AND q.status='approved' GROUP BY q.id ORDER BY votes DESC,q.created_at LIMIT 100",[s.id,req.params.aid]);res.json(r.rows);
 }catch(e){sendError(res,e)}});
app.post('/api/join/:code/activities/:aid/questions/:qid/upvote',async(req,res)=>{try{
 const who=await audienceIdentity(req,req.params.code,req.params.aid);if(!who){res.status(403).json({error:'join_or_open_activity_required'});return}
 const q=await db.query("SELECT id FROM audience_questions WHERE id=$1 AND session_id=$2 AND activity_id=$3 AND status='approved'",[req.params.qid,who.sessionId,req.params.aid]);if(!q.rowCount){res.status(404).end();return}
 await db.query('INSERT INTO audience_question_votes(question_id,participant_id) VALUES($1,$2) ON CONFLICT DO NOTHING',[req.params.qid,who.participantId]);res.json({ok:true});
 }catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/activities/:aid/questions',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const r=await db.query('SELECT q.id,q.body,q.status,q.created_at,count(v.participant_id)::int AS votes FROM audience_questions q LEFT JOIN audience_question_votes v ON v.question_id=q.id WHERE q.session_id=$1 AND q.activity_id=$2 GROUP BY q.id ORDER BY q.created_at LIMIT 200',[s.id,req.params.aid]);res.json(r.rows);
 }catch(e){sendError(res,e)}});
app.patch('/api/sessions/:id/activities/:aid/questions/:qid',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 if(!moderationStatus(req.body?.status)||req.body.status==='pending'){res.status(400).json({error:'invalid_moderation_status'});return}
 const r=await db.query('UPDATE audience_questions SET status=$4,moderated_at=now() WHERE id=$1 AND session_id=$2 AND activity_id=$3 RETURNING id',[req.params.qid,s.id,req.params.aid,req.body.status]);if(!r.rowCount){res.status(404).end();return}res.json({ok:true});
 }catch(e){sendError(res,e)}});
app.get('/api/health/live',(_,res)=>res.json({status:'ok'}));app.get('/api/health/ready',async(_,res)=>{try{await db.query('SELECT 1');res.json({status:'ok'})}catch{res.status(503).json({status:'unavailable'})}});
async function activeSmtpConfig(){const r=await db.query('SELECT encrypted_config FROM smtp_configuration WHERE id=1');return r.rowCount?openSmtpConfig(r.rows[0].encrypted_config,secret):smtpConfigFromEnv(process.env)}
app.post('/api/auth/register',async(req,res)=>{try{const email=String(req.body?.email||'').trim().toLowerCase(),password=req.body?.password;if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)||email.length>254||typeof password!=='string'||password.length<12||password.length>256){res.status(400).json({error:'invalid_registration'});return}const org=(await db.query('SELECT id FROM organizations ORDER BY id LIMIT 1')).rows[0];if(!org){res.status(503).json({error:'organization_unavailable'});return}await db.query('INSERT INTO users(id,organization_id,email,password_hash,role,approved) VALUES($1,$2,$3,$4,$5,false)',[randomUUID(),org.id,email,await bcrypt.hash(password,12),'user']);res.status(202).json({status:'pending_admin_approval'})}catch(e){if((e as any)?.code==='23505'){res.status(409).json({error:'account_exists'});return}sendError(res,e)}});
// Password recovery does not reveal account existence. SMTP must be configured to deliver tokens.
app.post('/api/auth/password-reset/request',async(req,res)=>{try{
 const email=normalizeResetEmail(req.body?.email);if(!email){res.status(400).json({error:'invalid_email'});return}
 const config=await activeSmtpConfig();if(!config){res.status(503).json({error:'recovery_not_configured'});return}
 // Database-backed one-per-minute gate, safe with multiple API replicas.
 const key=hash(`password-reset:${req.ip||'unknown'}:${email}`),bucket=Math.floor(Date.now()/60000);
 const limit=await db.query(`INSERT INTO api_rate_windows(client_hash,bucket,hits) VALUES($1,$2,1)
 ON CONFLICT(client_hash,bucket) DO UPDATE SET hits=api_rate_windows.hits+1 RETURNING hits`,[key,bucket]);
 if(Number(limit.rows[0].hits)>1){res.status(202).json({accepted:true});return}
 const user=await db.query('SELECT id FROM users WHERE email=$1 AND approved=true',[email]);
 if(user.rowCount){const token=generateResetToken(),digest=resetTokenDigest(token);
 await db.query("UPDATE password_reset_tokens SET used_at=now() WHERE user_id=$1 AND used_at IS NULL",[user.rows[0].id]);
 await db.query("INSERT INTO password_reset_tokens(user_id,token_hash,expires_at) VALUES($1,$2,now()+interval '20 minutes')",[user.rows[0].id,digest]);
 try{await sendPasswordResetEmail(config,email,resetLink(publicBase,token))}catch(e){console.error('password reset email delivery failed',e instanceof Error?e.message:'unknown')}
 }
 res.status(202).json({accepted:true});
 }catch(e){sendError(res,e)}});
app.post('/api/auth/password-reset/confirm',async(req,res)=>{const token=req.body?.token,password=req.body?.new_password;
 if(!validResetToken(token)||!validNewPassword(password)){res.status(400).json({error:'invalid_reset_request'});return}
 const client=await db.connect();try{await client.query('BEGIN');
 const found=await client.query('SELECT id,user_id FROM password_reset_tokens WHERE token_hash=$1 AND used_at IS NULL AND expires_at>now() FOR UPDATE',[resetTokenDigest(token)]);
 if(!found.rowCount){await client.query('ROLLBACK');res.status(400).json({error:'invalid_or_expired_token'});return}
 await client.query('UPDATE users SET password_hash=$2,password_changed_at=now(),must_change_password=false WHERE id=$1',[found.rows[0].user_id,await bcrypt.hash(password,12)]);
 await client.query('UPDATE password_reset_tokens SET used_at=now() WHERE user_id=$1 AND used_at IS NULL',[found.rows[0].user_id]);
 await client.query('COMMIT');res.clearCookie('q_auth',{path:'/'});res.json({ok:true,mfa_still_required:true});
 }catch(e){await client.query('ROLLBACK');sendError(res,e)}finally{client.release()}});
// OIDC authorization code + PKCE. Accounts are never silently linked by email.
const oidcProviders=providersFromEnv();
// Federated authorization state is persisted in PostgreSQL for cross-replica callbacks.
app.get('/api/auth/oidc/providers',(_,res)=>res.json({providers:[...oidcProviders.map(x=>({id:x.id,label:x.label||x.id})),...socialProviders().map(x=>({id:x.id}))]}));
app.get('/api/auth/oidc/:provider/start',async(req,res)=>{try{
 const p=oidcProviders.find(x=>x.id===req.params.provider);if(!p){res.status(404).json({error:'provider_unavailable'});return}
 const d=validateDiscovery(p,await fetchOidcJson(p.issuer.replace(/\/$/,'')+'/.well-known/openid-configuration'));
 const state=nonce(),verifier=nonce()+nonce(),nonceValue=nonce();

 // Optional account linking requires an existing authenticated session.
 const linkUser=req.query.link==='true'?auth(req):null;
 if(req.query.link==='true'&&!linkUser){res.status(401).json({error:'authentication_required'});return}
 await db.query("INSERT INTO auth_flows(state_hash,kind,provider,nonce,verifier,link_user,expires_at) VALUES($1,'oidc',$2,$3,$4,$5,now()+interval '5 minutes')",[hash(state),p.id,nonceValue,verifier,linkUser]);
 res.cookie('q_oidc_state',state,{httpOnly:true,sameSite:'lax',secure:true,maxAge:300000,path:'/api/auth/oidc'});
 res.redirect(authorizationUrl(p,d,state,pkceChallenge(verifier),nonceValue));
 }catch(e){console.error('oidc start',e instanceof Error?e.message:'error');res.status(502).json({error:'oidc_unavailable'})}});
app.get('/api/auth/oidc/:provider/callback',async(req,res)=>{const state=typeof req.query.state==='string'?req.query.state:'',code=req.query.code;
 const flow=await db.query("DELETE FROM auth_flows WHERE state_hash=$1 AND kind='oidc' AND expires_at>now() RETURNING provider,nonce,verifier,link_user",[hash(state)]).catch(()=>null);if(!flow){res.status(503).json({error:'auth_state_unavailable'});return}const pending=flow.rows[0]?{provider:flow.rows[0].provider,nonce:flow.rows[0].nonce,verifier:flow.rows[0].verifier,linkUser:flow.rows[0].link_user,expires:Date.now()+1}:null;res.clearCookie('q_oidc_state',{path:'/api/auth/oidc'});
 if(!pending||pending.expires<Date.now()||pending.provider!==req.params.provider||cookies(req.headers.cookie).q_oidc_state!==state||typeof code!=='string'||code.length>4096){res.status(400).json({error:'oidc_state_invalid'});return}
 const p=oidcProviders.find(x=>x.id===pending.provider);if(!p){res.status(400).json({error:'oidc_provider_missing'});return}
 try{const d=validateDiscovery(p,await fetchOidcJson(p.issuer.replace(/\/$/,'')+'/.well-known/openid-configuration'));
 const tokenReply=await fetch(d.token_endpoint,{method:'POST',signal:AbortSignal.timeout(8000),headers:{'content-type':'application/x-www-form-urlencoded'},body:new URLSearchParams({grant_type:'authorization_code',code,redirect_uri:p.redirectUri,client_id:p.clientId,client_secret:p.clientSecret,code_verifier:pending.verifier})});
 if(!tokenReply.ok){res.status(401).json({error:'oidc_exchange_failed'});return}
 const tokens=await tokenReply.json();if(typeof tokens.id_token!=='string'||tokens.id_token.length>20000){res.status(401).json({error:'oidc_token_missing'});return}
 const verified=await verifyIdToken(tokens.id_token,p,pending.nonce,await fetchOidcJson(d.jwks_uri));
 let userId:string;
 if(pending.linkUser){const user=await db.query('SELECT id,approved FROM users WHERE id=$1',[pending.linkUser]);if(!user.rowCount||!user.rows[0].approved){res.status(403).json({error:'link_not_allowed'});return}
 const linked=await db.query('INSERT INTO oidc_identities(provider,subject,user_id) VALUES($1,$2,$3) ON CONFLICT (provider,subject) DO NOTHING RETURNING user_id',[p.id,verified.subject,pending.linkUser]);if(!linked.rowCount){res.status(409).json({error:'identity_already_linked'});return}res.redirect('/?oidc_linked=1');return;
 }
 const existing=await db.query('SELECT u.id,u.approved,u.must_change_password,u.totp_enabled FROM oidc_identities i JOIN users u ON u.id=i.user_id WHERE i.provider=$1 AND i.subject=$2',[p.id,verified.subject]);
 if(!existing.rowCount){res.status(403).json({error:'identity_not_linked',message:'Sign in with your password and link your identity in account settings first.'});return}
 const u=existing.rows[0];if(!u.approved||u.must_change_password){res.status(403).json({error:'account_not_approved'});return}
 // Strict policy: users with TOTP cannot bypass MFA through OIDC.
 if(u.totp_enabled){res.status(403).json({error:'oidc_mfa_requires_local_login'});return}
 userId=u.id;const expires=Date.now()+8*3600*1000;const body=`${userId}.${expires}`;
 res.cookie('q_auth',`${body}.${sign(body)}`,{httpOnly:true,sameSite:'strict',secure:true,maxAge:8*3600*1000,path:'/'});res.redirect('/?oidc_login=1');
 }catch(e){console.error('oidc callback',e instanceof Error?e.message:'error');res.status(502).json({error:'oidc_verification_failed'})}});

// GitHub/Facebook OAuth2: account linking is explicit, never based on email.
// These providers do not issue standard OIDC id_tokens; obtain the immutable provider user ID via their HTTPS API.
// Social OAuth uses the same single-consume PostgreSQL state store.
app.get('/api/auth/social/:provider/start',async(req,res)=>{try{
 const p=socialProviders().find(x=>x.id===req.params.provider);if(!p){res.status(404).json({error:'provider_unavailable'});return}
 const linkUser=req.query.link==='true'?auth(req):null;
 if(req.query.link==='true'&&!linkUser){res.status(401).json({error:'authentication_required'});return}

 const state=socialState();await db.query("INSERT INTO auth_flows(state_hash,kind,provider,link_user,expires_at) VALUES($1,'social',$2,$3,now()+interval '5 minutes')",[hash(state),p.id,linkUser]);
 res.cookie('q_social_state',state,{httpOnly:true,sameSite:'lax',secure:true,maxAge:300000,path:'/api/auth/social'});
 res.redirect(socialAuthorizationUrl(p,state));
 }catch(e){sendError(res,e)}});
app.get('/api/auth/social/:provider/callback',async(req,res)=>{
 const state=typeof req.query.state==='string'?req.query.state:'';
 const flow=await db.query("DELETE FROM auth_flows WHERE state_hash=$1 AND kind='social' AND expires_at>now() RETURNING provider,link_user",[hash(state)]).catch(()=>null);if(!flow){res.status(503).json({error:'auth_state_unavailable'});return}const pending=flow.rows[0]?{provider:flow.rows[0].provider,linkUser:flow.rows[0].link_user,expires:Date.now()+1}:null;res.clearCookie('q_social_state',{path:'/api/auth/social'});
 const code=req.query.code;
 if(!pending||pending.expires<Date.now()||pending.provider!==req.params.provider||cookies(req.headers.cookie).q_social_state!==state||typeof code!=='string'||code.length>4096){res.status(400).json({error:'social_state_invalid'});return}
 const p=socialProviders().find(x=>x.id===pending.provider);if(!p){res.status(404).json({error:'provider_unavailable'});return}
 try{const subject=await socialSubject(p,await exchangeSocialCode(p,code));
 if(pending.linkUser){const user=await db.query('SELECT id,approved,must_change_password FROM users WHERE id=$1',[pending.linkUser]);
 if(!user.rowCount||!user.rows[0].approved||user.rows[0].must_change_password){res.status(403).json({error:'link_not_allowed'});return}
 const linked=await db.query('INSERT INTO oidc_identities(provider,subject,user_id) VALUES($1,$2,$3) ON CONFLICT (provider,subject) DO NOTHING RETURNING user_id',[p.id,subject,pending.linkUser]);
 if(!linked.rowCount){res.status(409).json({error:'identity_already_linked'});return}
 res.redirect('/?oidc_linked=1');return}
 const existing=await db.query('SELECT u.id,u.approved,u.must_change_password,u.totp_enabled FROM oidc_identities i JOIN users u ON u.id=i.user_id WHERE i.provider=$1 AND i.subject=$2',[p.id,subject]);
 if(!existing.rowCount){res.status(403).json({error:'identity_not_linked'});return}
 const u=existing.rows[0];if(!u.approved||u.must_change_password){res.status(403).json({error:'account_not_approved'});return}
 if(u.totp_enabled){res.status(403).json({error:'social_mfa_requires_local_login'});return}
 const expires=Date.now()+8*3600*1000;const body=`${u.id}.${expires}`;
 res.cookie('q_auth',`${body}.${sign(body)}`,{httpOnly:true,sameSite:'strict',secure:true,maxAge:8*3600*1000,path:'/'});res.redirect('/?oidc_login=1');
 }catch(e){console.error('social oauth callback',e instanceof Error?e.message:'error');res.status(502).json({error:'social_authentication_failed'})}
});
app.post('/api/auth/login',async(req,res)=>{try{const {email,password}=req.body||{};if(typeof email!=='string'||typeof password!=='string'){res.status(400).json({error:'invalid_request'});return}const r=await db.query('SELECT id,email,password_hash,approved,must_change_password,role,totp_enabled,totp_secret FROM users WHERE lower(email)=$1 OR lower(nickname)=$1',[email.trim().toLowerCase()]);if(!r.rowCount||!await bcrypt.compare(password,r.rows[0].password_hash)){res.status(401).json({error:'invalid_credentials'});return}if(!r.rows[0].approved){res.status(403).json({error:'account_pending_approval'});return}if(r.rows[0].totp_enabled){const otp=String(req.body?.totp_code||'');if(!validTotpCode(otp)||!verifyTotp(openTotp(r.rows[0].totp_secret,secret),otp)){const backup=String(req.body?.recovery_code||'');if(!validRecoveryCode(backup)){res.status(401).json({error:'mfa_code_required_or_invalid'});return}const used=await db.query('DELETE FROM mfa_recovery_codes WHERE user_id=$1 AND code_hash=$2 RETURNING code_hash',[r.rows[0].id,recoveryCodeDigest(backup,secret)]);if(!used.rowCount){res.status(401).json({error:'mfa_code_required_or_invalid'});return}}}const expires=Date.now()+8*3600*1000;const body=`${r.rows[0].id}.${expires}`;res.cookie('q_auth',`${body}.${sign(body)}`,{httpOnly:true,sameSite:'strict',secure:base.startsWith('https:'),maxAge:8*3600*1000,path:'/'});res.json({email:r.rows[0].email,role:r.rows[0].role,must_change_password:r.rows[0].must_change_password})}catch(e){sendError(res,e)}});
app.post('/api/auth/logout',(_,res)=>{res.clearCookie('q_auth',{path:'/'});res.json({ok:true})});
app.get('/api/auth/me',requireAuth,async(req,res)=>{try{const r=await db.query('SELECT id,email,nickname,is_primary_admin,role,approved,must_change_password,totp_enabled FROM users WHERE id=$1',[auth(req)]);res.json(r.rows[0]||null)}catch(e){sendError(res,e)}});
async function requireAdmin(req:express.Request,res:express.Response,next:express.NextFunction){const u=await db.query('SELECT role,approved,must_change_password FROM users WHERE id=$1',[auth(req)]);if(!u.rowCount||!u.rows[0].approved||u.rows[0].must_change_password||u.rows[0].role!=='platform_admin'){res.status(403).json({error:'admin_required'});return}next()}
async function requirePresenter(req:express.Request,res:express.Response,next:express.NextFunction){const u=await db.query('SELECT role,approved,must_change_password FROM users WHERE id=$1',[auth(req)]);if(!u.rowCount||!u.rows[0].approved||u.rows[0].must_change_password||!['presenter','platform_admin','org_admin'].includes(u.rows[0].role)){res.status(403).json({error:'approved_presenter_required'});return}next()}
app.post('/api/auth/change-password',requireAuth,async(req,res)=>{try{const current=req.body?.current_password,next=req.body?.new_password;if(typeof current!=='string'||typeof next!=='string'||next.length<12||next.length>256||current===next){res.status(400).json({error:'invalid_password'});return}const r=await db.query('SELECT password_hash FROM users WHERE id=$1',[auth(req)]);if(!r.rowCount||!await bcrypt.compare(current,r.rows[0].password_hash)){res.status(403).json({error:'invalid_credentials'});return}await db.query('UPDATE users SET password_hash=$2,must_change_password=false,password_changed_at=now() WHERE id=$1',[auth(req),await bcrypt.hash(next,12)]);res.json({ok:true})}catch(e){sendError(res,e)}});

// TOTP is optional and bound to a fully authenticated user. Enrolment remains
// inactive until a valid authenticator code is provided.
app.post('/api/auth/mfa/setup',requireAuth,async(req,res)=>{try{
 if(!await activeSmtpConfig()){res.status(409).json({error:'smtp_required_before_mfa'});return} const uid=auth(req)!;const r=await db.query('SELECT totp_enabled FROM users WHERE id=$1',[uid]);if(!r.rowCount||r.rows[0].totp_enabled){res.status(409).json({error:'mfa_already_enabled'});return}
 const secretValue=generateTotpSecret();await db.query('UPDATE users SET totp_pending_secret=$2 WHERE id=$1',[uid,sealTotp(secretValue,secret)]);
 const email=(await db.query('SELECT email FROM users WHERE id=$1',[uid])).rows[0].email;
 res.json({secret:secretValue,otpauth_url:totpAuthUrl(secretValue,email)});
 }catch(e){sendError(res,e)}});
app.get('/api/auth/mfa/qr',requireAuth,async(req,res)=>{try{
 const account=await db.query('SELECT email,totp_pending_secret,totp_enabled FROM users WHERE id=$1',[auth(req)]);
 if(!account.rowCount||account.rows[0].totp_enabled||!account.rows[0].totp_pending_secret){res.status(404).end();return}
 const code=totpAuthUrl(openTotp(account.rows[0].totp_pending_secret,secret),account.rows[0].email);
 res.setHeader('Cache-Control','no-store, private');res.setHeader('X-Content-Type-Options','nosniff');
 res.type('image/png').send(await QRCode.toBuffer(code,{width:256,margin:2}));
 }catch(e){sendError(res,e)}});
app.post('/api/auth/mfa/confirm',requireAuth,async(req,res)=>{try{
 const uid=auth(req)!;const code=String(req.body?.code||'');if(!validTotpCode(code)){res.status(400).json({error:'invalid_code'});return}
 const r=await db.query('SELECT totp_pending_secret,totp_enabled FROM users WHERE id=$1',[uid]);if(!r.rowCount||r.rows[0].totp_enabled||!r.rows[0].totp_pending_secret){res.status(409).json({error:'mfa_setup_required'});return}
 if(!verifyTotp(openTotp(r.rows[0].totp_pending_secret,secret),code)){res.status(403).json({error:'invalid_code'});return}
 const codes=generateRecoveryCodes();const client=await db.connect();try{await client.query('BEGIN');await client.query('UPDATE users SET totp_secret=totp_pending_secret,totp_pending_secret=NULL,totp_enabled=true WHERE id=$1',[uid]);await client.query('DELETE FROM mfa_recovery_codes WHERE user_id=$1',[uid]);for(const c of codes)await client.query('INSERT INTO mfa_recovery_codes(user_id,code_hash) VALUES($1,$2)',[uid,recoveryCodeDigest(c,secret)]);await client.query('COMMIT')}catch(e){await client.query('ROLLBACK');throw e}finally{client.release()}res.json({enabled:true,recovery_codes:codes});
 }catch(e){sendError(res,e)}});
app.post('/api/auth/mfa/disable',requireAuth,async(req,res)=>{try{
 const uid=auth(req)!;const code=String(req.body?.code||'');const password=String(req.body?.password||'');const r=await db.query('SELECT password_hash,totp_secret,totp_enabled FROM users WHERE id=$1',[uid]);
 if(!r.rowCount||!r.rows[0].totp_enabled||!await bcrypt.compare(password,r.rows[0].password_hash)||!validTotpCode(code)||!verifyTotp(openTotp(r.rows[0].totp_secret,secret),code)){res.status(403).json({error:'invalid_credentials'});return}
 await db.query('UPDATE users SET totp_secret=NULL,totp_pending_secret=NULL,totp_enabled=false WHERE id=$1',[uid]);await db.query('DELETE FROM mfa_recovery_codes WHERE user_id=$1',[uid]);res.json({enabled:false});
 }catch(e){sendError(res,e)}});
app.post('/api/auth/mfa/recovery-codes/rotate',requireAuth,async(req,res)=>{try{const uid=auth(req)!;const {password,code}=req.body||{};const r=await db.query('SELECT password_hash,totp_secret,totp_enabled FROM users WHERE id=$1',[uid]);if(!r.rowCount||!r.rows[0].totp_enabled||typeof password!=='string'||!await bcrypt.compare(password,r.rows[0].password_hash)||!validTotpCode(code)||!verifyTotp(openTotp(r.rows[0].totp_secret,secret),code)){res.status(403).json({error:'invalid_credentials'});return}const codes=generateRecoveryCodes(),client=await db.connect();try{await client.query('BEGIN');await client.query('DELETE FROM mfa_recovery_codes WHERE user_id=$1',[uid]);for(const c of codes)await client.query('INSERT INTO mfa_recovery_codes(user_id,code_hash) VALUES($1,$2)',[uid,recoveryCodeDigest(c,secret)]);await client.query('COMMIT')}catch(e){await client.query('ROLLBACK');throw e}finally{client.release()}res.json({recovery_codes:codes});}catch(e){sendError(res,e)}});
app.get('/api/admin/smtp',requireAuth,requireAdmin,async(_req,res)=>{try{res.json(publicSmtpConfig(await activeSmtpConfig()))}catch(e){sendError(res,e)}});
app.put('/api/admin/smtp',requireAuth,requireAdmin,async(req,res)=>{try{
 const previous=await activeSmtpConfig();const body={...req.body,password:req.body?.password||previous?.password};
 const config=validateSmtpInput(body);
 const encrypted=sealSmtpConfig(config,secret);
 await db.query('INSERT INTO smtp_configuration(id,encrypted_config) VALUES(1,$1) ON CONFLICT(id) DO UPDATE SET encrypted_config=excluded.encrypted_config,updated_at=now()',[encrypted]);
 res.json(publicSmtpConfig(config));
 }catch(e){if(String(e).includes('invalid_')||String(e).includes('SMTP')){res.status(400).json({error:'invalid_smtps_configuration'});return}sendError(res,e)}});

app.post('/api/admin/smtp/test',requireAuth,requireAdmin,async(req,res)=>{try{
 const config=await activeSmtpConfig();if(!config){res.status(503).json({error:'smtp_not_configured'});return}
 const recipient=String(req.body?.recipient||'');if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(recipient)||recipient.length>254){res.status(400).json({error:'invalid_recipient'});return}
 await sendTestEmail(config,recipient);res.json({sent:true});
 }catch(e){console.error('smtp test failed',e instanceof Error?e.message:'unknown');res.status(502).json({error:'smtp_delivery_failed'})}});
app.patch('/api/auth/profile',requireAuth,async(req,res)=>{try{
 const nickname=req.body?.nickname===null?null:String(req.body?.nickname||'').trim().toLowerCase();
 if(nickname!==null&&!/^[a-z][a-z0-9_.-]{2,31}$/.test(nickname)){res.status(400).json({error:'invalid_nickname'});return}
 const current=await db.query('SELECT is_primary_admin FROM users WHERE id=$1',[auth(req)]);
 if(current.rows[0]?.is_primary_admin&&nickname!=='admin'){res.status(409).json({error:'primary_admin_nickname_immutable'});return}
 const result=await db.query('UPDATE users SET nickname=$2 WHERE id=$1 RETURNING id,email,nickname',[auth(req),nickname]);res.json(result.rows[0]);
 }catch(e){if((e as any)?.code==='23505'){res.status(409).json({error:'nickname_already_taken'});return}sendError(res,e)}});
// Security-sensitive helpdesk MFA reset. Never disclose TOTP seeds or recovery codes.
app.post('/api/admin/users/:id/mfa/reset',requireAuth,requireAdmin,async(req,res)=>{try{
 const actor=auth(req)!;
 if(actor===req.params.id){res.status(409).json({error:'use_self_service_mfa_disable'});return}
 const password=req.body?.admin_password;
 const otp=req.body?.admin_totp_code;
 if(typeof password!=='string'||password.length>256||req.body?.confirm!==true){res.status(400).json({error:'confirmation_required'});return}
 const admin=await db.query('SELECT password_hash,totp_enabled,totp_secret FROM users WHERE id=$1',[actor]);
 if(!admin.rowCount||!await bcrypt.compare(password,admin.rows[0].password_hash)){res.status(403).json({error:'invalid_admin_credentials'});return}
 if(admin.rows[0].totp_enabled&&(!validTotpCode(otp)||!verifyTotp(openTotp(admin.rows[0].totp_secret,secret),otp))){res.status(403).json({error:'invalid_admin_mfa'});return}
 const client=await db.connect();let changed=false;
 try{await client.query('BEGIN');
  const user=await client.query('SELECT id,is_primary_admin,totp_enabled FROM users WHERE id=$1 FOR UPDATE',[req.params.id]);
  if(!user.rowCount){await client.query('ROLLBACK');res.status(404).json({error:'user_not_found'});return}
  if(user.rows[0].is_primary_admin){await client.query('ROLLBACK');res.status(409).json({error:'primary_admin_mfa_protected'});return}
  await client.query('UPDATE users SET totp_secret=NULL,totp_pending_secret=NULL,totp_enabled=false WHERE id=$1',[req.params.id]);
  await client.query('DELETE FROM mfa_recovery_codes WHERE user_id=$1',[req.params.id]);
  await client.query('COMMIT');changed=true;
 }catch(e){await client.query('ROLLBACK');throw e}finally{client.release()}
 if(changed){for(const peers of sockets.values())for(const ws of peers)if((ws as any).uid===req.params.id)ws.close(1008,'MFA reset');
  console.info('admin_mfa_reset',JSON.stringify({actor,target:req.params.id,at:new Date().toISOString()}));}
 res.json({enabled:false,reset:true});
 }catch(e){sendError(res,e)}});
app.patch('/api/admin/users/:id/identity',requireAuth,requireAdmin,async(req,res)=>{try{
 const email=String(req.body?.email||'').trim().toLowerCase();
 if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)||email.length>254){res.status(400).json({error:'invalid_email'});return}
 const result=await db.query('UPDATE users SET email=$2 WHERE id=$1 RETURNING id,email,nickname,is_primary_admin',[req.params.id,email]);
 if(!result.rowCount){res.status(404).end();return}res.json(result.rows[0]);
 }catch(e){if((e as any)?.code==='23505'){res.status(409).json({error:'email_already_taken'});return}sendError(res,e)}});
app.post('/api/admin/users',requireAuth,requireAdmin,async(req,res)=>{try{const email=String(req.body?.email||'').trim().toLowerCase(),role=req.body?.role,password=req.body?.temporary_password,nickname=req.body?.nickname?String(req.body.nickname).trim().toLowerCase():null;if(nickname&&(!/^[a-z][a-z0-9_.-]{2,31}$/.test(nickname)||nickname==='admin')){res.status(400).json({error:'invalid_nickname'});return}if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)||!['user','presenter','moderator','org_admin','platform_admin'].includes(role)||typeof password!=='string'||password.length<12||password.length>256){res.status(400).json({error:'invalid_user'});return}const org=(await db.query('SELECT organization_id FROM users WHERE id=$1',[auth(req)])).rows[0];const r=await db.query('INSERT INTO users(id,organization_id,email,password_hash,role,approved,must_change_password,nickname) VALUES($1,$2,$3,$4,$5,true,true,$6) RETURNING id,email,nickname,role,approved',[randomUUID(),org.organization_id,email,await bcrypt.hash(password,12),role,nickname]);res.status(201).json(r.rows[0])}catch(e){if((e as any)?.code==='23505'){res.status(409).json({error:'account_exists'});return}sendError(res,e)}});
app.patch('/api/admin/users/:id/nickname',requireAuth,requireAdmin,async(req,res)=>{try{const nickname=req.body?.nickname==null||req.body.nickname===''?null:String(req.body.nickname).trim().toLowerCase();if(nickname&&(!/^[a-z][a-z0-9_.-]{2,31}$/.test(nickname)||nickname==='admin')){res.status(400).json({error:'invalid_nickname'});return}const r=await db.query('UPDATE users SET nickname=$2 WHERE id=$1 AND is_primary_admin=false RETURNING id,nickname',[req.params.id,nickname]);if(!r.rowCount){res.status(409).json({error:'primary_admin_immutable_or_missing'});return}res.json(r.rows[0])}catch(e){if((e as any)?.code==='23505'){res.status(409).json({error:'nickname_already_taken'});return}sendError(res,e)}});
app.get('/api/admin/users',requireAuth,requireAdmin,async(req,res)=>{try{
 const page=Number(req.query.page||1),pageSize=Number(req.query.page_size||(req.query.page===undefined?100:10)),search=String(req.query.search||'').trim().slice(0,160),status=String(req.query.approval||'all');
 if(!Number.isSafeInteger(page)||page<1||!Number.isSafeInteger(pageSize)||pageSize<1||pageSize>100||!['all','approved','pending'].includes(status)){res.status(400).json({error:'invalid_pagination'});return}
 const terms=[`($1='' OR email ILIKE '%'||$1||'%' OR coalesce(nickname,'') ILIKE '%'||$1||'%')`,`($2='all' OR approved=($2='approved'))`].join(' AND ');
 const total=await db.query(`SELECT count(*)::int AS total FROM users WHERE ${terms}`,[search,status]);
 const rows=await db.query(`SELECT id,email,nickname,is_primary_admin,role,approved,totp_enabled,created_at FROM users WHERE ${terms} ORDER BY created_at DESC,id DESC LIMIT $3 OFFSET $4`,[search,status,pageSize,(page-1)*pageSize]);
 res.json(req.query.page===undefined?rows.rows:{items:rows.rows,total:total.rows[0].total,page,page_size:pageSize});
 }catch(e){sendError(res,e)}});
app.patch('/api/admin/users/:id',requireAuth,requireAdmin,async(req,res)=>{try{const role=req.body?.role,approved=req.body?.approved;const primary=await db.query('SELECT is_primary_admin FROM users WHERE id=$1',[req.params.id]);if(primary.rows[0]?.is_primary_admin&&(!approved||role!=='platform_admin')){res.status(409).json({error:'primary_admin_immutable'});return}if(!['platform_admin','org_admin','presenter','moderator','user'].includes(role)||typeof approved!=='boolean'){res.status(400).json({error:'invalid_update'});return}if(req.params.id===auth(req)&&(!approved||role!=='platform_admin')){res.status(409).json({error:'cannot_demote_self'});return}const r=await db.query('UPDATE users SET role=$2,approved=$3 WHERE id=$1 RETURNING id,email,role,approved',[req.params.id,role,approved]);if(r.rowCount)for(const peers of sockets.values())for(const ws of peers)if((ws as any).uid===req.params.id)ws.close(1008,'account permissions changed');if(!r.rowCount){res.status(404).end();return}res.json(r.rows[0])}catch(e){sendError(res,e)}});
app.delete('/api/admin/users/:id',requireAuth,requireAdmin,async(req,res)=>{try{if(req.params.id===auth(req)){res.status(409).json({error:'cannot_delete_self'});return}if((await db.query('SELECT is_primary_admin FROM users WHERE id=$1',[req.params.id])).rows[0]?.is_primary_admin){res.status(409).json({error:'primary_admin_immutable'});return}const r=await db.query('DELETE FROM users WHERE id=$1 RETURNING id',[req.params.id]);if(!r.rowCount){res.status(409).json({error:'user_has_dependent_data_or_not_found'});return}res.status(204).end()}catch(e){if((e as any)?.code==='23503'){res.status(409).json({error:'user_has_dependent_data'});return}sendError(res,e)}});
app.get('/api/admin/settings',requireAuth,requireAdmin,async(_req,res)=>{try{const r=await db.query('SELECT key,value FROM platform_settings');res.json(Object.fromEntries(r.rows.map(x=>[x.key,x.value])))}catch(e){sendError(res,e)}});
app.patch('/api/admin/settings',requireAuth,requireAdmin,async(req,res)=>{try{const {public_base_url,closed_session_retention_days,max_upload_mb}=req.body||{};if(public_base_url!==undefined){if(typeof public_base_url!=='string'||!/^https:\/\/[^\s/?#]+(?::[0-9]{2,5})?$/.test(public_base_url)){res.status(400).json({error:'invalid_public_url'});return}await db.query("INSERT INTO platform_settings(key,value) VALUES('public_base_url',$1) ON CONFLICT(key) DO UPDATE SET value=$1,updated_at=now()",[public_base_url]);publicBase=public_base_url}if(closed_session_retention_days!==undefined){if(!validRetentionDays(closed_session_retention_days)){res.status(400).json({error:'invalid_retention'});return}await db.query("INSERT INTO platform_settings(key,value) VALUES('closed_session_retention_days',$1) ON CONFLICT(key) DO UPDATE SET value=$1,updated_at=now()",[String(closed_session_retention_days)])}if(max_upload_mb!==undefined){if(!Number.isInteger(max_upload_mb)||max_upload_mb<1||max_upload_mb>1024){res.status(400).json({error:'invalid_upload_limit'});return}await db.query("INSERT INTO platform_settings(key,value) VALUES('max_upload_mb',$1) ON CONFLICT(key) DO UPDATE SET value=$1,updated_at=now()",[String(max_upload_mb)])}res.json({ok:true,ingress_regeneration_required:max_upload_mb!==undefined})}catch(e){sendError(res,e)}});
app.use('/api/sessions',requireAuth,requirePresenter);
// Profile images are private uploads, never arbitrary externally hosted URLs.
const profilePhotoFolder=()=>path.join(assetRoot,'profile-photos');
const profilePhotoPath=(id:string)=>path.join(profilePhotoFolder(),id);
app.post('/api/auth/profile/photo',requireAuth,async(req,res)=>{try{
 const uid=auth(req)!;const type=String(req.headers['content-type']||'').split(';')[0].trim().toLowerCase();
 const size=Number(req.headers['content-length']);const limit=5*1024*1024;
 if(!['image/png','image/jpeg','image/webp'].includes(type)){res.status(415).json({error:'unsupported_profile_image'});return}
 if(!Number.isSafeInteger(size)||size<1||size>limit){res.status(413).json({error:'profile_image_too_large'});return}
 const id=randomUUID();const received=await receiveAssetStream(req,profilePhotoFolder(),id,type,limit,size);
 try{await scanUploadedFile(received.destination)}catch(e){await unlink(received.destination).catch(()=>{});throw e}
 const url=`/api/auth/profile/photo/${id}`;
 const prior=await db.query('UPDATE users SET profile_photo_url=$2 WHERE id=$1 RETURNING profile_photo_url',[uid,url]);
 if(!prior.rowCount){await unlink(received.destination).catch(()=>{});res.status(404).end();return}
 res.status(201).json({profile_photo_url:url});
 }catch(e){sendError(res,e)}});
app.get('/api/auth/profile/photo/:imageId',requireAuth,async(req,res)=>{try{
 const id=String(req.params.imageId);if(!/^[0-9a-f]{8}-[0-9a-f-]{27,}$/i.test(id)){res.status(404).end();return}
 const r=await db.query('SELECT profile_photo_url FROM users WHERE id=$1',[auth(req)]);
 if(r.rows[0]?.profile_photo_url!==`/api/auth/profile/photo/${id}`){res.status(404).end();return}
 const data=await readFile(profilePhotoPath(id));let type='image/png';if(data[0]===255&&data[1]===216)type='image/jpeg';else if(data.toString('ascii',8,12)==='WEBP')type='image/webp';
 res.setHeader('Content-Type',type);res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Cache-Control','private, no-store');res.send(data);
 }catch(e){if((e as NodeJS.ErrnoException).code==='ENOENT'){res.status(404).end();return}sendError(res,e)}});
app.delete('/api/auth/profile/photo',requireAuth,async(req,res)=>{try{
 await db.query('UPDATE users SET profile_photo_url=NULL WHERE id=$1',[auth(req)]);res.json({profile_photo_url:null});
 }catch(e){sendError(res,e)}});
app.get('/api/presenters/me/profile',requireAuth,requirePresenter,async(req,res)=>{try{const u=await db.query('SELECT id,email,display_name,profile_photo_url FROM users WHERE id=$1',[auth(req)]);res.json(u.rows[0])}catch(e){sendError(res,e)}});
app.patch('/api/presenters/me/profile',requireAuth,requirePresenter,async(req,res)=>{try{const name=String(req.body?.display_name||'').trim();const saved=await db.query('SELECT profile_photo_url FROM users WHERE id=$1',[auth(req)]);const photo=saved.rows[0]?.profile_photo_url||null;if(name.length<2||name.length>100){res.status(400).json({error:'invalid_profile'});return}const u=await db.query('UPDATE users SET display_name=$2,profile_photo_url=$3 WHERE id=$1 RETURNING id,email,display_name,profile_photo_url',[auth(req),name,photo]);res.json(u.rows[0])}catch(e){sendError(res,e)}});
app.get('/api/join/:code/presenters/:presenterId/photo',async(req,res)=>{try{
 const session=await publicSession(req.params.code);if(!session||session.status==='closed'){res.status(404).end();return}
 const profile=await db.query(`SELECT profile_photo_url FROM users WHERE id=$1 AND (id=$2 OR EXISTS(SELECT 1 FROM session_presenters WHERE session_id=$3 AND user_id=$1))`,[req.params.presenterId,session.owner_id,session.id]);
 const url=String(profile.rows[0]?.profile_photo_url||'');const match=/^\/api\/auth\/profile\/photo\/([0-9a-f-]{36})$/.exec(url);
 if(!match){res.status(404).end();return}
 const data=await readFile(profilePhotoPath(match[1]));let mime='image/png';if(data[0]===255&&data[1]===216)mime='image/jpeg';else if(data.toString('ascii',8,12)==='WEBP')mime='image/webp';
 res.setHeader('Content-Type',mime);res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Cache-Control','no-store');res.send(data);
 }catch(e){if((e as NodeJS.ErrnoException).code==='ENOENT'){res.status(404).end();return}sendError(res,e)}});
app.get('/api/join/:code/presenter-profiles',async(req,res)=>{try{const session=await publicSession(req.params.code);if(!session||session.status==='closed'){res.status(404).end();return}const profiles=await db.query("SELECT u.id,coalesce(nullif(u.display_name,''),'Presentatore') AS name,u.profile_photo_url FROM users u WHERE u.id=$1 OR u.id IN (SELECT user_id FROM session_presenters WHERE session_id=$2)",[session.owner_id,session.id]);res.json(profiles.rows)}catch(e){sendError(res,e)}});
// A session may have no scheduled dates, or any explicitly selected set of dates.
app.get('/api/sessions/:id/schedule',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const dates=await db.query('SELECT scheduled_date::text AS date FROM session_schedule_dates WHERE session_id=$1 ORDER BY scheduled_date',[s.id]);res.json(dates.rows.map(r=>r.date));
 }catch(e){sendError(res,e)}});
app.put('/api/sessions/:id/schedule',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 if(s.owner_id!==auth(req)){res.status(403).json({error:'owner_required'});return}
 const dates=req.body?.dates;if(!Array.isArray(dates)||dates.length>100||!dates.every(d=>typeof d==='string'&&validDate(d))||new Set(dates).size!==dates.length){res.status(400).json({error:'invalid_schedule'});return}
 const cx=await db.connect();try{await cx.query('BEGIN');await cx.query('DELETE FROM session_schedule_dates WHERE session_id=$1',[s.id]);for(const d of dates)await cx.query('INSERT INTO session_schedule_dates(session_id,scheduled_date) VALUES($1,$2)',[s.id,d]);await cx.query('COMMIT')}catch(e){await cx.query('ROLLBACK');throw e}finally{cx.release()}
 res.json({dates:dates.slice().sort()});
 }catch(e){sendError(res,e)}});
// All appointments are interpreted in the specified IANA timezone; date/time are never silently converted to UTC.
const appointmentValid=(a:any)=>a&&typeof a.date==='string'&&validDate(a.date)&&typeof a.start_time==='string'&&/^([01]\d|2[0-3]):[0-5]\d$/.test(a.start_time)&&Number.isInteger(a.duration_minutes)&&a.duration_minutes>=5&&a.duration_minutes<=1440&&typeof a.time_zone==='string'&&a.time_zone.length<=64&&(()=>{try{new Intl.DateTimeFormat('en',{timeZone:a.time_zone});return true}catch{return false}})();
app.get('/api/calendar',requireAuth,requirePresenter,async(req,res)=>{try{
 const from=String(req.query.from||'').slice(0,10),to=String(req.query.to||'').slice(0,10);
 if(!validDate(from)||!validDate(to)||from>to){res.status(400).json({error:'invalid_date_range'});return}
 const r=await db.query(`SELECT a.id,a.session_id,s.title,a.scheduled_date::text AS date,to_char(a.start_time,'HH24:MI') AS start_time,a.duration_minutes,a.time_zone,CASE WHEN s.owner_id=$1 THEN 'owner' ELSE 'collaborator' END AS access_role FROM session_appointments a JOIN sessions s ON s.id=a.session_id WHERE (s.owner_id=$1 OR EXISTS (SELECT 1 FROM session_presenters p WHERE p.session_id=s.id AND p.user_id=$1)) AND a.scheduled_date BETWEEN $2::date AND $3::date ORDER BY a.scheduled_date,a.start_time LIMIT 2000`,[auth(req),from,to]);res.json(r.rows);
 }catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/appointments',requireAuth,async(req,res)=>{try{const session=await owner(req.params.id,auth(req)!);if(!session){res.status(404).end();return}const r=await db.query("SELECT id,scheduled_date::text AS date,to_char(start_time,'HH24:MI') AS start_time,duration_minutes,time_zone FROM session_appointments WHERE session_id=$1 ORDER BY scheduled_date,start_time",[session.id]);res.json(r.rows)}catch(e){sendError(res,e)}});
app.put('/api/sessions/:id/appointments',requireAuth,async(req,res)=>{const cx=await db.connect();try{
 const session=await owner(req.params.id,auth(req)!);if(!session){res.status(404).end();return}if(session.owner_id!==auth(req)){res.status(403).json({error:'owner_required'});return}
 const appointments=req.body?.appointments;if(!Array.isArray(appointments)||appointments.length>100||!appointments.every(appointmentValid)){res.status(400).json({error:'invalid_appointments'});return}
 await cx.query('BEGIN');await cx.query('DELETE FROM session_appointments WHERE session_id=$1',[session.id]);
 for(const a of appointments)await cx.query('INSERT INTO session_appointments(id,session_id,scheduled_date,start_time,duration_minutes,time_zone) VALUES($1,$2,$3,$4,$5,$6)',[randomUUID(),session.id,a.date,a.start_time,a.duration_minutes,a.time_zone]);
 await cx.query('COMMIT');res.json({ok:true});
 }catch(e){await cx.query('ROLLBACK');sendError(res,e)}finally{cx.release()}});
app.get('/api/sessions/:id/presenter-profiles',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}const users=await db.query("SELECT u.id,coalesce(nullif(u.display_name,''),'Presentatore') AS name,u.profile_photo_url FROM users u WHERE u.id=$1 OR u.id IN (SELECT user_id FROM session_presenters WHERE session_id=$2)",[s.owner_id,s.id]);res.json(users.rows)}catch(e){sendError(res,e)}});
app.get('/api/sessions',requireAuth,requirePresenter,async(req,res)=>{try{
 const page=Number(req.query.page||1),pageSize=Number(req.query.page_size||(req.query.page===undefined?100:10)),search=String(req.query.search||'').trim().slice(0,160),role=String(req.query.role||'all');
 if(!Number.isSafeInteger(page)||page<1||!Number.isSafeInteger(pageSize)||pageSize<1||pageSize>100||!['all','owner','collaborator'].includes(role)){res.status(400).json({error:'invalid_pagination'});return}
 const where=`(s.owner_id=$1 OR EXISTS (SELECT 1 FROM session_presenters sp WHERE sp.session_id=s.id AND sp.user_id=$1)) AND ($2='' OR s.title ILIKE '%'||$2||'%' OR s.join_code ILIKE '%'||$2||'%' OR s.status ILIKE '%'||$2||'%' OR EXISTS (SELECT 1 FROM session_schedule_dates sd WHERE sd.session_id=s.id AND sd.scheduled_date::text ILIKE '%'||$2||'%')) AND ($3='all' OR ($3='owner' AND s.owner_id=$1) OR ($3='collaborator' AND s.owner_id<>$1))`;
 const params=[auth(req),search,role];const total=await db.query(`SELECT count(*)::int AS total FROM sessions s WHERE ${where}`,params);
 const result=await db.query(`SELECT s.*,CASE WHEN s.owner_id=$1 THEN 'owner' ELSE 'collaborator' END AS access_role FROM sessions s WHERE ${where} ORDER BY s.created_at DESC,s.id DESC LIMIT $4 OFFSET $5`,[...params,pageSize,(page-1)*pageSize]);
 res.json(req.query.page===undefined?result.rows.map(strip):{items:result.rows.map(strip),total:total.rows[0].total,page,page_size:pageSize});
 }catch(e){sendError(res,e)}});
app.post('/api/sessions',requireAuth,requirePresenter,async(req,res)=>{try{const title=String(req.body?.title||'').trim();const referenceDate=String(req.body?.reference_date||new Date().toISOString().slice(0,10));if(!title||title.length>160||!validDate(referenceDate)){res.status(400).json({error:'invalid_title'});return}const uid=auth(req)!;const u=(await db.query('SELECT organization_id FROM users WHERE id=$1',[uid])).rows[0];if(!u){res.status(401).end();return}const id=randomUUID(),code=randomBytes(5).toString('hex').toUpperCase(),joinSecret=randomBytes(20).toString('base64url');const r=await db.query("INSERT INTO sessions(id,organization_id,owner_id,title,join_code,join_secret,expires_at,reference_date) VALUES($1,$2,$3,$4,$5,$6,now()+interval '1 day',$7) RETURNING *",[id,u.organization_id,uid,title,code,joinSecret,referenceDate]);res.status(201).json(strip(r.rows[0]))}catch(e){sendError(res,e)}});

// Portable definition exports intentionally omit participant data and join credentials.
async function portableSession(id:string){const session=(await db.query('SELECT title,reference_date,theme,allow_anonymous,show_results FROM sessions WHERE id=$1',[id])).rows[0];const activities=(await db.query('SELECT type,title,options,correct_option_id,correct_option_ids,answer_mode,answer_required,duration_seconds,page_design,result_design FROM activities WHERE session_id=$1 ORDER BY position',[id])).rows;return {format:'quorivio-session',version:1,session,activities}}
function validPortable(x:any){return x?.format==='quorivio-session'&&x.version===1&&typeof x.session?.title==='string'&&x.session.title.trim().length>0&&x.session.title.length<=160&&validDate(String(x.session.reference_date))&&validPageDesign(x.session.theme)&&typeof x.session.allow_anonymous==='boolean'&&typeof x.session.show_results==='boolean'&&Array.isArray(x.activities)&&x.activities.length<=200&&x.activities.every((a:any)=>['poll','quiz','timed_quiz'].includes(a.type)&&typeof a.title==='string'&&a.title.trim().length>0&&a.title.length<=240&&validateOptions(a.options)&&validAnswerMode(a.answer_mode||'single')&&typeof (a.answer_required??true)==='boolean'&& (a.correct_option_ids===undefined||Array.isArray(a.correct_option_ids)&&a.correct_option_ids.every((v:any)=>typeof v==='string'&&a.options.some((o:any)=>o.id===v)))&&validPageDesign(a.page_design)&&validPageDesign(a.result_design)&&(!['quiz','timed_quiz'].includes(a.type)||!['single','multiple'].includes(a.answer_mode||'single')||(a.answer_mode==='multiple'?Array.isArray(a.correct_option_ids)&&a.correct_option_ids.length>0:a.options.some((o:any)=>o.id===a.correct_option_id)))&&(a.type!=='timed_quiz'||['single','multiple'].includes(a.answer_mode||'single')&&Number.isInteger(a.duration_seconds)&&a.duration_seconds>=5&&a.duration_seconds<=600)&&(a.duration_seconds==null||Number.isInteger(a.duration_seconds)&&a.duration_seconds>=5&&a.duration_seconds<=600));}
async function createFromPortable(data:any,uid:string){const cx=await db.connect();try{await cx.query('BEGIN');const u=(await cx.query('SELECT organization_id FROM users WHERE id=$1',[uid])).rows[0];if(!u)throw Error('missing_user');const sid=randomUUID();await cx.query("INSERT INTO sessions(id,organization_id,owner_id,title,reference_date,join_code,join_secret,expires_at,theme,allow_anonymous,show_results) VALUES($1,$2,$3,$4,$5,$6,$7,now()+interval '1 day',$8,$9,$10)",[sid,u.organization_id,uid,data.session.title,data.session.reference_date,randomBytes(5).toString('hex').toUpperCase(),randomBytes(20).toString('base64url'),JSON.stringify(data.session.theme),data.session.allow_anonymous,data.session.show_results]);for(let i=0;i<data.activities.length;i++){const a=data.activities[i];await cx.query('INSERT INTO activities(id,session_id,type,title,options,correct_option_id,duration_seconds,page_design,result_design,position,answer_mode,answer_required,correct_option_ids) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)',[randomUUID(),sid,a.type,a.title,JSON.stringify(a.options),['quiz','timed_quiz'].includes(a.type)?a.correct_option_id:null,a.duration_seconds,JSON.stringify(a.page_design),JSON.stringify(a.result_design),i,a.answer_mode||'single',a.answer_required??true,JSON.stringify(a.correct_option_ids||[])])}await cx.query('COMMIT');return sid}catch(e){await cx.query('ROLLBACK');throw e}finally{cx.release()}}
// Asset endpoints accept raw bytes with a strictly bounded Content-Length and file signatures.
// Storage is intentionally private and local; configure a shared persistent volume before production.
const assetRoot=path.resolve(process.env.QUORIVIO_ASSET_DIR||'/app/assets');
async function cleanupSessionFiles(sessionId:string){if(!/^[0-9a-f]{8}-[0-9a-f-]{27,}$/i.test(sessionId))throw Error('invalid session id');await rm(path.join(assetRoot,sessionId),{recursive:true,force:true})}
async function allowedUploadBytes(){const r=await db.query("SELECT value FROM platform_settings WHERE key='max_upload_mb'");return Math.max(1,Math.min(1024,Number(r.rows[0]?.value||100)))*1024*1024}
// Participant file submissions are scoped to the currently open page and to an actual file widget.
// The server never trusts a client-supplied session id, participant id, or asset owner.
app.post('/api/join/:code/activities/:aid/widgets/:wid/upload',async(req,res)=>{try{
 const who=await audienceIdentity(req,req.params.code,req.params.aid);
 if(!who){res.status(403).json({error:'join_or_open_activity_required'});return}
 const activity=await db.query('SELECT page_design FROM activities WHERE id=$1 AND session_id=$2',[req.params.aid,who.sessionId]);
 const widget=(activity.rows[0]?.page_design?.widgets||[]).find((w:any)=>w.id===req.params.wid&&w.kind==='question'&&w.answerMode==='file');
 if(!widget){res.status(404).json({error:'file_widget_not_found'});return}
 const cap=await allowedUploadBytes();const length=Number(req.headers['content-length']);
 if(!Number.isSafeInteger(length)||length<1||length>cap){res.status(413).json({error:'invalid_upload_size'});return}
 const declared=String(req.headers['content-type']||'').split(';')[0].trim().toLowerCase();
 if(!['image/png','image/jpeg','image/gif','image/webp','application/pdf','video/mp4','video/webm'].includes(declared)){res.status(415).json({error:'unsupported_media'});return}
 // Quota checked before accepting a potentially large body.
 const count=await db.query('SELECT count(*)::int AS n FROM session_assets WHERE session_id=$1 AND participant_id=$2',[who.sessionId,who.participantId]);
 if(Number(count.rows[0].n)>=10){res.status(429).json({error:'participant_upload_quota_exceeded'});return}
 const id=randomUUID();const folder=path.join(assetRoot,who.sessionId);
 const received=await receiveAssetStream(req,folder,id,declared,cap,length);
 try{await scanUploadedFile(received.destination);await db.query('INSERT INTO session_assets(id,session_id,uploaded_by,participant_id,mime_type,byte_size,sha256) VALUES($1,$2,NULL,$3,$4,$5,$6)',[id,who.sessionId,who.participantId,declared,received.size,received.sha256])}catch(e){await unlink(received.destination);throw e}
 res.status(201).json({asset_id:id,mime_type:declared,bytes:received.size});
 }catch(e){sendError(res,e)} });
app.post('/api/sessions/:id/assets',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 if(s.status==='closed'){res.status(409).json({error:'session_closed'});return}
 const cap=await allowedUploadBytes();const length=Number(req.headers['content-length']);
 if(!Number.isSafeInteger(length)||length<1||length>cap){res.status(413).json({error:'invalid_upload_size'});return}
 const declared=String(req.headers['content-type']||'').split(';')[0].trim().toLowerCase();
 if(!['image/png','image/jpeg','image/gif','image/webp','application/pdf','video/mp4','video/webm'].includes(declared)){res.status(415).json({error:'unsupported_media'});return}
 const id=randomUUID();const folder=path.join(assetRoot,s.id);
 const received=await receiveAssetStream(req,folder,id,declared,cap,length);
 try{await scanUploadedFile(received.destination);await db.query('INSERT INTO session_assets(id,session_id,uploaded_by,mime_type,byte_size,sha256) VALUES($1,$2,$3,$4,$5,$6)',[id,s.id,auth(req),declared,received.size,received.sha256])}catch(e){await unlink(received.destination);throw e}
 res.status(201).json({id,mime_type:declared,bytes:received.size,url:`/api/sessions/${s.id}/assets/${id}`});
 }catch(e){sendError(res,e)}});
// Asset inventory and removal are always scoped to an authorized session presenter.
app.get('/api/sessions/:id/assets',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const r=await db.query('SELECT id,mime_type,byte_size,sha256,created_at FROM session_assets WHERE session_id=$1 ORDER BY created_at DESC LIMIT 500',[s.id]);
 res.json(r.rows.map(x=>({...x,url:`/api/sessions/${s.id}/assets/${x.id}`})));
 }catch(e){sendError(res,e)}});
app.delete('/api/sessions/:id/assets/:assetId',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 if(s.status==='closed'){res.status(409).json({error:'session_closed'});return}
 const widgetLink=await db.query("SELECT 1 FROM activities WHERE session_id=$1 AND page_design->'widgets' @> $2::jsonb LIMIT 1",[s.id,JSON.stringify([{assetId:req.params.assetId}])]);
 if(widgetLink.rowCount){res.status(409).json({error:'asset_in_use_by_widget'});return}
 const linked=await db.query('SELECT 1 FROM presentation_slide_assets WHERE asset_id=$1 LIMIT 1',[req.params.assetId]);
 if(linked.rowCount){res.status(409).json({error:'asset_in_use_by_slide'});return}
 const r=await db.query('DELETE FROM session_assets WHERE id=$1 AND session_id=$2 RETURNING id',[req.params.assetId,s.id]);
 if(!r.rowCount){res.status(404).end();return}
 await unlink(path.join(assetRoot,s.id,req.params.assetId)).catch(e=>{if((e as NodeJS.ErrnoException).code!=='ENOENT')console.error('asset cleanup pending',s.id,req.params.assetId)});
 res.status(204).end();
 }catch(e){sendError(res,e)}});
// A deliberately one-way reporting export: never import historical votes from JSON definitions.
app.get('/api/sessions/:id/report.json',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const [activities,totals,assets,invalidations]=await Promise.all([
 db.query('SELECT id,title,type,status,revision FROM activities WHERE session_id=$1 ORDER BY position',[s.id]),
 db.query('SELECT a.id AS activity_id,count(r.id)::int AS total,count(r.id) FILTER (WHERE r.invalidated_at IS NULL)::int AS valid,count(r.id) FILTER (WHERE r.invalidated_at IS NOT NULL)::int AS invalidated FROM activities a LEFT JOIN responses r ON a.id=r.activity_id WHERE a.session_id=$1 GROUP BY a.id',[s.id]),
 db.query('SELECT id,mime_type,byte_size,sha256 FROM session_assets WHERE session_id=$1 ORDER BY created_at',[s.id]),
 db.query('SELECT r.activity_id,r.invalidated_at,r.invalidated_by FROM responses r JOIN activities a ON a.id=r.activity_id WHERE a.session_id=$1 AND r.invalidated_at IS NOT NULL ORDER BY r.invalidated_at LIMIT 10000',[s.id])]);
 res.setHeader('Cache-Control','private, no-store');res.setHeader('Content-Disposition',`attachment; filename="quorivio-report-${s.join_code}.json"`);
 res.json({format:'quorivio-session-report',version:1,generated_at:new Date().toISOString(),session:{id:s.id,title:s.title,reference_date:s.reference_date,status:s.status},activities:activities.rows,totals:totals.rows,assets:assets.rows,invalidations:invalidations.rows,privacy_note:'Aggregate report with invalidation audit; no participant identifiers or raw participant responses. Not an instance backup.'});
 }catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/assets/:assetId',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const r=await db.query('SELECT mime_type FROM session_assets WHERE id=$1 AND session_id=$2',[req.params.assetId,s.id]);if(!r.rowCount){res.status(404).end();return}
 const data=await readFile(path.join(assetRoot,s.id,req.params.assetId));res.setHeader('Content-Type',r.rows[0].mime_type);res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Content-Security-Policy',"default-src 'none'; sandbox");res.setHeader('Cache-Control','private, no-store');res.send(data);
 }catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/export.json',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}res.setHeader('Content-Disposition','attachment; filename="quorivio-session.json"');res.json(await portableSession(s.id))}catch(e){sendError(res,e)}});
app.post('/api/sessions/import',requireAuth,requirePresenter,async(req,res)=>{try{if(!validPortable(req.body)){res.status(400).json({error:'invalid_import'});return}const id=await createFromPortable(req.body,auth(req)!);res.status(201).json({id})}catch(e){sendError(res,e)}});
app.post('/api/sessions/:id/duplicate',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}const portable=await portableSession(s.id);portable.session.title=(portable.session.title+' — Copia').slice(0,160);const id=await createFromPortable(portable,auth(req)!);res.status(201).json({id})}catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/presenters',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}const r=await db.query('SELECT u.id,u.email FROM users u JOIN session_presenters sp ON u.id=sp.user_id WHERE sp.session_id=$1',[s.id]);res.json(r.rows)}catch(e){sendError(res,e)}});
app.post('/api/sessions/:id/presenters',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}if(s.owner_id!==auth(req)){res.status(403).json({error:'owner_required'});return}const email=String(req.body?.email||'').toLowerCase();const r=await db.query("SELECT id FROM users WHERE organization_id=$1 AND email=$2 AND approved=true AND must_change_password=false AND role IN ('presenter','org_admin','platform_admin')",[s.organization_id,email]);if(!r.rowCount){res.status(404).json({error:'eligible_presenter_not_found'});return}await db.query('INSERT INTO session_presenters(session_id,user_id) VALUES($1,$2) ON CONFLICT DO NOTHING',[s.id,r.rows[0].id]);res.status(201).json({ok:true})}catch(e){sendError(res,e)}});
app.delete('/api/sessions/:id/presenters/:uid',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}if(s.owner_id!==auth(req)){res.status(403).end();return}await db.query('DELETE FROM session_presenters WHERE session_id=$1 AND user_id=$2',[s.id,req.params.uid]);res.status(204).end()}catch(e){sendError(res,e)}});
app.patch('/api/sessions/:id/activities/:aid',requireAuth,async(req,res)=>{const cx=await db.connect();try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}if(s.status==='closed'){res.status(409).json({error:'session_closed'});return}const {title,options,correct_option_id}=req.body||{};if(typeof title!=='string'||!title.trim()||title.length>240||!validateOptions(options)){res.status(400).json({error:'invalid_activity'});return}await cx.query('BEGIN');const a=await cx.query('SELECT * FROM activities WHERE id=$1 AND session_id=$2 FOR UPDATE',[req.params.aid,s.id]);if(!a.rowCount){await cx.query('ROLLBACK');res.status(404).end();return}if(['quiz','timed_quiz'].includes(a.rows[0].type)&&!options.some((o:any)=>o.id===correct_option_id)){await cx.query('ROLLBACK');res.status(400).json({error:'invalid_correct_option'});return}const newIds=new Set(options.map((o:any)=>o.id));const historical=(await cx.query('SELECT DISTINCT option_id FROM responses WHERE activity_id=$1',[req.params.aid])).rows.map(x=>x.option_id);if(['quiz','timed_quiz'].includes(a.rows[0].type) && correct_option_id!==a.rows[0].correct_option_id && (await cx.query('SELECT 1 FROM responses WHERE activity_id=$1 AND invalidated_at IS NULL LIMIT 1',[req.params.aid])).rowCount){await cx.query('ROLLBACK');res.status(409).json({error:'invalidate_answers_before_changing_correct_option'});return}if(historical.some(x=>!newIds.has(x))){await cx.query('ROLLBACK');res.status(409).json({error:'existing_response_option_must_remain'});return}await cx.query('UPDATE activities SET title=$3,options=$4,correct_option_id=$5,revision=revision+1 WHERE id=$1 AND session_id=$2',[req.params.aid,s.id,title,JSON.stringify(options),['quiz','timed_quiz'].includes(a.rows[0].type)?correct_option_id:null]);await cx.query('COMMIT');await broadcast(s.id);res.json({ok:true})}catch(e){await cx.query('ROLLBACK');sendError(res,e)}finally{cx.release()}});
app.post('/api/sessions/:id/activities/:aid/invalidate',requireAuth,async(req,res)=>{const cx=await db.connect();try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}await cx.query('BEGIN');const a=await cx.query('SELECT id FROM activities WHERE id=$1 AND session_id=$2 FOR UPDATE',[req.params.aid,s.id]);if(!a.rowCount){await cx.query('ROLLBACK');res.status(404).end();return}const r=await cx.query('UPDATE responses SET invalidated_at=now(),invalidated_by=$2 WHERE activity_id=$1 AND invalidated_at IS NULL RETURNING id',[req.params.aid,auth(req)]);await cx.query('COMMIT');await broadcast(s.id);res.json({invalidated:r.rowCount})}catch(e){await cx.query('ROLLBACK');sendError(res,e)}finally{cx.release()}});
app.get('/api/sessions/:id',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}res.json(await snapshot(s.id))}catch(e){sendError(res,e)}});

// Editable session metadata; live edits preserve the session identifier and all responses.
app.patch('/api/sessions/:id/metadata',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}if(s.status==='closed'){res.status(409).json({error:'session_closed'});return}const title=req.body?.title,referenceDate=req.body?.reference_date;if(typeof title!=='string'||!title.trim()||title.length>160||typeof referenceDate!=='string'||!validDate(referenceDate)){res.status(400).json({error:'invalid_metadata'});return}await db.query('UPDATE sessions SET title=$2,reference_date=$3 WHERE id=$1',[s.id,title.trim(),referenceDate]);await broadcast(s.id);res.json({ok:true})}catch(e){sendError(res,e)}});
app.patch('/api/sessions/:id/design',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}if(!validPageDesign(req.body?.theme)){res.status(400).json({error:'invalid_page_design'});return}await db.query('UPDATE sessions SET theme=$2 WHERE id=$1',[s.id,JSON.stringify(req.body.theme)]);await broadcast(s.id);res.json({ok:true})}catch(e){sendError(res,e)}});
app.patch('/api/sessions/:id/results-visibility',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}if(typeof req.body?.show_results!=='boolean'){res.status(400).json({error:'invalid_value'});return}await db.query('UPDATE sessions SET show_results=$2 WHERE id=$1',[s.id,req.body.show_results]);await broadcast(s.id);res.json({ok:true})}catch(e){sendError(res,e)}});
app.patch('/api/sessions/:id/anonymous',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}if(typeof req.body?.allow_anonymous!=='boolean'){res.status(400).json({error:'invalid_value'});return}await db.query('UPDATE sessions SET allow_anonymous=$2 WHERE id=$1',[s.id,req.body.allow_anonymous]);res.json({ok:true})}catch(e){sendError(res,e)}});
app.patch('/api/sessions/:id/activities/:aid/design',requireAuth,async(req,res)=>{const cx=await db.connect();try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 if(s.status==='closed'){res.status(409).json({error:'session_closed'});return}
 if(!validPageDesign(req.body?.page_design)||!validPageDesign(req.body?.result_design)){res.status(400).json({error:'invalid_page_design'});return}
 await cx.query('BEGIN');
 const a=await cx.query('SELECT page_design,result_design FROM activities WHERE id=$1 AND session_id=$2 FOR UPDATE',[req.params.aid,s.id]);
 if(!a.rowCount){await cx.query('ROLLBACK');res.status(404).end();return}
 const previous=a.rows[0].page_design?.widgets||[];
 const next=req.body.page_design.widgets||[];
 // A changed question is a new revision, not a reinterpretation of historical answers.
 for(const widget of next.filter((w:any)=>w.kind==='question')){
  const old=previous.find((w:any)=>w.id===widget.id&&w.kind==='question');
  if(!old)continue;
  if(widgetAnswerShapeChanged(old,widget)){
   await cx.query('INSERT INTO widget_revisions(activity_id,widget_id,revision,definition,changed_by) VALUES($1,$2,1,$3,$4) ON CONFLICT DO NOTHING',[req.params.aid,widget.id,JSON.stringify(old),auth(req)]);
   const current=await cx.query('SELECT coalesce(max(revision),1)::int AS rev FROM widget_revisions WHERE activity_id=$1 AND widget_id=$2',[req.params.aid,widget.id]);
   const revision=Number(current.rows[0].rev)+1;
   await cx.query('INSERT INTO widget_revisions(activity_id,widget_id,revision,definition,changed_by) VALUES($1,$2,$3,$4,$5)',[req.params.aid,widget.id,revision,JSON.stringify(widget),auth(req)]);
  }
 }
 // Removed questions remain in audit/history; never delete their submissions implicitly.
 await cx.query('UPDATE activities SET page_design=$3,result_design=$4 WHERE id=$1 AND session_id=$2',[req.params.aid,s.id,JSON.stringify(req.body.page_design),JSON.stringify(req.body.result_design)]);
 await cx.query('COMMIT');await broadcast(s.id);res.json({ok:true});
 }catch(e){await cx.query('ROLLBACK');sendError(res,e)}finally{cx.release()}});
app.post('/api/sessions/:id/activities/:aid/duplicate',requireAuth,async(req,res)=>{
 const cx=await db.connect();let begun=false;
 try{
  await cx.query('BEGIN');begun=true;
  const s=await cx.query('SELECT id,status FROM sessions WHERE id=$1 AND (owner_id=$2 OR EXISTS (SELECT 1 FROM session_presenters WHERE session_id=$1 AND user_id=$2)) FOR UPDATE',[req.params.id,auth(req)]);
  if(!s.rowCount){await cx.query('ROLLBACK');begun=false;res.status(404).end();return}
  if(s.rows[0].status==='closed'){await cx.query('ROLLBACK');begun=false;res.status(409).json({error:'session_closed'});return}
  const a=await cx.query('SELECT * FROM activities WHERE id=$1 AND session_id=$2',[req.params.aid,req.params.id]);
  if(!a.rowCount){await cx.query('ROLLBACK');begun=false;res.status(404).end();return}
  const src=a.rows[0],id=randomUUID();
  const n=await cx.query('SELECT coalesce(max(position),-1)+1 AS position FROM activities WHERE session_id=$1',[req.params.id]);
  await cx.query('INSERT INTO activities(id,session_id,type,title,options,correct_option_id,correct_option_ids,answer_mode,answer_required,duration_seconds,page_design,result_design,position) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)',[id,req.params.id,src.type,src.title+' (copy)',src.options,src.correct_option_id,src.correct_option_ids,src.answer_mode,src.answer_required,src.duration_seconds,src.page_design,src.result_design,n.rows[0].position]);
  await cx.query('COMMIT');begun=false;await broadcast(req.params.id);res.status(201).json({id});
 }catch(e){if(begun)await cx.query('ROLLBACK').catch(()=>{});sendError(res,e)}finally{cx.release()}
});
app.put('/api/sessions/:id/pages/order',requireAuth,async(req,res)=>{
 const ids=req.body?.activity_ids;
 if(!Array.isArray(ids)||ids.length>500||!ids.every((v:unknown)=>typeof v==='string'&&/^[0-9a-f-]{36}$/i.test(v))||new Set(ids).size!==ids.length){res.status(400).json({error:'invalid_page_sequence'});return}
 const cx=await db.connect();let begun=false;
 try{
  await cx.query('BEGIN');begun=true;
  const s=await cx.query('SELECT s.id,s.status FROM sessions s WHERE s.id=$1 AND (s.owner_id=$2 OR EXISTS (SELECT 1 FROM session_presenters p WHERE p.session_id=s.id AND p.user_id=$2)) FOR UPDATE',[req.params.id,auth(req)]);
  if(!s.rowCount){await cx.query('ROLLBACK');begun=false;res.status(404).end();return}
  if(s.rows[0].status==='closed'){await cx.query('ROLLBACK');begun=false;res.status(409).json({error:'session_closed'});return}
  const existing=await cx.query('SELECT id FROM activities WHERE session_id=$1 ORDER BY position FOR UPDATE',[req.params.id]);
  const current=existing.rows.map(r=>r.id as string);
  if(!validPageOrder(ids,current)){await cx.query('ROLLBACK');begun=false;res.status(409).json({error:'stale_page_sequence'});return}
  // Displace positions first to avoid the UNIQUE(session_id,position) constraint.
  await cx.query('UPDATE activities SET position= -position-1 WHERE session_id=$1',[req.params.id]);
  for(let i=0;i<ids.length;i++)await cx.query('UPDATE activities SET position=$3 WHERE id=$1 AND session_id=$2',[ids[i],req.params.id,i]);
  await cx.query('COMMIT');begun=false;await broadcast(req.params.id);res.json({activity_ids:ids});
 }catch(e){if(begun)await cx.query('ROLLBACK').catch(()=>{});sendError(res,e)}finally{cx.release()}
});
// Images already checked and stored privately may be promoted to presentation slides.
// This preserves the original session independent presentation mode and avoids untrusted URLs.
app.post('/api/sessions/:id/slides',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);
 if(!s){res.status(404).end();return}
 if(s.status==='closed'){res.status(409).json({error:'session_closed'});return}
 const assetId=String(req.body?.asset_id||'');const title=String(req.body?.title||'').trim();
 if(!/^[0-9a-f-]{36}$/i.test(assetId)||!title||title.length>240){res.status(400).json({error:'invalid_slide'});return}
 const asset=await db.query("SELECT id FROM session_assets WHERE session_id=$1 AND id=$2 AND mime_type IN ('image/png','image/jpeg','image/webp') AND participant_id IS NULL",[s.id,assetId]);
 if(!asset.rowCount){res.status(404).json({error:'slide_image_not_found'});return}
 const cx=await db.connect();try{await cx.query('BEGIN');await cx.query('SELECT id FROM sessions WHERE id=$1 FOR UPDATE',[s.id]);
 const position=await cx.query('SELECT coalesce(max(position)+1,0)::int AS p FROM activities WHERE session_id=$1',[s.id]);
 const id=randomUUID();await cx.query("INSERT INTO activities(id,session_id,type,title,options,position,page_design,result_design,answer_mode,answer_required) VALUES($1,$2,'slide',$3,'[]'::jsonb,$4,$5,'{}'::jsonb,'text',false)",[id,s.id,title,position.rows[0].p,JSON.stringify({media:[{kind:'image',url:`/api/join/${s.join_secret}/slides/${id}/image`,alt:title}]})]);
 await cx.query('INSERT INTO presentation_slide_assets(activity_id,asset_id) VALUES($1,$2)',[id,assetId]);await cx.query('COMMIT');await broadcast(s.id);res.status(201).json({id,title,position:position.rows[0].p});
 }catch(e){await cx.query('ROLLBACK');throw e}finally{cx.release()}
 }catch(e){sendError(res,e)}});
// Opt-in PDF/PPTX import. Execute in a dedicated, resource-constrained conversion
// container; never enable in production without an isolated worker policy.
app.post('/api/sessions/:id/presentation-import',requireAuth,async(req,res)=>{
 const s=await owner(req.params.id,auth(req)!);
 if(!s){res.status(404).end();return}
 if(s.status==='closed'){res.status(409).json({error:'session_closed'});return}
 if(process.env.QUORIVIO_ENABLE_CONVERTER!=='true'){
  res.status(503).json({error:'conversion_worker_not_configured'});return;
 }
 const mime=String(req.headers['content-type']||'').split(';')[0].trim().toLowerCase();
 if(!['application/pdf','application/vnd.openxmlformats-officedocument.presentationml.presentation'].includes(mime)){
  res.status(415).json({error:'unsupported_presentation'});return;
 }
 const cap=Math.min(await allowedUploadBytes(),100*1024*1024),length=Number(req.headers['content-length']);
 if(!Number.isSafeInteger(length)||length<8||length>cap){res.status(413).json({error:'invalid_presentation_size'});return}
 const workerUrl=process.env.QUORIVIO_CONVERTER_WORKER_URL;
 const workerToken=process.env.QUORIVIO_WORKER_TOKEN||'';
 if(!workerUrl||!/^http:\/\/[a-zA-Z0-9.-]+:\d{2,5}$/.test(workerUrl)||workerToken.length<32){res.status(503).json({error:'conversion_worker_not_configured'});return}
 const conversionRoot=process.env.QUORIVIO_CONVERSION_DIR||'/conversions';
 const scratch=path.join(conversionRoot,randomBytes(16).toString('hex'));await mkdir(scratch,{recursive:false,mode:0o700});
 const source=path.join(scratch,mime==='application/pdf'?'source.pdf':'source.pptx');
 const output=path.join(scratch,'pages');
 const created:string[]=[];const cx=await db.connect();let transaction=false;
 try{
  const received=await receiveAssetStream(req,scratch,path.basename(source),mime,cap,length);
  await scanUploadedFile(received.destination);
  // Execute only in the private converter container, never in the API process.
  const controller=new AbortController();const deadline=setTimeout(()=>controller.abort(),240000);
  try{
   const reply=await fetch(`${workerUrl}/convert`,{method:'POST',headers:{'Authorization':`Bearer ${workerToken}`,'Content-Type':'application/json'},body:JSON.stringify({job:path.basename(scratch)}),signal:controller.signal});
   if(!reply.ok)throw Error('conversion_worker_failed');
  }finally{clearTimeout(deadline)}
  const manifest=JSON.parse(await readFile(path.join(output,'manifest.json'),'utf8'));
  if(manifest.format!=='quorivio-presentation-pages'||manifest.version!==1||!Number.isInteger(manifest.page_count)||manifest.page_count<1||manifest.page_count>200||!Array.isArray(manifest.pages)||manifest.pages.length!==manifest.page_count)throw Error('invalid_conversion_manifest');
  const expectedSourceType=mime==='application/pdf'?'pdf':'pptx';
  const sourceHash=createHash('sha256').update(await readFile(source)).digest('hex');
  if(manifest.source_type!==expectedSourceType||manifest.source_sha256!==sourceHash)throw Error('invalid_conversion_source');
  const folder=path.join(assetRoot,s.id);await mkdir(folder,{recursive:true});
  await cx.query('BEGIN');transaction=true;
  const next=await cx.query('SELECT COALESCE(MAX(position),-1)+1 AS p FROM activities WHERE session_id=$1',[s.id]);
  const ids:string[]=[];
  for(let i=0;i<manifest.pages.length;i++){
   const entry=manifest.pages[i],filename=String(entry.image);
   if(filename!==`page-${String(i+1).padStart(4,'0')}.png`||entry.position!==i+1)throw Error('invalid_page_filename');
   const contents=await readFile(path.join(output,filename));
   if(contents.length<8||!contents.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10]))||contents.length!==entry.bytes||createHash('sha256').update(contents).digest('hex')!==entry.sha256)throw Error('invalid_page_checksum');
   const aid=randomUUID(),assetId=randomUUID(),dest=path.join(folder,assetId);
   await writeFile(dest,contents,{flag:'wx',mode:0o600});created.push(dest);
   await cx.query('INSERT INTO session_assets(id,session_id,uploaded_by,mime_type,byte_size,sha256) VALUES($1,$2,$3,$4,$5,$6)',[assetId,s.id,auth(req),'image/png',contents.length,entry.sha256]);
   const title=`Slide ${i+1}`;
   await cx.query("INSERT INTO activities(id,session_id,type,title,options,position,page_design,result_design,answer_mode,answer_required) VALUES($1,$2,'slide',$3,'[]'::jsonb,$4,$5,'{}'::jsonb,'text',false)",[aid,s.id,title,Number(next.rows[0].p)+i,JSON.stringify({media:[{kind:'image',url:`/api/join/${s.join_secret}/slides/${aid}/image`,alt:title}]})]);
   await cx.query('INSERT INTO presentation_slide_assets(activity_id,asset_id) VALUES($1,$2)',[aid,assetId]);ids.push(aid);
  }
  await cx.query('COMMIT');transaction=false;await broadcast(s.id);
  res.status(201).json({created:ids.length,activity_ids:ids});
 }catch(e){if(transaction)await cx.query('ROLLBACK').catch(()=>{});for(const f of created)await unlink(f).catch(()=>{});sendError(res,e)}
 finally{cx.release();await rm(scratch,{recursive:true,force:true}).catch(()=>{})}
});
// Uploaded media is never public by asset ID alone: it must appear on the active slide.
app.get('/api/join/:code/activities/:aid/media/:assetId',async(req,res)=>{try{
 const s=await publicSession(req.params.code);
 if(!s||s.status!=='active'||s.current_activity_id!==req.params.aid){res.status(404).end();return}
 const a=await db.query('SELECT page_design FROM activities WHERE id=$1 AND session_id=$2 AND status=$3',[req.params.aid,s.id,'open']);
 if(!a.rowCount||!Array.isArray(a.rows[0].page_design?.widgets)||!a.rows[0].page_design.widgets.some((w:any)=>['image','video'].includes(w.kind)&&w.assetId===req.params.assetId)){res.status(404).end();return}
 const r=await db.query('SELECT mime_type FROM session_assets WHERE id=$1 AND session_id=$2',[req.params.assetId,s.id]);
 if(!r.rowCount||!['image/png','image/jpeg','image/gif','image/webp','video/mp4','video/webm'].includes(r.rows[0].mime_type)){res.status(404).end();return}
 res.setHeader('Cache-Control','private, no-store');res.setHeader('X-Content-Type-Options','nosniff');res.type(r.rows[0].mime_type);
 res.sendFile(path.join(assetRoot,s.id,req.params.assetId));
 }catch(e){sendError(res,e)}});
// Public slide images are accessible only while THAT slide is the current page of an active session.
app.get('/api/join/:code/slides/:aid/image',async(req,res)=>{try{
 const s=await publicSession(req.params.code);
 if(!s||s.current_activity_id!==req.params.aid){res.status(404).end();return}
 const r=await db.query('SELECT sa.id,sa.mime_type FROM presentation_slide_assets psa JOIN session_assets sa ON sa.id=psa.asset_id WHERE psa.activity_id=$1 AND sa.session_id=$2',[req.params.aid,s.id]);
 if(!r.rowCount){res.status(404).end();return}
 const {id,mime_type}=r.rows[0];res.setHeader('Cache-Control','no-store');res.setHeader('X-Content-Type-Options','nosniff');res.type(mime_type);
 res.sendFile(path.join(assetRoot,s.id,id));
 }catch(e){sendError(res,e)}});
app.post('/api/sessions/:id/activities',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}if(s.status==='closed'){res.status(409).json({error:'session_closed'});return}const {title,type,options,correct_option_id,duration_seconds}=req.body||{};const answerMode=req.body?.answer_mode||'single';const required=req.body?.answer_required!==false;const validOpts=answerMode==='text'||answerMode==='file'?(Array.isArray(options)&&options.length===0):validateOptions(options);const correctIds=req.body?.correct_option_ids;const validCorrect=answerMode!=='multiple'||(Array.isArray(correctIds)&&correctIds.length>0&&correctIds.length<=options.length&&new Set(correctIds).size===correctIds.length&&correctIds.every((id:unknown)=>typeof id==='string'&&options.some((o:any)=>o.id===id)));if(type==='timed_quiz'&&(!['single','multiple'].includes(answerMode)||!Number.isInteger(duration_seconds)||duration_seconds<5||duration_seconds>600)||!['poll','quiz','timed_quiz'].includes(type)||typeof title!=='string'||!title.trim()||title.length>240||!validAnswerMode(answerMode)||typeof required!=='boolean'||!validOpts||!validCorrect||(['quiz','timed_quiz'].includes(type)&&answerMode==='single'&&!options.some((o:any)=>o.id===correct_option_id))){res.status(400).json({error:'invalid_activity'});return}const r=await db.query("INSERT INTO activities(id,session_id,type,title,options,correct_option_id,duration_seconds,position,answer_mode,answer_required,correct_option_ids) VALUES($1,$2,$3,$4,$5,$6,$7,(SELECT count(*) FROM activities WHERE session_id=$2),$8,$9,$10) RETURNING *",[randomUUID(),s.id,type,title,JSON.stringify(options),['quiz','timed_quiz'].includes(type)?correct_option_id:null,type==='timed_quiz'&&Number.isInteger(duration_seconds)&&duration_seconds>=5&&duration_seconds<=600?duration_seconds:null,answerMode,required,JSON.stringify(answerMode==='multiple'&&Array.isArray(req.body?.correct_option_ids)?req.body.correct_option_ids:[]) ]);await broadcast(s.id);res.status(201).json(r.rows[0])}catch(e){sendError(res,e)}});
app.post('/api/sessions/:id/status',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}const target=req.body?.status as SessionStatus;if(!validTransition(s.status,target)){res.status(409).json({error:'invalid_transition'});return}await db.query('UPDATE sessions SET status=$1 WHERE id=$2',[target,s.id]);if(target==='closed')await db.query('UPDATE sessions SET closed_at=now() WHERE id=$1',[s.id]);if(target==='closed')await db.query("UPDATE activities SET status='closed' WHERE session_id=$1 AND status='open'",[s.id]);await broadcast(s.id);res.json({ok:true})}catch(e){sendError(res,e)}});
app.post('/api/sessions/:id/activities/:aid/open',requireAuth,async(req,res)=>{const cx=await db.connect();try{await cx.query('BEGIN');const s=await cx.query('SELECT * FROM sessions WHERE id=$1 AND (owner_id=$2 OR EXISTS (SELECT 1 FROM session_presenters WHERE session_id=$1 AND user_id=$2)) FOR UPDATE',[req.params.id,auth(req)]);if(!s.rowCount||s.rows[0].status!=='active'){await cx.query('ROLLBACK');res.status(409).json({error:'session_not_active'});return}const a=await cx.query('SELECT id FROM activities WHERE id=$1 AND session_id=$2',[req.params.aid,req.params.id]);if(!a.rowCount){await cx.query('ROLLBACK');res.status(404).end();return}await cx.query("UPDATE activities SET status='closed' WHERE session_id=$1 AND status='open'",[req.params.id]);await cx.query("UPDATE activities SET status='open',opened_at=now() WHERE id=$1",[req.params.aid]);await cx.query('UPDATE sessions SET current_activity_id=$1 WHERE id=$2',[req.params.aid,req.params.id]);await cx.query('COMMIT');await broadcast(req.params.id);res.json({ok:true})}catch(e){await cx.query('ROLLBACK');sendError(res,e)}finally{cx.release()}});
app.post('/api/sessions/:id/activities/:aid/close',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}await db.query("UPDATE activities SET status='closed' WHERE id=$1 AND session_id=$2 AND status='open'",[req.params.aid,s.id]);await broadcast(s.id);res.json({ok:true})}catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/qr',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}const url=`${publicBase}/join/${s.join_secret}`;const type=req.query.format==='svg'?'svg':'png';res.setHeader('Content-Disposition',`attachment; filename="quorivio-${s.join_code}.${type}"`);if(type==='svg'){res.type('image/svg+xml').send(await QRCode.toString(url,{type:'svg',margin:2}))}else{res.type('png').send(await QRCode.toBuffer(url,{width:800,margin:2}))}}catch(e){sendError(res,e)}});
// GDPR data lifecycle: only the session owner can revoke access, set retention or erase a session.
app.post('/api/sessions/:id/revoke',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}if(s.owner_id!==auth(req)){res.status(403).json({error:'owner_required'});return}const updated=await db.query("UPDATE sessions SET join_code=$2,join_secret=$3,status='closed',closed_at=now(),expires_at=now() WHERE id=$1 RETURNING *",[s.id,randomBytes(5).toString('hex').toUpperCase(),randomBytes(20).toString('base64url')]);await db.query("UPDATE activities SET status='closed' WHERE session_id=$1 AND status='open'",[s.id]);await broadcast(s.id);for(const ws of sockets.get(s.id)||[])ws.close(1008,'access revoked');res.json({ok:true,session:strip(updated.rows[0])})}catch(e){sendError(res,e)}});
app.patch('/api/sessions/:id/retention',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}const days=req.body?.retention_days;if(!validRetentionDays(days)){res.status(400).json({error:'invalid_retention_days'});return}const r=await db.query("UPDATE sessions SET retention_days=$2 WHERE id=$1 RETURNING retention_days",[s.id,days]);res.json(r.rows[0])}catch(e){sendError(res,e)}});
app.delete('/api/sessions/:id',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}if(s.owner_id!==auth(req)){res.status(403).json({error:'owner_required'});return}await db.query('DELETE FROM sessions WHERE id=$1 AND owner_id=$2',[s.id,auth(req)]);await cleanupSessionFiles(s.id).catch(e=>console.error('asset directory cleanup pending',s.id,e instanceof Error?e.message:'unknown'));for(const ws of sockets.get(s.id)||[])ws.close(1008,'session deleted');res.status(204).end()}catch(e){sendError(res,e)}});
// A session may be auto-purged only after its retention window AND after closure/expiry.
async function purgeExpiredSessions(){const r=await db.query("DELETE FROM sessions WHERE (status='closed' OR expires_at<now()) AND COALESCE(closed_at,expires_at) + (SELECT value::int FROM platform_settings WHERE key='closed_session_retention_days') * interval '1 day' < now() RETURNING id");for(const row of r.rows){await cleanupSessionFiles(row.id).catch(e=>console.error('expired asset cleanup pending',row.id,e instanceof Error?e.message:'unknown'));for(const ws of sockets.get(row.id)||[])ws.close(1008,'expired')}}
app.get('/api/sessions/:id/export.csv',requireAuth,async(req,res)=>{try{const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}const r=await db.query('SELECT a.title,a.type,r.option_id,r.correct,r.submitted_at FROM responses r JOIN activities a ON a.id=r.activity_id WHERE a.session_id=$1 AND r.invalidated_at IS NULL ORDER BY r.submitted_at',[s.id]);const esc=escapeCsvCell;res.setHeader('Content-Type','text/csv; charset=utf-8');res.setHeader('Content-Disposition',`attachment; filename="quorivio-${s.join_code}.csv"`);res.send('\uFEFF' + [['activity','type','option_id','correct','submitted_at'],...r.rows.map(x=>[x.title,x.type,x.option_id,x.correct,x.submitted_at.toISOString()])].map(row=>row.map(esc).join(',')).join('\r\n'))}catch(e){sendError(res,e)}});
async function publicSession(secretOrCode:string){const r=await db.query('SELECT * FROM sessions WHERE (join_secret=$1 OR join_code=$1) AND status=$2 AND expires_at>now()',[secretOrCode,'active']);return r.rows[0]}
app.get('/api/join/:code',async(req,res)=>{try{const s=await publicSession(req.params.code);if(!s){res.status(404).json({error:'session_unavailable'});return}const a=s.current_activity_id?(await db.query('SELECT * FROM activities WHERE id=$1',[s.current_activity_id])).rows[0]:null;res.json({session:{id:s.id,title:s.title,status:s.status},activity:a?publicActivity(a):null,allow_anonymous:s.allow_anonymous,show_results:s.show_results,theme:s.theme})}catch(e){sendError(res,e)}});
// Read-only QR endpoint; embeds only the public participant URL, never access privileges.
app.get('/api/join/:code/qr.svg',async(req,res)=>{try{const s=await publicSession(req.params.code);if(!s){res.status(404).end();return}const url=`${publicBase}/join/${s.join_secret}`;res.setHeader('Cache-Control','no-store');res.type('image/svg+xml').send(await QRCode.toString(url,{type:'svg',margin:2}))}catch(e){sendError(res,e)}});
app.post('/api/join/:code',async(req,res)=>{try{const s=await publicSession(req.params.code);if(!s){res.status(404).json({error:'session_unavailable'});return}const pseudonym=req.body?.pseudonym;if(!s.allow_anonymous){res.status(403).json({error:'anonymous_disabled'});return}if(!validPseudonym(pseudonym)){res.status(400).json({error:'pseudonym_required'});return}const existing=cookies(req.headers.cookie)[`q_part_${s.id}`];if(existing&&(await db.query('SELECT 1 FROM participants WHERE session_id=$1 AND token_hash=$2',[s.id,hash(existing)])).rowCount){res.json({ok:true,rejoined:true});return}const token=randomBytes(32).toString('base64url'),id=randomUUID();await db.query('INSERT INTO participants(id,session_id,token_hash,pseudonym) VALUES($1,$2,$3,$4)',[id,s.id,hash(token),pseudonym.trim()]);res.cookie(`q_part_${s.id}`,token,{httpOnly:true,sameSite:'strict',secure:base.startsWith('https:'),maxAge:86400000,path:'/'});res.json({ok:true})}catch(e){sendError(res,e)}});
app.post('/api/join/:code/reactions',async(req,res)=>{try{
 const s=await publicSession(req.params.code);if(!s||s.status!=='active'){res.status(404).json({error:'session_unavailable'});return}
 const token=cookies(req.headers.cookie)[`q_part_${s.id}`];const p=token?await db.query('SELECT id FROM participants WHERE session_id=$1 AND token_hash=$2',[s.id,hash(token)]):null;
 if(!p?.rowCount){res.status(401).json({error:'join_first'});return}
 const activityId=req.body?.activity_id,emoji=req.body?.emoji;
 if(!validReaction(emoji)){res.status(400).json({error:'invalid_reaction'});return}
 const a=await db.query('SELECT id FROM activities WHERE id=$1 AND session_id=$2',[activityId,s.id]);if(!a.rowCount||s.current_activity_id!==activityId){res.status(409).json({error:'page_not_current'});return}
 const r=await db.query('INSERT INTO page_reactions(session_id,activity_id,participant_id,emoji) VALUES($1,$2,$3,$4) ON CONFLICT(activity_id,participant_id) DO NOTHING RETURNING emoji',[s.id,activityId,p.rows[0].id,emoji]);
 if(r.rowCount)await broadcast(s.id);res.json({ok:true,already_reacted:!r.rowCount});
 }catch(e){sendError(res,e)}});
app.post('/api/join/:code/ratings',async(req,res)=>{try{
 const s=await publicSession(req.params.code);if(!s){res.status(404).json({error:'session_unavailable'});return}
 const token=cookies(req.headers.cookie)[`q_part_${s.id}`];const part=token?await db.query('SELECT id FROM participants WHERE session_id=$1 AND token_hash=$2',[s.id,hash(token)]):null;
 if(!part?.rowCount){res.status(401).json({error:'join_first'});return}
 const aid=req.body?.activity_id,score=req.body?.score,widgetId=req.body?.widget_id;const comment=req.body?.comment; if(comment!==undefined&&(typeof comment!=='string'||comment.length>1000||/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(comment))){res.status(400).json({error:'invalid_rating_comment'});return}
 if(!Number.isInteger(score)||score<0||score>10){res.status(400).json({error:'rating_out_of_range'});return}
 if(aid!==s.current_activity_id){res.status(409).json({error:'page_not_current'});return}
 const a=await db.query("SELECT page_design FROM activities WHERE id=$1 AND session_id=$2 AND status='open'",[aid,s.id]);
 const widgets=a.rows[0]?.page_design?.widgets||[];
 const widget=widgets.find((w:any)=>w.kind==='rating'&&(widgetId===undefined||w.id===widgetId));
 if(!widget){res.status(409).json({error:'rating_widget_not_enabled'});return}
 const kind=widget.targetKind||'question';const target=widget.targetId||(kind==='session'?s.id:aid);
 if(kind==='presenter'&&!await db.query('SELECT 1 FROM users WHERE id=$1 AND (id=$2 OR id IN (SELECT user_id FROM session_presenters WHERE session_id=$3))',[target,s.owner_id,s.id]).then(r=>r.rowCount)){res.status(400).json({error:'invalid_presenter_target'});return}
 const result=await db.query('INSERT INTO page_ratings(session_id,activity_id,participant_id,widget_id,target_kind,target_id,score,comment_text) VALUES($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT(activity_id,participant_id,widget_id) DO NOTHING RETURNING score',[s.id,aid,part.rows[0].id,widget.id,kind,target,score,comment?.trim()||null]);
 if(result.rowCount)await broadcast(s.id);res.json({ok:true,already_rated:!result.rowCount});
 }catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/ratings/stats',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const byPage=(await db.query('SELECT a.id AS activity_id,a.title,count(pr.score)::int AS responses,round(avg(pr.score)::numeric,2) AS mean FROM activities a LEFT JOIN page_ratings pr ON pr.activity_id=a.id WHERE a.session_id=$1 GROUP BY a.id,a.title,a.position ORDER BY a.position',[s.id])).rows;
 const byWidget=(await db.query('SELECT widget_id,target_kind,target_id,count(*)::int AS responses,round(avg(score)::numeric,2) AS mean FROM page_ratings WHERE session_id=$1 GROUP BY widget_id,target_kind,target_id ORDER BY target_kind,widget_id',[s.id])).rows;
 const distribution=(await db.query('SELECT score,count(*)::int AS count FROM page_ratings WHERE session_id=$1 GROUP BY score ORDER BY score',[s.id])).rows;
 const overall=(await db.query('SELECT count(*)::int AS responses,round(avg(score)::numeric,2) AS mean FROM page_ratings WHERE session_id=$1',[s.id])).rows[0];
 res.json({overall,by_page:byPage,by_widget:byWidget,distribution});
 }catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/reactions/stats',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const groups=(await db.query('SELECT a.id AS activity_id,a.title,pr.emoji,count(*)::int AS count FROM page_reactions pr JOIN activities a ON a.id=pr.activity_id WHERE pr.session_id=$1 GROUP BY a.id,a.title,pr.emoji ORDER BY a.title,pr.emoji',[s.id])).rows;
 const perUser=(await db.query('SELECT p.id,p.pseudonym,count(*)::int AS count FROM page_reactions pr JOIN participants p ON p.id=pr.participant_id WHERE pr.session_id=$1 GROUP BY p.id,p.pseudonym ORDER BY count DESC',[s.id])).rows;
 res.json({by_page:groups,by_user:perUser,by_session:groups.reduce((acc:any,row:any)=>{acc[row.emoji]=(acc[row.emoji]||0)+row.count;return acc},{})});
 }catch(e){sendError(res,e)}});
// Each topic widget has its own question stream; it never modifies quiz results.
app.post('/api/join/:code/activities/:aid/topic-widgets/:wid/questions',async(req,res)=>{try{
 const who=await audienceIdentity(req,req.params.code,req.params.aid);if(!who){res.status(403).json({error:'join_or_open_activity_required'});return}
 const body=req.body?.body;if(typeof body!=='string'||body.trim().length<5||body.length>2000){res.status(400).json({error:'invalid_topic_question'});return}
 const a=await db.query('SELECT page_design FROM activities WHERE id=$1 AND session_id=$2',[req.params.aid,who.sessionId]);
 if(!a.rows[0]?.page_design?.widgets?.some((w:any)=>w.id===req.params.wid&&w.kind==='topic-question')){res.status(404).json({error:'topic_widget_not_found'});return}
 const count=await db.query('SELECT count(*)::int AS n FROM topic_widget_questions WHERE participant_id=$1 AND activity_id=$2 AND widget_id=$3',[who.participantId,req.params.aid,req.params.wid]);
 if(count.rows[0].n>=10){res.status(429).json({error:'topic_question_limit'});return}
 await db.query('INSERT INTO topic_widget_questions(id,session_id,activity_id,widget_id,participant_id,body) VALUES($1,$2,$3,$4,$5,$6)',[randomUUID(),who.sessionId,req.params.aid,req.params.wid,who.participantId,body.trim()]);await broadcast(who.sessionId);res.status(201).json({ok:true});
 }catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/activities/:aid/topic-widgets/:wid/questions',requireAuth,async(req,res)=>{try{
 const session=await owner(req.params.id,auth(req)!);if(!session){res.status(404).end();return}
 const a=await db.query('SELECT page_design FROM activities WHERE id=$1 AND session_id=$2',[req.params.aid,session.id]);
 const w=a.rows[0]?.page_design?.widgets?.find((x:any)=>x.id===req.params.wid&&x.kind==='topic-question');if(!w){res.status(404).json({error:'topic_widget_not_found'});return}
 const page=Math.max(1,Math.min(100000,Number.parseInt(String(req.query.page||'1'),10)||1));
 const total=await db.query('SELECT count(*)::int AS n FROM topic_widget_questions WHERE session_id=$1 AND activity_id=$2 AND widget_id=$3',[session.id,req.params.aid,req.params.wid]);
 const rows=await db.query(`SELECT q.id,q.body,q.created_at,p.pseudonym AS participant_name FROM topic_widget_questions q JOIN participants p ON p.id=q.participant_id WHERE q.session_id=$1 AND q.activity_id=$2 AND q.widget_id=$3 ORDER BY q.created_at,q.id LIMIT 10 OFFSET $4`,[session.id,req.params.aid,req.params.wid,(page-1)*10]);
 res.json({page,page_size:10,total:total.rows[0].n,items:rows.rows.map((r:any)=>({...r,participant_name:w.showNames?r.participant_name:null}))});
 }catch(e){sendError(res,e)}});
// Question widgets have independent submissions; an activity's primary answer is unaffected.
app.post('/api/join/:code/activities/:aid/widgets/:wid/respond',async(req,res)=>{const cx=await db.connect();try{
 const who=await audienceIdentity(req,req.params.code,req.params.aid);
 if(!who){res.status(403).json({error:'join_or_open_activity_required'});return}
 await cx.query('BEGIN');
 // Serialize edits and submissions on the activity row to bind each response to a stable revision.
 const a=await cx.query('SELECT page_design FROM activities WHERE id=$1 AND session_id=$2 FOR SHARE',[req.params.aid,who.sessionId]);
 const widget=(a.rows[0]?.page_design?.widgets||[]).find((w:any)=>w.kind==='question'&&w.id===req.params.wid);
 if(!widget){await cx.query('ROLLBACK');res.status(404).json({error:'widget_not_found'});return}
 const mode=validAnswerMode(widget.answerMode)?widget.answerMode:'text';
 const options=Array.isArray(widget.options)?widget.options:[];
 const value=mode==='single'?req.body?.option_id:mode==='multiple'?req.body?.option_ids:mode==='text'?req.body?.text:req.body?.asset_id;
 const answer=validateSubmittedAnswer(mode,widget.required!==false,value,options);
 if(!answer){await cx.query('ROLLBACK');res.status(400).json({error:'invalid_widget_answer'});return}
 if(answer.assetId){const owned=await cx.query('SELECT id FROM session_assets WHERE id=$1 AND session_id=$2 AND (participant_id IS NULL OR participant_id=$3)',[answer.assetId,who.sessionId,who.participantId]);if(!owned.rowCount){await cx.query('ROLLBACK');res.status(400).json({error:'attachment_not_in_session'});return}}
 const rev=await cx.query('SELECT coalesce(max(revision),1)::int AS revision FROM widget_revisions WHERE activity_id=$1 AND widget_id=$2',[req.params.aid,req.params.wid]);
 const revision=Number(rev.rows[0].revision);
 const r=await cx.query('INSERT INTO widget_answers(id,session_id,activity_id,participant_id,widget_id,answer_mode,answer_payload,revision) VALUES($1,$2,$3,$4,$5,$6,$7,$8) ON CONFLICT(activity_id,participant_id,widget_id,revision) DO NOTHING RETURNING id',[randomUUID(),who.sessionId,req.params.aid,who.participantId,req.params.wid,mode,JSON.stringify(answer),revision]);
 await cx.query('COMMIT');if(r.rowCount)await broadcast(who.sessionId);res.json({ok:true,already_submitted:!r.rowCount,revision});
 }catch(e){await cx.query('ROLLBACK');sendError(res,e)}finally{cx.release()}});
app.get('/api/sessions/:id/widget-answers',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const r=await db.query('SELECT activity_id,widget_id,revision,answer_mode,count(*)::int AS responses FROM widget_answers WHERE session_id=$1 GROUP BY activity_id,widget_id,revision,answer_mode ORDER BY activity_id,widget_id,revision',[s.id]);
 res.json(r.rows);
 }catch(e){sendError(res,e)}});
app.get('/api/sessions/:id/widget-answers/detail',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const activity=String(req.query.activity_id||''), widget=String(req.query.widget_id||'');
 if(!/^[0-9a-f-]{36}$/i.test(activity)||!/^[a-zA-Z0-9_-]{1,48}$/.test(widget)){res.status(400).json({error:'invalid_filter'});return}
 const r=await db.query('SELECT revision,answer_mode,answer_payload FROM widget_answers WHERE session_id=$1 AND activity_id=$2 AND widget_id=$3 ORDER BY submitted_at',[s.id,activity,widget]);
 const revisions=aggregateWidgetAnswerRevisions(r.rows);
 res.json({activity_id:activity,widget_id:widget,revisions});
 }catch(e){sendError(res,e)}});
// Only authorized presenters can read identities and rankings; the start is the server's page-open timestamp.
app.get('/api/sessions/:id/activities/:aid/timed-leaderboard',requireAuth,async(req,res)=>{try{
 const s=await owner(req.params.id,auth(req)!);if(!s){res.status(404).end();return}
 const a=await db.query('SELECT id,type,opened_at FROM activities WHERE id=$1 AND session_id=$2',[req.params.aid,s.id]);if(a.rows[0]?.type!=='timed_quiz'){res.status(404).json({error:'not_timed_quiz'});return}
 const summary=await db.query('SELECT count(*)::int AS answers,count(*) FILTER (WHERE correct)::int AS correct FROM responses WHERE activity_id=$1 AND invalidated_at IS NULL',[req.params.aid]);
 const ranking=await db.query(`SELECT p.pseudonym AS participant_name,r.elapsed_ms AS duration_ms,r.submitted_at FROM responses r JOIN participants p ON p.id=r.participant_id WHERE r.activity_id=$1 AND r.correct=true AND r.invalidated_at IS NULL AND r.elapsed_ms IS NOT NULL ORDER BY r.elapsed_ms ASC,r.submitted_at ASC,r.id ASC LIMIT 100`,[req.params.aid]);
 res.json({activity_id:req.params.aid,opened_at:a.rows[0].opened_at,...summary.rows[0],ranking:ranking.rows.map((r:any,i:number)=>({...r,rank:i+1}))});
 }catch(e){sendError(res,e)}});
app.post('/api/join/:code/respond',async(req,res)=>{const cx=await db.connect();try{await cx.query('BEGIN');const s=await cx.query("SELECT * FROM sessions WHERE (join_secret=$1 OR join_code=$1) AND status='active' AND expires_at>now() FOR SHARE",[req.params.code]);if(!s.rowCount){await cx.query('ROLLBACK');res.status(404).json({error:'session_unavailable'});return}if(!s.rows[0].allow_anonymous){await cx.query('ROLLBACK');res.status(403).json({error:'anonymous_disabled'});return}const sid=s.rows[0].id;const token=cookies(req.headers.cookie)[`q_part_${sid}`];const p=token?await cx.query('SELECT id FROM participants WHERE session_id=$1 AND token_hash=$2',[sid,hash(token)]):null;if(!p?.rowCount){await cx.query('ROLLBACK');res.status(401).json({error:'join_first'});return}const a=await cx.query("SELECT * FROM activities WHERE id=$1 AND session_id=$2 AND status='open' FOR SHARE",[req.body?.activity_id,sid]);if(!a.rowCount||s.rows[0].current_activity_id!==req.body?.activity_id){await cx.query('ROLLBACK');res.status(409).json({error:'activity_not_open'});return}const act=a.rows[0] as Activity & {opened_at:Date};const mode=validAnswerMode((act as any).answer_mode)?(act as any).answer_mode:'single';
const raw=mode==='single'?req.body?.option_id:mode==='multiple'?req.body?.option_ids:mode==='text'?req.body?.text:req.body?.asset_id;
const answer=validateSubmittedAnswer(mode,(act as any).answer_required!==false,raw,act.options);
if(!answer){await cx.query('ROLLBACK');res.status(400).json({error:'invalid_answer'});return}
if(answer.assetId){const asset=await cx.query('SELECT id FROM session_assets WHERE id=$1 AND session_id=$2 AND (participant_id IS NULL OR participant_id=$3)',[answer.assetId,sid,p.rows[0].id]);if(!asset.rowCount){await cx.query('ROLLBACK');res.status(400).json({error:'attachment_not_in_session'});return}}
const option=answer.optionIds.join(',');if(act.duration_seconds&&Date.now()>new Date(act.opened_at).getTime()+act.duration_seconds*1000){await cx.query('ROLLBACK');res.status(409).json({error:'timer_elapsed'});return}const correct=mode==='single'?checkAnswer(act,option):mode==='multiple'&&Array.isArray((act as any).correct_option_ids)&&answer.optionIds.length>0&&answer.optionIds.length===(act as any).correct_option_ids.length&&answer.optionIds.every(x=>(act as any).correct_option_ids.includes(x));
const elapsedMs=act.type==='timed_quiz'?Math.max(0,Date.now()-new Date(act.opened_at).getTime()):null;const r=await cx.query('INSERT INTO responses(id,activity_id,participant_id,option_id,correct,answer_payload,elapsed_ms) VALUES($1,$2,$3,$4,$5,$6,$7) ON CONFLICT(activity_id,participant_id) WHERE invalidated_at IS NULL DO NOTHING RETURNING id',[randomUUID(),act.id,p.rows[0].id,option,correct,JSON.stringify(answer),elapsedMs]);await cx.query('COMMIT');if(r.rowCount)await broadcast(sid);res.json({ok:true,already_submitted:!r.rowCount})}catch(e){await cx.query('ROLLBACK');sendError(res,e)}finally{cx.release()}});
server.on('upgrade',async(req,socket,head)=>{try{const origin=req.headers.origin;if(origin&&new URL(origin).host!==new URL(base).host){socket.destroy();return}const url=new URL(req.url||'/',base);if(url.pathname!=='/live'){socket.destroy();return}const sid=url.searchParams.get('session');if(!sid){socket.destroy();return}const s=(await db.query('SELECT * FROM sessions WHERE id=$1',[sid])).rows[0];if(!s||s.status==='closed'||new Date(s.expires_at).getTime()<=Date.now()){socket.destroy();return}const uid=auth(req as express.Request);const part=cookies(req.headers.cookie)[`q_part_${sid}`];const ownerAccount=uid&&(uid===s.owner_id||(await db.query('SELECT 1 FROM session_presenters WHERE session_id=$1 AND user_id=$2',[sid,uid])).rowCount)?(await db.query("SELECT 1 FROM users WHERE id=$1 AND approved=true AND must_change_password=false AND role IN ('presenter','platform_admin','org_admin')",[uid])).rowCount:false;const allowed=ownerAccount||(part&&s.allow_anonymous&&(await db.query('SELECT id FROM participants WHERE session_id=$1 AND token_hash=$2',[sid,hash(part)])).rowCount);if(!allowed){socket.destroy();return}wss.handleUpgrade(req,socket,head,ws=>{(ws as any).view=ownerAccount?'owner':'participant';(ws as any).uid=ownerAccount?uid:null;wss.emit('connection',ws,req,sid)})}catch{socket.destroy()}});
wss.on('connection',(ws:WebSocket,_req:unknown,sid:string)=>{let group=sockets.get(sid);if(!group){group=new Set();sockets.set(sid,group)}group.add(ws);snapshot(sid).then(data=>{if(ws.readyState===WebSocket.OPEN)ws.send(JSON.stringify({type:'snapshot',data:(ws as any).view==='owner'?data:participantSnapshot(data)}))});ws.on('close',()=>{group?.delete(ws);if(!group?.size)sockets.delete(sid)})});
function participantSnapshot(data:any){if(!data)return data;return {session:{id:data.session.id,title:data.session.title,status:data.session.status},activities:data.activities.filter((a:Activity)=>a.id===data.session.current_activity_id).map(publicActivity),results:data.session.show_results?data.results.filter((r:any)=>r.activity_id===data.session.current_activity_id):[],totals:data.session.show_results?data.totals.filter((r:any)=>r.activity_id===data.session.current_activity_id):[]}}
const webRoot=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../web/dist');if(existsSync(webRoot)){app.use(express.static(webRoot));app.get('*',(_,res)=>res.sendFile(path.join(webRoot,'index.html')))}
async function initialize(){const schema=readFileSync(path.join(path.dirname(fileURLToPath(import.meta.url)),'../src/schema.sql'),'utf8');await db.query(schema);publicBase=(await db.query("SELECT value FROM platform_settings WHERE key='public_base_url'")).rows[0]?.value||base;const email=process.env.ADMIN_EMAIL?.toLowerCase(),password=process.env.ADMIN_PASSWORD;if(email&&password){if(password.length<12&&!(process.env.ALLOW_INSECURE_DEV_BOOTSTRAP==='true'&&process.env.NODE_ENV!=='production'&&password==='000000'))throw new Error('ADMIN_PASSWORD must be >=12 characters (insecure demo bootstrap allowed only outside production)');const count=await db.query('SELECT count(*)::int AS n FROM users');if(count.rows[0].n===0){const oid=randomUUID(),uid=randomUUID();await db.query('INSERT INTO organizations(id,name) VALUES($1,$2)',[oid,'Default']);await db.query('INSERT INTO users(id,organization_id,email,password_hash,role) VALUES($1,$2,$3,$4,$5)',[uid,oid,email,await bcrypt.hash(password,12),'platform_admin']);await db.query('UPDATE users SET approved=true,must_change_password=true,is_primary_admin=true,nickname=$2 WHERE id=$1',[uid,'admin']);console.log('Initial admin provisioned; password change required')}}await db.query("UPDATE users SET is_primary_admin=true,nickname='admin' WHERE id=(SELECT id FROM users WHERE role='platform_admin' AND approved=true ORDER BY created_at ASC LIMIT 1) AND NOT EXISTS (SELECT 1 FROM users WHERE is_primary_admin=true)");startSessionBus(async()=>{const client=new pg.Client({connectionString:process.env.DATABASE_URL});await client.connect();return client},broadcastLocal);await purgeExpiredSessions();setInterval(()=>purgeExpiredSessions().catch(e=>console.error('retention purge error',e instanceof Error?e.message:'unknown')),3600000).unref();setInterval(()=>db.query("DELETE FROM auth_flows WHERE expires_at<now(); DELETE FROM api_rate_windows WHERE bucket<floor(extract(epoch from now())/60)-3").catch(e=>console.error('auth cleanup error',e instanceof Error?e.message:'unknown')),3600000).unref();server.listen(Number(process.env.PORT||8080),'0.0.0.0',()=>console.log('Quorivio API ready'))}
initialize().catch(e=>{console.error('startup failed',e);process.exit(1)});
