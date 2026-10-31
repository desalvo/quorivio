/** Single-owner browser live transport. It never accepts events from retired sockets.
 * All timers, online state and sockets are injected so recovery can be tested
 * deterministically without an actual network or leaking participant data.
 */
import {nextLiveRetryMs} from './participant-state.ts';

export type LiveConnectionStatus='connecting'|'connected'|'disconnected'|'blocked';
export type LiveSocket={
 readyState:number;
 close:()=>void;
 onopen:((event:Event)=>void)|null;
 onclose:((event:CloseEvent)=>void)|null;
 onerror:((event:Event)=>void)|null;
 onmessage:((event:MessageEvent)=>void)|null;
};
export type LiveRuntime={
 createSocket:(url:string)=>LiveSocket;
 isOnline:()=>boolean;
 schedule:(callback:()=>void,ms:number)=>number;
 cancel:(timer:number)=>void;
};

export function jitteredLiveRetryMs(attempt:number,random:number):number{
 const unit=Number.isFinite(random)?Math.max(0,Math.min(1,random)):0.5;
 return Math.max(1,Math.min(30000,Math.round(nextLiveRetryMs(attempt)*(0.8+0.4*unit))));
}

export function createLiveConnection(options:{
 sessionId:string;
 url:string;
 runtime:LiveRuntime;
 onSnapshot:(snapshot:unknown)=>void;
 onConnection?:(status:LiveConnectionStatus)=>void;
 random?:()=>number;
 handshakeTimeoutMs?:number;
 /** Server broadcasts snapshots at ~20s intervals; never trust a silent open socket indefinitely. */
 snapshotTimeoutMs?:number;
}){
 const {runtime,sessionId,url,onSnapshot,onConnection}=options;
 if(!sessionId||!url)throw new Error('live connection requires session and URL');
 let disposed=false;
 let terminal=false;
 let socket:LiveSocket|null=null;
 let retry:number|undefined;
 let handshake:number|undefined;
 let freshness:number|undefined;
 let attempt=0;
 let status:LiveConnectionStatus|undefined;
 const notify=(next:LiveConnectionStatus)=>{if(status!==next){status=next;onConnection?.(next)}};
 const cancelRetry=()=>{if(retry!==undefined){runtime.cancel(retry);retry=undefined}};
 const cancelHandshake=()=>{if(handshake!==undefined){runtime.cancel(handshake);handshake=undefined}};
 const cancelFreshness=()=>{if(freshness!==undefined){runtime.cancel(freshness);freshness=undefined}};
 const retire=(own:LiveSocket)=>{
  if(disposed||socket!==own)return;
  socket=null;cancelHandshake();cancelFreshness();notify('disconnected');
  try{own.close()}catch{ /* The socket is already closing; retry is still required. */ }
  scheduleRetry();
 };
 const armFreshness=(own:LiveSocket)=>{
  cancelFreshness();
  const timeout=Math.max(5000,Math.min(300000,options.snapshotTimeoutMs??65000));
  freshness=runtime.schedule(()=>{freshness=undefined;retire(own)},timeout);
 };
 const scheduleRetry=()=>{
  if(disposed||terminal||!runtime.isOnline()||socket||retry!==undefined)return;
  const delay=jitteredLiveRetryMs(attempt++,options.random?.()??0.5);
  retry=runtime.schedule(()=>{retry=undefined;connect()},delay);
 };
 const connect=()=>{
  if(disposed||terminal||!runtime.isOnline()||socket)return;
  cancelRetry();
  notify('connecting');
  let own:LiveSocket;
  try{own=runtime.createSocket(url)}catch{notify('disconnected');scheduleRetry();return}
  socket=own;
  const current=()=>!disposed&&socket===own;
  own.onopen=()=>{if(!current())return;cancelHandshake();attempt=0;notify('connected');armFreshness(own)};
  own.onclose=(event)=>{
   if(!current())return;
   cancelHandshake();cancelFreshness();socket=null;
   if(event.code===4003||event.code===1008){terminal=true;cancelRetry();notify('blocked');return}
   notify('disconnected');
   scheduleRetry();
  };
  own.onerror=()=>{if(current())retire(own)};
  own.onmessage=(event)=>{
   if(!current())return;
   try{
    if(typeof event.data!=='string')return;
    const message=JSON.parse(event.data);
    if(message?.type==='snapshot'&&message.data?.session?.id===sessionId){
     armFreshness(own);onSnapshot(message.data);
    }
   }catch{ /* Invalid and cross-session payloads are not rendered. */ }
  };
  const timeout=Math.max(1000,Math.min(60000,options.handshakeTimeoutMs??15000));
  handshake=runtime.schedule(()=>{
   if(!current()||own.readyState===1)return;
   // Fence the timed-out socket BEFORE closing it: a late event must not
   // close a newly connected socket or replace its visible status.
   retire(own);
  },timeout);
 };
 const offline=()=>{
  if(disposed)return;
  cancelRetry();cancelHandshake();cancelFreshness();
  const previous=socket;socket=null;
  if(!terminal)notify('disconnected');
  previous?.close();
 };
 const online=()=>{if(!disposed&&!terminal&&runtime.isOnline()&&!socket){cancelRetry();connect()}};
 const dispose=()=>{
  if(disposed)return;
  disposed=true;cancelRetry();cancelHandshake();cancelFreshness();
  const previous=socket;socket=null;previous?.close();
 };
 if(!runtime.isOnline())notify('disconnected');
 else connect();
 return {online,offline,dispose};
}
