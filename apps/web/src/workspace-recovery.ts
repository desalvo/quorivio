/** Non-sensitive workspace route only. Never store credentials, answers or unsaved page data. */
export type WorkspaceLocation={sessionId:string;section:'workspace'|'new'|'open'|'calendar'|'session'|'master'|'users'|'settings'|'sso'|'mfa'|'profile';tab:'overview'|'pages'|'audience'|'results';pageId:string};
const KEY='quorivio.workspace.v1';
const EMPTY:WorkspaceLocation={sessionId:'',section:'workspace',tab:'overview',pageId:''};
const id=/^[a-f0-9-]{36}$/i;
export function parseWorkspaceLocation(raw:string|null):WorkspaceLocation{
 if(!raw||raw.length>512)return {...EMPTY};
 try{const x=JSON.parse(raw);if(!x||typeof x!=='object'||Array.isArray(x))return {...EMPTY};
  const sessionId=typeof x.sessionId==='string'&&id.test(x.sessionId)?x.sessionId:'';
  const section=typeof x.section==='string'&&['workspace','new','open','calendar','session','master','users','settings','sso','mfa','profile'].includes(x.section)?x.section:EMPTY.section;
  const tab=typeof x.tab==='string'&&['overview','pages','audience','results'].includes(x.tab)?x.tab:EMPTY.tab;
  const pageId=typeof x.pageId==='string'&&id.test(x.pageId)?x.pageId:'';
  return {sessionId,section:sessionId?section:'workspace',tab,pageId:sessionId?pageId:''};
 }catch{return {...EMPTY}}
}
export function readWorkspaceLocation():WorkspaceLocation{
 try{return parseWorkspaceLocation(sessionStorage.getItem(KEY))}catch{return {...EMPTY}}
}
export function writeWorkspaceLocation(location:WorkspaceLocation):void{
 try{sessionStorage.setItem(KEY,JSON.stringify(parseWorkspaceLocation(JSON.stringify(location))))}catch{/* Blocked storage must not block the app. */}
}
