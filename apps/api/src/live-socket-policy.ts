/** Shared, fail-closed authorization policy for already-open live sockets. */
export type LiveSession = {id:string;owner_id:string;status:string;expires_at:string|Date};
export type LiveAccount = {id:string;role:string;approved:boolean;must_change_password:boolean;auth_revoked_at?:Date|string|null;password_changed_at?:Date|string|null};
export function liveSessionActive(session:LiveSession|undefined, now=Date.now()):boolean {
 return !!session && session.status!=='closed' && Number.isFinite(new Date(session.expires_at).getTime()) && new Date(session.expires_at).getTime()>now;
}
export function livePresenterAuthorized(session:LiveSession|undefined, account:LiveAccount|undefined, isPresenter:boolean, issuedAt:number|null, now=Date.now()):boolean {
 if(!liveSessionActive(session,now)||!account||!account.approved||account.must_change_password||!['presenter','platform_admin','org_admin'].includes(account.role)||!Number.isFinite(issuedAt)||!issuedAt)return false;
 if(account.id!==session!.owner_id&&!isPresenter)return false;
 for(const date of [account.auth_revoked_at,account.password_changed_at])if(date && new Date(date).getTime()>issuedAt!)return false;
 return true;
}

/** Participant sockets must still belong to the same session after a revoke/delete. */
export function liveParticipantAuthorized(session:LiveSession|undefined, participantId:string|null|undefined, belongsToSession:boolean, now=Date.now()):boolean {
 return liveSessionActive(session,now)&&typeof participantId==='string'&&participantId.length>0&&belongsToSession;
}
