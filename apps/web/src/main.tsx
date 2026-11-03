import {answerFieldHeight,answerFieldHeightForKey} from './answer-field-resize.js';
import {readWorkspaceLocation,writeWorkspaceLocation} from './workspace-recovery';
import {DEFAULT_TITLE_STYLE,newTitleWidget,newFooterWidget,widgetDisplay,slidePageNumber,footerPageNumber} from './slide-master';
import {resolveSlideMasterWidgets,masterWidgetTemplate,normalizeLegacyFooter} from './master-widget-utils';
import {consumeRecoveryTokenFromUrl} from './password-recovery-url';
import {validPageDesign} from '../../api/src/domain';
import type {PageDesign,WidgetTextStyle,WidgetInlineMark,WidgetSubquestion} from '../../api/src/domain';
import {pageDraftSignature as serializePageDraft,pageDraftFromActivity,validDesignRevision,type EditablePageDraft} from './page-draft';
import {autosaveRecoveryDecision,recoverableAutosaveTransportError,retryAutosaveDelay} from './page-autosave';
import {widgetAppearanceStyle,widgetTypographyStyle} from './widget-appearance.js';
import {widgetArtData,widgetTimerFace,type WidgetTimerFace} from './widget-art.js';
import {styledSegments,inlineMarkCss,formatTextRange,remapMarks,changedRegion,inlineKeys,applySelectionInlineStyle,selectionUniformValue,scaleWidgetFont,scaleAllWidgetTypography,formatSelectedOrEntireField,applyAllWidgetTypeface,type InlineStyle,type TextMark} from './widget-text-marks.js';
import {RichWidgetText} from './widget-rich-editor.js';
import {RatingChoices} from './rating-choices.js';
import {ReactionChoices} from './reaction-choices.js';
import {eligibleStatisticSources,linkedStatisticSource,effectiveResultView,sampleStatisticRows,rehearsalFreeTextRows,rowsFromWidgetAnswerDetail,topicQuestionRows,REHEARSAL_EMOJIS,type StatRow} from './widget-results.js';
import {rejectWidgetCollisions,moveWidgetsToCollisionLimit,resizeWidgetToCollisionLimit,magneticSnapWithGuides,snapWidgetGroupDelta,freeWidgetPosition} from './widget-placement.js';
import {widgetGeometryStyle} from './widget-geometry';
import {mediaUploadMime} from './widget-asset-upload';
import {backgroundUploadError} from './background-upload-error';
import {answerInputStyle,answerOptionStyle,answerSubmitStyle,requiresAnswerSubmit} from './widget-answer-style';
import {cloudRankColor,rankCloudItems} from './word-cloud-rank';
import {topResultRows,splitResultLabel} from './result-top-rows';
import {phoneStageScale} from './rehearsal-phone-scale';
import {MOBILE_PAGE_WIDTH,mobileStageHeight,mobilePageWidgets,captureMobilePositions,pruneMobilePageLayout} from './mobile-page-layout';
import type {MobilePageLayout} from '../../api/src/domain';
import {autoFitExpandedPosition,widgetMayAutoFit,measuredContentOverflowPx} from './widget-auto-fit';
import {canvasWidgetAtPoint} from './editor-context-hit';
import {startsWidgetSelectionOnPointerDown} from './editor-context-input';
import {activateRehearsalDialog} from './rehearsal-dialog';
import {questionModeOptions,invalidPageWidgetReason} from './editor-save-safety';
import {contextMenuCoordinates,floatingWidgetMenuPosition} from './editor-context-menu';
import {WidgetShapeOutline} from './widget-shape-outline';
import {WidgetGraphic} from './widget-graphic';
import {canSubmitRehearsalAnswer,commitRehearsalAnswer,changeRehearsalReaction,changeRehearsalRating,REHEARSAL_REACTION_PREFIX} from './rehearsal-responses';
import {rehearsalDurationSeconds,rehearsalExpired,maySubmitTimedRehearsal,pageCountdownSeconds,pageInteractionExpired} from './rehearsal-timer';
import {mergePageDrafts,type MergeChoice} from './page-merge';
import {createPageDraftBackup,parsePageDraftBackup,planPageDraftRecovery} from './page-draft-recovery';
import {arrangeWidgets,type ArrangeMode} from './widget-arrange';
import {normalizeJoinCode,canSubmitParticipantAnswer,publicActivityFromSnapshot} from './participant-state';
import {moveWidgetGroup,pasteWidgetGroup} from './widget-group';
import {createLiveConnection} from './live-connection';
import {reorderWidgetLayers,type LayerAction} from './widget-layer';
import {existingWidgetIds,deleteWidgetSelection,insertWidgetGroupInFreeSpace,nudgeWidgetSelection} from './widget-selection';
import {pasteWidget} from './widget-clipboard';
import {saveEditorWidgetClipboard,readEditorWidgetClipboard} from './editor-cross-page-clipboard';
import {newWidgetHistory,editWidgets,reconcileWidgetAutoFit,beginWidgetGesture,endWidgetGesture,undoWidgets,redoWidgets} from './widget-history';
import {movePageId} from './page-order';
import {presenterPageIndex,presenterAdjacentPage,presenterKeyboardDirection} from './presenter-navigation';
import {commitAndReconcilePageOrder} from './page-order-recovery';
import React,{useEffect,useState,useRef} from 'react';import{createPortal}from'react-dom';import{createRoot}from'react-dom/client';import{ArrowRight,BarChart3,Download,ExternalLink,LogOut,Play,Plus,Radio,ShieldCheck,Square,Users,Wifi,Type,Image as ImageIcon,Clock3,MessageCircle,FileText,Minus,MoreVertical,Settings2,Undo2,Redo2,Save,Maximize2,Star,Smile,StickyNote,UserCircle,Video,QrCode,Timer,MessageSquareText,BadgeCheck,Gauge,Heading1,PanelBottom,Presentation,BarChartHorizontal,FileQuestion,Vote,Hash,BookImage,Bold as BoldIcon,Italic as ItalicIcon,Underline as UnderlineIcon,Strikethrough as StrikethroughIcon,AlignLeft,AlignCenter,AlignRight,PaintBucket,Palette as PaletteIcon,SlidersHorizontal,X,MoveHorizontal,MoveVertical}from'lucide-react';import './style.css';
// Editor windows live outside the slide flow. Only their title bars initiate a drag:
// inputs and typography controls keep their focus and text selections.
function EditorFloatingWindow({children,className,ariaLabel,role='region',placement='properties',portal=false,onMouseDownCapture}:{children:React.ReactNode;className:string;ariaLabel:string;role?:'toolbar'|'region';placement?:'palette'|'properties'|'page';portal?:boolean;onMouseDownCapture?:React.MouseEventHandler<HTMLDivElement>}){
 const panel=useRef<HTMLDivElement|null>(null);
 const pointer=useRef<{id:number;startX:number;startY:number;left:number;top:number}|null>(null);
 const [point,setPoint]=useState<{left:number;top:number}>(()=>{
  const vw=typeof window==='undefined'?1440:window.innerWidth, vh=typeof window==='undefined'?900:window.innerHeight;
  if(placement==='palette')return {left:Math.max(12,Math.round((vw-Math.min(850,vw-24))/2)),top:Math.max(12,Math.round(vh-Math.min(190,vh/3)-22))};
  return {left:Math.max(12,vw-Math.min(440,vw-24)-28),top:Math.max(12,Math.min(110,vh/8))};
 });
 const bound=(left:number,top:number)=>{
  const width=panel.current?.offsetWidth||Math.min(850,window.innerWidth-24);
  const height=panel.current?.offsetHeight||180;
  return {left:Math.max(8,Math.min(left,Math.max(8,window.innerWidth-width-8))),top:Math.max(8,Math.min(top,Math.max(8,window.innerHeight-height-8)))};
 };
 useEffect(()=>{
  const constrain=()=>setPoint(previous=>{const next=bound(previous.left,previous.top);return next.left===previous.left&&next.top===previous.top?previous:next});
  constrain();window.addEventListener('resize',constrain);
   const resize=new ResizeObserver(constrain);if(panel.current)resize.observe(panel.current);
   return ()=>{window.removeEventListener('resize',constrain);resize.disconnect()};
 },[]);
 const start=(e:React.PointerEvent<HTMLDivElement>)=>{
  if(e.button!==0||!((e.target as HTMLElement).closest('.palette-ribbon-head,.editor-drawer-heading')))return;
  if((e.target as HTMLElement).closest('button,input,textarea,select,a,[contenteditable=true]'))return;
  pointer.current={id:e.pointerId,startX:e.clientX,startY:e.clientY,left:point.left,top:point.top};
  e.currentTarget.setPointerCapture(e.pointerId);
  e.preventDefault();
 };
 const move=(e:React.PointerEvent<HTMLDivElement>)=>{
  const drag=pointer.current;if(!drag||drag.id!==e.pointerId)return;
  setPoint(bound(drag.left+e.clientX-drag.startX,drag.top+e.clientY-drag.startY));
 };
 const stop=(e:React.PointerEvent<HTMLDivElement>)=>{if(pointer.current?.id===e.pointerId)pointer.current=null};
 const content=<div ref={panel} className={className+' editor-floating-panel'} data-floating-editor={placement} role={role} aria-label={ariaLabel} style={{left:point.left,top:point.top}} onMouseDownCapture={onMouseDownCapture} onKeyDownCapture={e=>{if((e.target as HTMLElement).closest('input,select,textarea,[contenteditable=true]'))e.stopPropagation()}} onPointerDown={start} onPointerMove={move} onPointerUp={stop} onPointerCancel={stop} onLostPointerCapture={stop}>{children}</div>;
 return portal?createPortal(placement==='palette'?content:<div className="editor-ux-v2 editor-floating-scope">{content}</div>,document.body):content;
}

/** Scale only rendered content, never resize the author-defined widget or its handles.
 * The frame uses native layout dimensions and reports when it was downscaled.
 * The same component is used for editor, presenter and rehearsal surfaces. */
function WidgetContentFit({children,editor=false,allowScale=true,minScale=.12}:{children:React.ReactNode;editor?:boolean;allowScale?:boolean;minScale?:number}){
 const frame=useRef<HTMLDivElement>(null),body=useRef<HTMLDivElement>(null);
 const [factor,setFactor]=useState(1);
 useEffect(()=>{
  let raf=0;const measure=()=>{cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>{
   const a=frame.current,b=body.current;if(!a||!b)return;
   const availableW=Math.max(1,a.clientWidth),availableH=Math.max(1,a.clientHeight);
   // Scroll bounds are measured before the visual transform and include wrapped text.
   const width=Math.max(b.scrollWidth,b.clientWidth),height=Math.max(b.scrollHeight,b.clientHeight);
   const next=Math.max(minScale,Math.min(1,availableW/Math.max(1,width),availableH/Math.max(1,height)));
   setFactor(previous=>Math.abs(previous-next)<.012?previous:next);
  })};
  if(!allowScale){setFactor(1);return;}
  measure();const resize=new ResizeObserver(measure);
  if(frame.current)resize.observe(frame.current);if(body.current)resize.observe(body.current);
  const changes=new MutationObserver(measure);if(body.current)changes.observe(body.current,{childList:true,characterData:true,subtree:true});
  return()=>{cancelAnimationFrame(raf);resize.disconnect();changes.disconnect()};
 },[children,allowScale,minScale]);
 return <><div className="widget-fit-frame" ref={frame} data-scaled={allowScale&&factor<.985} data-fit-mode={allowScale?'scale':'scroll'}>
  <div className="widget-fit-content" ref={body} style={{transform:allowScale&&factor<.985?`scale(${factor})`:undefined}}>{children}</div>
 </div>{editor&&allowScale&&factor<.985&&<span className="widget-rescale-indicator" role="status" title={`Contenuto ridotto al ${Math.round(factor*100)}% per entrare nel widget`} aria-label={`Contenuto ridotto al ${Math.round(factor*100)}%`}>↘ {Math.round(factor*100)}%</span>}</>;
}

type Session={id:string;owner_id?:string;access_role?:'owner'|'collaborator';title:string;reference_date?:string;join_code:string;join_url:string;status:string;current_activity_id:string|null;expires_at:string;retention_days?:number;allow_anonymous?:boolean;show_results?:boolean;theme?:any};type Activity={id:string;type:'poll'|'quiz'|'timed_quiz'|'slide';title:string;options:{id:string;label:string}[];correct_option_id?:string;status:string;duration_seconds:number|null;opened_at?:string;answer_mode?:'single'|'multiple'|'text'|'file';answer_required?:boolean;page_design?:any};type Snapshot={connected_participants?:number;session:Session;activities:Activity[];results:{activity_id:string;option_id:string;count:number}[];totals:{activity_id:string;count:number}[]};
async function request<T=any>(url:string,method='GET',body?:unknown):Promise<T>{const res=await fetch('/api'+url,{method,credentials:'include',headers:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});if(!res.ok){let info:any={};try{info=await res.json()}catch{}throw new Error(info.error||`HTTP ${res.status}`)}return res.json()}
function useLive(id:string|undefined,update:(s:Snapshot)=>void,onConnection?:(state:'connecting'|'connected'|'disconnected'|'blocked')=>void){
 const updateRef=useRef(update);
 const connectionRef=useRef(onConnection);
 updateRef.current=update;
 connectionRef.current=onConnection;
 useEffect(()=>{
  if(!id)return;
  const transport=createLiveConnection({
   sessionId:id,
   url:`${location.protocol==='https:'?'wss':'ws'}://${location.host}/live?session=${encodeURIComponent(id)}`,
   runtime:{
    createSocket:url=>new WebSocket(url),
    isOnline:()=>navigator.onLine,
    schedule:(callback,ms)=>window.setTimeout(callback,ms),
    cancel:timer=>window.clearTimeout(timer),
   },
   random:()=>Math.random(),
   onSnapshot:s=>updateRef.current(s as Snapshot),
   onConnection:state=>connectionRef.current?.(state),
  });
  const onOnline=()=>transport.online();
  const onOffline=()=>transport.offline();
  window.addEventListener('online',onOnline);
  window.addEventListener('offline',onOffline);
  return()=>{window.removeEventListener('online',onOnline);window.removeEventListener('offline',onOffline);transport.dispose()};
 },[id]);
}
const text={it:{subtitle:'Dai voce a ogni pubblico',login:'Accedi come presentatore',password:'Password',email:'Email',sessions:'Le tue sessioni',newSession:'Nuova sessione',create:'Crea',enter:'Entra',active:'Attiva',draft:'Bozza',closed:'Chiusa',ready:'Pronta',activity:'Attività',vote:'Invia risposta',thankyou:'Risposta registrata',scan:'Scansiona per partecipare',results:'Risultati in tempo reale'},en:{subtitle:'Give every audience a voice',login:'Presenter sign in',password:'Password',email:'Email',sessions:'Your sessions',newSession:'New session',create:'Create',enter:'Join',active:'Active',draft:'Draft',closed:'Closed',ready:'Ready',activity:'Activity',vote:'Submit answer',thankyou:'Answer received',scan:'Scan to participate',results:'Live results'}};
const participantCopy={
 it:{skip:'Vai al contenuto principale',loading:'Caricamento sessione…',unavailable:'Sessione non disponibile',unavailableHelp:'Il codice potrebbe essere errato oppure la sessione è terminata.',retry:'Riprova',another:'Inserisci un altro codice',checking:'Verifica della partecipazione…',joining:'Accesso in corso…',sending:'Invio in corso…',connected:'● Collegamento live attivo',connecting:'Collegamento live in corso…',disconnected:'Collegamento interrotto: riconnessione automatica',blocked:'Accesso live non autorizzato. Ricarica la pagina o chiedi al presentatore.',paused:'Sessione terminata o sospesa',pausedHelp:'Attendi che il presentatore riattivi la sessione.'},
 en:{skip:'Skip to main content',loading:'Loading session…',unavailable:'Session unavailable',unavailableHelp:'The code may be invalid or the session may have ended.',retry:'Retry',another:'Enter another code',checking:'Checking participation…',joining:'Joining…',sending:'Sending…',connected:'● Live connection active',connecting:'Connecting to live session…',disconnected:'Connection interrupted: reconnecting automatically',blocked:'Live access denied. Reload the page or contact the presenter.',paused:'Session ended or paused',pausedHelp:'Wait for the presenter to restart the session.'}
};
function PageTimer({openedAt,duration,label,face='hourglass'}:{openedAt?:string;duration?:number|null;label?:string;face?:WidgetTimerFace}){const [startedAt]=useState(Date.now());const [now,setNow]=useState(Date.now());useEffect(()=>{const id=setInterval(()=>setNow(Date.now()),1000);return ()=>clearInterval(id)},[]);const seconds=Math.max(1,duration||60);const origin=openedAt?new Date(openedAt).getTime():startedAt;const left=Math.max(0,Math.ceil((origin+seconds*1000-now)/1000));const progress=Math.max(0,Math.min(100,((seconds-left)/seconds)*100));const urgent=left<=Math.max(10,Math.floor(seconds*0.15));return <div className={'widget-timer-display'+(urgent?' timer-urgent':'')} data-timer-face={face} style={{'--timer-progress':String(progress)} as React.CSSProperties} role="timer" aria-label={(label||'Tempo rimanente')+': '+Math.floor(left/60)+':'+String(left%60).padStart(2,'0')}><div className="widget-timer-visual" aria-hidden="true"><div className="widget-timer-ring"/><div className="widget-timer-hourglass">{face==='dial'?'◷':face==='digital'?'':'⌛'}</div></div><div className="widget-timer-copy"><span className="widget-timer-label">{label||'Tempo rimanente'}</span><strong className="widget-timer-value">{Math.floor(left/60)}:{String(left%60).padStart(2,'0')}</strong>{!openedAt&&<small className="widget-timer-note">anteprima</small>}</div></div>}
function TimedLeaderboard({sessionId,activityId}:{sessionId:string;activityId:string}){
 const [data,setData]=useState<any>(null);
 const [page,setPage]=useState(1);
 useEffect(()=>{setPage(1);setData(null)},[sessionId,activityId]);
 useEffect(()=>{let alive=true;const load=()=>fetch(`/api/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(activityId)}/timed-leaderboard?page=${page}`,{credentials:'same-origin'}).then(r=>r.ok?r.json():null).then(v=>{if(alive)setData(v)}).catch(()=>{});void load();const timer=setInterval(load,2000);return()=>{alive=false;clearInterval(timer)}},[sessionId,activityId,page]);
 return <section aria-label="Classifica quiz a tempo"><h3>Classifica quiz a tempo</h3>{data?<><p>Risposte corrette: {data.correct} / {data.answers}</p>{data.ranking.length?<ol className="timed-rankings" aria-label="Posizioni a pari merito">{data.ranking.map((r:any,i:number)=><li key={`${r.rank}-${i}`} value={Number(r.rank)}>#{r.rank} · {r.participant_name}: {(Number(r.duration_ms)/1000).toFixed(3)} s</li>)}</ol>:<p>Nessuna risposta corretta in questa pagina.</p>}<nav aria-label="Pagine della classifica"><button type="button" disabled={page<=1} onClick={()=>setPage(v=>Math.max(1,v-1))}>Precedente</button><span> Pagina {data.page} di {data.total_pages} </span><button type="button" disabled={page>=data.total_pages} onClick={()=>setPage(v=>v+1)}>Successiva</button></nav></>:<p>Caricamento classifica…</p>}</section>
}
function WidgetTimedLeaderboard({sessionId,activityId,widget}:{sessionId:string;activityId:string;widget:any}){
 const [page,setPage]=useState(1),[data,setData]=useState<any>(null);
 useEffect(()=>{setPage(1);setData(null)},[sessionId,activityId,widget.id]);
 useEffect(()=>{let live=true;const load=()=>request<any>(`/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(activityId)}/widgets/${encodeURIComponent(widget.id)}/timed-leaderboard?page=${page}`).then(v=>{if(live)setData(v)}).catch(()=>{});void load();const timer=window.setInterval(load,2000);return()=>{live=false;window.clearInterval(timer)}},[sessionId,activityId,widget.id,page]);
 return <section className="panel" aria-label={`Classifica ${widget.label||'quiz a tempo'}`}><h4>{widget.label||'Quiz a tempo'} · Classifica</h4>{data?<><p>{data.correct} corrette / {data.answers} risposte · revisione {data.revision}</p><ol className="timed-rankings" aria-label="Posizioni a pari merito">{data.ranking.map((r:any,i:number)=><li key={`${r.rank}-${i}`} value={Number(r.rank)}>#{r.rank} · {r.participant_name}: {(Number(r.duration_ms)/1000).toFixed(3)} s</li>)}</ol><button disabled={page<=1} onClick={()=>setPage(p=>p-1)}>Precedente</button> Pagina {data.page} / {data.total_pages} <button disabled={page>=data.total_pages} onClick={()=>setPage(p=>p+1)}>Successiva</button></>:<p>Caricamento…</p>}</section>
}
/** Each question widget retains its own revisions and result display choice. */
function WidgetResults({sessionId,activityId,widget,questionId=''}:{sessionId:string;activityId:string;widget:any;questionId?:string}){
 const [data,setData]=useState<any>(null);
 useEffect(()=>{let active=true;const load=()=>request<any>(`/sessions/${encodeURIComponent(sessionId)}/widget-answers/detail?activity_id=${encodeURIComponent(activityId)}&widget_id=${encodeURIComponent(widget.id)}&question_id=${encodeURIComponent(questionId)}`).then(v=>{if(active)setData(v)}).catch(()=>{});void load();const interval=window.setInterval(load,3000);return()=>{active=false;window.clearInterval(interval)}},[sessionId,activityId,widget.id,questionId]);
 const mode=['bars','pie','table','cloud'].includes(widget.resultsView)?widget.resultsView:'bars';
 return <section className="panel" aria-label={`Risultati ${widget.label||'domanda'}`}><h4>{widget.label||'Domanda'} · {mode==='bars'?'Barre':mode==='pie'?'Torta':mode==='cloud'?'Nuvola':'Tabella'}</h4>{!data?<p>Caricamento risultati…</p>:data.revisions?.length?data.revisions.map((rev:any)=><div key={rev.revision}><p>Revisione {rev.revision} · {rev.responses} risposte · {rev.texts||0} testi · {rev.attachments||0} allegati</p>{Object.keys(rev.options||{}).length>0&&<div className={'widget-results-'+mode}>{mode==='pie'&&<div role="img" aria-label="Distribuzione risposte" style={{width:110,height:110,borderRadius:'50%',margin:'12px auto',background:`conic-gradient(${Object.values(rev.options).map((v:any,i:number,all:any[])=>{const start=all.slice(0,i).reduce((a:number,b:any)=>a+Number(b),0)/Math.max(1,all.reduce((a:number,b:any)=>a+Number(b),0))*100;const end=(all.slice(0,i+1).reduce((a:number,b:any)=>a+Number(b),0))/Math.max(1,all.reduce((a:number,b:any)=>a+Number(b),0))*100;return `${['#536fd7','#40a8a0','#e4a84b','#9b71c7','#d76d84'][i%5]} ${start}% ${end}%`}).join(',')})`}}/>}{(mode==='cloud'?rankCloudItems(Object.entries(rev.options),entry=>Number(entry[1]),entry=>entry[0]):Object.entries(rev.options)).map(([key,value],index)=>{const count=Number(value),total=Math.max(1,Object.values(rev.options).reduce((a:number,b:any)=>a+Number(b),0));const label=widget.options?.find((o:any)=>o.id===key)?.label||key;return mode==='cloud'?<span key={key} className="result-cloud-word" style={{fontSize:`${Math.round(14+26*count/total)}px`,color:cloudRankColor(index)}} title={`${label}: ${count}`}><span>{label}</span><small> [{count}]</small></span>:<div key={key}><span>{label}: {count}</span>{mode==='bars'&&<progress max={total} value={count}/>}</div>})}</div>}</div>):<p>Nessuna risposta per questo widget.</p>}</section>
}
/** Preserve editable native PowerPoint picture crops in projection and preview. */
function CroppedImage({src,alt,crop,className}:{src:string;alt:string;crop?:any;className?:string}){
 if(!crop)return <img className={className} src={src} alt={alt}/>;
 const l=crop.left,r=crop.right,t=crop.top,b=crop.bottom;
 if(![l,r,t,b].every(v=>typeof v==='number'&&Number.isFinite(v)&&v>=0&&v<=0.95)||l+r>=0.99||t+b>=0.99)return <img className={className} src={src} alt={alt}/>;
 const width=100/(1-l-r),height=100/(1-t-b);
 return <div className={'pptx-cropped-image '+(className||'')} role="img" aria-label={alt}>
  <img src={src} alt="" aria-hidden="true" draggable={false} style={{position:'absolute',maxWidth:'none',maxHeight:'none',width:width+'%',height:height+'%',left:-l*width+'%',top:-t*height+'%'}}/>
 </div>;
}
/** Render session-owned media rather than a placeholder on the projected canvas. */
/** Renders only plain string fragments and validated inline style values (never raw HTML). */
function WidgetStyledText({text,widget,field}:{text:string;widget:any;field:string}){
 return <>{styledSegments(text,widget.textMarks,field).map((part,i)=><span key={i} style={inlineMarkCss(part.style)}>{part.text}</span>)}</>;
}
/** The exact same chart is used in editor, both rehearsals and presenter projection. */
function LinkedResultChart({widget,widgets,rows,emptyLabel}:{widget:any;widgets:any[];rows?:StatRow[];emptyLabel?:string}){
 const source=linkedStatisticSource(widget,widgets);
 const chart=effectiveResultView(widget,widgets);
 if(!source)return <div className="linked-results linked-results-unconfigured" role="status">{widget.showTitle!==false&&!widget.resultsOnly&&<strong>{widget.label||'Risultati'}</strong>}<small>Collega un widget statistico di questa pagina dalle proprietà.</small></div>;
 const data=rows||sampleStatisticRows(source,1,{},widget.targetQuestionId||'');
 const displayRows=topResultRows(chart==='cloud'?rankCloudItems(data,r=>r.count,r=>r.label):data,widget.resultTopCount);
 const total=data.reduce((n,r)=>n+r.count,0);
 return <section className={'linked-results result-view-'+chart} aria-label={'Risultati '+(source.label||source.kind)}>
  {!widget.resultsOnly&&<>{widget.showTitle!==false&&<strong><WidgetStyledText text={widget.label||'Risultati'} widget={widget} field="label"/></strong>}<small>{source.label||source.kind} · {total} risposte{emptyLabel?' · '+emptyLabel:''}</small></>}
  {chart==='pie'&&total>0&&<div className="linked-results-pie" role="img" aria-label="Distribuzione percentuale" style={{background:`conic-gradient(${data.map((r,i)=>{const from=data.slice(0,i).reduce((n,x)=>n+x.count,0)/total*100;const to=data.slice(0,i+1).reduce((n,x)=>n+x.count,0)/total*100;return `${['#277fd1','#e87947','#51a580','#a477ca','#d35482','#b5a337'][i%6]} ${from}% ${to}%`}).join(',')})`}}/>}
  <div className="linked-results-items">{displayRows.map((r,i)=><div className="linked-results-row" key={r.id} style={chart==='cloud'?{fontSize:`${Math.round(14+24*r.count/Math.max(1,total))}px`,color:cloudRankColor(i)}:undefined}><span className="linked-result-pair"><span className="linked-result-label">{splitResultLabel(r.label).prefix}</span><span className="linked-result-final">{splitResultLabel(r.label).last}<output>{chart==='cloud'?`[${r.count}]`:r.count}</output></span></span>{chart==='bars'&&<div className="linked-results-track"><div style={{width:(total?100*r.count/total:0)+'%'}}/></div>}</div>)}</div>
 </section>;
}
/** Authenticated, source-scoped live results. Never leak statistics to participant projection. */
function PresenterLinkedResult({sessionId,activity,widget,widgets}:{sessionId:string;activity:any;widget:any;widgets:any[]}){
 const source=linkedStatisticSource(widget,widgets);
 const [rows,setRows]=useState<StatRow[]>([]);
 useEffect(()=>{
  if(!source){setRows([]);return;}
  let alive=true;
  const load=async()=>{
   try{
    let next:StatRow[]=[];
    if(source.kind==='question'){
     const data=await request<any>(`/sessions/${encodeURIComponent(sessionId)}/widget-answers/detail?activity_id=${encodeURIComponent(activity.id)}&widget_id=${encodeURIComponent(source.id)}&question_id=${encodeURIComponent(widget.targetQuestionId||'')}`);
     next=rowsFromWidgetAnswerDetail(source,data,widget.targetQuestionId||'');
    }else if(source.kind==='rating'){
     const data=await request<any>(`/sessions/${encodeURIComponent(sessionId)}/ratings/stats`);
     const info=(data.by_widget||[]).find((x:any)=>x.widget_id===source.id);
     next=[{id:'responses',label:'Voti',count:Number(info?.responses||0)},{id:'mean',label:'Media ×10',count:Math.round(Number(info?.mean||0)*10)}];
    }else if(source.kind==='reactions'){
     const data=await request<any>(`/sessions/${encodeURIComponent(sessionId)}/reactions/stats`);
     next=REHEARSAL_EMOJIS.map(emoji=>({id:emoji,label:emoji,count:(data.by_page||[]).filter((x:any)=>x.activity_id===activity.id&&x.emoji===emoji).reduce((n:number,x:any)=>n+Number(x.count),0)}));
    }else if(source.kind==='timed-quiz'){
     const data=await request<any>(`/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(activity.id)}/widgets/${encodeURIComponent(source.id)}/timed-leaderboard?page=1`);
     next=[{id:'correct',label:'Corrette',count:Number(data.correct||0)},{id:'answers',label:'Totale',count:Number(data.answers||0)}];
    }else if(source.kind==='topic-question'){
     // Presenter-authorized, source/page-scoped PostgreSQL total. Never send
     // the free-text questions or their authors to participant projections.
     const data=await request<any>(`/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(activity.id)}/topic-widgets/${encodeURIComponent(source.id)}/stats`);
     next=topicQuestionRows(data.total);
    }
    if(alive)setRows(next);
   }catch{if(alive)setRows([])}
  };
  void load();const timer=window.setInterval(()=>void load(),8000);return()=>{alive=false;window.clearInterval(timer)};
 },[sessionId,activity.id,source?.id,source?.kind,widget.targetQuestionId]);
 return <LinkedResultChart widget={widget} widgets={widgets} rows={rows} emptyLabel="live"/>;
}

/** Read-only authored question controls on the real presenter screen.
 * Reuse the same answer typography, field height and submit sizing as the
 * interactive rehearsal. The screen must never accept or display answers. */
function ProjectedQuestionPart({widget,part,questionId}:{widget:any;part:any;questionId:string}){
 const mode=part.answerMode||(widget.kind==='timed-quiz'?'single':'text');
 const field=(key:string)=>questionId?'question:'+questionId+':'+key:key;
 return <section className="projection-interactive-widget" data-question-id={questionId} data-readonly-preview="true" aria-label={part.label||'Domanda'}>
  {(questionId||widget.showTitle!==false)&&<strong><WidgetStyledText text={part.label||'Domanda'} widget={widget} field={field('label')}/></strong>}
  {part.description&&<p><WidgetStyledText text={part.description} widget={widget} field={field('description')}/></p>}
  {['single','multiple'].includes(mode)?<div role="group" aria-label="Opzioni di risposta">{(part.options||[]).map((option:any)=><label className="widget-answer-option" style={answerOptionStyle(widget.style)} key={option.id}><input type={mode==='multiple'?'checkbox':'radio'} disabled tabIndex={-1} name={'projected-question-'+widget.id+'-'+questionId}/><WidgetStyledText text={option.label} widget={widget} field={field('option:'+option.id)}/></label>)}</div>:
   mode==='file'?<div className="projection-readonly-file" style={answerOptionStyle(widget.style)} aria-label="Risposta con allegato, non disponibile nello schermo presentatore">Allegato da inviare</div>:
   <textarea className="widget-free-answer-field" style={answerInputStyle(widget.style)} readOnly disabled tabIndex={-1} aria-label="Casella di risposta, sola anteprima presentatore" placeholder="Scrivi una risposta…"/>}
  <button type="button" className="outline small projection-readonly-submit" disabled tabIndex={-1} style={answerSubmitStyle(widget.style)}>Invia risposta</button>
 </section>;
}
function SlideCanvasNumber({widgets,pageNumber}:{widgets:any[];pageNumber:number}){
 const item=footerPageNumber(widgets,pageNumber);
 if(!item)return null;
 return <span className="slide-canvas-page-number" data-custom-number={'x' in item?'true':'false'} aria-label={`Numero pagina ${item.text}`}
  style={{fontFamily:item.fontFamily,fontSize:`${(item.fontSize/12.8).toFixed(5)}cqw`,color:item.color,'--footer-pad-right':`${(item.paddingRight/12.8).toFixed(5)}cqw`,'--footer-pad-bottom':`${(item.paddingBottom/12.8).toFixed(5)}cqw`,...('x' in item?{'--footer-number-x':`${item.x}%`,'--footer-number-y':`${item.y}%`,right:'auto',bottom:'auto',transform:'translate(-100%,-100%)'}:{})} as React.CSSProperties}>{item.text}</span>;
}
/** QR widget: the text is fetched from the same server URL policy as the QR image.
 * It intentionally never guesses a join URL from a public join code or internal origin. */
function ParticipantAccessQr({sessionId,joinCode,publicAccess=false,widget}:{sessionId:string;joinCode?:string;publicAccess?:boolean;widget:any}){
 const [url,setUrl]=useState('');
 const [failed,setFailed]=useState(false);
 const accessKey=publicAccess?joinCode:sessionId;
 const base=publicAccess?`/api/join/${encodeURIComponent(joinCode||'')}`:`/api/sessions/${encodeURIComponent(sessionId)}`;
 useEffect(()=>{
  const controller=new AbortController();setUrl('');setFailed(false);
  if(!accessKey){setFailed(true);return()=>controller.abort()}
  const endpoint=publicAccess?`${base}/qr-url`:`${base}/qr?format=json`;
  void fetch(endpoint,{credentials:'same-origin',signal:controller.signal,headers:{Accept:'application/json'}})
   .then(async response=>{if(!response.ok)throw Error('qr_link_unavailable');return response.json()})
   .then(value=>{if(typeof value?.url!=='string'||!/^https?:\/\/[^\s]+$/.test(value.url))throw Error('invalid_qr_url');if(!controller.signal.aborted)setUrl(value.url)})
   .catch(()=>{if(!controller.signal.aborted)setFailed(true)});
  return()=>controller.abort();
 },[base,accessKey,publicAccess,joinCode]);
 const imageSrc=publicAccess?`${base}/qr.svg`:`${base}/qr?format=svg`;
 return <div className="projection-sample-qr participant-access-qr" data-qr-target="participants" aria-label="Accesso dei partecipanti">
  <strong><WidgetStyledText text={widget.label||'Accesso partecipanti'} widget={widget} field="label"/></strong>
  {url?<><img src={imageSrc} alt="Scansiona il QR per accedere come partecipante" loading="lazy"/><span className="participant-qr-url" aria-label="URL di accesso dei partecipanti">{url}</span></>:
   <small className="participant-qr-unavailable" role="status">{failed?'Link partecipanti non disponibile':'Caricamento QR partecipanti…'}</small>}
 </div>;
}
function ProjectionWidgetContent({sessionId,widget,activity,peerWidgets=[],joinCode,usePrivateProfile=false,sessionTitle="",pageNumber=1,masterTitleStyle}:{sessionId:string;widget:any;activity:any;peerWidgets?:any[];joinCode?:string;usePrivateProfile?:boolean;sessionTitle?:string;pageNumber?:number;masterTitleStyle?:any}){
 const kind=widget.kind;
 if(kind==='line'||kind==='shape')return widget.showTitle===false?null:<span className="widget-graphic-label"><WidgetStyledText text={widget.label||(kind==='shape'?'Forma':'Linea')} widget={widget} field="label"/></span>;
 const display=widgetDisplay(widget,{pageTitle:activity?.title,sessionTitle,pageNumber,masterTitleStyle});
 if(kind==='title'&&widget.showTitle===false)return null;
 if(kind==='title')return <h2 className="projection-slide-title"><WidgetStyledText text={display.title} widget={widget} field="label"/></h2>;
 if(kind==='footer')return <div className="projection-slide-footer"><span className="slide-footer-center"><WidgetStyledText text={widget.showTitle===false?'':display.center} widget={widget} field="label"/></span></div>;
 const media=['image','logo','video','pdf'].includes(kind);
 const assetId=typeof widget.assetId==='string'?widget.assetId:'';
 const url=assetId?`/api/sessions/${encodeURIComponent(sessionId)}/assets/${encodeURIComponent(assetId)}`:'';
 if(media){
  if(!url)return <span className="projection-missing-media">{widget.label||kind} · nessun file selezionato</span>;
  if(kind==='image'||kind==='logo')return <CroppedImage className="projection-media" src={url} alt={widget.label||kind} crop={widget.crop}/>;
  if(kind==='video')return <video className="projection-media" src={url} controls playsInline preload="metadata" aria-label={widget.label||'Video'}/>;
  return <div className="projection-document"><a href={url} target="_blank" rel="noopener noreferrer">{widget.label||'Apri PDF'} ↗</a><iframe src={url} title={widget.label||'Documento PDF'} loading="lazy"/></div>;
 }
 if(kind==='participant-count')return <div className="projection-participant-count"><strong><WidgetStyledText text={widget.label||'Partecipanti connessi'} widget={widget} field="label"/></strong><span data-live-participants="true">{(activity as any).connected_participants??0}</span></div>;
 if(kind==='timer')return <div className="projection-sample-timer"><strong><WidgetStyledText text={widget.label||'Timer'} widget={widget} field="label"/></strong><PageTimer openedAt={activity.opened_at} duration={widget.durationSeconds||activity.duration_seconds||60} label="Tempo rimanente" face={widgetTimerFace(widget.style)}/></div>;
 if(kind==='question'||kind==='timed-quiz')return <div className="projection-question-group" aria-label="Gruppo di domande"><ProjectedQuestionPart widget={widget} part={widget} questionId=""/>{(widget.questions||[]).map((q:any)=><ProjectedQuestionPart key={q.id} widget={widget} part={q} questionId={q.id}/>)}{kind==='timed-quiz'&&<PageTimer openedAt={activity.opened_at} duration={widget.durationSeconds||activity.duration_seconds||30} label="Tempo rimanente" face={widgetTimerFace(widget.style)}/>}</div>;
 if(kind==='rating')return <div className="projection-sample-rating">{widget.showTitle!==false&&<strong><WidgetStyledText text={widget.label||'Gradimento'} widget={widget} field="label"/></strong>}<RatingChoices view={widget.style?.ratingView} size={widget.style?.ratingButtonSize} readOnly/></div>;
 if(kind==='reactions')return <div className="projection-sample-reactions">{widget.showTitle!==false&&<strong><WidgetStyledText text={widget.label||'Reazioni'} widget={widget} field="label"/></strong>}<ReactionChoices size={widget.reactionIconSize||32} readOnly/></div>;
 if(kind==='qr')return <ParticipantAccessQr sessionId={sessionId} joinCode={joinCode} widget={widget}/>;
 if(kind==='results-button')return <LinkedResultChart widget={widget} widgets={peerWidgets} rows={linkedStatisticSource(widget,peerWidgets)?sampleStatisticRows(linkedStatisticSource(widget,peerWidgets)!,42):undefined} emptyLabel="simulazione"/>;
 if(kind==='profile')return joinCode&&!usePrivateProfile?<div className="projection-sample-profile"><PresenterProfileWidget code={joinCode} presenterId={widget.presenterId} label={widget.label} description={widget.description} showEmail={widget.showEmail===true}/></div>:<div className="projection-sample-profile"><EditorPresenterProfileWidget sessionId={sessionId} presenterId={widget.presenterId} label={widget.label} description={widget.description} showEmail={widget.showEmail!==false}/></div>;
 if(kind==='topic-question')return <div className="projection-sample-topic" data-readonly-preview="true"><strong><WidgetStyledText text={widget.label||'Domande del pubblico'} widget={widget} field="label"/></strong><textarea className="widget-free-answer-field" style={answerInputStyle(widget.style)} readOnly disabled tabIndex={-1} aria-label="Casella per la domanda, sola anteprima presentatore" placeholder="Scrivi una domanda…"/><button type="button" className="outline small projection-readonly-submit" disabled tabIndex={-1} style={answerSubmitStyle(widget.style)}>Invia domanda</button></div>;
 const textStyle={fontFamily:widget.style?.fontFamily||undefined,fontSize:undefined,color:widget.style?.color||undefined,fontWeight:widget.style?.bold?'bold':undefined,fontStyle:widget.style?.italic?'italic':undefined,textDecoration:[widget.style?.underline?'underline':'',widget.style?.strikethrough?'line-through':''].filter(Boolean).join(' ')||undefined};
 if(kind==='text'||kind==='postit')return <div className="projection-text-widget" style={kind==='postit'?{...textStyle,textAlign:widget.style?.textAlign||undefined,display:widget.style?.verticalAlign?'flex':undefined,flexDirection:widget.style?.verticalAlign?'column':undefined,justifyContent:widget.style?.verticalAlign==='middle'?'center':widget.style?.verticalAlign==='bottom'?'flex-end':undefined,backgroundColor:'transparent'}:{...textStyle,textAlign:widget.style?.textAlign||undefined,display:widget.style?.verticalAlign?'flex':undefined,flexDirection:widget.style?.verticalAlign?'column':undefined,justifyContent:widget.style?.verticalAlign==='middle'?'center':widget.style?.verticalAlign==='bottom'?'flex-end':undefined}}><span style={{whiteSpace:'pre-wrap'}}>{widget.description?.startsWith(widget.label||'')?<WidgetStyledText text={widget.description} widget={widget} field="description"/>:<><WidgetStyledText text={widget.label||''} widget={widget} field="label"/>{widget.description&&<><br/><WidgetStyledText text={widget.description} widget={widget} field="description"/></>}</>}</span></div>;
 return <strong><WidgetStyledText text={widget.label||kind} widget={widget} field="label"/></strong>;
}
function PresenterPageResults({sessionId,activity,snapshot,renderResults}:{sessionId:string;activity:any;snapshot:any;renderResults:(snapshot:any,activity:any,mode?:string)=>React.ReactNode}){
 const [visible,setVisible]=useState(false);
 const [canControlTimer,setCanControlTimer]=useState(false);
 const [restartBusy,setRestartBusy]=useState(false);
 const [restartMessage,setRestartMessage]=useState('');
 useEffect(()=>{let alive=true;setCanControlTimer(false);void request(`/sessions/${encodeURIComponent(sessionId)}`).then(()=>{if(alive)setCanControlTimer(true)}).catch(()=>{});return()=>{alive=false}},[sessionId]);
 const restart=async()=>{
  if(restartBusy)return;
  const clearResponses=window.confirm('Riavviare il timer E AZZERARE le risposte precedenti?\nOK: azzera risposte.\nAnnulla: scegli se mantenerle.');
  if(!clearResponses&&!window.confirm('Riavviare il timer MANTENENDO le risposte precedenti?'))return;
  setRestartBusy(true);setRestartMessage('');
  try{await request(`/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(activity.id)}/restart-timer`,'POST',{confirmation:'RESTART_PAGE_TIMER',clear_responses:clearResponses});setRestartMessage(clearResponses?'Timer riavviato; risposte azzerate':'Timer riavviato; risposte mantenute')}
  catch(e){setRestartMessage(e instanceof Error?e.message:String(e))}finally{setRestartBusy(false)}
 };
 useEffect(()=>setVisible(false),[activity.id]);
 activity={...activity,connected_participants:snapshot.connected_participants};
 const widgets=resolveSlideMasterWidgets(activity.page_design?.widgets||[],snapshot.session.theme?.master?.widgets);
 const control=widgets.find((w:any)=>w.kind==='results-button');
 return <>
 <div className="projection-page-content" aria-label="Pagina del presentatore" style={activity.page_design?.backgroundAssetId?{backgroundImage:`url(/api/sessions/${sessionId}/assets/${activity.page_design.backgroundAssetId})`,backgroundSize:"cover",backgroundPosition:"center"}:activity.page_design?.backgroundUrl?{backgroundImage:`url(${activity.page_design.backgroundUrl})`,backgroundSize:"cover",backgroundPosition:"center"}:activity.page_design?.backgroundColor?{backgroundColor:activity.page_design.backgroundColor}:undefined}>
 {widgets.map((w:any)=><div key={w.id} className="projection-widget" data-widget-kind={w.kind} data-vertical-align={w.style?.verticalAlign||'top'} data-show-title={w.showTitle!==false} data-footer-separator={w.kind==='footer'?String(w.footerSeparator!==false):undefined} {...widgetArtData(w.style)} style={{...(w.kind==='footer'?{'--footer-divider-color':w.footerSeparatorColor||'#9ca3af'} as React.CSSProperties:{}),...(w.position?widgetGeometryStyle(w.position):{}),...widgetAppearanceStyle(w.style,w.style?.fillImageAssetId?`/api/sessions/${sessionId}/assets/${w.style.fillImageAssetId}`:undefined),...widgetTypographyStyle(w.kind==='title'?widgetDisplay(w,{pageTitle:activity.title,masterTitleStyle:snapshot.session.theme?.master?.titleStyle}).style:w.style)}}>{w.kind!=='shape'&&<WidgetShapeOutline style={w.style}/> }<WidgetGraphic kind={w.kind} style={w.style}/>{w.kind==='timer'&&canControlTimer&&<div className="presenter-timer-controls"><button type="button" disabled={restartBusy} onClick={()=>void restart()} title="Riavvia manualmente il countdown e consenti nuove risposte"><Timer size={17}/> Riavvia timer</button>{restartMessage&&<small role="status">{restartMessage}</small>}</div>}<WidgetContentFit allowScale={w.kind!=='results-button'||w.autoFit!==false} minScale={w.kind==='results-button'?.04:.12}>{w.kind==='results-button'?<PresenterLinkedResult sessionId={sessionId} activity={activity} widget={w} widgets={widgets}/>:<ProjectionWidgetContent sessionId={sessionId} widget={w} activity={activity} joinCode={snapshot.session.join_code} sessionTitle={snapshot.session.title} pageNumber={slidePageNumber(snapshot.activities,activity.id)} masterTitleStyle={snapshot.session.theme?.master?.titleStyle}/>}</WidgetContentFit></div>)}
  <SlideCanvasNumber widgets={widgets} pageNumber={slidePageNumber(snapshot.activities,activity.id)}/>
 </div>
 {<button type="button" className="primary presenter-results-button" onClick={()=>setVisible(v=>!v)} aria-expanded={visible} aria-controls="presenter-page-results">Risultati</button>}
 {visible&&<div id="presenter-page-results" role="region" aria-label="Risultati della pagina" className="presenter-page-results" style={activity.result_design?.backgroundAssetId?{backgroundImage:`url(/api/sessions/${sessionId}/assets/${activity.result_design.backgroundAssetId})`,backgroundSize:"cover",backgroundPosition:"center"}:activity.result_design?.backgroundColor?{backgroundColor:activity.result_design.backgroundColor}:undefined}>{renderResults(snapshot,activity,control?effectiveResultView(control,widgets):'bars')}{activity.type==='timed_quiz'&&<TimedLeaderboard sessionId={sessionId} activityId={activity.id}/>}{widgets.filter((w:any)=>w.kind==='timed-quiz').map((w:any)=><WidgetTimedLeaderboard key={w.id} sessionId={sessionId} activityId={activity.id} widget={w}/>)}{widgets.filter((w:any)=>w.kind==='question').flatMap((w:any)=>[<WidgetResults key={w.id} sessionId={sessionId} activityId={activity.id} widget={w}/>,...(w.questions||[]).map((q:any)=><WidgetResults key={w.id+':'+q.id} sessionId={sessionId} activityId={activity.id} questionId={q.id} widget={{...q,id:w.id,resultsView:w.resultsView}}/>)])}{widgets.filter((w:any)=>w.kind==='topic-question').map((w:any)=><TopicPresenterList key={w.id} sessionId={sessionId} activityId={activity.id} widget={w}/>)}</div>}
 </>;
}
function AudienceExtensions({joinCode,activityId,joined}:{joinCode:string;activityId:string;joined:boolean}){
 const [word,setWord]=useState(''),[question,setQuestion]=useState('');
 const [questions,setQuestions]=useState<any[]>([]),[status,setStatus]=useState('');
 const [busy,setBusy]=useState(false);
 const prefix=`/join/${encodeURIComponent(joinCode)}/activities/${encodeURIComponent(activityId)}`;
 useEffect(()=>{setWord('');setQuestion('');setStatus('');setQuestions([])},[joinCode,activityId]);
 useEffect(()=>{let active=true;const refresh=()=>request<any[]>(`${prefix}/questions`).then(rows=>{if(active)setQuestions(rows)}).catch(()=>{if(active)setStatus(v=>v||'Aggiornamento delle domande non disponibile')});void refresh();const timer=window.setInterval(refresh,6000);return()=>{active=false;window.clearInterval(timer)}},[prefix]);
 async function submit(endpoint:string,body:unknown,clear:()=>void){
  if(busy)return;setBusy(true);setStatus('Invio in corso…');
  try{
   const result=await request<any>(`${prefix}/${endpoint}`,'POST',body);
   clear();
   setStatus(endpoint==='words'?(result.already_submitted?'Hai già inviato una parola per questa pagina':'Parola registrata'):endpoint==='questions'?`Domanda inviata per approvazione · ${result.remaining} disponibili`:result.already_voted?'Voto già registrato':'Voto registrato');
   void request<any[]>(`${prefix}/questions`).then(setQuestions).catch(()=>{});
  }catch(e){setStatus(e instanceof Error?e.message:String(e))}finally{setBusy(false)}
 }
 return <section className="panel" aria-label="Strumenti interattivi"><h3>Nuvola di parole e domande dal pubblico</h3><p className="muted tiny">Una parola per partecipante, fino a tre domande per pagina. Le domande diventano pubbliche solo dopo approvazione.</p>
 <label>Una parola per descrivere la pagina<input maxLength={48} value={word} disabled={busy} onChange={e=>setWord(e.target.value)}/></label>
 <button type="button" className="outline small" disabled={!joined||busy||!word.trim()} onClick={()=>void submit('words',{word},()=>setWord(''))}>Invia parola</button>
 <label>La tua domanda<textarea maxLength={500} rows={3} value={question} disabled={busy} onChange={e=>setQuestion(e.target.value)}/></label>
 <button type="button" className="outline small" disabled={!joined||busy||question.trim().length<5} onClick={()=>void submit('questions',{body:question},()=>setQuestion(''))}>Invia per moderazione</button>
 <div role="status" aria-live="polite">{status}</div>
 <button type="button" className="outline small" disabled={busy} onClick={()=>void request<any[]>(`${prefix}/questions`).then(setQuestions).catch(e=>setStatus(String(e)))}>Aggiorna domande approvate</button>
 {questions.length===0&&<p className="muted">Nessuna domanda approvata.</p>}
 {questions.map(q=><div key={q.id} className="activity-row"><span>{q.body} · {q.votes} voti</span><button type="button" className="outline small" disabled={!joined||busy} onClick={()=>void submit(`questions/${q.id}/upvote`,{},()=>{})}>▲ Vota</button></div>)}
 </section>
}
function TopicQuestionWidget({code,activityId,widget}:{code:string;activityId:string;widget:any}){
 const [body,setBody]=useState('');const [message,setMessage]=useState('');
 async function submit(){try{await request(`/join/${encodeURIComponent(code)}/activities/${encodeURIComponent(activityId)}/topic-widgets/${encodeURIComponent(widget.id)}/questions`,'POST',{body});setBody('');setMessage('Domanda inviata al presentatore')}catch(e){setMessage(String(e))}}
 return <section className="widget-question" aria-label={widget.label||'Domande sul tema'}><strong>{widget.label||'Domande sul tema'}</strong><textarea className="widget-free-answer-field" style={answerInputStyle(widget.style)} maxLength={2000} rows={3} value={body} placeholder="Scrivi una domanda su questo argomento" onChange={e=>setBody(e.target.value)}/><button type="button" style={answerSubmitStyle(widget.style)} disabled={body.trim().length<5} onClick={()=>void submit()}>Invia domanda</button><small aria-live="polite">{message}</small></section>
}
function TopicPresenterList({sessionId,activityId,widget}:{sessionId:string;activityId:string;widget:any}){
 const [page,setPage]=useState(1),[data,setData]=useState<{total:number;items:any[]}>({total:0,items:[]});
 useEffect(()=>{let mounted=true;const refresh=()=>{void request<any>(`/sessions/${sessionId}/activities/${activityId}/topic-widgets/${encodeURIComponent(widget.id)}/questions?page=${page}`).then(v=>{if(mounted)setData(v)}).catch(()=>{})};refresh();const timer=window.setInterval(refresh,5000);return()=>{mounted=false;window.clearInterval(timer)}},[sessionId,activityId,widget.id,page]);
 return <section className="panel"><h4>{widget.label||'Domande per argomento'}</h4><p>{data.total} domande · massimo 10 per pagina</p>{data.items.map(q=><div className="activity-row" key={q.id}><span>{q.body}</span><small>{q.participant_name||'Anonimo'}</small></div>)}<button disabled={page<=1} onClick={()=>setPage(v=>v-1)}>Precedente</button><span> Pagina {page} </span><button disabled={page*10>=data.total} onClick={()=>setPage(v=>v+1)}>Successiva</button></section>
}
type ModerationQueue={page:number;page_size:number;total:number;total_pages:number;counts:{pending:number;approved:number;rejected:number};items:{id:string;body:string;status:'pending'|'approved'|'rejected';votes:number;created_at:string}[]};
function PresenterAudienceExtensions({sessionId,activityId}:{sessionId:string;activityId:string}){
 const [filter,setFilter]=useState<'pending'|'approved'|'rejected'|'all'>('pending'),[page,setPage]=useState(1);
 const [queue,setQueue]=useState<ModerationQueue|null>(null),[words,setWords]=useState<any[]>([]);
 const [error,setError]=useState(''),[busy,setBusy]=useState<string|null>(null);
 const [selectedQuestions,setSelectedQuestions]=useState<string[]>([]);
 const prefix=`/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(activityId)}`;
 useEffect(()=>{setPage(1);setFilter('pending');setQueue(null);setWords([]);setError('')},[sessionId,activityId]);
 useEffect(()=>{setSelectedQuestions([]);setQueue(null)},[prefix,filter,page]);
 async function refresh(){
  const [q,w]=await Promise.all([request<ModerationQueue>(`${prefix}/questions/queue?status=${filter}&page=${page}`),request<any[]>(`${prefix}/words`)]);
  setQueue(q);setWords(w);setError('');
 }
 useEffect(()=>{let active=true;const load=async()=>{try{
   const [q,w]=await Promise.all([request<ModerationQueue>(`${prefix}/questions/queue?status=${filter}&page=${page}`),request<any[]>(`${prefix}/words`)]);
   if(active){setQueue(q);setWords(w);setError('');if(q.page>q.total_pages)setPage(q.total_pages)}
  }catch(e){if(active)setError(e instanceof Error?e.message:String(e))}};
  void load();const timer=window.setInterval(load,6000);return()=>{active=false;window.clearInterval(timer)}
 },[prefix,filter,page]);
 async function bulkModerate(status:'approved'|'rejected'){
  if(busy||selectedQuestions.length===0)return;setBusy('bulk');setError('');
  try{await request(`${prefix}/questions/bulk`,'PATCH',{status,ids:selectedQuestions});setSelectedQuestions([]);await refresh()}
  catch(e){setError(e instanceof Error?e.message:String(e))}finally{setBusy(null)}
 }
 async function moderate(id:string,status:'approved'|'rejected'){
  if(busy)return;setBusy(id);setError('');
  try{await request(`${prefix}/questions/${encodeURIComponent(id)}`,'PATCH',{status});await refresh();if(queue?.items.length===1&&page>1&&filter!==status)setPage(p=>p-1)}
  catch(e){setError(e instanceof Error?e.message:String(e))}finally{setBusy(null)}
 }
 const counts=queue?.counts;
 return <section className="panel" aria-label="Moderazione domande del pubblico"><h3>Moderazione Q&A e nuvola di parole</h3>
 <button type="button" className="outline small" onClick={()=>void refresh().catch(e=>setError(String(e)))}>Aggiorna</button>
 <p role="status" aria-live="polite">{error}</p>
 <h4>Parole più frequenti</h4><div className="word-cloud" aria-label="Nuvola di parole">{words.length?rankCloudItems(words,w=>w.count,w=>w.word).map((w,i)=><span key={w.word} style={{fontSize:`${Math.min(30,14+w.count*2)}px`,marginRight:12,color:cloudRankColor(i)}}>{w.word} [{w.count}]</span>):<p className="muted">Ancora nessuna parola.</p>}</div>
 <h4>Domande del pubblico</h4>
 <div className="downloads" role="group" aria-label="Moderazione multipla">
 <button type="button" className="outline small" disabled={!queue?.items.length||!!busy} onClick={()=>setSelectedQuestions(queue?.items.map(q=>q.id)||[])}>Seleziona pagina</button>
 <button type="button" className="outline small" disabled={!selectedQuestions.length||!!busy} onClick={()=>setSelectedQuestions([])}>Deseleziona</button>
 <button type="button" className="outline small" disabled={!selectedQuestions.length||!!busy} onClick={()=>void bulkModerate('approved')}>Approva selezionate ({selectedQuestions.length})</button>
 <button type="button" className="outline small" disabled={!selectedQuestions.length||!!busy} onClick={()=>void bulkModerate('rejected')}>Rifiuta selezionate ({selectedQuestions.length})</button>
 </div>
 {counts&&<p className="muted" aria-live="polite">In attesa: {counts.pending} · Approvate: {counts.approved} · Rifiutate: {counts.rejected}</p>}
 <label>Filtro domande<select value={filter} onChange={e=>{setPage(1);setFilter(e.target.value as typeof filter)}}><option value="pending">In attesa</option><option value="approved">Approvate</option><option value="rejected">Rifiutate</option><option value="all">Tutte</option></select></label>
 {queue?.items.length===0&&<p className="muted">Nessuna domanda in questa categoria.</p>}
 {queue?.items.map(q=><div className="activity-row" key={q.id}><label className="small"><input type="checkbox" aria-label={`Seleziona domanda ${q.body}`} checked={selectedQuestions.includes(q.id)} disabled={!!busy} onChange={e=>setSelectedQuestions(old=>e.target.checked?[...old,q.id]:old.filter(id=>id!==q.id))}/>{q.body} · {q.status} · {q.votes} voti</label><div className="row-actions">
 {q.status!=='approved'&&<button type="button" className="outline small" disabled={!!busy} onClick={()=>void moderate(q.id,'approved')}>Approva</button>}
 {q.status!=='rejected'&&<button type="button" className="outline small" disabled={!!busy} onClick={()=>void moderate(q.id,'rejected')}>Rifiuta</button>}
 </div></div>)}
 {queue&&<nav aria-label="Pagine della moderazione"><button type="button" className="outline small" disabled={page<=1} onClick={()=>setPage(p=>Math.max(1,p-1))}>Precedente</button><span> Pagina {page} di {queue.total_pages} · {queue.total} domande </span><button type="button" className="outline small" disabled={page>=queue.total_pages} onClick={()=>setPage(p=>p+1)}>Successiva</button></nav>}
 </section>
}
function PresenterProfileWidget({code,presenterId,label,showEmail=false,description}:{code:string;presenterId?:string;label?:string;showEmail?:boolean;description?:string}){const [profiles,setProfiles]=useState<any[]>([]);useEffect(()=>{fetch(`/api/join/${encodeURIComponent(code)}/presenter-profiles`).then(r=>r.ok?r.json():[]).then(setProfiles).catch(()=>setProfiles([]))},[code]);const chosen=presenterId?profiles.filter(p=>p.id===presenterId):profiles.slice(0,1);return <div className="page-widget" data-widget-kind="profile">{chosen.length===0&&<strong>{label||'Presentatore'}</strong>}{chosen.map(p=><div key={p.id}>{p.photo_url&&<img src={p.photo_url} alt="Foto presentatore" style={{maxWidth:96,maxHeight:96,borderRadius:'50%'}}/>}<p>{p.name}</p>{showEmail&&p.email&&<a href={'mailto:'+p.email}>{p.email}</a>}</div>)}{description?.trim()&&<p className="presenter-profile-custom-text">{description}</p>}</div>}
/** Authenticated editor preview may render profile data before the public page is published. */
function EditorPresenterProfileWidget({sessionId,presenterId,label,showEmail=false,description}:{sessionId:string;presenterId?:string;label?:string;showEmail?:boolean;description?:string}){
 const [profiles,setProfiles]=useState<any[]>([]);
 useEffect(()=>{let active=true;request<any[]>(`/sessions/${encodeURIComponent(sessionId)}/presenter-profiles`).then(data=>{if(active)setProfiles(data)}).catch(()=>{if(active)setProfiles([])});return()=>{active=false}},[sessionId]);
 const chosen=presenterId?profiles.filter(p=>p.id===presenterId):profiles.filter(p=>p.is_owner).slice(0,1);
 return <div className="page-widget" data-widget-kind="profile">{chosen.length===0&&<strong>{label||'Presentatore'}</strong>}{chosen.map(p=><div key={p.id}>{p.profile_photo_url&&<img src={p.profile_photo_url} alt="Foto presentatore"/>}<p>{p.name}</p>{showEmail&&p.email&&<a href={'mailto:'+p.email}>{p.email}</a>}</div>)}{description?.trim()&&<p className="presenter-profile-custom-text">{description}</p>}</div>;
}
function QuestionWidget({code,activityId,widget}:{code:string;activityId:string;widget:any}){
 return <div className="widget-question-group" aria-label={widget.label||'Gruppo di domande'}>
  <QuestionWidgetSingle key={widget.id+':primary'} code={code} activityId={activityId} widget={widget} questionId="" marks={widget}/>
  {(widget.questions||[]).map((question:any)=><QuestionWidgetSingle key={widget.id+':'+question.id} code={code} activityId={activityId} widget={{...question,id:widget.id,kind:widget.kind,durationSeconds:widget.durationSeconds,allowAnswerChange:question.allowAnswerChange===true}} questionId={question.id} marks={widget}/>)}
 </div>;
}
function QuestionWidgetSingle({code,activityId,widget,questionId,marks}:{code:string;activityId:string;widget:any;questionId:string;marks:any}){
 const [choice,setChoice]=useState('');const [many,setMany]=useState<string[]>([]);const [body,setBody]=useState('');const [attachment,setAttachment]=useState('');const [status,setStatus]=useState('');const [busy,setBusy]=useState(false),[submitted,setSubmitted]=useState(false);
 useEffect(()=>{setChoice('');setMany([]);setBody('');setAttachment('');setStatus('');setBusy(false);setSubmitted(false)},[activityId,widget.id,questionId]);
 const mode=widget.kind==='timed-quiz'?(widget.answerMode==='multiple'?'multiple':'single'):(widget.answerMode||'text');const options=widget.options||[];
 const uploadParticipantFile=async(file:File|undefined)=>{if(!file)return;setStatus('Caricamento...');try{const response=await fetch(`/api/join/${encodeURIComponent(code)}/activities/${encodeURIComponent(activityId)}/widgets/${encodeURIComponent(widget.id)}/upload?question_id=${encodeURIComponent(questionId)}`,{method:'POST',credentials:'include',headers:{'Content-Type':file.type},body:file});const result=await response.json();if(!response.ok)throw Error(result.error||'Upload non riuscito');setAttachment(result.asset_id);setStatus('Allegato caricato, puoi inviare la risposta')}catch(e){setStatus(e instanceof Error?e.message:String(e))}};
 const submit=async()=>{
  if(busy||(submitted&&widget.allowAnswerChange!==true))return;
  setBusy(true);setStatus('Invio in corso…');
  try{
   const payload={...(mode==='single'?{option_id:choice}:mode==='multiple'?{option_ids:many}:mode==='file'?{asset_id:attachment}:{text:body}),question_id:questionId};
   const r=await request<any>(`/join/${encodeURIComponent(code)}/activities/${encodeURIComponent(activityId)}/widgets/${encodeURIComponent(widget.id)}/respond`,'POST',payload);
   setSubmitted(true);setStatus(r.already_submitted?'Risposta già registrata':r.changed?'Risposta aggiornata':'Risposta registrata');
  }catch(e){
   const message=e instanceof Error?e.message:String(e);
   setStatus(message.includes('timer_elapsed')?'Tempo scaduto: la risposta non è stata registrata':message);
  }finally{setBusy(false)}
 };
 return <section className="widget-question" aria-label={widget.label||'Domanda aggiuntiva'}><strong><WidgetStyledText text={widget.label||'Domanda'} widget={marks} field={questionId?`question:${questionId}:label`:"label"}/></strong>{widget.description&&<p><WidgetStyledText text={widget.description} widget={marks} field={questionId?`question:${questionId}:description`:'description'}/></p>}{(mode==='single'||mode==='multiple')?options.map((o:any)=><label className="widget-answer-option" style={answerOptionStyle(marks.style)} key={o.id}><input type={mode==='single'?'radio':'checkbox'} disabled={busy||(submitted&&widget.allowAnswerChange!==true)} name={`widget-${widget.id}-${questionId}`} checked={mode==='single'?choice===o.id:many.includes(o.id)} onChange={()=>mode==='single'?setChoice(o.id):setMany(old=>old.includes(o.id)?old.filter(x=>x!==o.id):[...old,o.id])}/><WidgetStyledText text={o.label} widget={marks} field={questionId?`question:${questionId}:option:${o.id}`:'option:'+o.id}/></label>):mode==='text'?<textarea className="widget-free-answer-field" style={answerInputStyle(marks.style)} rows={3} maxLength={5000} disabled={busy||(submitted&&widget.allowAnswerChange!==true)} value={body} onChange={e=>setBody(e.target.value)}/>:<label>Carica un allegato (PNG, JPEG, GIF, WebP, PDF, MP4 o WebM)<input type="file" accept="image/png,image/jpeg,image/gif,image/webp,application/pdf,video/mp4,video/webm" disabled={busy||(submitted&&widget.allowAnswerChange!==true)} onChange={e=>{void uploadParticipantFile(e.target.files?.[0])}}/>{attachment&&<small>Allegato pronto: {attachment}</small>}</label>}<button type="button" className="outline small" style={answerSubmitStyle(marks.style)} onClick={()=>void submit()} disabled={busy||(submitted&&widget.allowAnswerChange!==true)||(mode==='single'&&!choice)||(mode==='multiple'&&many.length===0)||(mode==='text'&&!body.trim())||(mode==='file'&&!attachment)} aria-busy={busy}>Invia risposta al widget</button><p role="status" aria-live="polite">{status}</p></section>
}

type RehearsalMode='presenter'|'participant'|'both'|'mobile';
/** Local interaction rehearsal: no mutation endpoints, and presenter/participant share one draft and response state. */
/** A broken or legacy widget must never trap the presenter in an unusable editor. */
class RehearsalErrorBoundary extends React.Component<{onClose:()=>void;children:React.ReactNode},{failed:boolean}> {
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true};}
 componentDidCatch(error:Error){console.error('Rehearsal render failed:',error.name);}
 render(){return this.state.failed?createPortal(<div className="rehearsal-backdrop" role="alertdialog" aria-modal="true" aria-label="Errore anteprima"><div className="rehearsal-shell rehearsal-error-fallback"><p>Impossibile visualizzare questa anteprima. La bozza rimane disponibile nell'editor.</p><button type="button" autoFocus onClick={this.props.onClose}>Chiudi anteprima e torna all'editor</button></div></div>,document.body):this.props.children;}
}
/** Phone-specific 390px layout with independent widget positions and background.
 * The frame scrolls vertically instead of shrinking all typography to 30%. */
function PhoneRehearsalStage({children,height}:{children:React.ReactNode;height:number}){
 const viewport=useRef<HTMLDivElement>(null);
 const [scale,setScale]=useState(()=>phoneStageScale(372));
 useEffect(()=>{
  const measure=()=>{if(viewport.current)setScale(phoneStageScale(viewport.current.clientWidth))};
  measure();const observer=new ResizeObserver(measure);
  if(viewport.current)observer.observe(viewport.current);
  return()=>observer.disconnect();
 },[]);
 return <div className="rehearsal-phone-frame" ref={viewport} aria-label="Schermo smartphone partecipante 390 pixel">
   <div className="rehearsal-phone-stage-sizer" style={{height:height*scale}}>
    <div className="rehearsal-phone-stage" style={{width:MOBILE_PAGE_WIDTH,height,transform:`scale(${scale})`}}>{children}</div>
   </div>
  </div>;
}
function SessionRehearsal({snapshot,onClose,initialPageId,initialMode='participant'}:{snapshot:Snapshot;onClose:()=>void;initialPageId?:string;initialMode?:RehearsalMode}){
 const [mode,setMode]=useState<RehearsalMode>(initialMode);
 const [participantDevice,setParticipantDevice]=useState<'desktop'|'phone'>('desktop');
 useEffect(()=>{setMode(initialMode)},[initialMode]);
 const [page,setPage]=useState(()=>Math.max(0,snapshot.activities.findIndex(a=>a.id===initialPageId)));
 const [responses,setResponses]=useState<Record<string,string|string[]>>({});
 // Draft edits never change presenter statistics until an explicit local submit.
 const [submittedAnswers,setSubmittedAnswers]=useState<Record<string,string|string[]>>({});
 // Presenter controls never reflect the participant's draft or submitted choices.
 const [demoResultsVisible,setDemoResultsVisible]=useState(false);
 // Page-scoped local counts: rehearsal is intentionally disconnected from POST APIs.
 const [topicSubmissions,setTopicSubmissions]=useState<Record<string,number>>({});
 const [seed,setSeed]=useState(()=>Math.floor(Math.random()*0x7fffffff));
 const [pageStartedAt,setPageStartedAt]=useState(()=>Date.now());
 const [rehearsalNow,setRehearsalNow]=useState(()=>Date.now());
 const activities=snapshot.activities||[];const activity=activities[page] as any;
 // One clock for both panes. It resets on page navigation or explicit restart,
 // not when changing from presenter to participant or to side-by-side.
 useEffect(()=>{const instant=Date.now();setPageStartedAt(instant);setRehearsalNow(instant);setDemoResultsVisible(false)},[activity?.id,seed]);
 useEffect(()=>{const timer=window.setInterval(()=>setRehearsalNow(Date.now()),1000);return()=>window.clearInterval(timer)},[]);
 const widgets=resolveSlideMasterWidgets((activity?.page_design?.widgets||[]) as any[],snapshot.session.theme?.master?.widgets);
 const pageExpired=pageInteractionExpired(widgets,pageStartedAt,rehearsalNow);
 const [fullScreen,setFullScreen]=useState(false);const shellRef=useRef<HTMLDivElement>(null);
 const closeRef=useRef(onClose);closeRef.current=onClose;
 useEffect(()=>{const root=shellRef.current;return root?activateRehearsalDialog(root,()=>closeRef.current()):undefined},[]);
 useEffect(()=>{const handler=()=>setFullScreen(!!document.fullscreenElement);document.addEventListener('fullscreenchange',handler);return()=>document.removeEventListener('fullscreenchange',handler)},[]);
 const choose=(id:string,value:string,multiple=false)=>setResponses(previous=>{
  const before=previous[id];const list=Array.isArray(before)?before:[];
  return {...previous,[id]:multiple?(list.includes(value)?list.filter(item=>item!==value):[...list,value]):value};
 });
 const submitDemoAnswer=(id:string,mode:string,timedSeconds?:number)=>{
  const draft=responses[id];
  // Guard in the callback too, not only disabled buttons: a queued click at
  // the deadline must not submit a late answer.
  if(pageInteractionExpired(widgets,pageStartedAt,Date.now())||(timedSeconds!==undefined&&rehearsalExpired(pageStartedAt,timedSeconds,Date.now())))return;
  setSubmittedAnswers(previous=>{
   const source=widgets.find(w=>id===w.id||id.startsWith(w.id+':'));
   const questionId=id===source?.id?'':id.slice((source?.id||'').length+1);
   const part=questionId?source?.questions?.find((q:any)=>q.id===questionId):source;
   if(part?.allowAnswerChange===true&&canSubmitRehearsalAnswer(mode,draft))return {...previous,[id]:Array.isArray(draft)?[...draft]:draft!};
   return commitRehearsalAnswer(previous,id,draft,mode);
  });
 };
 const submitDemoDirect=(widgetId:string,kind:'reactions'|'rating',value:string)=>{
  if(pageInteractionExpired(widgets,pageStartedAt,Date.now()))return;
  setSubmittedAnswers(previous=>{
   if(kind==='reactions'){
    const pageKey=REHEARSAL_REACTION_PREFIX+activity.id;
    return changeRehearsalReaction(previous,pageKey,widgetId,value);
   }
   return changeRehearsalRating(previous,widgetId,value);
  });
 };
 const submitDemoTopic=(widgetId:string)=>{
  const draft=responses[widgetId];const clean=typeof draft==='string'?draft.trim():'';
  const key=activity?.id+':'+widgetId;
  if(pageInteractionExpired(widgets,pageStartedAt,Date.now())||clean.length<5||clean.length>2000||(topicSubmissions[key]||0)>=10)return;
  setTopicSubmissions(previous=>(previous[key]||0)>=10?previous:{...previous,[key]:(previous[key]||0)+1});
  setResponses(previous=>({...previous,[widgetId]:''}));
 };
 const renderSlide=(viewer:'presenter'|'participant',mobile=false)=><section className="rehearsal-slide" aria-label={viewer==='presenter'?'Pagina del presentatore':'Pagina del partecipante'} style={mobile?{backgroundImage:activity?.page_design?.mobile?.backgroundAssetId?`url(/api/sessions/${snapshot.session.id}/assets/${activity.page_design.mobile.backgroundAssetId})`:'none',backgroundColor:activity?.page_design?.mobile?.backgroundColor||'#ffffff',backgroundSize:'cover',backgroundPosition:'center'}:activity?.page_design?.backgroundAssetId?{backgroundImage:`url(/api/sessions/${snapshot.session.id}/assets/${activity.page_design.backgroundAssetId})`,backgroundSize:'cover',backgroundPosition:'center'}:activity?.page_design?.backgroundUrl?{backgroundImage:`url(${activity.page_design.backgroundUrl})`,backgroundSize:'cover',backgroundPosition:'center'}:activity?.page_design?.backgroundColor?{backgroundColor:activity.page_design.backgroundColor}:undefined}>
  {!widgets.length&&<h2 className="rehearsal-empty-title">{activity?.page_design?.header||activity?.title}</h2>}
  {pageExpired&&<div className="rehearsal-page-expired" role="status">Tempo scaduto · interazioni della pagina disabilitate</div>}
   <div className="rehearsal-widgets">{(mobile?mobilePageWidgets(widgets,activity?.page_design?.mobile):widgets).filter(w=>viewer==='presenter'||!['results-button','participant-count'].includes(w.kind)).map(w=>{
   const answer=viewer==='participant'?responses[w.id]:undefined;const isMulti=w.answerMode==='multiple';
   const style={...{'--stage-x':`${w.position?.x??0}%`,'--stage-y':`${w.position?.y??0}%`,'--stage-width':`${w.position?.width??45}%`,'--stage-height':`${w.position?.height??24}%`},left:`${w.position?.x??0}%`,top:`${w.position?.y??0}%`,width:`${w.position?.width??45}%`,height:`${w.position?.height??24}%`,transform:`rotate(${w.position?.rotation||0}deg)`,...widgetAppearanceStyle(w.style,w.style?.fillImageAssetId?`/api/sessions/${snapshot.session.id}/assets/${w.style.fillImageAssetId}`:undefined),...widgetTypographyStyle(w.kind==='title'?widgetDisplay(w,{pageTitle:activity.title,masterTitleStyle:snapshot.session.theme?.master?.titleStyle}).style:w.style),'--authored-widget-font-size':widgetTypographyStyle(w.kind==='title'?widgetDisplay(w,{pageTitle:activity.title,masterTitleStyle:snapshot.session.theme?.master?.titleStyle}).style:w.style).fontSize,...(mobile?{fontSize:`${w.style?.fontSize||16}px`,'--mobile-widget-font-size':`${w.style?.fontSize||16}px`}:{})} as React.CSSProperties;
   const kind=w.kind;
   return <div key={w.id} data-widget-kind={kind} data-vertical-align={w.style?.verticalAlign||'top'} className={'rehearsal-widget rehearsal-'+kind} data-show-title={w.showTitle!==false} data-footer-separator={kind==='footer'?String(w.footerSeparator!==false):undefined} {...widgetArtData(w.style)} style={{...style,...(kind==='footer'?{'--footer-divider-color':w.footerSeparatorColor||'#9ca3af'} as React.CSSProperties:{})}}>{w.kind!=='shape'&&<WidgetShapeOutline style={w.style}/>}<WidgetGraphic kind={w.kind} style={w.style}/><WidgetContentFit allowScale={!mobile&&(kind!=='results-button'||w.autoFit!==false)} minScale={kind==='results-button'?.005:.12}>
    {kind==='results-button'?<LinkedResultChart widget={w} widgets={widgets} rows={(()=>{const source=linkedStatisticSource(w,widgets);if(!source)return undefined;const actual=rehearsalFreeTextRows(source,submittedAnswers,w.targetQuestionId||'');return actual.length?actual:sampleStatisticRows(source,seed,submittedAnswers,w.targetQuestionId||'',{[source.id]:topicSubmissions[activity.id+':'+source.id]||0})})()} emptyLabel="simulazione"/>:
    kind==='reactions'&&viewer==='presenter'?<ProjectionWidgetContent sessionId={snapshot.session.id} widget={w} activity={activity} joinCode={snapshot.session.join_code} usePrivateProfile={true} sessionTitle={snapshot.session.title} pageNumber={page+1} masterTitleStyle={snapshot.session.theme?.master?.titleStyle}/>:kind==='reactions'?<div className="projection-sample-reactions">{w.showTitle!==false&&<strong><WidgetStyledText text={w.label||'Reazioni'} widget={w} field="label"/></strong>}<ReactionChoices size={w.reactionIconSize||32} selected={typeof submittedAnswers[w.id]==='string'?submittedAnswers[w.id] as string:undefined} disabled={pageExpired} onSelect={emoji=>submitDemoDirect(w.id,'reactions',emoji)}/></div>:
    kind==='rating'&&viewer==='presenter'?<ProjectionWidgetContent sessionId={snapshot.session.id} widget={w} activity={activity} joinCode={snapshot.session.join_code} usePrivateProfile={true} sessionTitle={snapshot.session.title} pageNumber={page+1} masterTitleStyle={snapshot.session.theme?.master?.titleStyle}/>:kind==='rating'?<div className="projection-sample-rating">{w.showTitle!==false&&<strong><WidgetStyledText text={w.label||'Gradimento'} widget={w} field="label"/></strong>}<RatingChoices view={w.style?.ratingView} readOnly={viewer==='presenter'} disabled={pageExpired} selected={typeof submittedAnswers[w.id]==='string'?submittedAnswers[w.id] as string:undefined} onSelect={n=>submitDemoDirect(w.id,'rating',String(n))}/></div>:
    (kind==='question'||kind==='timed-quiz')?<div className="projection-question-group" aria-label="Domande interattive di prova">
     {[{...w,_questionId:''},...(w.questions||[]).map((q:any)=>({...q,_questionId:q.id}))].map((q:any)=>{
      const questionId=q._questionId as string;const key=questionId?`${w.id}:${questionId}`:w.id;const current=viewer==='participant'?responses[key]:undefined;const sent=viewer==='participant'&&submittedAnswers[key]!==undefined;const multiple=q.answerMode==='multiple';const answerMode=q.answerMode||(kind==='timed-quiz'?'single':'text');const field=(key:string)=>questionId?'question:'+questionId+':'+key:key;const timedSeconds=kind==='timed-quiz'?rehearsalDurationSeconds(w.durationSeconds,activity?.duration_seconds):undefined;const mayChange=q.allowAnswerChange===true;const canInteract=viewer==='participant'&&!pageExpired&&(timedSeconds===undefined||maySubmitTimedRehearsal(pageStartedAt,timedSeconds,rehearsalNow,mayChange?false:sent))&&(!sent||mayChange);
      return <section className="projection-interactive-widget" data-question-id={questionId} key={key}><strong><WidgetStyledText text={q.label||'Domanda'} widget={w} field={field('label')}/></strong>{q.description&&<p><WidgetStyledText text={q.description} widget={w} field={field('description')}/></p>}
       {['single','multiple'].includes(answerMode)?(q.options||[]).map((o:any)=><label className="widget-answer-option" style={answerOptionStyle(w.style)} key={o.id}><input type={multiple?'checkbox':'radio'} disabled={!canInteract} name={'rehearsal-'+key} checked={Array.isArray(current)?current.includes(o.id):current===o.id} onChange={()=>choose(key,o.id,multiple)}/><WidgetStyledText text={o.label} widget={w} field={field('option:'+o.id)}/></label>):answerMode==='file'?<label>Allegato di prova (non caricato)<input type="file" accept="image/png,image/jpeg,image/gif,image/webp,application/pdf,video/mp4,video/webm" disabled={!canInteract} onChange={e=>choose(key,e.target.files?.[0]?.name||'')}/></label>:<textarea className="widget-free-answer-field" style={answerInputStyle(w.style)} aria-label={'Risposta simulata '+key} maxLength={5000} disabled={!canInteract} readOnly={viewer==='presenter'} value={typeof current==='string'?current:''} placeholder="Scrivi una risposta di prova" onChange={e=>choose(key,e.target.value)}/>}{<button type="button" className="outline small" disabled={!canInteract||!canSubmitRehearsalAnswer(answerMode,current)} style={answerSubmitStyle(w.style)} onClick={()=>submitDemoAnswer(key,answerMode,timedSeconds)}>{viewer==='presenter'?'Invia risposta':'Invia risposta di prova'}</button>}{sent&&<small role="status" aria-live="polite">Risposta simulata inviata{q.allowAnswerChange===true?' · modificabile':''} · nessun dato salvato</small>}{timedSeconds!==undefined&&rehearsalExpired(pageStartedAt,timedSeconds,rehearsalNow)&&!sent&&<small role="status" aria-live="polite">Tempo scaduto: risposta di prova non più inviabile</small>}</section>;
     })}{kind==='timed-quiz'&&<PageTimer openedAt={new Date(pageStartedAt).toISOString()} duration={rehearsalDurationSeconds(w.durationSeconds,activity?.duration_seconds)} label="Tempo rimanente nella prova" face={widgetTimerFace(w.style)}/>}</div>:
    kind==='participant-count'?<div className="projection-participant-count"><strong><WidgetStyledText text={w.label||'Partecipanti connessi'} widget={w} field="label"/></strong><span data-simulated-participants="true">{(seed%37)+12}</span><small>Dati di simulazione</small></div>:
    kind==='timer'?<div className="projection-sample-timer"><strong><WidgetStyledText text={w.label||'Timer'} widget={w} field="label"/></strong><PageTimer openedAt={new Date(pageStartedAt).toISOString()} duration={w.durationSeconds??60} label="Tempo rimanente nella prova" face={widgetTimerFace(w.style)}/></div>:
    kind==='topic-question'&&viewer==='participant'?<div className="projection-sample-topic"><strong><WidgetStyledText text={w.label||'Domande del pubblico'} widget={w} field="label"/></strong><textarea className="widget-free-answer-field" style={answerInputStyle(w.style)} aria-label={'Domanda simulata '+w.id} disabled={pageExpired} maxLength={2000} value={typeof answer==='string'?answer:''} onChange={e=>choose(w.id,e.target.value)}/><button type="button" disabled={pageExpired||typeof answer!=='string'||answer.trim().length<5||(topicSubmissions[activity.id+':'+w.id]||0)>=10} style={answerSubmitStyle(w.style)} onClick={()=>submitDemoTopic(w.id)}>Invia domanda di prova</button><small>{topicSubmissions[activity.id+':'+w.id]||0} / 10 domande simulate inviate, non salvate</small></div>:
    kind==='topic-question'&&viewer==='presenter'?<ProjectionWidgetContent sessionId={snapshot.session.id} widget={w} activity={activity} usePrivateProfile={true} sessionTitle={snapshot.session.title} pageNumber={page+1} masterTitleStyle={snapshot.session.theme?.master?.titleStyle}/>:
    <ProjectionWidgetContent sessionId={snapshot.session.id} widget={w} activity={activity} joinCode={snapshot.session.join_code} usePrivateProfile={true} sessionTitle={snapshot.session.title} pageNumber={page+1} masterTitleStyle={snapshot.session.theme?.master?.titleStyle}/>}
</WidgetContentFit>   </div>;
  })}<SlideCanvasNumber widgets={widgets} pageNumber={page+1}/></div>
 </section>;
 // Render the modal at document.body. When it is nested inside editor/dashboard,
 // an ancestor can become inert or aria-hidden during focus/background isolation,
 // leaving a visually correct dialog invisible to the accessibility tree.
 return createPortal(<div className="rehearsal-backdrop" onClick={e=>{if(e.target===e.currentTarget)onClose()}} role="dialog" aria-modal="true" aria-label="Anteprima interattiva della sessione"><div ref={shellRef} tabIndex={-1} className={'rehearsal-shell rehearsal-mode-'+mode}>
  <header className="rehearsal-toolbar"><strong>ANTEPRIMA · {snapshot.session.title}</strong><span>Nessuna risposta di prova viene salvata</span><div className="rehearsal-mode-switch" role="group" aria-label="Modalità anteprima"><button type="button" aria-pressed={mode==='presenter'} onClick={()=>setMode('presenter')}>Presentatore</button><button type="button" aria-pressed={mode==='participant'} onClick={()=>setMode('participant')}>Partecipante</button><button type="button" aria-pressed={mode==='both'} onClick={()=>setMode('both')}>Affiancate</button><button type="button" aria-pressed={mode==='mobile'} onClick={()=>setMode('mobile')}>Smartphone</button></div>{mode==='both'&&<div className="rehearsal-device-switch" role="group" aria-label="Dispositivo partecipante"><button type="button" aria-pressed={participantDevice==='desktop'} onClick={()=>setParticipantDevice('desktop')}>Desktop</button><button type="button" aria-pressed={participantDevice==='phone'} onClick={()=>setParticipantDevice('phone')}>Smartphone</button></div>}<button type="button" onClick={()=>{void(document.fullscreenElement?document.exitFullscreen():shellRef.current?.requestFullscreen())?.catch(()=>setFullScreen(false))}} aria-pressed={fullScreen} aria-label="Visualizza anteprima a tutto schermo">{fullScreen?'Riduci':'⛶ Tutto schermo'}</button><button type="button" onClick={onClose} aria-label="Chiudi anteprima">× Chiudi</button></header>
  <div className="rehearsal-stage">{activity?<div className="rehearsal-panes">{(mode==='presenter'||mode==='both')&&<div className="rehearsal-pane"><strong className="rehearsal-pane-heading">Presentatore · statistiche simulate</strong>{renderSlide('presenter')}{demoResultsVisible&&<section id="rehearsal-simulated-results" className="rehearsal-statistics" aria-label="Statistiche della simulazione">{widgets.filter(w=>w.kind==='results-button').map(w=>{const source=linkedStatisticSource(w,widgets);const rows=source?rehearsalFreeTextRows(source,submittedAnswers,w.targetQuestionId||''):[];return <LinkedResultChart key={w.id} widget={w} widgets={widgets} rows={source?(rows.length?rows:sampleStatisticRows(source,seed,submittedAnswers,w.targetQuestionId||'',{[source.id]:topicSubmissions[activity.id+':'+source.id]||0})):undefined} emptyLabel="simulazione"/>})}</section>}</div>}{(mode==='participant'||mode==='both'||mode==='mobile')&&<div className={'rehearsal-pane'+(mode==='mobile'||(mode==='both'&&participantDevice==='phone')?' rehearsal-pane-phone':'')}><strong className="rehearsal-pane-heading">Partecipante · {mode==='mobile'||(mode==='both'&&participantDevice==='phone')?'smartphone':'prova interattiva'}</strong>{mode==='mobile'||(mode==='both'&&participantDevice==='phone')?<PhoneRehearsalStage height={mobileStageHeight(widgets)}>{renderSlide('participant',true)}</PhoneRehearsalStage>:renderSlide('participant')}</div>}</div>:<p>Questa sessione non contiene ancora pagine.</p>}</div>
  <footer className="rehearsal-footer"><button type="button" disabled={page===0} onClick={()=>setPage(v=>v-1)}>← Precedente</button><span>{Object.keys(submittedAnswers).filter(key=>!key.startsWith(REHEARSAL_REACTION_PREFIX)).length+Object.values(topicSubmissions).reduce((sum,count)=>sum+count,0)} interazioni simulate · non inviate</span><button type="button" disabled={page>=activities.length-1} onClick={()=>setPage(v=>v+1)}>Successiva →</button><button type="button" onClick={()=>{setResponses({});setSubmittedAnswers({});setTopicSubmissions({});setSeed(Math.floor(Math.random()*0x7fffffff));setPage(0)}}>Ricomincia prova</button></footer>
 </div></div>,document.body);
}

const editorWidgetKinds=['rating','reactions','text','shape','line','timer','qr','profile','question','postit','image','video','logo','pdf','topic-question','timed-quiz','results-button','participant-count','title','footer'] as const;
const editorWidgetNames:Record<string,string>={rating:'Gradimento',reactions:'Reazioni',text:'Testo',divider:'Separatore (legacy)',shape:'Forme',line:'Linee',timer:'Timer',qr:'Codice QR',profile:'Profilo presentatore',question:'Domanda o sondaggio',postit:'Nota adesiva',image:'Immagine',video:'Video',logo:'Logo',pdf:'Documento PDF','topic-question':'Domande sul tema','timed-quiz':'Quiz a tempo','results-button':'Risultati','participant-count':'Partecipanti connessi',title:'Titolo',footer:'Footer'};
function EditorWidgetIcon({kind}:{kind:string}){
 const icons:Record<string,React.ReactNode>={rating:<Star size={21}/>,reactions:<Smile size={21}/>,text:<Type size={21}/>,shape:<Square size={21}/>,line:<Minus size={21}/>,timer:<Clock3 size={21}/>,qr:<Hash size={21}/>,profile:<Presentation size={21}/>,question:<Vote size={21}/>,postit:<StickyNote size={21}/>,image:<BookImage size={21}/>,video:<Video size={21}/>,logo:<BadgeCheck size={21}/>,pdf:<FileQuestion size={21}/>, 'topic-question':<MessageSquareText size={21}/>, 'timed-quiz':<Timer size={21}/>, 'results-button':<BarChartHorizontal size={21}/>, 'participant-count':<Gauge size={21}/>,title:<Heading1 size={21}/>,footer:<PanelBottom size={21}/>};
 return <>{icons[kind]||<Square size={21}/>}</>;
}
/** Text remains available to assistive technology, hover, keyboard focus and touch. */
function EditorIconTool({label,children,onClick,disabled=false,draggable=false,onDragStart,kind}:{label:string;children:React.ReactNode;onClick?:()=>void;disabled?:boolean;draggable?:boolean;onDragStart?:(e:React.DragEvent<HTMLButtonElement>)=>void;kind?:string}){
 const buttonRef=useRef<HTMLButtonElement>(null);
 const [tip,setTip]=useState<{left:number;top:number;side:'left'|'right'|'above'}|null>(null);
 const showTip=()=>{
  const button=buttonRef.current;if(!button)return;
  const b=button.getBoundingClientRect();
  // A body-level portal escapes the scrolling widget rail and the canvas stacking context.
  const side=b.left>232?'left':b.right+224<window.innerWidth?'right':'above';
  const left=side==='left'?Math.max(12,b.left-12):side==='right'?Math.min(window.innerWidth-12,b.right+12):Math.max(115,Math.min(window.innerWidth-115,b.left+b.width/2));
  const top=side==='above'?Math.max(12,b.top-10):Math.max(18,Math.min(window.innerHeight-18,b.top+b.height/2));
  setTip({left,top,side});
 };
 useEffect(()=>{if(!tip)return;const reposition=()=>setTip(null);window.addEventListener('scroll',reposition,true);window.addEventListener('resize',reposition);return()=>{window.removeEventListener('scroll',reposition,true);window.removeEventListener('resize',reposition)}},[!!tip]);
 return <span className="editor-icon-wrapper" onMouseEnter={showTip} onMouseLeave={()=>setTip(null)} onFocus={showTip} onBlur={()=>setTip(null)}>
   <button ref={buttonRef} type="button" className="editor-icon-tool" data-widget-kind={kind} aria-label={label} disabled={disabled} draggable={draggable} onDragStart={onDragStart} onClick={onClick} onPointerDown={e=>{if(e.pointerType!=='mouse')showTip()}}>{children}</button>
   {tip&&createPortal(<span className={'editor-floating-tooltip tooltip-'+tip.side} role="tooltip" style={{left:tip.left,top:tip.top}}>{label}</span>,document.body)}
 </span>;
}
/** Unified appearance editor: every widget uses the same server-validated style schema. */
function WidgetAppearanceEditor({widget,onPatch}:{widget:any;onPatch:(style:Record<string,unknown>)=>void}){
 const style=widget.style||{};
 return <fieldset className="editor-widget-appearance" aria-label="Aspetto del widget"><legend>Riempimento e bordo del widget</legend>
 <p className="muted tiny">Le impostazioni vengono applicate nel canvas, nell’anteprima e nella proiezione e salvate automaticamente.</p>
 <div className="widget-art-controls" role="group" aria-label="Tema artistico del widget">
  <label>Tema visivo<select aria-label="Tema artistico del widget" value={style.artTheme||'studio'} onChange={e=>onPatch({artTheme:e.target.value})}><option value="studio">Studio · elegante</option><option value="glass">Vetro · luminoso</option><option value="playful">Pop · creativo</option><option value="minimal">Essenziale · sobrio</option></select></label>
  <label>Effetto speciale<select aria-label="Effetto artistico del widget" value={style.artEffect||'none'} onChange={e=>onPatch({artEffect:e.target.value})}><option value="none">Nessuno</option><option value="float">Fluttuazione delicata</option><option value="glow">Bagliore</option><option value="tilt">Profondità 3D</option></select></label>
  {['timer','timed-quiz'].includes(widget.kind)&&<label>Quadrante timer<select aria-label="Quadrante grafico timer" value={widgetTimerFace(style)} onChange={e=>onPatch({timerFace:e.target.value})}><option value="hourglass">Clessidra</option><option value="dial">Orologio circolare</option><option value="digital">Digitale</option></select></label>}
  <small>Le immagini e i colori scelti manualmente hanno la precedenza sul tema. Gli effetti rispettano l’opzione di sistema «Riduci movimento».</small>
 </div>
 <label className="appearance-switch"><input type="checkbox" checked={!!style.fillNone} onChange={e=>onPatch({fillNone:e.target.checked})}/> Sfondo trasparente</label>
 <label>Colore di sfondo<input type="color" aria-label="Colore di sfondo del widget" disabled={!!style.fillNone} value={style.fillColor||'#ffffff'} onChange={e=>onPatch({fillNone:false,fillColor:e.target.value})}/></label>
 <label>Tipo di bordo<select aria-label="Tipo di bordo del widget" value={style.strokeNone||(style.strokeWidth??0)===0?'none':'visible'} onChange={e=>onPatch({strokeNone:e.target.value==='none',strokeWidth:e.target.value==='none'?0:(style.strokeWidth||1),strokeColor:style.strokeColor||'#334155'})}><option value="visible">Bordo visibile</option><option value="none">Nessun bordo</option></select></label>
 <label>Stile bordo<select aria-label="Stile bordo del widget" disabled={!!style.strokeNone} value={style.strokeDash||'solid'} onChange={e=>onPatch({strokeDash:e.target.value,strokeNone:false,strokeWidth:style.strokeWidth||1,strokeColor:style.strokeColor||'#334155'})}><option value="solid">Continuo</option><option value="dash">Tratteggiato</option><option value="dot">Puntinato</option></select></label>
 <label>Spessore bordo (pt)<input type="number" aria-label="Spessore bordo del widget" disabled={!!style.strokeNone} min={0} max={12} step={0.25} value={style.strokeWidth??0} onChange={e=>{const n=Number(e.target.value);if(Number.isFinite(n)&&n>=0&&n<=12)onPatch({strokeWidth:n,strokeNone:false,strokeColor:style.strokeColor||'#334155'})}}/></label>
 <label>Colore bordo<input type="color" aria-label="Colore bordo del widget" disabled={!!style.strokeNone} value={style.strokeColor||'#334155'} onChange={e=>onPatch({strokeColor:e.target.value,strokeNone:false,strokeWidth:style.strokeWidth||1})}/></label>
 <label>Forma del widget<select aria-label="Forma del widget" value={style.shapeType||'rectangle'} onChange={e=>onPatch({shapeType:e.target.value,rounded:false})}>{[['rectangle','Rettangolo'],['rounded-rectangle','Rettangolo arrotondato'],['ellipse','Ovale'],['circle','Cerchio'],['triangle','Triangolo'],['diamond','Rombo'],['hexagon','Esagono'],['cloud','Nuvola'],['speech','Fumetto']].map(([id,name])=><option key={id} value={id}>{name}</option>)}</select></label>
 <label>Tipo riempimento<select aria-label="Tipo riempimento" value={style.fillMode||'solid'} onChange={e=>onPatch({fillMode:e.target.value,fillNone:false})}><option value="solid">Solido</option><option value="gradient">Gradiente</option><option value="image">Immagine della libreria</option></select></label>
 <label>Trasparenza riempimento (%)<input type="range" aria-label="Trasparenza riempimento" min={0} max={100} value={Math.round((1-(style.fillOpacity??1))*100)} onChange={e=>onPatch({fillOpacity:1-Number(e.target.value)/100})}/><output>{Math.round((1-(style.fillOpacity??1))*100)}%</output></label>
 {style.fillMode==='gradient'&&<label>Secondo colore del gradiente<input type="color" aria-label="Secondo colore del gradiente" value={style.gradientEndColor||'#57a6f8'} onChange={e=>onPatch({gradientEndColor:e.target.value})}/></label>}
 {style.fillMode==='image'&&<p className="muted tiny">Scegli un'immagine privata della sessione dal selettore nel pannello proprietà. Ogni widget può avere la sua immagine.</p>}
 
 </fieldset>;
}

/** The presenter edits questions and answer options in one authoritative drawer. */
function WidgetChoiceEditor({widget,onPatch}:{widget:any;onPatch:(changes:Record<string,unknown>)=>void}){
 const quiz=widget.kind==='timed-quiz';
 const mode=widget.answerMode||(quiz?'single':'text');
 const choices=Array.isArray(widget.options)?widget.options:[];
 const selectionMode=mode==='single'||mode==='multiple';
 const addChoice=()=>{if(choices.length>=12)return;onPatch({options:[...choices,{id:'opt_'+crypto.randomUUID().replace(/-/g,'').slice(0,24),label:'Nuova opzione'}]})};
 const deleteChoice=(id:string)=>onPatch({options:choices.filter((o:any)=>o.id!==id),textMarks:(widget.textMarks||[]).filter((m:TextMark)=>m.field!=='option:'+id),correctOptionId:widget.correctOptionId===id?undefined:widget.correctOptionId,correctOptionIds:(widget.correctOptionIds||[]).filter((x:string)=>x!==id)});
 return <fieldset className="editor-widget-choices" aria-label="Configurazione risposte del widget"><legend>{quiz?'Domanda e risposte del quiz':'Risposte alla domanda o al sondaggio'}</legend>
  <label>Tipo di risposta<select aria-label="Tipo risposta" value={mode} onChange={e=>onPatch({answerMode:e.target.value,options:questionModeOptions(choices,e.target.value),correctOptionId:undefined,correctOptionIds:[]})}><option value="single">Scelta singola</option><option value="multiple">Scelta multipla</option>{!quiz&&<><option value="text">Testo libero</option><option value="file">Allegato</option></>}</select></label>
  {selectionMode&&<div className="widget-choice-list"><strong>Opzioni di risposta (massimo 12)</strong><p className="widget-choice-caption">Le opzioni vengono mostrate sotto al testo della domanda, nel canvas e ai partecipanti. Il simbolo di scelta è sempre a sinistra della risposta.</p>
   {choices.map((o:any,i:number)=><div className="widget-choice-editor-row" key={o.id}>
     <label className="widget-choice-text">Opzione {i+1}<input aria-label={'Testo opzione '+(i+1)} maxLength={160} value={o.label||''} onChange={e=>onPatch({options:choices.map((c:any)=>c.id===o.id?{...c,label:e.target.value}:c),textMarks:remapMarks(widget.textMarks||[],'option:'+o.id,o.label||'',e.target.value)})}/></label>
     {quiz&&<label className="widget-choice-correct"><input type={mode==='multiple'?'checkbox':'radio'} name={'correct-'+widget.id} aria-label={'Risposta corretta opzione '+(i+1)} checked={mode==='multiple'?(widget.correctOptionIds||[]).includes(o.id):widget.correctOptionId===o.id} onChange={e=>{if(mode==='multiple'){const values=(widget.correctOptionIds||[]).filter((x:string)=>x!==o.id);onPatch({correctOptionIds:e.target.checked?[...values,o.id]:values,correctOptionId:undefined})}else onPatch({correctOptionId:o.id,correctOptionIds:[o.id]})}}/> Corretta</label>}
     <button type="button" aria-label={'Rimuovi opzione '+(i+1)} onClick={()=>deleteChoice(o.id)}>×</button>
   </div>)}
   <button type="button" disabled={choices.length>=12} onClick={addChoice}>+ Aggiungi opzione</button>
   {choices.length<2&&<p className="widget-choice-caption" role="status">Aggiungi almeno due opzioni per una domanda a scelta.</p>}
  </div>}
  {!selectionMode&&<p className="widget-choice-caption">Questa modalità raccoglie {mode==='file'?'un allegato':'un testo libero'} e non richiede opzioni.</p>}
  {quiz&&<label>Durata (secondi)<input type="number" min={5} max={600} value={widget.durationSeconds??30} onChange={e=>onPatch({durationSeconds:Math.max(5,Math.min(600,Number(e.target.value)||30))})}/></label>}
 </fieldset>;
}

function newIndependentQuestion(kind:string){
 const id='q_'+crypto.randomUUID().replace(/-/g,'').slice(0,22);
 return kind==='timed-quiz'?{id,label:'Nuova domanda indipendente',answerMode:'single',options:[{id:'opt_a',label:'Opzione A'},{id:'opt_b',label:'Opzione B'}],correctOptionId:'opt_a',correctOptionIds:['opt_a'],required:true}:{id,label:'Nuova domanda indipendente',answerMode:'text',required:true,options:[]};
}
/** Each additional question has its own persisted definition, response key and text marks. */
function WidgetSubquestionEditor({widget,onPatch}:{widget:any;onPatch:(changes:Record<string,unknown>)=>void}){
 const questions=widget.questions||[];
 const update=(qid:string,changes:Record<string,unknown>)=>onPatch({questions:questions.map((q:any)=>q.id===qid?{...q,...changes}:q)});
 const add=()=>{if(questions.length>=5)return;onPatch({questions:[...questions,newIndependentQuestion(widget.kind)]})};
 return <fieldset className="widget-subquestion-editor" aria-label="Domande indipendenti del widget"><legend>Domande indipendenti</legend>
  <p className="muted tiny">La domanda principale rimane indipendente dalle altre. Ogni domanda ha una propria risposta per partecipante, statistiche e opzioni.</p>
  {questions.map((q:any,index:number)=><div key={q.id} className="widget-subquestion-editor-row">
   <strong>Domanda {index+2}</strong>
   <label>Testo della domanda<input maxLength={240} aria-label={'Testo domanda indipendente '+(index+2)} value={q.label||''} onChange={e=>update(q.id,{label:e.target.value})}/></label>
   <label>Descrizione<textarea rows={2} maxLength={500} aria-label={'Descrizione domanda indipendente '+(index+2)} value={q.description||''} onChange={e=>update(q.id,{description:e.target.value})}/></label>
   <label><input type="checkbox" checked={q.allowAnswerChange===true} onChange={e=>update(q.id,{allowAnswerChange:e.target.checked})}/>Consenti modifica della risposta dopo l'invio</label>
   <label>Modalità risposta<select aria-label={'Modalità domanda indipendente '+(index+2)} value={q.answerMode||'text'} onChange={e=>update(q.id,{answerMode:e.target.value,options:['single','multiple'].includes(e.target.value)&&(!q.options||q.options.length<2)?[{id:'opt_a',label:'Opzione A'},{id:'opt_b',label:'Opzione B'}]:q.options||[],correctOptionId:undefined,correctOptionIds:[]})}><option value="text">Testo libero</option><option value="single">Scelta singola</option><option value="multiple">Scelta multipla</option>{widget.kind!=='timed-quiz'&&<option value="file">Allegato</option>}</select></label>
   {['single','multiple'].includes(q.answerMode)&&<div className="widget-subquestion-choices">{(q.options||[]).map((o:any,i:number)=><label key={o.id}>Risposta {i+1}<input maxLength={160} aria-label={'Opzione '+(i+1)+' domanda '+(index+2)} value={o.label} onChange={e=>update(q.id,{options:q.options.map((old:any)=>old.id===o.id?{...old,label:e.target.value}:old)})}/><button type="button" disabled={q.options.length<=2} aria-label={'Rimuovi opzione '+(i+1)+' domanda '+(index+2)} onClick={()=>onPatch({questions:questions.map((item:any)=>item.id===q.id?{...item,options:item.options.filter((v:any)=>v.id!==o.id)}:item),textMarks:(widget.textMarks||[]).filter((mark:TextMark)=>mark.field!==`question:${q.id}:option:${o.id}`)})}>×</button>{widget.kind==='timed-quiz'&&<input type={q.answerMode==='multiple'?'checkbox':'radio'} aria-label={'Corretta opzione '+(i+1)+' domanda '+(index+2)} name={'correct-question-'+q.id} checked={q.answerMode==='multiple'?(q.correctOptionIds||[]).includes(o.id):q.correctOptionId===o.id} onChange={e=>update(q.id,q.answerMode==='multiple'?{correctOptionIds:e.target.checked?[...(q.correctOptionIds||[]).filter((x:string)=>x!==o.id),o.id]:(q.correctOptionIds||[]).filter((x:string)=>x!==o.id)}:{correctOptionId:o.id,correctOptionIds:[o.id]})}/>}</label>)}<button type="button" disabled={(q.options||[]).length>=12} onClick={()=>update(q.id,{options:[...(q.options||[]),{id:'opt_'+crypto.randomUUID().replace(/-/g,'').slice(0,20),label:'Nuova risposta'}]})}>+ Opzione</button></div>}
   <button type="button" className="outline small" onClick={()=>{if(!window.confirm('Eliminare questa domanda indipendente?'))return;onPatch({questions:questions.filter((x:any)=>x.id!==q.id),textMarks:(widget.textMarks||[]).filter((mark:TextMark)=>!mark.field.startsWith('question:'+q.id+':'))})}}>Rimuovi domanda</button>
  </div>)}
  <button type="button" onClick={add} disabled={questions.length>=5}>+ Aggiungi domanda indipendente ({questions.length+1}/6)</button>
 </fieldset>;
}
/** The author can resize the response box independently of the surrounding widget.
 * The saved value is in logical pixels of the 1280-wide slide, not device px. */
function EditorAnswerFieldPreview({style,canvasRef,onHeightChange,onBeginGesture,onEndGesture,questionField=false}:{style?:WidgetTextStyle;canvasRef:React.RefObject<HTMLDivElement|null>;onHeightChange:(height:number)=>void;onBeginGesture?:()=>void;onEndGesture?:()=>void;questionField?:boolean}){
 const drag=useRef<{pointerId:number;startY:number;height:number;stageWidth:number}|null>(null);
 const height=answerFieldHeight(style?.answerFieldHeight);
 const stop=(e:React.PointerEvent<HTMLSpanElement>)=>{if(drag.current?.pointerId!==e.pointerId)return;drag.current=null;onEndGesture?.()};
 const cancel=(e:React.PointerEvent<HTMLSpanElement>)=>{const start=drag.current;if(!start||start.pointerId!==e.pointerId)return;drag.current=null;onHeightChange(start.height);onEndGesture?.()};
 return <div className="widget-answer-field-editor"><textarea className="widget-free-answer-field" aria-label={questionField?"Casella domanda libera nell’editor":"Casella di risposta libera nell’editor"} placeholder={questionField?"Scrivi una domanda…":"Scrivi una risposta…"} readOnly tabIndex={-1} rows={2} style={answerInputStyle(style)}/><span role="slider" tabIndex={0} className="widget-answer-height-handle" aria-label="Altezza casella risposta libera" aria-orientation="vertical" aria-valuemin={48} aria-valuemax={400} aria-valuenow={height} aria-valuetext={`${height} pixel logici`} title="Trascina o usa frecce su/giù, PagSu/PagGiù, Inizio/Fine" onKeyDown={e=>{if(e.altKey||e.ctrlKey||e.metaKey)return;const next=answerFieldHeightForKey(height,e.key,e.shiftKey);if(next===null)return;e.preventDefault();e.stopPropagation();if(next===height)return;onBeginGesture?.();onHeightChange(next);onEndGesture?.()}} onPointerDown={e=>{if(e.button!==0)return;e.stopPropagation();const width=canvasRef.current?.getBoundingClientRect().width||1280;drag.current={pointerId:e.pointerId,startY:e.clientY,height,stageWidth:width};onBeginGesture?.();e.currentTarget.setPointerCapture(e.pointerId);e.preventDefault()}} onPointerMove={e=>{const g=drag.current;if(!g||g.pointerId!==e.pointerId)return;const next=Math.max(48,Math.min(400,Math.round((g.height+(e.clientY-g.startY)*1280/g.stageWidth)/8)*8));if(next!==height)onHeightChange(next);e.stopPropagation()}} onPointerUp={stop} onPointerCancel={cancel} onLostPointerCapture={stop}>↕</span></div>;
}
function WidgetCanvas({widgets,onChange,pageTitle="",sessionTitle="",pageNumber=1,masterTitleStyle,assets=[],backgrounds=[],sessionId="",joinCode,onUpload,assetBusy=false,backgroundAssetId="",onBackgroundSelect,onBackgroundUpload,onBackgroundColorChange,mobileMode=false,mobileHeight=720,mobileBackgroundColor,onBeginGesture,onEndGesture,onAutoFit,onInspectWidget,onSelectionChange,onOpenPageSettings,onRenamePage,onSaveRequested,onContextOpen,dismissContextMenus=false,suspendFormattingRibbon=false}: {widgets:any[];pageTitle?:string;sessionTitle?:string;pageNumber?:number;masterTitleStyle?:any;onChange:(items:any[])=>void;onBeginGesture?:()=>void;onEndGesture?:()=>void;onAutoFit?:(base:any[],fitted:any[])=>void;assets?:any[];backgrounds?:any[];sessionId?:string;joinCode?:string;onUpload?:(widgetId:string,file:File|undefined,kind:string)=>Promise<void>;assetBusy?:boolean;backgroundAssetId?:string;onBackgroundSelect?:(id:string)=>void;onBackgroundUpload?:(file:File|undefined)=>Promise<boolean>;onBackgroundColorChange?:(value:string)=>void;mobileMode?:boolean;mobileHeight?:number;mobileBackgroundColor?:string;onInspectWidget?:(id:string)=>void;onSelectionChange?:(ids:string[])=>void;onOpenPageSettings?:()=>void;onRenamePage?:()=>void;onSaveRequested?:()=>void;onContextOpen?:()=>void;dismissContextMenus?:boolean;suspendFormattingRibbon?:boolean}){
 const ref=useRef<HTMLDivElement>(null);
 const contextHold=useRef<ReturnType<typeof setTimeout>|null>(null);
 const widgetHold=useRef<ReturnType<typeof setTimeout>|null>(null);
 const clearWidgetHold=()=>{if(widgetHold.current){clearTimeout(widgetHold.current);widgetHold.current=null}};
 const clearContextHold=()=>{if(contextHold.current!==null){clearTimeout(contextHold.current);contextHold.current=null}};
 const gesture=useRef<{id:string;pointerId:number;mode:'move'|'resize'|'rotate';edge:string;startX:number;startY:number;pos:{x:number;y:number;width:number;height:number;rotation?:number};startAngle?:number;groupBase?:any[];groupIds?:string[]}|null>(null);
 const [active,setActive]=useState<string|null>(null);
 const [selectedWidgets,setSelectedWidgets]=useState<string[]>([]);
 const [ribbonDismissed,setRibbonDismissed]=useState(false);
 useEffect(()=>{onSelectionChange?.(selectedWidgets)},[selectedWidgets]);
 const toggleSelection=(id:string,extend=false)=>{setRibbonDismissed(false);setFormatScope('widget');setToolbarRange(null);textSelection.current=null;pendingTextStyle.current=null;setEditing(null);setActive(id);setSelectedWidgets(old=>extend?(old.includes(id)?old.filter(x=>x!==id):[...old,id]):[id])};
 const arrangeSelected=(mode:ArrangeMode)=>{const ids=selectedWidgets.length?selectedWidgets:active?[active]:[];onChange(rejectWidgetCollisions(widgets,arrangeWidgets(widgets,ids,mode),ids))};
 const [editing,setEditing]=useState<string|null>(null);
 const textSelection=useRef<{id:string;field:string;start:number;end:number}|null>(null);
 const [toolbarRange,setToolbarRange]=useState<{id:string;field:string;start:number;end:number}|null>(null);
 const [formatScope,setFormatScope]=useState<'widget'|'label'|'description'|'answers'>('widget');
 const recordTextSelection=(id:string,field:string,range:{start:number;end:number})=>{
  const next={id,field,...range};textSelection.current=next;
  setFormatScope(field.startsWith('option:')||field.includes(':option:')?'answers':field==='description'||field.includes(':description')?'description':'label');
  setToolbarRange(prev=>prev?.id===id&&prev.field===field&&prev.start===range.start&&prev.end===range.end?prev:next);
 };

 const pendingTextStyle=useRef<{id:string;field:string;style:InlineStyle}|null>(null);
 const editContent=(widget:any,field:string,oldValue:string,newValue:string,changes:Record<string,unknown>)=>{
  let marks=remapMarks(widget.textMarks||[],field,oldValue,newValue);
  const pending=pendingTextStyle.current;
  if(pending!==null&&pending.id===widget.id&&pending.field===field){const part=changedRegion(oldValue,newValue);if(part.end>part.start)marks=formatTextRange(marks,field,part.start,part.end,pending.style)}
  patch(widget.id,{...changes,textMarks:marks});
 };
 const [snapGrid,setSnapGrid]=useState(false);
 const [alignmentGuides,setAlignmentGuides]=useState<{axis:'x'|'y';at:number;source:'canvas'|'widget'}[]>([]);
 const [contextWidget,setContextWidget]=useState<string|null>(null);
 const [contextPoint,setContextPoint]=useState({x:12,y:12});
 // Preserve ownership from the genuine secondary-pointer down: browsers can
 // retarget contextmenu after capture or a layout change. Never reuse across
 // different coordinates or outside the same immediate pointer gesture.
 const contextPointer=useRef<{id:string;x:number;y:number;at:number}|null>(null);
 const positionMenu=(element:HTMLElement,x?:number,y?:number)=>{
  const rect=element.getBoundingClientRect();
  setContextPoint(floatingWidgetMenuPosition(rect,window.innerWidth,window.innerHeight,y));
 };
 useEffect(()=>{
  if(!contextWidget)return;
  const dismiss=(event:PointerEvent)=>{if(!(event.target as Element)?.closest?.('.canvas-context-menu'))setContextWidget(null)};
  const onEscape=(event:KeyboardEvent)=>{if(event.key==='Escape')setContextWidget(null)};
  document.addEventListener('pointerdown',dismiss,true);
  document.addEventListener('keydown',onEscape,true);
  const dismissOnViewportChange=()=>setContextWidget(null);
  window.addEventListener('scroll',dismissOnViewportChange,true);
  window.addEventListener('resize',dismissOnViewportChange);
  return()=>{document.removeEventListener('pointerdown',dismiss,true);document.removeEventListener('keydown',onEscape,true);window.removeEventListener('scroll',dismissOnViewportChange,true);window.removeEventListener('resize',dismissOnViewportChange)};
 },[contextWidget]);
 const [backgroundMenu,setBackgroundMenu]=useState(false);
  const [backgroundUploadStatus,setBackgroundUploadStatus]=useState('');
  const [backgroundUploading,setBackgroundUploading]=useState(false);
 // Keep the page popover a genuine modal-independent floating viewport layer.
 // Clicking outside or pressing Escape dismisses it without changing selection.
 useEffect(()=>{
  if(!backgroundMenu)return;
  const dismissOutside=(event:PointerEvent)=>{
   if(!(event.target as Element)?.closest?.('.canvas-background-context-floating'))setBackgroundMenu(false);
  };
  const dismissEscape=(event:KeyboardEvent)=>{if(event.key==='Escape')setBackgroundMenu(false)};
  document.addEventListener('pointerdown',dismissOutside,true);
  document.addEventListener('keydown',dismissEscape,true);
  return()=>{document.removeEventListener('pointerdown',dismissOutside,true);document.removeEventListener('keydown',dismissEscape,true)};
 },[backgroundMenu]);
 const backgroundFileRef=useRef<HTMLInputElement>(null);
 const openBlankMenu=()=>{onContextOpen?.();setContextWidget(null);setArrangeMenu(false);setBackgroundUploadStatus('');setBackgroundMenu(true)};
 // RC83: Own the pointer context gesture at the canvas capture boundary.
 // In Chromium, transformed/clipped widget content can send the contextmenu
 // to the underlying canvas even though the pointer lies within the widget.
 // A geometry fallback only applies to the *actual* pointer coordinate; the
 // empty canvas still opens the page background menu.
 // Native secondary clicks must not select/reflow at pointerdown; ownership
 // is established only when the contextmenu event reaches the canvas.
 const openWidgetContextMenu=(widgetId:string,element:HTMLElement,x?:number,y?:number)=>{
  clearContextHold();clearWidgetHold();positionMenu(element,x,y);
  setBackgroundMenu(false);setArrangeMenu(false);setContextWidget(widgetId);
  setActive(widgetId);onContextOpen?.();
 };
 const handleCanvasContext=(e:React.MouseEvent<HTMLDivElement>)=>{
  const target=e.target as Element;
  if(target.closest('.canvas-background-context,.canvas-context-menu')){e.preventDefault();return}
  const canvas=e.currentTarget;
  const direct=target.closest('.widget-canvas-item') as HTMLElement|null;
  const pointer=contextPointer.current;
  contextPointer.current=null;
  const prior=pointer&&performance.now()-pointer.at<1500&&Math.hypot(pointer.x-e.clientX,pointer.y-e.clientY)<8
   ?Array.from(canvas.querySelectorAll<HTMLElement>('.widget-canvas-item')).find(node=>node.dataset.widgetId===pointer.id)||null:null;
  const widget=direct&&canvas.contains(direct)?direct:prior||canvasWidgetAtPoint(canvas,e.clientX,e.clientY);
  e.preventDefault();e.stopPropagation();
  if(widget){
   const widgetId=widget.getAttribute('data-widget-id');
   if(widgetId&&widgets.some(w=>w.id===widgetId)){
    openWidgetContextMenu(widgetId,widget,e.clientX,e.clientY);
    return;
   }
  }
  clearContextHold();openBlankMenu();
 };

 useEffect(()=>{if(dismissContextMenus){setBackgroundMenu(false);setArrangeMenu(false);setContextWidget(null)}},[dismissContextMenus]);
 const [arrangeMenu,setArrangeMenu]=useState(false);
 const pasteCount=useRef(0);
 // Clipboard contents belong to the session, not the page. Refresh the
 // paste action when a copy/cut happens without changing canvas widgets.
 const [clipboardAvailable,setClipboardAvailable]=useState(()=>readEditorWidgetClipboard(sessionId).length>0);
 useEffect(()=>{setClipboardAvailable(readEditorWidgetClipboard(sessionId).length>0)},[sessionId]);
 // The parent may remove a widget (e.g. after reloading a page). Never retain an orphan inspector or context menu.
 useEffect(()=>{
  if(active&&!widgets.some(w=>w.id===active))setActive(null);
  setSelectedWidgets(old=>{const next=old.filter(id=>widgets.some(w=>w.id===id));return next.length===old.length?old:next});
  if(editing&&!widgets.some(w=>w.id===editing))setEditing(null);
  if(contextWidget&&!widgets.some(w=>w.id===contextWidget))setContextWidget(null);
 },[widgets,active,editing,contextWidget]);
 const snap=(n:number)=>snapGrid?Math.round(n/5)*5:n;
 const duplicateWidget=(w:any)=>{const copy=pasteWidget(w,crypto.randomUUID());const p=copy.position||{x:0,y:0,width:22,height:20};const position=freeWidgetPosition(widgets,{x:p.x,y:p.y},p.width,p.height);if(!position){window.alert('Non c’è spazio per duplicare questo widget.');return}copy.position={...p,...position};onChange([...widgets,copy]);setActive(copy.id)};
 const clipboardSelection=()=>widgets.filter(w=>selectedWidgets.includes(w.id)).length?widgets.filter(w=>selectedWidgets.includes(w.id)):widgets.filter(w=>w.id===active);
 const copySelectedWidget=()=>{const items=clipboardSelection();if(items.length){saveEditorWidgetClipboard(sessionId,items);setClipboardAvailable(true);pasteCount.current=0}};
 const pasteCopiedWidget=()=>{const source=readEditorWidgetClipboard(sessionId);if(!source.length)return;if(widgets.length+source.length>16){window.alert('Massimo 16 widget per pagina.');return}pasteCount.current++;const result=insertWidgetGroupInFreeSpace(widgets,source,source.map(w=>crypto.randomUUID()),Math.min(5*pasteCount.current,40));if(!result){window.alert('Impossibile incollare i widget: controlla la geometria.');return}onChange(result.widgets);setSelectedWidgets(result.selected);setActive(result.selected[0])};
 const cutSelectedWidget=()=>{const items=clipboardSelection();if(!items.length||!window.confirm(`Tagliare e rimuovere ${items.length} widget?`))return;saveEditorWidgetClipboard(sessionId,items);setClipboardAvailable(true);pasteCount.current=0;onChange(deleteWidgetSelection(widgets,items.map(w=>w.id)));setSelectedWidgets([]);setActive(null)};
 const reorderWidget=(id:string,direction:'front'|'back')=>onChange(reorderWidgetLayers(widgets,[id],direction));
 const groupSelection=()=>existingWidgetIds(widgets,selectedWidgets.length?selectedWidgets:active?[active]:[]);
 const layerSelected=(direction:LayerAction)=>onChange(reorderWidgetLayers(widgets,groupSelection(),direction));
 const deleteSelected=()=>{const ids=groupSelection();if(!ids.length||!window.confirm(`Eliminare ${ids.length} widget selezionati?`))return;onChange(deleteWidgetSelection(widgets,ids));setSelectedWidgets([]);setActive(null);setContextWidget(null);setEditing(null)};
 const duplicateSelected=()=>{const ids=groupSelection();if(!ids.length)return;const selected=widgets.filter(w=>ids.includes(w.id));const result=insertWidgetGroupInFreeSpace(widgets,selected,selected.map(w=>crypto.randomUUID()));if(!result){window.alert('Impossibile duplicare i widget: controlla la geometria.');return}onChange(result.widgets);setSelectedWidgets(result.selected);setActive(result.selected[0]||null)};
 const nudgeSelected=(dx:number,dy:number)=>{const ids=groupSelection();if(ids.length)onChange(nudgeWidgetSelection(widgets,ids,dx,dy))};
 // Canvas keyboard shortcuts remain available when the floating palette has focus.
 // Native input/textarea/contenteditable selections always take precedence.
 useEffect(()=>{const onShortcut=(event:KeyboardEvent)=>{
  if(event.defaultPrevented||event.altKey||!sessionId)return;
  const target=event.target as HTMLElement|null;
  if(target?.closest('input,textarea,select,[contenteditable="true"],[role="textbox"],[contenteditable]'))return;
  const modifier=event.metaKey||event.ctrlKey;
  const key=event.key.toLowerCase();
  if(modifier&&!event.shiftKey&&key==='c'&&active){event.preventDefault();copySelectedWidget();return}
  if(modifier&&!event.shiftKey&&key==='v'&&readEditorWidgetClipboard(sessionId).length){event.preventDefault();pasteCopiedWidget();return}
  if(!modifier&&!event.shiftKey&&(event.key==='Backspace'||event.key==='Delete')){
   if(!selectedWidgets.length&&!active)return;
   event.preventDefault();deleteSelected();
  }
 };window.addEventListener('keydown',onShortcut);
 return()=>window.removeEventListener('keydown',onShortcut);
 },[widgets,active,selectedWidgets,sessionId]);
 const update=(id:string,position:{x:number;y:number;width:number;height:number})=>onChange(widgets.map(w=>w.id===id?{...w,position}:w));
 // Automatic content sizing is the default. A manual resize sets autoFit=false.
 // Grow only when measured content overflows; never move another widget and
 // never exceed the slide. The next render re-measures after text/font changes.
 useEffect(()=>{
  if(!ref.current||gesture.current)return;
  const stage=ref.current;
  const rect=stage.getBoundingClientRect();if(rect.height<=0)return;
  let changes:any[]|null=null;
  for(const w of widgets){
   if(!widgetMayAutoFit(w.kind,w.autoFit))continue;
   const node=Array.from(stage.querySelectorAll<HTMLElement>('.widget-canvas-item')).find(el=>el.dataset.widgetId===w.id);
   if(!node)continue;
   const p=w.position;if(!p||!p.height)continue;
   // Never measure the outer widget: its resize handles deliberately extend
   // beyond the bottom/right border, inflating scrollHeight at every render.
   // Only actual text/answers/media inside the bounded content shell count.
   const frame=node.querySelector<HTMLElement>(':scope > .widget-fit-frame');
   const content=frame?.querySelector<HTMLElement>(':scope > .widget-fit-content');
   if(!frame||!content)continue;
   const overflow=measuredContentOverflowPx(frame.clientHeight,content.scrollHeight);
   if(overflow<=2)continue;
   const next=autoFitExpandedPosition(p,overflow,rect.height);
   if(!next)continue;
   const current: any[]=changes??widgets;
   const proposal:any[]=current.map((z:any)=>z.id===w.id?{...z,position:{...z.position,height:next.height}}:z);
   const accepted:any[]=rejectWidgetCollisions(current,proposal,[w.id]);
   if(accepted.find(z=>z.id===w.id)?.position?.height>p.height+.1)changes=accepted;
  }
  if(changes){
   // Layout derived from actual DOM content must not add a second undo entry.
   // In the page editor the parent reconciles this with the current history.
   if(onAutoFit)onAutoFit(widgets,changes);else onChange(changes);
  }
 },[widgets,editing,onAutoFit]);
 const patch=(id:string,changes:Record<string,unknown>)=>onChange(widgets.map(w=>{
  if(w.id!==id)return w;
  const updated={...w,...changes};
  // Inspector, inline canvas, and API must agree on persisted plain-text offsets.
  if(!Object.prototype.hasOwnProperty.call(changes,'textMarks')&&Array.isArray(w.textMarks)){
   let marks:TextMark[]=w.textMarks;
   if(typeof changes.label==='string')marks=remapMarks(marks,'label',w.label||'',changes.label);
   if(typeof changes.description==='string')marks=remapMarks(marks,'description',w.description||'',changes.description);
   if(Array.isArray(changes.options)){
    const existing=new Map((w.options||[]).map((o:any)=>[o.id,o.label]));
    const next=new Set((updated.options||[]).map((o:any)=>o.id));
    marks=marks.filter(m=>!m.field.startsWith('option:')||next.has(m.field.slice(7)));
    for(const o of updated.options||[]){const prev=existing.get(o.id);if(typeof prev==='string'&&prev!==o.label)marks=remapMarks(marks,'option:'+o.id,prev,o.label||'')}
   }
   updated.textMarks=marks;
  }
  return updated;
 }));
 const clamp=(n:number,min:number,max:number)=>Math.min(max,Math.max(min,n));
 function down(e:React.PointerEvent<HTMLDivElement>,w:any){
  if(gesture.current || (e.pointerType==='mouse' && e.button!==0))return;
  if((e.target as HTMLElement).closest('button,input,select,textarea,[contenteditable=true],[role=textbox],[role=slider]'))return;
  const edge=(e.target as HTMLElement).closest('[data-resize-edge]')?.getAttribute('data-resize-edge')||'';
  const rotate=!!(e.target as HTMLElement).closest('[data-rotate-handle]');
  const p=w.position||{x:0,y:0,width:48,height:24};
  setAlignmentGuides([]);
  onBeginGesture?.();
  const groupIds=!rotate&&!edge&&selectedWidgets.includes(w.id)?selectedWidgets:[w.id];
  gesture.current={id:w.id,pointerId:e.pointerId,mode:rotate?'rotate':edge?'resize':'move',edge,startX:e.clientX,startY:e.clientY,pos:{x:p.x,y:p.y,width:p.width,height:p.height??24,rotation:p.rotation??0},groupIds,groupBase:structuredClone(widgets)};
  if(rotate){const b=ref.current?.getBoundingClientRect();if(b){const cx=b.left+(p.x+p.width/2)*b.width/100,cy=b.top+(p.y+(p.height??24)/2)*b.height/100;gesture.current.startAngle=Math.atan2(e.clientY-cy,e.clientX-cx)*180/Math.PI;}}
  setActive(w.id);e.currentTarget.setPointerCapture(e.pointerId);e.preventDefault();
 }
 function move(e:React.PointerEvent<HTMLDivElement>){
  const g=gesture.current,b=ref.current?.getBoundingClientRect();if(!g||g.pointerId!==e.pointerId||!b)return;
  const dx=(e.clientX-g.startX)/b.width*100,dy=(e.clientY-g.startY)/b.height*100;
  let {x,y,width,height}=g.pos;
  if(g.mode==='rotate'){const cx=b.left+(g.pos.x+g.pos.width/2)*b.width/100,cy=b.top+(g.pos.y+g.pos.height/2)*b.height/100;const angle=Math.atan2(e.clientY-cy,e.clientX-cx)*180/Math.PI;const next=(g.pos.rotation??0)+(angle-(g.startAngle??angle));patch(g.id,{position:{...g.pos,rotation:+Math.max(-360,Math.min(360,next)).toFixed(4)}});return}
  if(g.mode==='move'){
   const base=g.groupBase||widgets,ids=g.groupIds||[g.id];
   const delta=snapGrid?snapWidgetGroupDelta(base,ids,dx,dy):{dx,dy};
   let moved=moveWidgetGroup(base,ids,delta.dx,delta.dy);
   let guides:typeof alignmentGuides=[];
   if(!snapGrid&&ids.length===1){
    const candidate=moved.find(w=>w.id===g.id);
    if(candidate){const aligned=magneticSnapWithGuides(candidate,base.filter(z=>z.id!==g.id));
     guides=aligned.guides;moved=moved.map(w=>w.id===g.id?aligned.widget:w);
    }
   }
   const candidate=moved.find(w=>w.id===g.id)?.position;
   const origin=base.find(w=>w.id===g.id)?.position;
   const accepted=candidate&&origin?moveWidgetsToCollisionLimit(base,ids,candidate.x-origin.x,candidate.y-origin.y):base;
   // Guides only when the original proposed snap is reachable without collision.
   setAlignmentGuides(accepted.find(w=>w.id===g.id)?.position?.x===candidate?.x&&accepted.find(w=>w.id===g.id)?.position?.y===candidate?.y?guides:[]);
   onChange(accepted);return;
  }
  else {
   if(g.edge.includes('e'))width=clamp(width+dx,0.01,100-x);
   if(g.edge.includes('s'))height=clamp(height+dy,0.01,100-y);
   if(g.edge.includes('w')){const nx=clamp(x+dx,0,x+width-0.01);width=width+x-nx;x=nx}
   if(g.edge.includes('n')){const ny=clamp(y+dy,0,y+height-0.01);height=height+y-ny;y=ny}
  }
  const base=g.groupBase||widgets;
  const nextPos={x:+clamp(snap(x),0,100-width).toFixed(4),y:+clamp(snap(y),0,100-height).toFixed(4),width:+clamp(snap(width),0.01,100-x).toFixed(4),height:+clamp(snap(height),0.01,100-y).toFixed(4)};
  onChange(resizeWidgetToCollisionLimit(base,g.id,nextPos));
 }
 function keyboardGeometry(e:React.KeyboardEvent<HTMLDivElement>,w:any){
  if((e.target as HTMLElement).closest('input,textarea,button,select,[contenteditable=true]'))return;
  if(e.key==='Delete'||e.key==='Backspace'){
   e.preventDefault();
   const ids=selectedWidgets.includes(w.id)?selectedWidgets:[w.id];if(!window.confirm(`Eliminare ${ids.length} widget dal canvas?`))return;onChange(deleteWidgetSelection(widgets,ids));
   setSelectedWidgets([]);setActive(null);setContextWidget(null);setEditing(null);
   return;
  }
  if(e.key==='Escape'){setSelectedWidgets([]);setActive(null);setContextWidget(null);setEditing(null);return;}
  if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;
  e.preventDefault();
  const p=w.position||{x:0,y:0,width:48,height:24,rotation:0};
  const step=e.ctrlKey?0.1:1;
  const direction=(e.key==='ArrowRight'||e.key==='ArrowDown')?step:-step;
  const horizontal=e.key==='ArrowLeft'||e.key==='ArrowRight';
  const position={x:p.x,y:p.y,width:p.width,height:p.height??24,rotation:p.rotation??0};
  if(e.altKey){position.rotation=+clamp(position.rotation+direction*(e.ctrlKey?1:5),-360,360).toFixed(4)}
  else if(e.shiftKey){
   if(horizontal)position.width=+clamp(position.width+direction,0.01,100-position.x).toFixed(4);
   else position.height=+clamp(position.height+direction,0.01,100-position.y).toFixed(4);
  }else{
   if(horizontal)position.x=+clamp(position.x+direction,0,100-position.width).toFixed(4);
   else position.y=+clamp(position.y+direction,0,100-position.height).toFixed(4);
  }
  if(!e.altKey&&!e.shiftKey&&selectedWidgets.length>1&&selectedWidgets.includes(w.id))nudgeSelected(horizontal?direction:0,horizontal?0:direction);
  else if(!e.altKey&&!e.shiftKey)onChange(moveWidgetsToCollisionLimit(widgets,[w.id],horizontal?direction:0,horizontal?0:direction));
  else if(e.shiftKey&&!e.altKey)onChange(resizeWidgetToCollisionLimit(widgets,w.id,position));
  else onChange(rejectWidgetCollisions(widgets,widgets.map(item=>item.id===w.id?{...item,position}:item),[w.id]));
 }
 function end(e:React.PointerEvent<HTMLDivElement>){if(gesture.current?.pointerId===e.pointerId){gesture.current=null;setAlignmentGuides([]);onEndGesture?.()}} // Keep the selected widget active so its properties editor remains usable after pointer release.
 function cancelGesture(e:React.PointerEvent<HTMLDivElement>){const g=gesture.current;if(!g||g.pointerId!==e.pointerId)return;onChange(g.groupBase||widgets);gesture.current=null;setAlignmentGuides([]);onEndGesture?.()}
 const nudge=(w:any,axis:'x'|'y',amount:number)=>{const p=w.position||{x:0,y:0,width:48,height:24,rotation:0};const width=p.width??48,height=p.height??24;patch(w.id,{position:{...p,[axis]:+clamp((p[axis]??0)+amount,0,100-(axis==='x'?width:height)).toFixed(1)}})};
 const edges=['n','ne','e','se','s','sw','w','nw'];
 const selectedQuestion=widgets.find(w=>w.id===active&&['question','timed-quiz','topic-question'].includes(w.kind));
 const selectedPicture=widgets.find(w=>w.id===active&&['image','logo'].includes(w.kind));
 const selectedShape=widgets.find(w=>w.id===active&&w.kind==='postit');
 const shapePaintEditor=selectedShape&&<section className="panel widget-shape-paint-editor" aria-label="Stile forma PowerPoint"><h4>Riempimento e contorno forma</h4>
 <label><input type="checkbox" aria-label="Nessun riempimento" checked={!!selectedShape.style?.fillNone} onChange={e=>patch(selectedShape.id,{style:{...selectedShape.style,fillNone:e.target.checked}})}/> Nessun riempimento</label>
 <label>Colore riempimento<input type="color" aria-label="Colore riempimento forma" disabled={!!selectedShape.style?.fillNone} value={selectedShape.style?.fillColor||'#ffffff'} onChange={e=>patch(selectedShape.id,{style:{...selectedShape.style,fillColor:e.target.value}})}/></label>
 <label><input type="checkbox" aria-label="Nessun contorno" checked={!!selectedShape.style?.strokeNone||(selectedShape.style?.strokeWidth??0)===0} onChange={e=>patch(selectedShape.id,{style:{...selectedShape.style,strokeNone:e.target.checked,strokeWidth:e.target.checked?0:(selectedShape.style?.strokeWidth||1)}})}/> Nessun contorno</label>
 <label>Colore contorno<input type="color" aria-label="Colore contorno forma" disabled={!!selectedShape.style?.strokeNone||(selectedShape.style?.strokeWidth??0)===0} value={selectedShape.style?.strokeColor||'#1f2937'} onChange={e=>patch(selectedShape.id,{style:{...selectedShape.style,strokeColor:e.target.value,strokeWidth:selectedShape.style?.strokeWidth||1,strokeNone:false}})}/></label>
 <label>Spessore contorno (pt)<input type="number" aria-label="Spessore contorno" min={0} max={12} step={0.25} disabled={!!selectedShape.style?.strokeNone||(selectedShape.style?.strokeWidth??0)===0} value={selectedShape.style?.strokeWidth??0} onChange={e=>{const v=Number(e.target.value);if(Number.isFinite(v)&&v>=0&&v<=12)patch(selectedShape.id,{style:{...selectedShape.style,strokeColor:selectedShape.style?.strokeColor||'#1f2937',strokeWidth:v}})}}/></label>
 <label>Tratteggio contorno<select aria-label="Tratteggio contorno" disabled={!!selectedShape.style?.strokeNone||(selectedShape.style?.strokeWidth??0)===0} value={selectedShape.style?.strokeDash||'solid'} onChange={e=>patch(selectedShape.id,{style:{...selectedShape.style,strokeColor:selectedShape.style?.strokeColor||'#1f2937',strokeDash:e.target.value}})}><option value="solid">Continuo</option><option value="dash">Tratteggiato</option><option value="dot">Puntinato</option></select></label>
 <p className="muted tiny">Le proprietà restano modificabili nel PowerPoint esportato. Le modifiche vengono salvate automaticamente.</p></section>;
 const cropEditor=selectedPicture&&<section className="panel widget-picture-crop-editor" aria-label="Ritaglio immagine PowerPoint"><h4>Ritaglio immagine</h4><p className="muted">Ritaglio modificabile: valori percentuali rispetto all'immagine originale. Le modifiche vengono salvate automaticamente.</p><div className="picture-crop-controls">{(['left','right','top','bottom'] as const).map(side=>{const current=selectedPicture.crop||{left:0,right:0,top:0,bottom:0};const other=side==='left'?'right':side==='right'?'left':side==='top'?'bottom':'top';return <label key={side}>{({left:'Sinistra',right:'Destra',top:'Alto',bottom:'Basso'} as const)[side]} (%)<input type="number" aria-label={'Ritaglio '+side} min={0} max={Math.floor(Math.min(.95,.989-Number(current[other]||0))*100)} step={1} value={Math.round(Number(current[side]||0)*100)} onChange={e=>{const next=Math.min(.95,.989-Number(current[other]||0),Math.max(0,Number(e.target.value)/100));if(Number.isFinite(next))patch(selectedPicture.id,{crop:{...current,[side]:+next.toFixed(4)}})}}/></label>})}</div><button type="button" className="outline small" onClick={()=>patch(selectedPicture.id,{crop:undefined})}>Ripristina immagine intera</button></section>;
 const questionEditor=selectedQuestion&&<section className="panel widget-question-editor" aria-label="Configura widget interattivo"><h4>Configura {selectedQuestion.kind==='timed-quiz'?'quiz a tempo':'domanda'}</h4>
 <label>Testo della domanda<input aria-label="Testo domanda widget" value={selectedQuestion.label||''} maxLength={240} onChange={e=>patch(selectedQuestion.id,{label:e.target.value})}/></label>
 <label>Modalità di risposta<select aria-label="Modalità risposta widget" value={selectedQuestion.answerMode||(selectedQuestion.kind==='timed-quiz'?'single':'text')} onChange={e=>patch(selectedQuestion.id,{answerMode:e.target.value,correctOptionId:undefined,correctOptionIds:[]})}><option value="single">Una scelta</option><option value="multiple">Scelta multipla</option>{selectedQuestion.kind==='question'&&<><option value="text">Testo libero</option><option value="file">File</option></>}</select></label>
 {['single','multiple'].includes(selectedQuestion.answerMode||(selectedQuestion.kind==='timed-quiz'?'single':'text'))&&<div className="widget-answer-options"><strong>Opzioni (massimo 12)</strong>{(selectedQuestion.options||[]).map((option:any,i:number)=><div className="widget-option-row" key={option.id}><input aria-label={'Opzione '+(i+1)} maxLength={160} value={option.label} onChange={e=>patch(selectedQuestion.id,{options:selectedQuestion.options.map((o:any)=>o.id===option.id?{...o,label:e.target.value}:o)})}/>{selectedQuestion.kind==='timed-quiz'&&<label><input type={selectedQuestion.answerMode==='multiple'?'checkbox':'radio'} name={'correct-'+selectedQuestion.id} checked={((selectedQuestion.correctOptionIds?.length?selectedQuestion.correctOptionIds:[selectedQuestion.correctOptionId])).includes(option.id)} onChange={e=>{const current=(selectedQuestion.correctOptionIds?.length?selectedQuestion.correctOptionIds:[selectedQuestion.correctOptionId]).filter(Boolean);const ids=selectedQuestion.answerMode==='multiple'?(e.target.checked?[...new Set([...current,option.id])]:current.filter((id:string)=>id!==option.id)):(e.target.checked?[option.id]:[]);patch(selectedQuestion.id,{correctOptionId:ids[0]||undefined,correctOptionIds:ids})}}/> Corretta</label>}<button type="button" aria-label={'Rimuovi opzione '+(i+1)} onClick={()=>{const options=selectedQuestion.options.filter((o:any)=>o.id!==option.id);patch(selectedQuestion.id,{options,correctOptionIds:(selectedQuestion.correctOptionIds||[]).filter((id:string)=>id!==option.id),correctOptionId:selectedQuestion.correctOptionId===option.id?undefined:selectedQuestion.correctOptionId})}}>×</button></div>)}<button type="button" disabled={(selectedQuestion.options||[]).length>=12} onClick={()=>patch(selectedQuestion.id,{options:[...(selectedQuestion.options||[]),{id:'opt_'+crypto.randomUUID().replace(/-/g,'').slice(0,24),label:'Nuova opzione'}]})}>Aggiungi opzione</button></div>}
 <label>Visualizzazione risultati<select aria-label="Visualizzazione risultati della domanda" value={selectedQuestion.resultsView||'bars'} onChange={e=>patch(selectedQuestion.id,{resultsView:e.target.value})}><option value="bars">Barre</option><option value="pie">Torta</option><option value="table">Tabella</option><option value="cloud">Nuvola animata</option></select></label>
 {selectedQuestion.kind==='timed-quiz'&&<label>Durata (secondi, 5–600)<input type="number" min={5} max={600} step={1} value={selectedQuestion.durationSeconds??30} onChange={e=>patch(selectedQuestion.id,{durationSeconds:Math.max(5,Math.min(600,Math.round(Number(e.target.value)||30)))})}/></label>}
 <label><input type="checkbox" checked={selectedQuestion.required!==false} onChange={e=>patch(selectedQuestion.id,{required:e.target.checked})}/> Risposta obbligatoria</label><p className="muted">Le modifiche vengono salvate automaticamente. Le modifiche alle risposte di un quiz live possono essere limitate dal server.</p></section>;
 return <div className="canvas-editor-group" data-canvas-device={mobileMode?'phone':'desktop'} data-tools-open={arrangeMenu} style={mobileMode?{'--phone-stage-height':`${mobileHeight}px`,'--phone-stage-ratio':`${MOBILE_PAGE_WIDTH}/${mobileHeight}`} as React.CSSProperties:undefined} onKeyDown={e=>{
 if(e.key==='Escape'){setContextWidget(null);setBackgroundMenu(false);setArrangeMenu(false)}
 if(!(e.ctrlKey||e.metaKey)||e.altKey||(e.target as HTMLElement).closest('input,textarea,select,[contenteditable=true],[role=textbox]'))return;
 const key=e.key.toLowerCase();
 if(key==='a'){e.preventDefault();setSelectedWidgets(widgets.map(w=>w.id));setActive(widgets[0]?.id||null)}
 else if(key==='d'&&active){e.preventDefault();duplicateSelected()}
 else if(key==='c'&&active){e.preventDefault();copySelectedWidget()}
 else if(key==='x'&&active){e.preventDefault();cutSelectedWidget()}
 else if(key==='v'&&readEditorWidgetClipboard(sessionId).length){e.preventDefault();pasteCopiedWidget()}
}}>{snapGrid&&<div className="widget-snap-grid" aria-hidden="true"/>}{alignmentGuides.length>0&&<div className="widget-alignment-guides" aria-hidden="true">{alignmentGuides.map(g=><span key={g.axis} className={"widget-alignment-guide axis-"+g.axis} data-guide-source={g.source} style={g.axis==='x'?{left:g.at+'%'}:{top:g.at+'%'}}/>)}</div>}{onBackgroundUpload&&<input ref={backgroundFileRef} style={{display:"none"}} aria-hidden="true" tabIndex={-1} type="file" accept="image/png,image/jpeg,image/gif,image/webp" disabled={assetBusy||backgroundUploading} onChange={e=>{const file=e.currentTarget.files?.[0];e.currentTarget.value="";if(!file)return;setBackgroundMenu(true);setBackgroundUploading(true);setBackgroundUploadStatus('Caricamento dello sfondo e applicazione alla pagina…');void onBackgroundUpload(file).then(applied=>{if(applied){setBackgroundUploadStatus('Sfondo caricato e applicato.');setBackgroundMenu(false)}else setBackgroundUploadStatus('Caricamento annullato: nessuna immagine applicata.')}).catch(error=>{setBackgroundUploadStatus('Caricamento non riuscito: '+(error instanceof Error?error.message:String(error)))}).finally(()=>setBackgroundUploading(false))}}/>} {contextWidget&&!onInspectWidget&&<div className="canvas-context-properties">{questionEditor}{cropEditor}{shapePaintEditor}</div>}<div className="canvas-editor-tools"><label><input type="checkbox" checked={snapGrid} onChange={e=>setSnapGrid(e.target.checked)}/> Aggancia alla griglia (5%)</label><button type="button" className="outline small" disabled={!active} onClick={copySelectedWidget}>Copia selezione</button><button type="button" className="outline small" disabled={!active} onClick={cutSelectedWidget}>Taglia selezione</button><button type="button" className="outline small" disabled={!clipboardAvailable} onClick={pasteCopiedWidget}>Incolla selezione</button><button type="button" className="outline small" disabled={!groupSelection().length} onClick={duplicateSelected}>Duplica selezione</button><button type="button" className="outline small" disabled={!groupSelection().length} onClick={deleteSelected}>Elimina selezione</button><span>Ctrl/Cmd+A seleziona tutti · Maiusc+clic seleziona più widget · trascina la selezione insieme · Ctrl/Cmd+C, X, V, D</span></div><div className="canvas-editor-tools" role="group" aria-label="Allineamento widget selezionati"><strong>{selectedWidgets.length} selezionati</strong>{([['left','Sinistra'],['center-x','Centro orizzontale'],['right','Destra'],['top','Alto'],['center-y','Centro verticale'],['bottom','Basso'],['same-width','Stessa larghezza'],['same-height','Stessa altezza'],['distribute-x','Distribuisci orizzontalmente'],['distribute-y','Distribuisci verticalmente'],['space-x','Spazi orizzontali uguali'],['space-y','Spazi verticali uguali'],['canvas-center-x','Centra selezione nel canvas orizzontalmente'],['canvas-center-y','Centra selezione nel canvas verticalmente'],['canvas-left','Allinea al bordo sinistro della pagina'],['canvas-right','Allinea al bordo destro della pagina'],['canvas-top','Allinea al bordo alto della pagina'],['canvas-bottom','Allinea al bordo basso della pagina']] as [ArrangeMode,string][]).map(([mode,label])=><button key={mode} type="button" className="outline small" disabled={selectedWidgets.length<(mode.startsWith('canvas-')?1:mode.startsWith('distribute')||mode.startsWith('space')?3:2)} onClick={()=>arrangeSelected(mode)}>{label}</button>)}<button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>{setSelectedWidgets([]);setActive(null)}}>Deseleziona</button><div className="canvas-editor-tools" role="group" aria-label="Ordine e spostamento widget selezionati"><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>layerSelected('front')}>Porta selezione davanti</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>layerSelected('back')}>Porta selezione dietro</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>layerSelected('forward')}>Un livello avanti</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>layerSelected('backward')}>Un livello indietro</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>nudgeSelected(-1,0)} aria-label="Sposta selezione a sinistra">←</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>nudgeSelected(1,0)} aria-label="Sposta selezione a destra">→</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>nudgeSelected(0,-1)} aria-label="Sposta selezione in alto">↑</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>nudgeSelected(0,1)} aria-label="Sposta selezione in basso">↓</button></div></div><div className="canvas-with-rulers"><div className="canvas-ruler-horizontal" aria-hidden="true">{Array.from({length:11},(_,i)=><span key={i}>{i*10}</span>)}</div><div className="canvas-ruler-vertical" aria-hidden="true">{Array.from({length:11},(_,i)=><span key={i}>{i*10}</span>)}</div><div className="widget-canvas" ref={ref} role="group" aria-label={mobileMode?"Canvas grafico smartphone":"Canvas grafico widget"} style={{"--editor-page-background":backgroundAssetId&&sessionId?`url(/api/sessions/${sessionId}/assets/${backgroundAssetId})`:"none",...(mobileMode?{'--editor-phone-background-color':mobileBackgroundColor||'#ffffff'}:{})} as React.CSSProperties} onClick={e=>{if(e.target===e.currentTarget){setSelectedWidgets([]);setActive(null);setEditing(null);setContextWidget(null)}}} onContextMenuCapture={handleCanvasContext} onPointerDownCapture={e=>{
  contextPointer.current=null;
  if(e.button!==2)return;
  const canvas=e.currentTarget;
  const direct=(e.target as Element).closest('.widget-canvas-item') as HTMLElement|null;
  const widget=direct&&canvas.contains(direct)?direct:canvasWidgetAtPoint(canvas,e.clientX,e.clientY);
  const id=widget?.dataset.widgetId;
  if(id&&widgets.some(w=>w.id===id))contextPointer.current={id,x:e.clientX,y:e.clientY,at:performance.now()};
 }} onPointerDown={e=>{if(e.pointerType!=="mouse"&&!(e.target as HTMLElement).closest("button,input,select,textarea,.widget-canvas-item")){clearContextHold();contextHold.current=setTimeout(openBlankMenu,580)}}} onPointerUp={clearContextHold} onPointerCancel={clearContextHold} onPointerLeave={clearContextHold} onDragOver={e=>{if(e.dataTransfer.types.includes('application/x-quorivio-widget'))e.preventDefault()}} onDrop={e=>{const kind=e.dataTransfer.getData('application/x-quorivio-widget');if(!kind||!['rating','reactions','text','shape','line','timer','qr','profile','question','postit','image','video','logo','pdf','topic-question','timed-quiz','results-button','participant-count','title','footer'].includes(kind))return;e.preventDefault();const b=ref.current?.getBoundingClientRect();const x=b?clamp((e.clientX-b.left)/b.width*100,0,72):0;const y=b?clamp((e.clientY-b.top)/b.height*100,0,76):0;{const position=kind==='footer'?newFooterWidget('new').position:freeWidgetPosition(widgets,{x,y},28,20);if(!position){window.alert('Non c’è spazio disponibile sul canvas per aggiungere questo widget.');return}onChange([...widgets,{...(kind==='footer'?newFooterWidget(crypto.randomUUID()):kind==='title'?newTitleWidget(pageTitle||'Titolo'):{}),id:crypto.randomUUID(),kind,...(['shape','line'].includes(kind)?{label:kind==='shape'?'Forma':'Linea',style:{fillNone:kind==='line',fillColor:kind==='shape'?'#dbeafe':'#ffffff',strokeWidth:2,strokeColor:'#334155',shapeType:'rectangle',lineDirection:'horizontal'}}:{}),...(kind==='results-button'&&eligibleStatisticSources(widgets).length?{targetWidgetId:eligibleStatisticSources(widgets)[0].id}:{}),label:kind==='footer'?'':kind==='qr'?'Accesso partecipanti':kind==='question'?'Nuova domanda':kind==='topic-question'?'Domande sul tema':kind,position:{...position,rotation:0}}])}}}>{backgroundMenu&&onBackgroundSelect&&createPortal(<div className="canvas-background-context canvas-background-context-floating" role="group" aria-label="Menu contestuale sfondo canvas" onContextMenu={e=>e.preventDefault()}><strong>Menu della pagina</strong>{onRenamePage&&<button type="button" onClick={()=>{setBackgroundMenu(false);onRenamePage()}}>Rinomina pagina</button>}<button type="button" onMouseDown={e=>e.stopPropagation()} onClick={()=>{setBackgroundMenu(false);setArrangeMenu(true)}}>Strumenti di selezione e allineamento</button><button type="button" title="Configurazione completa della pagina" onClick={()=>{onOpenPageSettings?.();setBackgroundMenu(false)}}>Impostazioni pagina e risultati</button><strong>{mobileMode?'Sfondo smartphone (indipendente dal desktop)':'Sfondo della pagina'}</strong>{mobileMode&&<label>Colore di sfondo smartphone<input type="color" aria-label="Colore sfondo smartphone" value={mobileBackgroundColor||'#ffffff'} onChange={e=>onBackgroundColorChange?.(e.target.value)}/></label>}<label>Sfondi dei presentatori{backgroundAssetId&&<small>Immagine applicata a questa pagina</small>}<select aria-label="Scegli sfondo canvas" value="" disabled={assetBusy} onChange={e=>{if(e.target.value)onBackgroundSelect(e.target.value)}}><option value="">Scegli dalla libreria</option>{backgrounds.map(a=><option key={a.id} value={a.id}>{a.mine?"Il mio sfondo":"Sfondo collaboratore"} · {new Date(a.created_at).toLocaleDateString("it-IT")} · {a.id.slice(0,8)}</option>)}</select></label>{onBackgroundUpload&&<button type="button" disabled={assetBusy||backgroundUploading} onClick={()=>{setBackgroundUploadStatus('');backgroundFileRef.current?.click()}}>Carica immagine nello sfondo e nella libreria…</button>}{backgroundUploadStatus&&<p className="canvas-background-upload-status" role="status" aria-live="polite">{backgroundUploadStatus}</p>}<button type="button" onClick={()=>{onBackgroundSelect("");setBackgroundMenu(false)}}>Rimuovi sfondo</button><button type="button" onClick={()=>{onSaveRequested?.();setBackgroundMenu(false)}}>Salva ora</button><button type="button" onClick={()=>setBackgroundMenu(false)}>Chiudi menu</button><small>Le modifiche vengono salvate automaticamente.</small></div>,document.body)}{widgets.map((w,i)=>{const pos=w.position||{x:4+(i%4)*24,y:4+Math.floor(i/4)*24,width:22,height:20,rotation:0};return <div key={w.id} className={'widget-canvas-item '+(selectedWidgets.includes(w.id)?'dragging':'')} data-widget-kind={w.kind} data-vertical-align={w.style?.verticalAlign||'top'} data-show-title={w.showTitle!==false} data-footer-separator={w.kind==='footer'?String(w.footerSeparator!==false):undefined} data-widget-id={w.id} {...widgetArtData(w.style)} onFocus={e=>{if(e.target===e.currentTarget)setActive(w.id)}} onClick={e=>{if(e.detail===0&&!(e.target as HTMLElement).closest('button,input,select,textarea'))toggleSelection(w.id,e.shiftKey)}} onContextMenu={e=>{e.preventDefault();e.stopPropagation();openWidgetContextMenu(w.id,e.currentTarget,e.clientX,e.clientY)}} onTouchStart={e=>{if((e.target as HTMLElement).closest("button,input,textarea,select"))return;const widgetElement=e.currentTarget;clearWidgetHold();widgetHold.current=setTimeout(()=>{positionMenu(widgetElement);setActive(w.id);setBackgroundMenu(false);setArrangeMenu(false);onContextOpen?.();setContextWidget(w.id)},600)}} onTouchMove={clearWidgetHold} onTouchEnd={clearWidgetHold} onTouchCancel={clearWidgetHold} style={{...widgetGeometryStyle(pos),...widgetAppearanceStyle(w.style,w.style?.fillImageAssetId&&sessionId?`/api/sessions/${sessionId}/assets/${w.style.fillImageAssetId}`:undefined),...widgetTypographyStyle(w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).style:w.style),...(mobileMode?{fontSize:`${w.style?.fontSize||16}px`,'--mobile-widget-font-size':`${w.style?.fontSize||16}px`}:{}),...(w.kind==='footer'?{'--footer-divider-color':w.footerSeparatorColor||'#9ca3af'} as React.CSSProperties:{})}} tabIndex={0} role="group" data-selected={selectedWidgets.includes(w.id)} onKeyDown={e=>{if(e.key==='ContextMenu'||(e.shiftKey&&e.key==='F10')){e.preventDefault();positionMenu(e.currentTarget);setContextWidget(w.id);setActive(w.id);onContextOpen?.();return}keyboardGeometry(e,w)}} aria-keyshortcuts="ArrowLeft ArrowRight ArrowUp ArrowDown Shift+ArrowRight Shift+ArrowDown Alt+ArrowRight Alt+ArrowDown Delete Backspace Escape" onPointerDown={e=>{if(!startsWidgetSelectionOnPointerDown(e.button))return;if(e.shiftKey){e.stopPropagation();toggleSelection(w.id,true);return}if(!selectedWidgets.includes(w.id))toggleSelection(w.id);down(e,w)}} onPointerMove={move} onPointerUp={end} onPointerCancel={cancelGesture} onLostPointerCapture={cancelGesture} onDoubleClick={e=>{if((e.target as HTMLElement).closest('[contenteditable=true]'))return;const targetField=(e.target as HTMLElement).closest('[data-widget-text-field]')?.getAttribute('data-widget-text-field')||'label';const root=e.currentTarget;setActive(w.id);setSelectedWidgets([w.id]);setRibbonDismissed(false);setContextWidget(null);setBackgroundMenu(false);setArrangeMenu(false);setEditing(w.id);setFormatScope(targetField.includes('option:')?'answers':targetField.endsWith('description')?'description':'label');requestAnimationFrame(()=>{const field=Array.from(root.querySelectorAll<HTMLElement>('[data-widget-text-field]')).find(node=>node.getAttribute('data-widget-text-field')===targetField)||root.querySelector<HTMLElement>('[contenteditable=true]');field?.focus()})}} aria-label={`Widget ${w.kind}; frecce spostano, Maiusc più frecce ridimensionano, Alt più frecce ruotano, Canc elimina`}>{w.kind!=='shape'&&<WidgetShapeOutline style={w.style}/>}<WidgetGraphic kind={w.kind} style={w.style}/><WidgetContentFit editor allowScale={!mobileMode&&editing!==w.id&&(w.kind!=='results-button'||w.autoFit!==false)} minScale={w.kind==='results-button'?.04:.12}>{w.showTitle!==false&&!(w.kind==='results-button'&&w.resultsOnly===true)&&<RichWidgetText value={w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).title:w.kind==='footer'?widgetDisplay(w,{sessionTitle,pageNumber}).center:w.label||''} marks={w.textMarks} field="label" active={editing===w.id} ariaLabel={'Titolo '+w.kind} maxLength={240} onSelection={r=>recordTextSelection(w.id,'label',r)} onChange={value=>editContent(w,'label',w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).title:w.kind==='footer'?widgetDisplay(w,{sessionTitle,pageNumber}).center:w.label||'',value,{label:value,...(w.kind==='title'?{titleFollowPage:false}:w.kind==='footer'?{footerShowSessionTitle:false}:{})})} onFinish={()=>setEditing(null)}/>}
 {(['question','timed-quiz'].includes(w.kind)&&(editing===w.id||!!w.description)||['text','postit'].includes(w.kind)&&editing===w.id)&&<RichWidgetText value={w.description||''} marks={w.textMarks} field="description" active={editing===w.id} ariaLabel={'Contenuto '+w.kind} maxLength={500} onSelection={r=>recordTextSelection(w.id,'description',r)} onChange={value=>editContent(w,'description',w.description||'',value,{description:value})} onFinish={()=>setEditing(null)}/>}
 {['question','timed-quiz'].includes(w.kind)&&Array.isArray(w.options)&&w.options.length>0&&<div className="canvas-widget-answer-preview" data-answer-mode={w.answerMode||'single'} style={answerOptionStyle(w.style)} aria-label="Opzioni di risposta del widget">{w.options.slice(0,12).map((o:any)=><label className="widget-answer-option" key={o.id||o.label}><input type={w.answerMode==='multiple'?'checkbox':'radio'} name={'editor-option-'+w.id} disabled tabIndex={-1} aria-hidden="true"/><RichWidgetText value={o.label} marks={w.textMarks} field={'option:'+o.id} active={editing===w.id} ariaLabel={'Modifica opzione '+o.label} maxLength={160} onSelection={r=>recordTextSelection(w.id,'option:'+o.id,r)} onChange={value=>editContent(w,'option:'+o.id,o.label,value,{options:w.options.map((item:any)=>item.id===o.id?{...item,label:value}:item)})} onFinish={()=>setEditing(null)}/></label>)}</div>}{['question','timed-quiz'].includes(w.kind)&&(w.questions||[]).map((q:any)=><div className="canvas-subquestion" data-question-id={q.id} key={q.id}>
  <RichWidgetText value={q.label} marks={w.textMarks} field={'question:'+q.id+':label'} active={editing===w.id} ariaLabel={'Domanda indipendente '+q.id} maxLength={240} onSelection={r=>recordTextSelection(w.id,'question:'+q.id+':label',r)} onChange={value=>{const updated=w.questions.map((item:any)=>item.id===q.id?{...item,label:value}:item);editContent(w,'question:'+q.id+':label',q.label,value,{questions:updated})}} onFinish={()=>setEditing(null)}/>
  {(editing===w.id||!!q.description)&&<RichWidgetText value={q.description||''} marks={w.textMarks} field={'question:'+q.id+':description'} active={editing===w.id} ariaLabel={'Descrizione domanda '+q.id} maxLength={500} onSelection={r=>recordTextSelection(w.id,'question:'+q.id+':description',r)} onChange={value=>{const updated=w.questions.map((item:any)=>item.id===q.id?{...item,description:value}:item);editContent(w,'question:'+q.id+':description',q.description||'',value,{questions:updated})}} onFinish={()=>setEditing(null)}/>}
  {['single','multiple'].includes(q.answerMode||'text')?(q.options||[]).map((o:any)=><div key={o.id} className="canvas-subquestion-option" style={answerOptionStyle(w.style)}><input type={(q.answerMode==='multiple'?'checkbox':'radio')} disabled tabIndex={-1} aria-hidden="true"/><RichWidgetText value={o.label} marks={w.textMarks} field={'question:'+q.id+':option:'+o.id} active={editing===w.id} ariaLabel={'Opzione '+q.id+' '+o.id} maxLength={160} onSelection={r=>recordTextSelection(w.id,'question:'+q.id+':option:'+o.id,r)} onChange={value=>{const updated=w.questions.map((item:any)=>item.id===q.id?{...item,options:item.options.map((x:any)=>x.id===o.id?{...x,label:value}:x)}:item);editContent(w,'question:'+q.id+':option:'+o.id,o.label,value,{questions:updated})}} onFinish={()=>setEditing(null)}/></div>):q.answerMode==='file'?<small>Risposta con allegato</small>:<EditorAnswerFieldPreview style={w.style} canvasRef={ref} onBeginGesture={onBeginGesture} onEndGesture={onEndGesture} onHeightChange={height=>patch(w.id,{style:{...w.style,answerFieldHeight:height}})}/>}
 <button type="button" className="canvas-widget-submit-preview" style={answerSubmitStyle(w.style)} disabled aria-label="Anteprima invio risposta della domanda">Invia risposta</button></div>)}{w.kind==='profile'&&w.description?.trim()&&<RichWidgetText value={w.description} marks={w.textMarks} field="description" active={editing===w.id} ariaLabel="Descrizione presentatore" maxLength={500} onSelection={r=>recordTextSelection(w.id,'description',r)} onChange={value=>editContent(w,'description',w.description||'',value,{description:value})} onFinish={()=>setEditing(null)}/>}{w.kind==='timer'&&<div className="widget-timer-design-preview" data-timer-face={widgetTimerFace(w.style)} role="img" aria-label="Anteprima artistica timer"><span className="widget-timer-design-hourglass" aria-hidden="true">{widgetTimerFace(w.style)==='dial'?'◷':widgetTimerFace(w.style)==='digital'?'▣':'⌛'}</span><span>{Math.floor((w.durationSeconds||60)/60)}:{String((w.durationSeconds||60)%60).padStart(2,'0')}</span></div>}{w.kind==='timed-quiz'&&<div className="canvas-widget-time-preview widget-timer-design-preview" data-timer-face={widgetTimerFace(w.style)} aria-label="Timer anteprima quiz"><span aria-hidden="true">{widgetTimerFace(w.style)==='dial'?'◷':widgetTimerFace(w.style)==='digital'?'▣':'⌛'}</span> {w.durationSeconds||30} secondi</div>}{w.kind==='question'&&(!w.options?.length)&&<div className="canvas-widget-answer-preview">{w.answerMode==='file'?<span>Allegato da inviare</span>:w.answerMode==='text'||!w.answerMode?<EditorAnswerFieldPreview style={w.style} canvasRef={ref} onBeginGesture={onBeginGesture} onEndGesture={onEndGesture} onHeightChange={height=>patch(w.id,{style:{...w.style,answerFieldHeight:height}})}/>:'Aggiungi opzioni dalla widget'}</div>}{w.kind==='topic-question'&&<div className="canvas-widget-answer-preview"><EditorAnswerFieldPreview questionField style={w.style} canvasRef={ref} onBeginGesture={onBeginGesture} onEndGesture={onEndGesture} onHeightChange={height=>patch(w.id,{style:{...w.style,answerFieldHeight:height}})}/></div>}{requiresAnswerSubmit(w.kind)&&<button type="button" className="canvas-widget-submit-preview" disabled tabIndex={-1} style={answerSubmitStyle(w.style)} aria-label="Anteprima pulsante invio risposte">{w.kind==='topic-question'?'Invia domanda':'Invia risposta'}</button>}{!['question','timed-quiz','topic-question','footer','title'].includes(w.kind)&&!(editing===w.id&&['text','postit'].includes(w.kind))&&<div className="canvas-widget-body-preview" aria-label={'Contenuto di prova '+w.kind}><ProjectionWidgetContent sessionId={sessionId} joinCode={joinCode} widget={['text','postit'].includes(w.kind)?{...w,label:''}:['rating','reactions','results-button'].includes(w.kind)?{...w,showTitle:false}:w} activity={{duration_seconds:w.durationSeconds||60}} peerWidgets={widgets}/></div>}</WidgetContentFit>{contextWidget===w.id&&createPortal(<div className="canvas-context-menu" style={{left:contextPoint.x,top:contextPoint.y}} role="group" aria-label={'Azioni widget '+w.kind} onPointerDown={e=>e.stopPropagation()}><button type="button" onClick={()=>{duplicateWidget(w);setContextWidget(null)}}>Duplica</button><button type="button" onClick={()=>{reorderWidget(w.id,'front');setContextWidget(null)}}>Porta avanti</button><button type="button" onClick={()=>{reorderWidget(w.id,'back');setContextWidget(null)}}>Porta indietro</button><button type="button" title="Configura questo widget" onClick={()=>{onInspectWidget?.(w.id);setContextWidget(null)}}>Proprietà widget</button><button type="button" onClick={()=>{setEditing(w.id);setContextWidget(null)}}>Modifica titolo</button>{['question','timed-quiz'].includes(w.kind)&&<button type="button" disabled={(w.questions||[]).length>=5} onClick={()=>{patch(w.id,{questions:[...(w.questions||[]),newIndependentQuestion(w.kind)]});setEditing(w.id);setContextWidget(null)}}>Aggiungi domanda indipendente</button>}{['question','timed-quiz'].includes(w.kind)&&<button type="button" disabled={(w.options||[]).length>=12} onClick={()=>{patch(w.id,{answerMode:w.answerMode||'single',options:[...(w.options||[]),{id:'opt_'+crypto.randomUUID().replace(/-/g,'').slice(0,24),label:'Nuova opzione'}]});setEditing(w.id);setContextWidget(null)}}>Aggiungi opzione di risposta</button>}{['image','video','logo','pdf'].includes(w.kind)&&<div className="canvas-context-assets"><label htmlFor={'canvas-asset-'+w.id}>Sostituisci file</label><select id={'canvas-asset-'+w.id} aria-label={'Seleziona asset '+w.kind} value={w.assetId||''} onChange={e=>patch(w.id,{assetId:e.target.value})}><option value="">Nessun file</option>{assets.filter(a=>w.kind==='pdf'?a.mime_type==='application/pdf':w.kind==='video'?a.mime_type.startsWith('video/'):a.mime_type.startsWith('image/')).map(a=><option key={a.id} value={a.id}>{a.mime_type} · {a.id.slice(0,8)}</option>)}</select>{onUpload&&<label className="canvas-context-upload">Carica nuovo file<input type="file" aria-label={'Carica file '+w.kind} accept={w.kind==='pdf'?'application/pdf':w.kind==='video'?'video/mp4,video/webm':'image/png,image/jpeg,image/gif,image/webp'} disabled={assetBusy} onChange={e=>{void onUpload(w.id,e.target.files?.[0],w.kind);e.target.value=''}}/></label>}<small>Salva il layout per applicare la modifica.</small></div>}<button type="button" onClick={()=>{if(!window.confirm('Eliminare questo widget dal canvas?'))return;onChange(widgets.filter(z=>z.id!==w.id));setActive(null);setContextWidget(null)}}>Elimina</button></div>,document.body)}<button type="button" className="canvas-remove" aria-label={'Rimuovi widget '+w.kind} title="Rimuovi widget" onClick={()=>{if(!window.confirm('Eliminare questo widget dal canvas?'))return;onChange(widgets.filter(z=>z.id!==w.id));setActive(null)}}>×</button><span className="widget-rotate-handle" data-rotate-handle="true" title="Ruota widget" aria-label="Ruota widget"/>{edges.map(edge=><span key={edge} role="presentation" data-resize-edge={edge} className={'widget-resize-edge edge-'+edge}/>)}</div>})}<SlideCanvasNumber widgets={widgets} pageNumber={pageNumber}/></div></div>{active&&!ribbonDismissed&&!suspendFormattingRibbon&&widgets.some(w=>w.id===active)&&<EditorFloatingWindow portal placement="palette" className="widget-selection-palette" role="toolbar" ariaLabel="Formattazione rapida widget selezionato" onMouseDownCapture={e=>{if((e.target as HTMLElement).closest("button"))e.preventDefault()}}>
 {(()=>{const w=widgets.find(z=>z.id===active)!;const style=w.style||{};
 const selectedRange=toolbarRange?.id===w.id&&editing===w.id?toolbarRange:null;
 const effectiveScope=selectedRange?(selectedRange.field.startsWith('option:')||selectedRange.field.includes(':option:')?'answers':selectedRange.field==='description'||selectedRange.field.includes(':description')?'description':'label'):formatScope;
 const activeTextField=selectedRange?selectedRange.field:effectiveScope==='label'?'label':effectiveScope==='description'?'description':null;
 const fieldText=(field:string):string=>{
  if(field==='label')return w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).title:w.kind==='footer'?widgetDisplay(w,{sessionTitle,pageNumber}).center:w.label||'';
  if(field==='description')return w.description||'';
  if(field.startsWith('option:'))return w.options?.find((o:any)=>'option:'+o.id===field)?.label||'';
  if(field.startsWith('question:')){const parts=field.split(':');const q=w.questions?.find((o:any)=>o.id===parts[1]);return parts[2]==='label'?q?.label||'':parts[2]==='description'?q?.description||'':q?.options?.find((o:any)=>o.id===parts[3])?.label||''}
  return '';
 };
 const baseline:InlineStyle=w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).style:style;
 const baselineField=effectiveScope==='answers'?{...baseline,fontFamily:style.answerFontFamily||style.fontFamily,fontSize:style.answerFontSize||style.fontSize,color:style.answerColor||style.color,bold:style.answerBold??style.bold,italic:style.answerItalic??style.italic}:baseline;
 const selectedValue=<K extends keyof InlineStyle>(key:K):InlineStyle[K]|undefined=>{
  if(selectedRange){
   const text=fieldText(selectedRange.field);
   const start=selectedRange.end>selectedRange.start?selectedRange.start:0;
   const end=selectedRange.end>selectedRange.start?selectedRange.end:text.length;
   if(end>start){const effective=selectionUniformValue(text,w.textMarks||[],selectedRange.field,start,end,baselineField,key);if(effective!==undefined)return effective;}
  }
  if(activeTextField){const text=fieldText(activeTextField);if(text.length){const effective=selectionUniformValue(text,w.textMarks||[],activeTextField,0,text.length,baselineField,key);if(effective!==undefined)return effective;}}
  return baselineField[key];
 };
 const selectedFlag=(key:'bold'|'italic'|'underline'|'strikethrough')=>selectedValue(key)===true;
 const selectedFont=selectedValue('fontFamily')||baseline.fontFamily||'Arial';
 const selectedSize=selectedValue('fontSize')||baseline.fontSize||16;
 const selectedColor=selectedValue('color')||baseline.color||'#000000';
 const setStyle=(changes:Record<string,unknown>)=>{
  const typographic=Object.keys(changes).every(k=>(inlineKeys as readonly string[]).includes(k));
  if(typographic&&activeTextField){
   const text=fieldText(activeTextField);
   const range=selectedRange?.field===activeTextField?selectedRange:null;
   const next=formatSelectedOrEntireField(w.textMarks||[],activeTextField,text,range,changes as InlineStyle);
   const freeze=w.kind==='title'&&activeTextField==='label'&&w.titleFollowPage!==false?{label:text,titleFollowPage:false}:w.kind==='footer'&&activeTextField==='label'&&w.footerShowSessionTitle!==false?{label:text,footerShowSessionTitle:false}:{};
   patch(w.id,{...freeze,textMarks:next});return;
  }
  if(effectiveScope==='answers'&&typographic){
   const mapping:Record<string,string>={fontFamily:'answerFontFamily',fontSize:'answerFontSize',color:'answerColor',bold:'answerBold',italic:'answerItalic'};
   const updated={...style};for(const [key,val] of Object.entries(changes))updated[mapping[key]||key]=val;
   const marks=(w.textMarks||[]).map((mark:TextMark)=>mark.field.startsWith('option:')||mark.field.includes(':option:')?{...mark,style:{...mark.style,...changes}}:mark);
   patch(w.id,{style:updated,textMarks:marks});return;
  }
  if(typographic){patch(w.id,applyAllWidgetTypeface(w,changes as InlineStyle));return;}
  patch(w.id,{style:{...style,...changes}});
 };
 const setSize=(next:number)=>{
  if(!Number.isInteger(next)||next<10||next>96)return;
  if(effectiveScope==='widget')patch(w.id,scaleAllWidgetTypography(w,next/(style.fontSize||16)));
  else setStyle({fontSize:next});
 };
 return <>
 <div className="palette-ribbon-head">
  <span className="palette-ribbon-context"><Type size={16} aria-hidden="true"/> Formato widget</span>
  <strong className="palette-widget-label" title={w.label||w.kind}>{w.label||w.kind}</strong>
  <span className="palette-ribbon-selection">{selectedRange&&selectedRange.end>selectedRange.start?`${selectedRange.end-selectedRange.start} caratteri selezionati`:'Seleziona del testo per formattarlo'}</span>
  <button type="button" className="palette-ribbon-dismiss" title="Chiudi finestra Formato widget senza deselezionare" aria-label="Chiudi Formato widget" onClick={()=>setRibbonDismissed(true)}><X size={17}/></button>
 </div>
 <div className="palette-ribbon-groups">
  <section className="palette-ribbon-group palette-ribbon-target" aria-label="Ambito formattazione">
   <div className="palette-ribbon-controls">
    <label>Applica a<select aria-label="Ambito della formattazione" value={effectiveScope} onChange={e=>{setFormatScope(e.target.value as 'widget'|'label'|'description'|'answers');setEditing(null);textSelection.current=null;setToolbarRange(null)}}>
     <option value="widget">Widget intero</option><option value="label">Titolo</option><option value="description">Descrizione</option>
     {['question','timed-quiz','topic-question'].includes(w.kind)&&<option value="answers">Risposte</option>}
    </select></label>
   </div><span className="palette-ribbon-group-title">Ambito</span>
  </section>
  <section className="palette-ribbon-group palette-ribbon-font" aria-label="Carattere">
   <div className="palette-ribbon-controls">
    <div className="palette-ribbon-font-picker">
     <select title="Tipo di carattere" aria-label="Font del testo" value={selectedFont} onChange={e=>setStyle({fontFamily:e.target.value})}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(font=><option key={font} value={font}>{font}</option>)}</select>
     {effectiveScope==='widget'?<div className="palette-ribbon-scale" role="group" aria-label="Scala proporzionale di tutti i testi"><button type="button" aria-label="Riduci tutti i testi del widget del 10%" onClick={()=>patch(w.id,scaleAllWidgetTypography(w,0.9))}>A−</button><button type="button" aria-label="Ingrandisci tutti i testi del widget del 10%" onClick={()=>patch(w.id,scaleAllWidgetTypography(w,1.1))}>A+</button></div>:<input type="number" title="Dimensione carattere del campo" min={10} max={96} value={selectedSize} aria-label="Dimensione del testo selezionato" onKeyDown={e=>e.stopPropagation()} onChange={e=>setSize(Number(e.target.value))}/>}
    </div>
    <div className="palette-ribbon-buttons" role="group" aria-label="Stile del testo">
     <button type="button" title="Grassetto (attiva o disattiva)" aria-label="Grassetto" aria-pressed={selectedFlag('bold')} onClick={()=>setStyle({bold:!selectedFlag('bold')})}><BoldIcon size={17}/></button>
     <button type="button" title="Corsivo (attiva o disattiva)" aria-label="Corsivo" aria-pressed={selectedFlag('italic')} onClick={()=>setStyle({italic:!selectedFlag('italic')})}><ItalicIcon size={17}/></button>
     <button type="button" title="Sottolineato (attiva o disattiva)" aria-label="Sottolineato" aria-pressed={selectedFlag('underline')} onClick={()=>setStyle({underline:!selectedFlag('underline')})}><UnderlineIcon size={17}/></button>
     <button type="button" title="Barrato (attiva o disattiva)" aria-label="Barrato" aria-pressed={selectedFlag('strikethrough')} onClick={()=>setStyle({strikethrough:!selectedFlag('strikethrough')})}><StrikethroughIcon size={17}/></button>
     <label className="palette-ribbon-color" title="Colore dei caratteri"><span className="palette-ribbon-color-letter" aria-hidden="true" style={{borderBottomColor:selectedColor}}>A</span><input type="color" aria-label="Colore del testo" value={selectedColor} onChange={e=>setStyle({color:e.target.value})}/></label>
    </div>
   </div>
   <span className="palette-ribbon-group-title">Carattere</span>
  </section>
  <section className="palette-ribbon-group palette-ribbon-paragraph" aria-label="Paragrafo">
   <div className="palette-ribbon-controls">
    <div className="palette-ribbon-buttons" role="group" aria-label="Allineamento del testo">
     <button type="button" title="Allinea a sinistra" aria-label="Allinea testo a sinistra" aria-pressed={(style.textAlign||'left')==='left'} onClick={()=>setStyle({textAlign:'left'})}><AlignLeft size={17}/></button>
     <button type="button" title="Centra testo" aria-label="Allinea testo al centro" aria-pressed={style.textAlign==='center'} onClick={()=>setStyle({textAlign:'center'})}><AlignCenter size={17}/></button>
     <button type="button" title="Allinea a destra" aria-label="Allinea testo a destra" aria-pressed={style.textAlign==='right'} onClick={()=>setStyle({textAlign:'right'})}><AlignRight size={17}/></button>
    </div>
    <div className="palette-ribbon-buttons" role="group" aria-label="Allineamento verticale del testo">
     <button type="button" title="Allinea testo in alto" aria-label="Allinea testo in alto" aria-pressed={(style.verticalAlign||'top')==='top'} onClick={()=>setStyle({verticalAlign:'top'})}>⇡</button>
     <button type="button" title="Centra testo verticalmente" aria-label="Centra testo verticalmente" aria-pressed={style.verticalAlign==='middle'} onClick={()=>setStyle({verticalAlign:'middle'})}>↕</button>
     <button type="button" title="Allinea testo in basso" aria-label="Allinea testo in basso" aria-pressed={style.verticalAlign==='bottom'} onClick={()=>setStyle({verticalAlign:'bottom'})}>⇣</button>
    </div><div className="palette-ribbon-help">Allineamento orizzontale e verticale</div>
   </div>
   <span className="palette-ribbon-group-title">Paragrafo</span>
  </section>
  <section className="palette-ribbon-group palette-ribbon-shape" aria-label="Formato forma">
   <div className="palette-ribbon-controls">
    <div className="palette-ribbon-buttons" role="group" aria-label="Riempimento e contorno">
     <label className="palette-ribbon-color" title="Riempimento forma"><PaintBucket size={17} aria-hidden="true"/><input aria-label="Colore di riempimento rapido" type="color" value={style.fillColor||'#ffffff'} onChange={e=>setStyle({fillColor:e.target.value,fillNone:false})}/></label>
     <button type="button" title="Nessun riempimento" aria-label="Riempimento trasparente" aria-pressed={!!style.fillNone} onClick={()=>setStyle({fillNone:!style.fillNone})}><span className="palette-ribbon-no-fill" aria-hidden="true"/></button>
     <label className="palette-ribbon-color" title="Colore del bordo"><Square size={17} aria-hidden="true"/><input aria-label="Colore bordo rapido" type="color" value={style.strokeColor||'#334155'} onChange={e=>setStyle({strokeColor:e.target.value,strokeNone:false,strokeWidth:style.strokeWidth||1})}/></label>
     <button type="button" title="Bordo tratteggiato / continuo" aria-label="Bordo tratteggiato" aria-pressed={style.strokeDash==='dash'} onClick={()=>setStyle({strokeDash:style.strokeDash==='dash'?'solid':'dash',strokeNone:false,strokeWidth:style.strokeWidth||1})}><span className="palette-ribbon-dashed" aria-hidden="true"/></button>
    </div>
    {['question','timed-quiz','topic-question'].includes(w.kind)&&<label className="palette-ribbon-answer" title="Sfondo risposta libera">Risposta <input aria-label="Colore sfondo casella risposta libera" type="color" value={style.answerFillColor||style.fillColor||'#ffffff'} onChange={e=>setStyle({answerFillColor:e.target.value})}/></label>}
   </div>
   <span className="palette-ribbon-group-title">Forma</span>
  </section>
  {requiresAnswerSubmit(w.kind)&&<section className="palette-ribbon-group palette-ribbon-answer-types" aria-label="Testo delle risposte">
    <div className="palette-ribbon-controls">
      <div className="palette-ribbon-font-picker">
        <select aria-label="Font delle risposte" title="Carattere della risposta" value={style.answerFontFamily||'Arial'} onChange={e=>patch(w.id,{style:{...style,answerFontFamily:e.target.value}})}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(font=><option key={font}>{font}</option>)}</select>
        <input aria-label="Dimensione testo risposte" type="number" min={10} max={96} value={style.answerFontSize||16} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=10&&n<=96)patch(w.id,{style:{...style,answerFontSize:n}})}}/>
      </div>
      <div className="palette-ribbon-buttons" role="group" aria-label="Stili risposte">
        <button type="button" title="Grassetto risposta" aria-label="Grassetto risposte" aria-pressed={!!style.answerBold} onClick={()=>patch(w.id,{style:{...style,answerBold:!style.answerBold}})}><BoldIcon size={16}/></button>
        <button type="button" title="Corsivo risposta" aria-label="Corsivo risposte" aria-pressed={!!style.answerItalic} onClick={()=>patch(w.id,{style:{...style,answerItalic:!style.answerItalic}})}><ItalicIcon size={16}/></button>
        <label className="palette-ribbon-color" title="Colore testo risposte"><span aria-hidden="true">A</span><input type="color" aria-label="Colore risposte" value={style.answerColor||'#152236'} onChange={e=>patch(w.id,{style:{...style,answerColor:e.target.value}})}/></label>
            <label className="palette-ribbon-answer" title="Larghezza del campo di risposta libera">Campo % <input type="number" aria-label="Larghezza risposta libera" min={25} max={100} step={5} value={style.answerFieldWidth||100} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=25&&n<=100)setStyle({answerFieldWidth:n})}}/></label>
        <label className="palette-ribbon-answer" title="Altezza del campo di risposta libera">Campo px <input type="number" aria-label="Altezza risposta libera" min={48} max={400} step={8} value={style.answerFieldHeight||96} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=48&&n<=400)setStyle({answerFieldHeight:n})}}/></label>
    <label className="palette-ribbon-answer" title="Dimensione del pulsante di invio">Invia <input type="number" aria-label="Dimensione tasto invio" min={12} max={40} value={style.submitButtonSize||16} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=12&&n<=40)setStyle({submitButtonSize:n})}}/></label>
      </div>
    </div><span className="palette-ribbon-group-title">Risposte</span>
  </section>}
  {w.kind==='footer'&&<section className="palette-ribbon-group" aria-label="Formato numero pagina">
    <div className="palette-ribbon-controls"><strong>Numero pagina</strong>
     <label>Font<select aria-label="Font numero pagina" value={style.footerNumberFontFamily||style.fontFamily||'Arial'} onChange={e=>patch(w.id,{style:{...style,footerNumberFontFamily:e.target.value}})}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(font=><option key={font} value={font}>{font}</option>)}</select></label>
     <label>Dimensione<input type="number" aria-label="Dimensione numero pagina" min={8} max={96} step={1} value={style.footerNumberFontSize||style.fontSize||14} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=8&&n<=96)patch(w.id,{style:{...style,footerNumberFontSize:n}})}}/></label>
     <label>Colore<input type="color" aria-label="Colore numero pagina" value={style.footerNumberColor||style.color||'#26364a'} onChange={e=>patch(w.id,{style:{...style,footerNumberColor:e.target.value}})}/></label>
     <label>Destra (px)<input type="number" aria-label="Padding destro numero pagina" min={0} max={80} value={style.footerNumberPaddingRight??5} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=0&&n<=80)patch(w.id,{style:{...style,footerNumberPaddingRight:n}})}}/></label>
     <label>Sotto (px)<input type="number" aria-label="Padding inferiore numero pagina" min={0} max={80} value={style.footerNumberPaddingBottom??5} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=0&&n<=80)patch(w.id,{style:{...style,footerNumberPaddingBottom:n}})}}/></label>
    </div><span className="palette-ribbon-group-title">Numero pagina</span></section>}
   {w.kind==='reactions'&&<section className="palette-ribbon-group" aria-label="Dimensione reazioni"><label>Dimensione emoji (px)<input type="number" aria-label="Dimensione emoji reazioni" min={16} max={96} value={w.reactionIconSize??32} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=16&&n<=96)patch(w.id,{reactionIconSize:n})}}/></label></section>}
   {w.kind==='rating'&&<section className="palette-ribbon-group" aria-label="Dimensione pulsanti gradimento"><label>Dimensione voto (px)<input type="number" aria-label="Dimensione pulsanti gradimento" min={10} max={64} value={style.ratingButtonSize??16} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=10&&n<=64)patch(w.id,{style:{...style,ratingButtonSize:n}})}}/></label></section>}
  <section className="palette-ribbon-group palette-ribbon-arrange" aria-label="Disponi">
   <div className="palette-ribbon-controls">
    <div className="palette-ribbon-buttons" role="group" aria-label="Posizione sul canvas">
     <button type="button" title="Centra il widget orizzontalmente" aria-label="Centra widget nel canvas" onClick={()=>arrangeSelected('canvas-center-x')}><MoveHorizontal size={18}/></button>
     <button type="button" title="Centra il widget verticalmente" aria-label="Centra widget in verticale" onClick={()=>arrangeSelected('canvas-center-y')}><MoveVertical size={18}/></button>
     <button type="button" title="Apri tutte le proprietà" aria-label="Mostra proprietà complete del widget" onClick={()=>onInspectWidget?.(w.id)}><SlidersHorizontal size={18}/></button>
    </div>
    {w.kind==='rating'&&<button type="button" className="palette-ribbon-rating" title="Visualizzazione gradimento" aria-label="Cambia visualizzazione gradimento" onClick={()=>setStyle({ratingView:style.ratingView==='select'?'buttons':'select'})}>0–9 ▾</button>}
   </div>
   <span className="palette-ribbon-group-title">Disponi</span>
  </section>
 </div> </>})()}
 </EditorFloatingWindow>}<details className="canvas-accessible-controls" role="region" aria-label="Organizzazione accessibile dei widget" onToggle={e=>{if(e.currentTarget.open)setBackgroundMenu(false)}}><summary>Controlli accessibili per tastiera e touchscreen</summary><h4>Widget della pagina</h4><p>Controlli alternativi per touchscreen e tastiera. Le frecce spostano di 5% e le modifiche usano lo stesso salvataggio del canvas.</p><div className="canvas-accessible-list">{widgets.map((w,i)=><div className="canvas-accessible-row" key={w.id}><strong>{i+1}. {w.label||w.kind}</strong><label><input type="checkbox" checked={selectedWidgets.includes(w.id)} onChange={e=>{setSelectedWidgets(old=>e.target.checked?[...new Set([...old,w.id])]:old.filter(id=>id!==w.id));setActive(w.id)}}/> Seleziona</label><div role="group" aria-label={'Posizione e livello '+(w.label||w.kind)}><button type="button" aria-label={'Sposta '+(w.label||w.kind)+' a sinistra'} onClick={()=>nudge(w,'x',-5)}>←</button><button type="button" aria-label={'Sposta '+(w.label||w.kind)+' a destra'} onClick={()=>nudge(w,'x',5)}>→</button><button type="button" aria-label={'Sposta '+(w.label||w.kind)+' in alto'} onClick={()=>nudge(w,'y',-5)}>↑</button><button type="button" aria-label={'Sposta '+(w.label||w.kind)+' in basso'} onClick={()=>nudge(w,'y',5)}>↓</button><button type="button" aria-label={'Duplica '+(w.label||w.kind)} onClick={()=>duplicateWidget(w)}>⧉</button><button type="button" aria-label={'Porta in primo piano '+(w.label||w.kind)} onClick={()=>reorderWidget(w.id,'front')}>Primo piano</button><button type="button" aria-label={'Porta sullo sfondo '+(w.label||w.kind)} onClick={()=>reorderWidget(w.id,'back')}>Sfondo</button></div></div>)}</div></details></div>
}

function CalendarAgenda({date,setDate,view,setView,entries,onSelect}:{date:string;setDate:(s:string)=>void;view:'day'|'week'|'month';setView:(s:'day'|'week'|'month')=>void;entries:any[];onSelect:(id:string)=>void}){
 const selected=new Date(date+'T12:00:00');const today=new Date().toLocaleDateString('en-CA');
 const iso=(d:Date)=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
 const first=new Date(selected);if(view==='month'){first.setDate(1);first.setDate(first.getDate()-(first.getDay()+6)%7)}else if(view==='week')first.setDate(first.getDate()-(first.getDay()+6)%7);
 const count=view==='day'?1:view==='week'?7:Math.ceil(((new Date(selected.getFullYear(),selected.getMonth()+1,0).getDate()+(new Date(selected.getFullYear(),selected.getMonth(),1).getDay()+6)%7)/7))*7;
 const days=Array.from({length:count},(_,i)=>{const d=new Date(first);d.setDate(d.getDate()+i);return iso(d)});
 const move=(direction:number)=>{const d=new Date(selected);if(view==='month')d.setMonth(d.getMonth()+direction);else d.setDate(d.getDate()+direction*(view==='week'?7:1));setDate(iso(d))};
 return <div className="agenda"><div className="agenda-toolbar"><div><h2>Calendario sessioni</h2><p className="muted">{selected.toLocaleDateString('it-IT',{month:'long',year:'numeric'})}</p></div><div className="agenda-controls"><button className="outline small" onClick={()=>setDate(today)}>Oggi</button><button className="outline small" aria-label="Precedente" onClick={()=>move(-1)}>‹</button><button className="outline small" aria-label="Successivo" onClick={()=>move(1)}>›</button><input aria-label="Seleziona data" type="date" value={date} onChange={e=>setDate(e.target.value)}/><select aria-label="Vista calendario" value={view} onChange={e=>setView(e.target.value as 'day'|'week'|'month')}><option value="day">Giorno</option><option value="week">Settimana</option><option value="month">Mese</option></select></div></div><div className={'agenda-grid agenda-'+view} role="grid" aria-label="Calendario sessioni">{days.map(day=><div role="gridcell" key={day} className={'agenda-day'+(day===today?' agenda-today':'')+(day.slice(0,7)!==date.slice(0,7)?' agenda-outside':'')}><button className="agenda-date" aria-label={'Apri '+day} onClick={()=>{setDate(day);setView('day')}}>{new Date(day+'T12:00:00').toLocaleDateString('it-IT',{weekday:'short',day:'numeric'})}</button><div className="agenda-events">{entries.filter((a:any)=>a.date===day).sort((a:any,b:any)=>String(a.start_time).localeCompare(String(b.start_time))).map((a:any)=><button key={a.id} className="agenda-event" title={`${a.title} · ${a.duration_minutes} min · ${a.time_zone}`} onClick={()=>onSelect(a.session_id)}><strong>{a.start_time}</strong> {a.title}<small>{a.duration_minutes} min · {a.time_zone}</small></button>)}</div></div>)}</div></div>
}
/** Keep account-specific SSO state out of public provider discovery. */
function FederatedIdentities({providers,onMessage}:{providers:{id:string;label?:string}[];onMessage:(message:string)=>void}){
 const [identities,setIdentities]=useState<{provider:string;linked_at:string}[]>([]);
 const [loading,setLoading]=useState(true);
 const [problem,setProblem]=useState('');
 const [password,setPassword]=useState('');
 const [selected,setSelected]=useState('');
 const [busy,setBusy]=useState(false);
 async function refresh(){
  setLoading(true);try{const result=await request<{identities:{provider:string;linked_at:string}[]}>('/auth/identities');setIdentities(result.identities);setProblem('')}
  catch(e){setProblem(e instanceof Error?e.message:'Errore di lettura delle identità')}
  finally{setLoading(false)}
 }
 useEffect(()=>{void refresh()},[]);
 async function unlinkIdentity(provider:string){
  if(busy||!password||selected!==provider)return;
  setBusy(true);try{
   await request('/auth/identities/unlink','POST',{provider,password});
   setPassword('');setSelected('');await refresh();onMessage('Identità scollegata. / Identity disconnected.');
  }catch(e){setProblem(e instanceof Error?e.message:'Impossibile scollegare l’identità')}
  finally{setBusy(false)}
 }
 return <section className="panel" aria-label="Gestione delle identità federate">
  <h3>Identità federate / SSO</h3>
  <p>Gestisci le identità con cui accedi. Per scollegarne una è richiesta la password del tuo account Quorivio.</p>
  <h4>Identità collegate / Linked identities</h4>
  {loading?<p role="status">Caricamento…</p>:identities.length?<ul>{identities.map(identity=><li key={identity.provider}>
   <strong>{providers.find(p=>p.id===identity.provider)?.label||identity.provider}</strong>
   <span className="muted tiny"> · Collegata / Linked {new Date(identity.linked_at).toLocaleDateString()}</span>
   {selected===identity.provider?<div className="panel" style={{marginTop:8}}>
    <p>Confermi di voler scollegare {identity.provider}? L’accesso tramite questa identità non funzionerà più finché non la ricolleghi.</p>
    <label>Password account / Current password<input type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} maxLength={256}/></label>
    <div className="activity-row"><button type="button" className="small" disabled={busy||!password} onClick={()=>void unlinkIdentity(identity.provider)}>Conferma scollegamento / Unlink</button>
    <button type="button" className="small outline" disabled={busy} onClick={()=>{setSelected('');setPassword('')}}>Annulla / Cancel</button></div>
   </div>:<button type="button" className="small outline" disabled={busy} onClick={()=>{setSelected(identity.provider);setPassword('');setProblem('')}}>Scollega / Unlink</button>}
  </li>)}</ul>:<p className="muted tiny">Nessuna identità collegata. / No linked identities.</p>}
  {problem&&<p role="alert">{problem}</p>}
  <button type="button" className="outline small" disabled={loading||busy} onClick={()=>void refresh()}>Aggiorna elenco / Refresh</button>
  <h4>Collega identità / Link identity</h4>
  {providers.length?<div className="activity-row">{providers.filter(p=>!identities.some(i=>i.provider===p.id)).map(p=><a key={p.id} className="button outline small" href={'/api/auth/'+(['github','facebook'].includes(p.id)?'social':'oidc')+'/'+encodeURIComponent(p.id)+'/start?link=true'}>Collega {p.label||p.id.toUpperCase()}</a>)}
  {providers.every(p=>identities.some(i=>i.provider===p.id))&&<p>Provider disponibili già collegati.</p>}</div>:<p className="muted tiny">Nessun provider configurato. Configura OIDC_PROVIDERS_JSON o OIDC_GOOGLE_* (oppure OAUTH_GITHUB_*/OAUTH_FACEBOOK_*) sul server.</p>}
 </section>;
}

// Authenticated projection screen. Audience clients receive a different snapshot
// through the live socket and never receive presenter navigation controls.
function PresenterLiveScreen({sessionId,renderResults}:{sessionId:string;renderResults:(s:Snapshot,a:Activity,mode?:string)=>React.ReactNode}){
 const [verified,setVerified]=useState(false);
 const [screenError,setScreenError]=useState('');
 const [data,setData]=useState<Snapshot|null>(null);
 const [connection,setConnection]=useState<'connecting'|'connected'|'disconnected'|'blocked'>('connecting');
 useLive(sessionId,setData,setConnection);
 const [busy,setBusy]=useState(false);
 const [full,setFull]=useState(false);
 const [mobileControls,setMobileControls]=useState(()=>window.matchMedia('(hover: none), (pointer: coarse)').matches);
 const stageRef=useRef<HTMLElement|null>(null);
 const pending=useRef(false);
 const activities=data?.activities||[];
 const currentId=data?.session?.current_activity_id;
 const active=data?.session?.status==='active';
 const index=presenterPageIndex(activities,currentId);
 const previous=presenterAdjacentPage(activities,currentId,-1);
 const next=presenterAdjacentPage(activities,currentId,1);
 const current=index>=0?activities[index]:null;
 useEffect(()=>{
  let mounted=true;
  setVerified(false);setData(null);setScreenError('');
  (async()=>{
   try{
    const s=await request<Snapshot>(`/sessions/${encodeURIComponent(sessionId)}`);
    if(!mounted)return;
    setVerified(true);setData(s);
    if(['active','ready'].includes(s.session.status)&&!s.session.current_activity_id&&s.activities.length){
     await request(`/sessions/${encodeURIComponent(sessionId)}/presentation/ensure-first-page`,'POST');
     const fresh=await request<Snapshot>(`/sessions/${encodeURIComponent(sessionId)}`);
     if(mounted)setData(fresh);
    }
   }catch(e){if(mounted)setScreenError(e instanceof Error?e.message:String(e))}
  })();
  return()=>{mounted=false};
 },[sessionId]);
 useEffect(()=>{
  const monitor=()=>setFull(document.fullscreenElement===stageRef.current);
  const mq=window.matchMedia('(hover: none), (pointer: coarse)');
  const update=()=>setMobileControls(mq.matches);
  document.addEventListener('fullscreenchange',monitor);mq.addEventListener('change',update);
  return()=>{document.removeEventListener('fullscreenchange',monitor);mq.removeEventListener('change',update)};
 },[]);
 const changePage=async(direction:-1|1)=>{
  if(!verified||!data||data.session.status!=='active'||pending.current)return;
  const target=presenterAdjacentPage(data.activities,data.session.current_activity_id,direction);
  if(!target)return;
  pending.current=true;setBusy(true);setScreenError('');
  try{
   await request(`/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(target.id)}/open`,'POST',{expected_current_activity_id:data.session.current_activity_id});
   setData(await request<Snapshot>(`/sessions/${encodeURIComponent(sessionId)}`));
  }catch(e){setScreenError(e instanceof Error?e.message:String(e));
   try{setData(await request<Snapshot>(`/sessions/${encodeURIComponent(sessionId)}`))}catch{}
  }finally{pending.current=false;setBusy(false)}
 };
 const latest=useRef(changePage);latest.current=changePage;
 useEffect(()=>{
  const onKey=(event:KeyboardEvent)=>{
   if(!verified||!active)return;
   const direction=presenterKeyboardDirection(event);
   if(direction===null)return;
   event.preventDefault();void latest.current(direction);
  };
  window.addEventListener('keydown',onKey);
  return()=>window.removeEventListener('keydown',onKey);
 },[verified,active]);
 const toggleFullscreen=async()=>{
  try{
   if(document.fullscreenElement===stageRef.current)await document.exitFullscreen();
   else await stageRef.current?.requestFullscreen();
  }catch(e){setScreenError(e instanceof Error?e.message:String(e))}
 };
 return <main id="main-content" ref={stageRef} className={'projection presenter-stage'+(mobileControls?' touch-controls':'')} style={data?.session?.theme?.backgroundUrl?{backgroundImage:`url(${data.session.theme.backgroundUrl})`,backgroundSize:'cover'}:undefined}>
  {!verified&&!screenError&&<div className="panel centered" role="status">Verifica accesso allo schermo presentatore…</div>}
  {verified&&<>
   <div className="presenter-stage-header"><div className="eyebrow"><Radio size={18}/> SCHERMO PRESENTATORE</div>
    <div className="presenter-stage-tools"><span className="presenter-page-indicator" aria-live="polite">{index>=0?`Pagina ${index+1} / ${activities.length}`:`${activities.length} pagine`}</span><button type="button" className="small outline" onClick={()=>void toggleFullscreen()} aria-label={full?'Esci dallo schermo intero':'Vai a schermo intero'}>{full?'Esci dallo schermo intero':'Schermo intero'} <Maximize2 size={15}/></button></div></div>
   {connection==='disconnected'||connection==='blocked'?<div className="live-stale-warning" role="status" aria-live="polite">{connection==='blocked'?'Connessione live non autorizzata':'Connessione live interrotta: aggiornamento in corso'}</div>:null}
   {screenError&&<div role="alert" className="presenter-stage-error">{screenError}</div>}
   {data?.session?.status==='paused'?<section className="panel centered"><h2>Presentazione in pausa</h2></section>:
    data?.session?.status==='closed'?<section className="panel centered"><h2>Sessione terminata</h2></section>:
    data?.session?.status==='ready'||data?.session?.status==='draft'?<section className="panel centered"><h2>Presentazione non ancora avviata</h2><p>Apri una sessione pronta per iniziare dalla prima pagina.</p></section>:
    current&&data?<section key={current.id} className="presenter-stage-slide" aria-label={`Pagina ${index+1}: ${current.title}`}>
     {!resolveSlideMasterWidgets(current.page_design?.widgets||[],data.session.theme?.master?.widgets).some((w:any)=>w.kind==='title')&&<h2>{current.title}</h2>}
     {current.type==='timed_quiz'&&<PageTimer openedAt={current.opened_at} duration={current.duration_seconds} label="Quiz a tempo"/>}
     <PresenterPageResults sessionId={sessionId} activity={current} snapshot={data} renderResults={renderResults}/>
    </section>:<section className="panel centered"><h2>In attesa di una pagina</h2><p>Nessuna pagina disponibile per la proiezione.</p></section>}
   {active&&current&&<nav className="presenter-slide-navigation" aria-label="Navigazione pagine del presentatore">
    <div className="presenter-nav-zone previous"><button type="button" className="presenter-nav-arrow" disabled={!previous||busy} aria-label="Pagina precedente" title="Precedente (←)" onClick={()=>void changePage(-1)}>‹</button></div>
    <div className="presenter-nav-zone next"><button type="button" className="presenter-nav-arrow" disabled={!next||busy} aria-label="Pagina successiva" title="Successiva (→)" onClick={()=>void changePage(1)}>›</button></div>
   </nav>}
  </>}
  {screenError&&!verified&&<div role="alert" className="panel">Accesso non autorizzato o schermo non disponibile: {screenError}</div>}
 </main>;
}

function App(){const [lang,setLang]=useState<'it'|'en'>('it');const t=text[lang];const pc=participantCopy[lang];const [me,setMe]=useState<any>(undefined);const [oidcProviders,setOidcProviders]=useState<{id:string;label?:string}[]>([]);useEffect(()=>{void request<{providers:{id:string;label?:string}[]}>('/auth/oidc/providers').then(v=>setOidcProviders(v.providers)).catch(()=>{})},[]);const [sessions,setSessions]=useState<Session[]>([]);const [selected,setSelected]=useState<string>(()=>readWorkspaceLocation().sessionId);const [snap,setSnap]=useState<Snapshot|null>(null);const [error,setError]=useState('');const [email,setEmail]=useState('');const [password,setPassword]=useState('');const [emailChallenge,setEmailChallenge]=useState('');const [mfaMethods,setMfaMethods]=useState<string[]>([]);const [mfaMethod,setMfaMethod]=useState('');const [showRecovery,setShowRecovery]=useState(false);const [emailCode,setEmailCode]=useState('');const [emailMfaPassword,setEmailMfaPassword]=useState('');const [emailEnrollmentId,setEmailEnrollmentId]=useState('');const [emailEnrollmentCode,setEmailEnrollmentCode]=useState('');const [totpCode,setTotpCode]=useState('');const [recoveryCode,setRecoveryCode]=useState('');const [recoveryCodes,setRecoveryCodes]=useState<string[]>([]);const [resetToken,setResetToken]=useState(()=>consumeRecoveryTokenFromUrl(window.location,window.history));const [resetPassword,setResetPassword]=useState('');const [resetPasswordConfirmation,setResetPasswordConfirmation]=useState('');const [resetSubmitPending,setResetSubmitPending]=useState(false);const resetSubmitLock=useRef(false);const [enrollment,setEnrollment]=useState<any>(null);const [mfaAdminCode,setMfaAdminCode]=useState('');const [smtpStatus,setSmtpStatus]=useState<any>(null);const [smtpRecipient,setSmtpRecipient]=useState('');const [smtpForm,setSmtpForm]=useState({host:'',port:465,user:'',password:'',from:'',senderName:'',secure:true});const [dashboardPage,setDashboardPage]=useState<'workspace'|'new'|'open'|'calendar'|'session'|'master'|'users'|'settings'|'sso'|'mfa'|'profile'>(readWorkspaceLocation().section);const [sidebarRename,setSidebarRename]=useState<string|null>(null);const [sidebarBusy,setSidebarBusy]=useState(false);const [selectedSessionRole,setSelectedSessionRole]=useState<'owner'|'collaborator'|null>(null);const [schemaWidgets,setSchemaWidgets]=useState<any[]>([]);const [schemaSaving,setSchemaSaving]=useState(false);const [schemaInspected,setSchemaInspected]=useState('');const [schemaSelected,setSchemaSelected]=useState<string[]>([]);const schemaBaseline=useRef('');const [title,setTitle]=useState('');const [newTitle,setNewTitle]=useState('');const [newReferenceDate,setNewReferenceDate]=useState('');const [sessionTitleEdit,setSessionTitleEdit]=useState('');const [sessionDateEdit,setSessionDateEdit]=useState('');const [scheduleDates,setScheduleDates]=useState<string[]>([]);const [scheduleNewDate,setScheduleNewDate]=useState('');const [appointments,setAppointments]=useState<{date:string;start_time:string;duration_minutes:number;time_zone:string}[]>([]);const [appointmentDate,setAppointmentDate]=useState('');const [appointmentTime,setAppointmentTime]=useState('09:00');const [appointmentMinutes,setAppointmentMinutes]=useState(60);const [appointmentZone,setAppointmentZone]=useState(Intl.DateTimeFormat().resolvedOptions().timeZone||'Europe/Rome');const [calendarMonth,setCalendarMonth]=useState(new Date().toLocaleDateString('en-CA'));const [calendarView,setCalendarView]=useState<'day'|'week'|'month'>('month');const [globalAppointments,setGlobalAppointments]=useState<any[]>([]);const [rehearsalOpen,setRehearsalOpen]=useState(false);const [rehearsalMode,setRehearsalMode]=useState<RehearsalMode>('participant');const [sessionTab,setSessionTab]=useState<'overview'|'pages'|'audience'|'results'>(()=>readWorkspaceLocation().tab);const [designActivity,setDesignActivity]=useState('');const [pageThumbMenu,setPageThumbMenu]=useState('');const [pageExportError,setPageExportError]=useState('');const [pageContextOpen,setPageContextOpen]=useState(false);const [inspectedWidget,setInspectedWidget]=useState('');const [editorTouchHint,setEditorTouchHint]=useState('');useEffect(()=>{if(!editorTouchHint)return;const id=window.setTimeout(()=>setEditorTouchHint(''),2400);return()=>window.clearTimeout(id)},[editorTouchHint]);const savedPageDraft=useRef('');const loadedDesignRevision=useRef(1);const [pageConflict,setPageConflict]=useState(false);const [mergeCandidate,setMergeCandidate]=useState<{remote:EditablePageDraft;revision:number;snapshot:Snapshot;base?:EditablePageDraft;local?:EditablePageDraft}|null>(null);const [mergeChoices,setMergeChoices]=useState<Record<string,MergeChoice>>({});type EditorWidgetPermissionFields = Pick<NonNullable<PageDesign['widgets']>[number], 'allowAnswerChange' | 'showEmail' | 'reactionIconSize' | 'titleFollowPage' | 'titleUseMaster' | 'footerShowSessionTitle' | 'footerShowPageNumber' | 'showTitle' | 'autoFit' | 'resultsOnly' | 'position' | 'resultTopCount'>;
const [widgetHistory,setWidgetHistory]=useState(()=>newWidgetHistory<{id:string;kind:string;label?:string;description?:string;answerMode?:string;options?:{id:string;label:string}[];required?:boolean;durationSeconds?:number;correctOptionId?:string;correctOptionIds?:string[];questions?:WidgetSubquestion[];textMarks?:WidgetInlineMark[];assetId?:string;targetWidgetId?:string;targetQuestionId?:string;style?:WidgetTextStyle} & EditorWidgetPermissionFields>([]));
const pageWidgets=widgetHistory.present;
useEffect(()=>{if(inspectedWidget&&!pageWidgets.some(w=>w.id===inspectedWidget))setInspectedWidget('')},[pageWidgets,inspectedWidget]);
const setPageWidgets:React.Dispatch<React.SetStateAction<typeof pageWidgets>>=(next)=>setWidgetHistory(history=>{const updated=typeof next==='function'?next(history.present):next;const validIds=new Set(updated.map(w=>w.id));return editWidgets(history,updated.map(w=>{if(w.kind!=='results-button'||!w.targetWidgetId)return w;const source=updated.find(s=>s.id===w.targetWidgetId);if(!source)return {...w,targetWidgetId:undefined,targetQuestionId:undefined};if(w.targetQuestionId&&!source.questions?.some(q=>q.id===w.targetQuestionId))return {...w,targetQuestionId:undefined};return w}));});
const reconcilePageAutoFit=React.useCallback((base:typeof pageWidgets, fitted:typeof pageWidgets)=>setWidgetHistory(h=>reconcileWidgetAutoFit(h,base,fitted)),[]);
const resetPageWidgets=(next:typeof pageWidgets)=>setWidgetHistory(newWidgetHistory(next));
const undoPageWidgets=()=>setWidgetHistory(undoWidgets);
const redoPageWidgets=()=>setWidgetHistory(redoWidgets);
const beginPageWidgetGesture=()=>setWidgetHistory(beginWidgetGesture);
const endPageWidgetGesture=()=>setWidgetHistory(endWidgetGesture);const [ratingSent,setRatingSent]=useState<string[]>([]);const [ratingPending,setRatingPending]=useState<string[]>([]);const pendingRatingVotes=useRef(new Set<string>());const [ratingVotes,setRatingVotes]=useState<Record<string,string>>({});const [ratingComments,setRatingComments]=useState<Record<string,string>>({});const [participantReadingMode,setParticipantReadingMode]=useState(()=>window.matchMedia('(max-width:700px)').matches);const [myProfile,setMyProfile]=useState<any>(null);const [profileName,setProfileName]=useState('');const [nickname,setNickname]=useState('');const [photoBusy,setPhotoBusy]=useState(false);const [profileSaving,setProfileSaving]=useState(false);const [adminSavingId,setAdminSavingId]=useState('');const [photoVersion,setPhotoVersion]=useState(0);const [profilePhoto,setProfilePhoto]=useState('');const [availablePresenters,setAvailablePresenters]=useState<any[]>([]);const [ratingStats,setRatingStats]=useState<any>(null);const [questionHeader,setQuestionHeader]=useState('');const [resultHeader,setResultHeader]=useState('');const [questionBackground,setQuestionBackground]=useState('');const [questionBackgroundColor,setQuestionBackgroundColor]=useState('');const [resultBackground,setResultBackground]=useState('');const [resultBackgroundColor,setResultBackgroundColor]=useState('');const [questionBackgroundAsset,setQuestionBackgroundAsset]=useState('');const [mobileLayoutDraft,setMobileLayoutDraft]=useState<MobilePageLayout>({});const [canvasDevice,setCanvasDevice]=useState<'desktop'|'phone'>('desktop');const [resultBackgroundAsset,setResultBackgroundAsset]=useState('');const [kind,setKind]=useState<'poll'|'quiz'|'timed_quiz'>('poll');const [options,setOptions]=useState('Sì\nNo');const [correct,setCorrect]=useState(0);const [answerMode,setAnswerMode]=useState<'single'|'multiple'|'text'|'file'>('single');const [answerRequired,setAnswerRequired]=useState(true);const [multipleAnswers,setMultipleAnswers]=useState<string[]>([]);const [freeText,setFreeText]=useState('');const [selectedReaction,setSelectedReaction]=useState('');const [reactions,setReactions]=useState<any>(null);const [code,setCode]=useState('');const [participant,setParticipant]=useState(false);const [answer,setAnswer]=useState('');const [sent,setSent]=useState(false);const [joined,setJoined]=useState(false);const [participantReady,setParticipantReady]=useState(false);const [joinPending,setJoinPending]=useState(false);const [votePending,setVotePending]=useState(false);const [joinStatus,setJoinStatus]=useState<'loading'|'ready'|'unavailable'>('loading');const [liveConnection,setLiveConnection]=useState<'connecting'|'connected'|'disconnected'|'blocked'>('connecting');const joining=useRef(false);const [pseudonym,setPseudonym]=useState(localStorage.getItem('quorivio_pseudonym')||'');const [consent,setConsent]=useState(false);const [newPassword,setNewPassword]=useState('');const [confirmNewPassword,setConfirmNewPassword]=useState('');const [registerMode,setRegisterMode]=useState(false);const [notice,setNotice]=useState('');const [newUserEmail,setNewUserEmail]=useState('');const [newUserNickname,setNewUserNickname]=useState('');const [userSearch,setUserSearch]=useState('');const [userPage,setUserPage]=useState(1);const [userPageSize,setUserPageSize]=useState(10);const [sessionSearch,setSessionSearch]=useState('');const [sessionPage,setSessionPage]=useState(1);const [sessionPageSize,setSessionPageSize]=useState(10);const [sessionTotal,setSessionTotal]=useState(0);const [userTotal,setUserTotal]=useState(0);const [cookieAcknowledged,setCookieAcknowledged]=useState(document.cookie.split('; ').some(x=>x.startsWith('q_cookie_notice=')));const [newUserTemporaryPassword,setNewUserTemporaryPassword]=useState('');const [adminUsers,setAdminUsers]=useState<any[]>([]);const [adminUrl,setAdminUrl]=useState('');const [adminRetention,setAdminRetention]=useState(60);const [adminUploadMb,setAdminUploadMb]=useState(100);const [slideMasterDraft,setSlideMasterDraft]=useState({...DEFAULT_TITLE_STYLE});const [pageBackground,setPageBackground]=useState('');const [pageLogo,setPageLogo]=useState('');const [mediaUrl,setMediaUrl]=useState('');const [mediaKind,setMediaKind]=useState<'image'|'video'|'pdf'>('image');const [coEmail,setCoEmail]=useState('');const [coPresenters,setCoPresenters]=useState<any[]>([]);const [assets,setAssets]=useState<any[]>([]);const [backgrounds,setBackgrounds]=useState<any[]>([]);const [assetBusy,setAssetBusy]=useState(false);const [editingActivity,setEditingActivity]=useState<string>('');const [editTitle,setEditTitle]=useState('');const [editOpts,setEditOpts]=useState('');const [editCorrect,setEditCorrect]=useState('');const path=location.pathname;const joinPath=path.startsWith('/join/');const publicPath=path.startsWith('/screen/');const joinCode=joinPath?normalizeJoinCode(path.slice(6)):'';const publicId=publicPath?path.slice(8):'';
useEffect(()=>{if(!notice&&!error)return;const timer=window.setTimeout(()=>{setNotice('');setError('')},7000);return()=>window.clearTimeout(timer)},[notice,error]);const notify=(e:unknown)=>setError(e instanceof Error?e.message:String(e));useEffect(()=>{if(dashboardPage!=='profile'||!me)return;let cancelled=false;void request<any>('/auth/profile').then(p=>{if(cancelled)return;setMyProfile(p);setProfileName(p.display_name||'');setProfilePhoto(p.profile_photo_url||'')}).catch(e=>{if(!cancelled)notify(e)});return()=>{cancelled=true}},[dashboardPage,me?.id]);useEffect(()=>{const dismiss=(event:KeyboardEvent)=>{if(event.key==='Escape'){setNotice('');setError('')}};window.addEventListener('keydown',dismiss);return()=>window.removeEventListener('keydown',dismiss)},[]);const load=()=>request<{items:Session[];total:number}>(`/sessions?page=${sessionPage}&page_size=${sessionPageSize}&search=${encodeURIComponent(sessionSearch)}`).then(v=>{setSessions(v.items);setSessionTotal(v.total)}).catch(notify);useEffect(()=>{if(joinPath||publicPath)return;request('/auth/me').then(v=>{setMe(v);setNickname(v?.nickname||'')}).catch(()=>setMe(null))},[]);useEffect(()=>{if(me)load()},[me,sessionPage,sessionPageSize,sessionSearch]);useEffect(()=>{setNickname(me?.nickname||'')},[me?.id,me?.nickname]);useEffect(()=>{if(!me||me.role!=='platform_admin')return;if(dashboardPage==='users')void request<{items:any[];total:number}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`).then(v=>{setAdminUsers(v.items);setUserTotal(v.total)}).catch(notify);if(dashboardPage==='settings')void request<any>('/admin/settings').then(cfg=>{setAdminUrl(cfg.public_base_url||'');setAdminRetention(Number(cfg.closed_session_retention_days||60));setAdminUploadMb(Number(cfg.max_upload_mb||100))}).catch(notify)},[dashboardPage,me?.role,userPage,userPageSize,userSearch]);useEffect(()=>{if(selected)request<Snapshot>(`/sessions/${selected}`).then(setSnap).catch(e=>{setSnap(null);writeWorkspaceLocation({sessionId:'',section:'workspace',tab:'overview',pageId:''});setSelected('');setDashboardPage('workspace');notify(e)})},[selected]);const workspaceRestore=useRef(readWorkspaceLocation());useEffect(()=>{if(me===undefined||!me)return;writeWorkspaceLocation({sessionId:selected,section:dashboardPage,tab:sessionTab,pageId:designActivity||(workspaceRestore.current.sessionId===selected?workspaceRestore.current.pageId:'')})},[me,selected,dashboardPage,sessionTab,designActivity]);
useEffect(()=>{if(!me||!selected||!snap||snap.session.id!==selected||designActivity||dashboardPage!=='session')return;const saved=workspaceRestore.current;workspaceRestore.current={...saved,pageId:''};if(saved.sessionId===selected&&saved.pageId&&snap.activities.some(a=>a.id===saved.pageId)){const page=snap.activities.find(a=>a.id===saved.pageId);if(page)beginPageDesign(page)}},[me?.id,selected,snap?.session.id,designActivity,dashboardPage]);
useEffect(()=>{if(selected){void request<string[]>(`/sessions/${selected}/schedule`).then(setScheduleDates).catch(()=>setScheduleDates([]));void request<any[]>(`/sessions/${selected}/appointments`).then(setAppointments).catch(()=>setAppointments([]))}},[selected]);useEffect(()=>{if(!me)return;const [year,month]=calendarMonth.split('-').map(Number);const end=new Date(Date.UTC(year,month,0)).toISOString().slice(0,10);void request<any[]>(`/calendar?from=${calendarMonth}-01&to=${end}`).then(setGlobalAppointments).catch(()=>setGlobalAppointments([]))},[calendarMonth,me?.id]);const [presenterLive,setPresenterLive]=useState<'connecting'|'connected'|'disconnected'|'blocked'>('connecting');useLive(selected||undefined,s=>{setSnap(s);setLiveFallback(false)},setPresenterLive);
 const [liveFallback,setLiveFallback]=useState(false);
 useEffect(()=>{
  if(!selected||!me||presenterLive==='connected'){setLiveFallback(false);return}
  let stopped=false;
  const poll=async()=>{try{const fresh=await request<Snapshot>(`/sessions/${encodeURIComponent(selected)}`);if(!stopped){setSnap(fresh);setLiveFallback(true)}}catch{if(!stopped)setLiveFallback(false)}};
  void poll();const timer=window.setInterval(()=>void poll(),12000);
  return()=>{stopped=true;window.clearInterval(timer)};
 },[selected,me?.id,presenterLive]);
const [entry,setEntry]=useState<any>(null);const [liveResults,setLiveResults]=useState<any[]>([]);
 const [audienceClock,setAudienceClock]=useState(Date.now());
 useEffect(()=>{if(!joinPath||!entry?.activity?.id)return;setAudienceClock(Date.now());const id=window.setInterval(()=>setAudienceClock(Date.now()),1000);return()=>window.clearInterval(id)},[joinPath,entry?.activity?.id]);
 const audiencePortrait=joinPath&&participantReadingMode&&window.matchMedia('(max-width:700px)').matches;
const audienceTimerSeconds=pageCountdownSeconds(entry?.activity?.page_design?.widgets||[]);
 const audienceTimerExpired=audienceTimerSeconds!==undefined&&(!entry?.activity?.opened_at||rehearsalExpired(new Date(entry.activity.opened_at).getTime(),audienceTimerSeconds,audienceClock));
const refreshPublicEntry=async()=>{
 try{const response=await request<any>(`/join/${encodeURIComponent(joinCode)}`);setEntry(response);setJoinStatus('ready')}
 catch(e){setEntry(null);setJoinStatus('unavailable');if(!(e instanceof Error)||e.message!=='session_unavailable')notify(e)}
};
useEffect(()=>{if(!joinPath)return;setJoinStatus('loading');setParticipantReady(false);setJoined(false);void refreshPublicEntry()},[joinCode]);
useEffect(()=>{
 if(!joinPath||!entry?.session?.id)return;
 let active=true;
 setParticipantReady(false);
 request<{joined:boolean}>(`/join/${encodeURIComponent(joinCode)}/participation`)
  .then(v=>{if(active&&!joining.current)setJoined(v.joined===true)})
  .catch(()=>{if(active&&!joining.current)setJoined(false)})
  .finally(()=>{if(active)setParticipantReady(true)});
 return()=>{active=false};
},[joinCode,entry?.session?.id]);
useLive(entry?.session?.id,(s)=>{
 setEntry((old:any)=>({...old,session:s.session,activity:publicActivityFromSnapshot(s)}));
 // The server has already removed results when the presenter disables publication.
 setLiveResults(s.results||[]);
},setLiveConnection);useEffect(()=>{setAnswer('');setSent(false);setRatingSent([]);setRatingComments({});setSelectedReaction('')},[entry?.activity?.id,entry?.activity?.opened_at]);
async function refreshAssets(){if(!selected)return;try{const [files,library]=await Promise.all([request<any[]>(`/sessions/${selected}/assets`),request<any[]>(`/sessions/${selected}/backgrounds`)]);setAssets(files);setBackgrounds(library)}catch(e){notify(e)}}
useEffect(()=>{if(selected){void refreshAssets()}else{setAssets([]);setBackgrounds([])}},[selected]);
async function uploadAsset(file:File|undefined){if(!file||!selected)return;setAssetBusy(true);try{
 const mime=mediaUploadMime(file,'asset');
 if(!mime)throw Error('Formato non supportato: JPG, PNG, GIF, WebP, PDF, MP4 o WebM.');
 // Use the same extension fallback as Logo and page backgrounds; the server
 // independently validates actual file bytes and the administrator's limit.
 const res=await fetch(`/api/sessions/${selected}/assets`,{method:'POST',credentials:'include',headers:{'Content-Type':mime},body:file});
 if(!res.ok)throw Error(`Upload HTTP ${res.status}: ${await res.text()}`);
 await refreshAssets();setNotice(lang==='it'?'File caricato':'Asset uploaded');
 }catch(e){notify(e)}finally{setAssetBusy(false)}}
async function uploadWidgetFillImage(widgetId:string,file:File|undefined){
 if(!file||!selected)return;
 const mime=mediaUploadMime(file,'image');
 if(!mime){setNotice('Il riempimento richiede PNG, JPEG, GIF o WebP.');return}
 setAssetBusy(true);
 try{
  const r=await fetch(`/api/sessions/${selected}/assets`,{method:'POST',credentials:'include',headers:{'Content-Type':mime},body:file});
  if(!r.ok)throw Error(`Upload riempimento HTTP ${r.status}`);
  const saved=await r.json();
  setPageWidgets(old=>old.map(w=>w.id===widgetId?{...w,style:{...w.style,fillMode:'image',fillNone:false,fillImageAssetId:saved.id}}:w));
  await refreshAssets();setNotice('Immagine del widget caricata; salvataggio automatico in corso.');
 }catch(e){notify(e)}finally{setAssetBusy(false)}
}
async function uploadWidgetMedia(widgetId:string,file:File|undefined,kind:string){if(!file||!selected)return;
 const mime=mediaUploadMime(file,kind);if(!mime){setNotice('Formato file non supportato. Usa JPG, PNG, GIF, WebP, MP4, WebM o PDF secondo il widget.');return}
 setAssetBusy(true);try{const r=await fetch(`/api/sessions/${selected}/assets`,{method:'POST',credentials:'include',headers:{'Content-Type':mime},body:file});
 if(!r.ok)throw Error(`Upload media HTTP ${r.status}: ${(await r.text()).slice(0,250)}`);const saved=await r.json();
 if(!/^[a-f0-9-]{36}$/i.test(String(saved.id)))throw Error('Upload senza identificativo media valido');
 setPageWidgets(old=>old.map(w=>w.id===widgetId?{...w,assetId:saved.id}:w));setAutoSaveBlockedSignature('');setPageSaveError('');await refreshAssets();setNotice('Allegato caricato e associato al widget. Salvataggio automatico in corso.')
 }catch(e){notify(e)}finally{setAssetBusy(false)}}
async function selectLibraryBackground(id:string,forResults:boolean,forMobile=false){
 if(!selected||!id)return;
 setAssetBusy(true);
 try{
  const applied=await request<{id:string;background_id:string}>(`/sessions/${selected}/backgrounds/${encodeURIComponent(id)}/use`,'POST');
  if(forMobile)setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));
  else if(forResults){setResultBackgroundAsset(applied.id);setResultBackground('')}
  else{setQuestionBackgroundAsset(applied.id);setQuestionBackground('')}
  await refreshAssets();setNotice('Sfondo applicato alla pagina e copiato nella tua libreria se apparteneva a un collaboratore.');
 }catch(e){notify(e)}finally{setAssetBusy(false)}
}
async function uploadBackground(file:File|undefined,forResults:boolean,forMobile=false):Promise<boolean>{
 if(!file)return false;
 if(!selected){const problem=Error('Apri una sessione prima di caricare lo sfondo.');notify(problem);throw problem;}
 const mime=mediaUploadMime(file,'image');
 if(!mime){const problem=Error('Formato sfondo non supportato: usa JPG, PNG, GIF o WebP.');notify(problem);throw problem;}
 setAssetBusy(true);
 try{
  const r=await fetch(`/api/sessions/${encodeURIComponent(selected)}/backgrounds`,{method:'POST',credentials:'include',headers:{'Content-Type':mime},body:file});
  if(!r.ok){
   const detail=await r.json().catch(()=>null);
   const code=typeof detail?.error==='string'?detail.error:'';
   throw Error(backgroundUploadError(r.status,code));
  }
  const applied=await r.json();
  if(typeof applied?.id!=='string'||!/^[-a-f0-9]{36}$/i.test(applied.id))throw Error('Il server non ha restituito un identificativo dello sfondo valido');
  if(forMobile){setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));}
  else if(forResults){setResultBackgroundAsset(applied.id);setResultBackground('')}
  else{setQuestionBackgroundAsset(applied.id);setQuestionBackground('')}
  await refreshAssets();setNotice(forMobile?'Immagine caricata nella libreria e applicata soltanto allo sfondo smartphone. Salvataggio del layout in corso.':'Immagine caricata nella libreria e applicata alla pagina. Salvataggio del layout in corso.');return true;
 }catch(e){notify(e);throw e}finally{setAssetBusy(false)}
}
async function deleteAsset(id:string){if(!window.confirm(lang==='it'?'Eliminare definitivamente il file?':'Delete this file permanently?'))return;try{
 await request(`/sessions/${selected}/assets/${id}`,'DELETE');await refreshAssets();
 }catch(e){notify(e)}}
async function duplicateSessionFrom(sourceId:string){
 if(!sourceId||!window.confirm('Duplicare la sessione in una nuova bozza? Saranno copiati pagine, widget e allegati, ma NON partecipanti, risposte, voti, statistiche o cronologia.'))return;
 try{const result=await request<{id:string;status:'draft';data_copied:false}>(`/sessions/${sourceId}/duplicate`,'POST');await load();setSelected(result.id);setSnap(null);setDashboardPage('session');setSessionTab('overview');setNotice('Nuova bozza creata senza risposte, partecipanti o statistiche della sessione sorgente')}
 catch(e){notify(e)}
}
async function duplicateSelected(){if(selected)await duplicateSessionFrom(selected)}
async function importQuorivioBundle(file:File|undefined){if(!file)return;try{if(file.size>100*1024*1024)throw Error('Archivio oltre 100 MB');const response=await fetch('/api/sessions/import.quorivio',{method:'POST',credentials:'include',headers:{'Content-Type':'application/vnd.quorivio.session+zip'},body:file});const result=await response.json();if(!response.ok)throw Error(result.error||'Importazione fallita');await load();setSelected(result.id);setDashboardPage('session');setNotice('Sessione Quorivio con asset importata')}catch(e){notify(e)}}
async function importSessionFile(file:File|undefined){if(!file)return;try{if(file.size>2*1024*1024)throw Error('JSON oltre 2 MB');const body=JSON.parse(await file.text());const r=await request<{id:string}>('/sessions/import','POST',body);await load();setSelected(r.id);setDashboardPage('session');setNotice('Definizione sessione importata')}catch(e){notify(e)}}
async function refreshCollaborators(){try{setCoPresenters(await request(`/sessions/${selected}/presenters`))}catch(e){notify(e)}}
async function addCollaborator(){try{await request(`/sessions/${selected}/presenters`,'POST',{email:coEmail.trim()});setCoEmail('');await refreshCollaborators()}catch(e){notify(e)}}
async function removeCollaborator(uid:string){if(!window.confirm('Rimuovere il co-presentatore?'))return;try{await request(`/sessions/${selected}/presenters/${uid}`,'DELETE');await refreshCollaborators()}catch(e){notify(e)}}
function beginActivityEdit(a:Activity){setEditingActivity(a.id);setEditTitle(a.title);setEditOpts(a.options.map(o=>`${o.id}|${o.label}`).join('\n'));setEditCorrect((a as any).correct_option_id||'')}
async function saveActivityEdit(){try{const original=snap?.activities.find(a=>a.id===editingActivity);if(!original)return;const next=editOpts.split('\n').filter(x=>x.trim()).map(x=>{const pos=x.indexOf('|');return {id:pos<0?'':x.slice(0,pos).trim(),label:pos<0?x.trim():x.slice(pos+1).trim()}});if(next.some(x=>!x.id||!x.label))throw Error('Ogni opzione deve conservare il suo ID: ID|testo');await request(`/sessions/${selected}/activities/${editingActivity}`,'PATCH',{title:editTitle,options:next,correct_option_id:['quiz','timed_quiz'].includes(original.type)?editCorrect:null});setEditingActivity('');setSnap(await request(`/sessions/${selected}`))}catch(e){notify(e)}}
async function invalidateActivity(a:Activity){if(!window.confirm('Invalidare tutte le risposte di questa attività? L’operazione è tracciata.'))return;try{await request(`/sessions/${selected}/activities/${a.id}/invalidate`,'POST');setSnap(await request(`/sessions/${selected}`))}catch(e){notify(e)}}
async function requestPasswordRecovery(){try{await request('/auth/password-reset/request','POST',{email});setNotice(lang==='it'?'Se l’account è registrato, riceverai un link di recupero.':'If the account exists, a recovery link will be emailed.')}catch(e){notify(e)}}
async function confirmPasswordRecovery(){if(resetSubmitLock.current||!resetToken||resetPassword.length<12||resetPassword!==resetPasswordConfirmation)return;resetSubmitLock.current=true;setResetSubmitPending(true);try{await request('/auth/password-reset/confirm','POST',{token:resetToken,new_password:resetPassword});setResetToken('');setResetPassword('');setResetPasswordConfirmation('');history.replaceState(null,'',location.pathname);setNotice(lang==='it'?'Password aggiornata. Accedi con la nuova password e il codice MFA, se richiesto.':'Password changed. Sign in with your new password and MFA code if enabled.')}catch(e){notify(e)}finally{resetSubmitLock.current=false;setResetSubmitPending(false)}}
async function handleLogin(e:React.FormEvent){e.preventDefault();try{const result=await request<any>('/auth/login','POST',{email,password});if(result.mfa_required){setEmailChallenge(result.challenge_id);setMfaMethods(result.methods);setMfaMethod(result.methods.includes('totp')?'totp':'email');setShowRecovery(false);setTotpCode('');setRecoveryCode('');return}setMe(await request('/auth/me'))}catch(e){notify(e)}}
async function chooseMfaMethod(method:string){setMfaMethod(method);setShowRecovery(false);if(method==='email'){try{await request('/auth/mfa/challenge/email','POST',{challenge_id:emailChallenge});setNotice('Codice email inviato / Email code sent')}catch(e){notify(e)}}}
async function verifyEmailLogin(){try{if(mfaMethod==='email')await request('/auth/email-mfa/verify','POST',{challenge_id:emailChallenge,code:emailCode});else await request('/auth/mfa/challenge/verify','POST',{challenge_id:emailChallenge,method:showRecovery?'recovery':'totp',code:showRecovery?recoveryCode:totpCode});setEmailChallenge('');setEmailCode('');setTotpCode('');setRecoveryCode('');setMe(await request('/auth/me'))}catch(e){notify(e)}}
async function register(){try{await request('/auth/register','POST',{email,password});setRegisterMode(false);setNotice(lang==='it'?'Registrazione ricevuta: attendi approvazione amministratore.':'Registration received: wait for administrator approval.');setPassword('')}catch(e){notify(e)}}
async function setResultsVisibility(visible:boolean){try{await request(`/sessions/${selected}/results-visibility`,'PATCH',{show_results:visible});setSnap(await request(`/sessions/${selected}`))}catch(e){notify(e)}}
async function setAnonymous(allowed:boolean){try{await request(`/sessions/${selected}/anonymous`,'PATCH',{allow_anonymous:allowed});setSnap(await request(`/sessions/${selected}`))}catch(e){notify(e)}}
async function createSession(){try{const s=await request<Session>('/sessions','POST',{title:newTitle,reference_date:newReferenceDate});setNewTitle('');await load();setSelected(s.id);setDashboardPage('session');setSessionTab('overview')}catch(e){notify(e)}}
// A permission obtained from an authenticated read, never from the public live snapshot.
useEffect(()=>{
 if(!selected||!me){setSelectedSessionRole(null);return}
 let cancelled=false;
 setSelectedSessionRole(null);
 void request<Snapshot>(`/sessions/${selected}`).then(value=>{
  if(!cancelled)setSelectedSessionRole(value.session.access_role||null);
 }).catch(()=>{if(!cancelled)setSelectedSessionRole(null)});
 return()=>{cancelled=true};
},[selected,me?.id]);
// Session actions remain visible in the navigation sidebar while one session is open.
// Closing the viewer is deliberately distinct from terminating the live session.
function leaveCurrentSession(){if(!confirmSchemaNavigation())return;workspaceRestore.current={sessionId:'',section:'workspace',tab:'overview',pageId:''};setSelectedSessionRole(null);setSidebarRename(null);setSelected('');setSnap(null);setDashboardPage('open');}
async function closeSidebarSession(){
 if(!selected||!snap||snap.session.status==='closed'||sidebarBusy)return;
 if(!window.confirm('Terminare definitivamente la sessione corrente? La presentazione e le interazioni live verranno chiuse. La duplicazione rimarrà disponibile.'))return;
 setSidebarBusy(true);
 try{await request(`/sessions/${selected}/status`,'POST',{status:'closed'});setSnap(await request<Snapshot>(`/sessions/${selected}`));await load();setNotice('Sessione terminata. Puoi ancora duplicarla senza risposte.');}
 catch(e){notify(e)}finally{setSidebarBusy(false)}
}
async function renameSidebarSession(){
 if(!selected||!snap||snap.session.status==='closed'||sidebarBusy||sidebarRename===null)return;
 const title=sidebarRename.trim();
 if(!title||title.length>160){setNotice('Il nome della sessione deve contenere da 1 a 160 caratteri.');return}
 setSidebarBusy(true);
 try{
  const reference_date=String(snap.session.reference_date||'').slice(0,10);
  await request(`/sessions/${selected}/metadata`,'PATCH',{title,reference_date});
  setSnap(await request<Snapshot>(`/sessions/${selected}`));await load();setSidebarRename(null);setNotice('Nome della sessione aggiornato.');
 }catch(e){notify(e)}finally{setSidebarBusy(false)}
}
// The scheme editor is a full canvas, using the same drag/resize/rotate engine as pages.
const schemaWidgetKinds=editorWidgetKinds;
function schemaMediaAssets(kind:string){return assets.filter(a=>typeof a.mime_type==='string'&&(kind==='pdf'?a.mime_type==='application/pdf':kind==='video'?a.mime_type.startsWith('video/'):a.mime_type.startsWith('image/')))}
function insertSchemaWidget(kind:string){
 if(!schemaWidgetKinds.includes(kind as any)||schemaSaving)return;
 if(['image','video','logo','pdf'].includes(kind)&&!schemaMediaAssets(kind).length){setNotice('Carica un allegato compatibile dalla sessione prima di inserirlo nello schema.');return}
 setSchemaWidgets(old=>{
  if(old.length>=16){setNotice('Lo schema supporta massimo 16 widget.');return old}
  if(['title','footer'].includes(kind)&&old.some(w=>w.kind===kind)){setNotice('È già presente un widget di questo tipo nello schema.');return old}
  const i=old.length;
  const placement=kind==='footer'?newFooterWidget('schema').position:freeWidgetPosition(old,{x:4+(i%4)*22,y:5+Math.floor(i/4)*18},20,15);
  if(!placement){setNotice('Non c’è spazio per inserire un altro widget nello schema.');return old}
  const id=crypto.randomUUID();
  const template=kind==='title'?newTitleWidget(snap?.session.title||'Titolo'):kind==='footer'?newFooterWidget(id):{};
  return [...old,{...template,id,kind,...(['image','video','logo','pdf'].includes(kind)?{assetId:schemaMediaAssets(kind)[0].id}:{}),label:kind==='footer'?'':kind==='question'?'Nuova domanda':editorWidgetNames[kind]||'Widget',style:{...((template as any).style||{}),fillNone:kind!=='shape',shapeType:'rectangle',...(kind==='shape'||kind==='line'?{strokeWidth:2,strokeColor:'#334155',lineDirection:'horizontal',fillColor:kind==='shape'?'#dbeafe':'#ffffff'}:{})},position:{...placement,rotation:0}}];
 });
}
function arrangeSchema(mode:ArrangeMode){
 if(!schemaSelected.length)return;
 setSchemaWidgets(old=>rejectWidgetCollisions(old,arrangeWidgets(old,schemaSelected,mode),schemaSelected));
}
function schemaStoredWidgets(value:any):any[]{return masterWidgetTemplate(Array.isArray(value)?value:[])}
function confirmSchemaNavigation(){
 if(dashboardPage!=='master')return true;
 if(schemaSaving){setNotice('Il salvataggio dello schema è ancora in corso.');return false}
 if(JSON.stringify(schemaWidgets)===schemaBaseline.current)return true;
 return window.confirm('Lo schema contiene modifiche non salvate. Uscire e scartarle?');
}
function navigateDashboard(page:typeof dashboardPage){if(confirmSchemaNavigation())setDashboardPage(page)}
function openSchemaEditor(){
 if(!selected||!snap)return;
 if(!confirmSchemaNavigation())return;
 const stored=snap.session.theme?.master?.widgets;
 const widgets=schemaStoredWidgets(stored);
 const initial=widgets.length?widgets:[newTitleWidget(snap.session.title),newFooterWidget('schema-footer')];
 schemaBaseline.current=JSON.stringify(widgets);
 setSchemaInspected('');setSchemaSelected([]);setSchemaWidgets(structuredClone(initial));
 setDashboardPage('master');
}

async function saveSchemaEditor(){
 if(!selected||!snap||schemaSaving||snap.session.status==='closed')return;
 setSchemaSaving(true);
 try{
  const canonical=masterWidgetTemplate(schemaWidgets);
  // Compare against the fresh authenticated snapshot, not the live websocket cache.
  // A collaborator updating the master must not have their work overwritten silently.
  const fresh=await request<Snapshot>(`/sessions/${selected}`);
  if(JSON.stringify(schemaStoredWidgets(fresh.session.theme?.master?.widgets))!==schemaBaseline.current){
   throw Error('Lo schema è stato aggiornato da un altro editor. Esci e riapri gli schemi per caricare la versione corrente.');
  }
  const theme={...(fresh.session.theme||{}),master:{...(fresh.session.theme?.master||{}),widgets:canonical}};
  if(!validPageDesign(theme))throw Error('Il modello contiene widget o proprietà non valide');
  await request(`/sessions/${selected}/design`,'PATCH',{theme});
  setSnap(await request<Snapshot>(`/sessions/${selected}`));
  schemaBaseline.current=JSON.stringify(canonical);
  setNotice('Schema Titolo/Footer aggiornato. Le pagine senza override locali lo ereditano.');
 }catch(e){notify(e)}finally{setSchemaSaving(false)}
}
function adoptSchemaOnCurrentPage(){
 if(!snap||!designActivity||snap.session.status==='closed')return;
 const stored=snap.session.theme?.master?.widgets||[];
 const schema=masterWidgetTemplate(stored);
 if(!schema.length){setNotice('Nessuno schema salvato: apri Modifica schemi.');return}
 if(!window.confirm('Applicare Titolo e Footer dallo schema alla pagina corrente? Le personalizzazioni locali di Titolo e Footer saranno sostituite; gli altri widget resteranno invariati.'))return;
 setPageWidgets(old=>[...old.filter(w=>w.kind!=='title'&&w.kind!=='footer'),...schema.map(w=>({...w,id:crypto.randomUUID()}))]);
 setNotice('Schema adottato nella bozza della pagina. Il salvataggio resta automatico.');
}
async function updateSessionMetadata(){try{await request(`/sessions/${selected}/metadata`,'PATCH',{title:sessionTitleEdit||snap?.session.title,reference_date:sessionDateEdit||String(snap?.session.reference_date||'').slice(0,10)});setSnap(await request(`/sessions/${selected}`));await load();setNotice('Sessione aggiornata')}catch(e){notify(e)}}
/** Only phone positions change in smartphone editing. All authored widget content and
 * the original desktop geometry remain in the canonical editor draft. */
function changeCanvasWidgets(items:any[]){
 if(canvasDevice==='desktop'){setPageWidgets(items);return;}
 const desktop=new Map(pageWidgets.map(w=>[w.id,w]));
 const canonical=items.map(w=>{const original=desktop.get(w.id);return original?{...w,position:original.position}:{...w,position:{x:10,y:12,width:45,height:24,rotation:0}}});
 if(JSON.stringify(canonical)!==JSON.stringify(pageWidgets))setPageWidgets(canonical);
 setMobileLayoutDraft(old=>({...old,positions:captureMobilePositions(items)}));
}
function currentPageDraft():EditablePageDraft{const mobile=pruneMobilePageLayout(mobileLayoutDraft,pageWidgets);return {widgets:pageWidgets,questionHeader,resultHeader,questionBackground,resultBackground,questionBackgroundColor,resultBackgroundColor,questionBackgroundAsset,resultBackgroundAsset,...(Object.keys(mobile).length?{mobile}:{})}}
function pageDraftSignature(){return serializePageDraft(currentPageDraft())}
const mergePreview=mergeCandidate?mergePageDrafts(mergeCandidate.base??JSON.parse(savedPageDraft.current) as EditablePageDraft,mergeCandidate.local??currentPageDraft(),mergeCandidate.remote,mergeChoices):null;
const unresolvedMergeConflicts=mergePreview?.conflicts.filter(c=>!mergeChoices[c.path])||[];
function describeMergeValue(value:unknown):string{if(value===undefined)return '(elemento eliminato)';const raw=typeof value==='string'?value:JSON.stringify(value);return raw.length>240?raw.slice(0,240)+'…':raw}
async function inspectPageConflict(){if(!designActivity||pendingPageSave.current)return;try{const latest=await request<Snapshot>(`/sessions/${selected}`);const page=latest.activities.find(a=>a.id===designActivity) as any;if(!page){setNotice('La pagina non esiste più sul server: esporta la bozza locale prima di uscire.');return}const revision=validDesignRevision(page.design_revision)?page.design_revision:1;const remote=pageDraftFromActivity(page);mergePageDrafts(JSON.parse(savedPageDraft.current) as EditablePageDraft,currentPageDraft(),remote);setMergeChoices({});setMergeCandidate({remote,revision,snapshot:latest});setNotice('Confronto disponibile: scegli come risolvere ogni modifica incompatibile, poi applica la bozza riconciliata.')}catch(e){notify(e)}}
async function applyPageRebase(){if(!mergeCandidate||!mergePreview||unresolvedMergeConflicts.length||pendingPageSave.current)return;const draftAtClick=latestPageDraft.current;try{const fresh=await request<Snapshot>(`/sessions/${selected}`);const current=fresh.activities.find(a=>a.id===designActivity) as any;if(!current){setNotice('La pagina non esiste più: esporta la bozza locale.');return}const revision=validDesignRevision(current.design_revision)?current.design_revision:1;if(revision!==mergeCandidate.revision){setMergeCandidate({...mergeCandidate,remote:pageDraftFromActivity(current),revision,snapshot:fresh});setMergeChoices({});setNotice('Il server è cambiato durante il confronto. Rivedi i nuovi conflitti prima di applicare la bozza.');return}}catch(e){notify(e);return}if(latestPageDraft.current!==draftAtClick){setNotice('La bozza è cambiata durante il confronto. Verifica nuovamente le scelte prima di applicarle.');return}const d=mergePreview.draft;resetPageWidgets(d.widgets as any[]);setQuestionHeader(d.questionHeader);setResultHeader(d.resultHeader);setQuestionBackground(d.questionBackground);setResultBackground(d.resultBackground);setQuestionBackgroundColor(d.questionBackgroundColor);setResultBackgroundColor(d.resultBackgroundColor);setQuestionBackgroundAsset(d.questionBackgroundAsset);setResultBackgroundAsset(d.resultBackgroundAsset);setMobileLayoutDraft(d.mobile||{});loadedDesignRevision.current=mergeCandidate.revision;savedPageDraft.current=serializePageDraft(mergeCandidate.remote);setSnap(mergeCandidate.snapshot);setPageConflict(false);setMergeCandidate(null);setMergeChoices({});setNotice('Bozza riconciliata localmente. Controlla il layout e premi Salva layout per pubblicarla; nessuna modifica è stata ancora inviata.')}
function downloadPageDraft(){if(!designActivity)return;const blob=new Blob([JSON.stringify(createPageDraftBackup(selected,designActivity,loadedDesignRevision.current,currentPageDraft(),JSON.parse(savedPageDraft.current) as EditablePageDraft),null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`quorivio-bozza-${designActivity}.json`;document.body.append(a);a.click();a.remove();window.setTimeout(()=>URL.revokeObjectURL(url),1000)}
function downloadPageDraftFor(a:Activity){
 if(designActivity===a.id){downloadPageDraft();return}
 const page=a as any,draft=pageDraftFromActivity(page),revision=validDesignRevision(page.design_revision)?page.design_revision:1;
 const blob=new Blob([JSON.stringify(createPageDraftBackup(selected,a.id,revision,draft,draft),null,2)],{type:'application/json'});
 const url=URL.createObjectURL(blob),link=document.createElement('a');link.href=url;link.download=`quorivio-bozza-${a.id}.json`;document.body.append(link);link.click();link.remove();window.setTimeout(()=>URL.revokeObjectURL(url),1000)
}
const [importPageTask,setImportPageTask]=useState<{pageId:string;file:File}|null>(null);
function openImportDraftFor(a:Activity,file:File|undefined){
 if(!file||!confirmPageNavigation())return;
 if(designActivity===a.id){void importPageDraft(file);return}
 setImportPageTask({pageId:a.id,file});beginPageDesign(a)
}
async function importPageDraft(file:File|undefined){
 if(!file||!designActivity||pendingPageSave.current)return;
 if(file.size>2_000_000){setNotice('La bozza supera il limite di 2 MB.');return}
 const pageId=designActivity,sessionId=selected,signature=latestPageDraft.current;
 try{
  const backup=parsePageDraftBackup(await file.text(),sessionId,pageId);
  const latest=await request<Snapshot>(`/sessions/${sessionId}`);
  if(designActivity!==pageId||selected!==sessionId||latestPageDraft.current!==signature){setNotice('La pagina o la bozza è cambiata durante il caricamento: ripeti l’importazione.');return}
  const activity=latest.activities.find(a=>a.id===pageId) as any;
  if(!activity){setNotice('La pagina non esiste più sul server.');return}
  const revision=validDesignRevision(activity.design_revision)?activity.design_revision:1;
  const plan=planPageDraftRecovery(backup,revision);
  if(plan.mode==='blocked'){setNotice(plan.reason==='legacy_backup_stale'?'La bozza precedente non include la versione di partenza e il server è cambiato: il ripristino automatico non è sicuro.':'La bozza non può essere ripristinata.');return}
  if(!window.confirm(plan.mode==='restore'?'Caricare questa bozza? Le modifiche locali saranno sostituite e il layout sarà sincronizzato automaticamente.':'Il server è cambiato dalla creazione della bozza. Aprire il confronto a tre vie senza pubblicare nulla?'))return;
  const remote=pageDraftFromActivity(activity);
  if(plan.mode==='reconcile'){
   setMergeCandidate({base:backup.base_draft,local:backup.draft,remote,revision,snapshot:latest});setMergeChoices({});setPageConflict(true);
   setNotice('Bozza importata per il confronto: risolvi i conflitti e applica la riconciliazione. Nessun dato è stato salvato.');return;
  }
  resetPageWidgets(backup.draft.widgets as any[]);
  setQuestionHeader(backup.draft.questionHeader);setResultHeader(backup.draft.resultHeader);
  setQuestionBackground(backup.draft.questionBackground);setResultBackground(backup.draft.resultBackground);
  setQuestionBackgroundColor(backup.draft.questionBackgroundColor);setResultBackgroundColor(backup.draft.resultBackgroundColor);
  setQuestionBackgroundAsset(backup.draft.questionBackgroundAsset);setResultBackgroundAsset(backup.draft.resultBackgroundAsset);setMobileLayoutDraft(backup.draft.mobile||{});
  loadedDesignRevision.current=revision;savedPageDraft.current=serializePageDraft(remote);setSnap(latest);
  setPageConflict(false);setMergeCandidate(null);setMergeChoices({});setNotice('Bozza recuperata: il layout verrà sincronizzato automaticamente.');
 }catch(e){notify(e)}
}
useEffect(()=>{if(!importPageTask||designActivity!==importPageTask.pageId)return;const file=importPageTask.file;setImportPageTask(null);void importPageDraft(file)},[importPageTask,designActivity]);
const pageHasUnsavedChanges=!!designActivity&&savedPageDraft.current!==pageDraftSignature();
const [pageSavePending,setPageSavePending]=useState(false);
 const [autoSaveBlockedSignature,setAutoSaveBlockedSignature]=useState('');
 const [autoSaveRetry,setAutoSaveRetry]=useState<{signature:string;attempts:number}>({signature:'',attempts:0});
 const [pageSaveError,setPageSaveError]=useState('');
const pendingPageSave=useRef(false);
const latestPageDraft=useRef('');
latestPageDraft.current=pageDraftSignature();
function confirmPageNavigation(){if(pendingPageSave.current||pageHasUnsavedChanges){setNotice('Salvataggio automatico in corso: attendi prima di cambiare pagina. Se persiste un errore usa Salva ora nel menu contestuale.');return false}return true}
useEffect(()=>{if(!pageHasUnsavedChanges)return;const onBeforeUnload=(e:BeforeUnloadEvent)=>{e.preventDefault();e.returnValue=''};window.addEventListener('beforeunload',onBeforeUnload);return()=>window.removeEventListener('beforeunload',onBeforeUnload)},[pageHasUnsavedChanges]);
async function updatePageDesign():Promise<boolean>{
 if(!designActivity||pendingPageSave.current)return false;
 if(pageConflict){setNotice('Salvataggio sospeso: occorre risolvere il conflitto con la versione del server.');return false}
 const unconfiguredMedia=pageWidgets.find(w=>['image','logo','video','pdf'].includes(w.kind)&&!w.assetId);
 if(unconfiguredMedia){setNotice(`Prima di salvare, scegli o carica un file per «${unconfiguredMedia.label||unconfiguredMedia.kind}» dal menu contestuale o dalle proprietà.`);setAutoSaveBlockedSignature(latestPageDraft.current);setPageSaveError('');return false}
 if(pageWidgets.length>16){setNotice('Impossibile salvare: la pagina può contenere al massimo 16 widget.');setAutoSaveBlockedSignature(latestPageDraft.current);setPageSaveError('Troppi widget');return false}
 pendingPageSave.current=true;setPageSavePending(true);setPageSaveError('');
 const savePageId=designActivity;const saveSessionId=selected;const savedSignature=pageDraftSignature();
 const requestedDraft=currentPageDraft();const expectedRevision=loadedDesignRevision.current;
 let confirmedPatchRevision:number|undefined;let committed=false;
 setNotice('Salvataggio del layout in corso…');
 try{
  const activity=snap?.activities.find(a=>a.id===savePageId) as any;
  const question={...(activity?.page_design||{}),header:questionHeader,widgets:pageWidgets.map(w=>w.kind==='rating'&&!w.label?.trim()?{...w,label:'Indice di gradimento'}:w),mobile:Object.keys(mobileLayoutDraft).length?pruneMobilePageLayout(mobileLayoutDraft,pageWidgets):undefined,backgroundUrl:questionBackground||undefined,backgroundColor:questionBackgroundColor||undefined,backgroundAssetId:questionBackgroundAsset||undefined};
  const result={...(activity?.result_design||{}),header:resultHeader,backgroundUrl:resultBackground||undefined,backgroundColor:resultBackgroundColor||undefined,backgroundAssetId:resultBackgroundAsset||undefined};
  if(!validPageDesign(question)||!validPageDesign(result)){
   throw new Error(invalidPageWidgetReason(question)||'Configurazione della pagina non valida: verifica le proprietà del widget, il testo delle opzioni e i file allegati.');
  }
  const saved=await request<{ok:boolean;design_revision:number}>(`/sessions/${saveSessionId}/activities/${savePageId}/design`,'PATCH',{page_design:question,result_design:result,expected_design_revision:loadedDesignRevision.current});
  if(!saved.ok||!validDesignRevision(saved.design_revision))throw new Error('Salvataggio non confermato dal server');
  confirmedPatchRevision=saved.design_revision;
  // Read back from the authoritative API; never claim success on PATCH alone.
  const refreshed=await request<Snapshot>(`/sessions/${saveSessionId}?verify_design_revision=${saved.design_revision}`);
  const persisted=refreshed.activities.find(a=>a.id===savePageId) as any;
  const stableJson=(value:unknown):string=>JSON.stringify(value,(_,v)=>v&&typeof v==='object'&&!Array.isArray(v)?Object.fromEntries(Object.entries(v).sort(([a],[b])=>a.localeCompare(b))):v);
  if(!persisted||persisted.design_revision!==saved.design_revision||stableJson(persisted.page_design?.widgets||[])!==stableJson(question.widgets)||stableJson(persisted.page_design?.mobile||{})!==stableJson(question.mobile||{})){
   throw new Error('Il server non ha restituito il layout appena salvato. La bozza locale è stata conservata: riprova o confronta la versione server.');
  }
  committed=true;
  setSnap(refreshed);
  if(savePageId===designActivity){
   loadedDesignRevision.current=saved.design_revision;savedPageDraft.current=savedSignature;
   setPageConflict(false);setMergeCandidate(null);setMergeChoices({});setAutoSaveRetry({signature:'',attempts:0});
   setNotice(latestPageDraft.current===savedSignature?'Layout sincronizzato':'Nuove modifiche da sincronizzare');setAutoSaveBlockedSignature('');setPageSaveError('');
  }
 }catch(e){
  // A dropped HTTP response may conceal a successful PostgreSQL COMMIT.
  // Read back FIRST, and never blindly retry an ambiguous PATCH.
  let verdict:'persisted'|'unchanged'|'conflict'|'unverifiable'='unverifiable';
  if(recoverableAutosaveTransportError(e)||confirmedPatchRevision!==undefined){
   try{
    const authoritative=await request<Snapshot>(`/sessions/${saveSessionId}`);
    const remote=authoritative.activities.find(a=>a.id===savePageId) as any;
    verdict=autosaveRecoveryDecision(remote,requestedDraft,expectedRevision,confirmedPatchRevision);
    if(verdict==='persisted' && remote){
     committed=true;
     setSnap(authoritative);
     if(designActivity===savePageId){
      loadedDesignRevision.current=remote.design_revision;savedPageDraft.current=savedSignature;
      setPageConflict(false);setMergeCandidate(null);setMergeChoices({});
      setAutoSaveRetry({signature:'',attempts:0});setAutoSaveBlockedSignature('');setPageSaveError('');
      setNotice(latestPageDraft.current===savedSignature?'Layout sincronizzato':'Nuove modifiche da sincronizzare');
     }
    }
   }catch{verdict='unverifiable'}
  }
  if(!committed){
   const knownConflict=e instanceof Error&&e.message==='design_revision_conflict';
   const retryable=verdict==='unchanged'&&recoverableAutosaveTransportError(e)&&!knownConflict;
   const attempts=autoSaveRetry.signature===savePageId+':'+savedSignature?autoSaveRetry.attempts:0;
   if(retryable&&attempts<3){
    setAutoSaveBlockedSignature('');setAutoSaveRetry({signature:savePageId+':'+savedSignature,attempts:attempts+1});
    setPageSaveError('Connessione interrotta; nuovo tentativo automatico');
    setNotice('Rete temporaneamente non disponibile. La pagina non è stata modificata sul server: riprovo automaticamente.');
   }else{
    setAutoSaveBlockedSignature(savedSignature);setPageSaveError(e instanceof Error?e.message:String(e));
    if(knownConflict||verdict==='conflict'){
     setPageConflict(true);setMergeCandidate(null);setMergeChoices({});
     setNotice('Conflitto: un altro presentatore ha aggiornato la pagina. La tua bozza è conservata.');
    }else setNotice(`Salvataggio non riuscito: ${e instanceof Error?e.message:String(e)}. Bozza conservata; usa Salva ora dal menu contestuale.`);
   }
  }
 }finally{pendingPageSave.current=false;setPageSavePending(false)}
 return committed;
}
// Debounced server-authoritative autosave; a failed revision/draft never auto-retries in a tight loop.
useEffect(()=>{
 if(!designActivity||!pageHasUnsavedChanges||pageSavePending||pageConflict||autoSaveBlockedSignature===latestPageDraft.current||widgetHistory.gestureBase!==null)return;
 const attempts=autoSaveRetry.signature===designActivity+':'+latestPageDraft.current?autoSaveRetry.attempts:0;
 const timer=window.setTimeout(()=>{if(!pendingPageSave.current)void updatePageDesign()},retryAutosaveDelay(attempts));
 return()=>window.clearTimeout(timer);
},[designActivity,selected,latestPageDraft.current,pageHasUnsavedChanges,pageSavePending,pageConflict,autoSaveBlockedSignature,autoSaveRetry,widgetHistory.gestureBase]);
async function exitPageEditor(){
 if(pageSavePending){setNotice('Attendi il completamento del salvataggio automatico.');return}
 if(pageHasUnsavedChanges){await updatePageDesign();if(latestPageDraft.current!==savedPageDraft.current){setNotice('La pagina contiene modifiche non sincronizzate: correggi l’errore prima di uscire.');return}}
 setInspectedWidget('');setPageContextOpen(false);setDesignActivity('');
}
useEffect(()=>{if(!designActivity)return;const onHistoryKey=(event:KeyboardEvent)=>{
 if(!(event.ctrlKey||event.metaKey)||event.altKey||event.key.toLowerCase()!=='z'&&event.key.toLowerCase()!=='y')return;
 const target=event.target as HTMLElement|null;
 if(target?.closest('input,textarea,select,[contenteditable=true],[role=textbox]'))return;
 if(event.key.toLowerCase()==='y'||event.shiftKey){if(widgetHistory.future.length&&widgetHistory.gestureBase===null){event.preventDefault();redoPageWidgets()}}
 else if(widgetHistory.past.length&&widgetHistory.gestureBase===null){event.preventDefault();undoPageWidgets()}
};window.addEventListener('keydown',onHistoryKey);return()=>window.removeEventListener('keydown',onHistoryKey)},[designActivity,widgetHistory]);
useEffect(()=>{if(!designActivity)return;const onEditorSave=(event:KeyboardEvent)=>{if((event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='s'){event.preventDefault();if(pageHasUnsavedChanges&&!pendingPageSave.current&&!pageConflict)void updatePageDesign()}};window.addEventListener('keydown',onEditorSave);return()=>window.removeEventListener('keydown',onEditorSave)},[designActivity,pageHasUnsavedChanges,pageWidgets,questionHeader,resultHeader,questionBackground,resultBackground,questionBackgroundColor,resultBackgroundColor,questionBackgroundAsset,resultBackgroundAsset,mobileLayoutDraft,pageConflict]);
function beginPageDesign(a:Activity){setSlideMasterDraft({...DEFAULT_TITLE_STYLE,...(snap?.session.theme?.master?.titleStyle||{})});if(designActivity&&designActivity!==a.id&&!confirmPageNavigation())return;void request<any[]>(`/sessions/${selected}/presenter-profiles`).then(setAvailablePresenters).catch(()=>setAvailablePresenters([]));const x=a as any;setDesignActivity(a.id);setPageThumbMenu('');setPageContextOpen(false);setInspectedWidget('');resetPageWidgets((x.page_design?.widgets||[]).map((w:any)=>normalizeLegacyFooter(w)));setQuestionHeader(x.page_design?.header||'');setResultHeader(x.result_design?.header||'');setQuestionBackground(x.page_design?.backgroundUrl||'');setQuestionBackgroundColor(x.page_design?.backgroundColor||'');setResultBackground(x.result_design?.backgroundUrl||'');setResultBackgroundColor(x.result_design?.backgroundColor||'');setQuestionBackgroundAsset(x.page_design?.backgroundAssetId||'');setResultBackgroundAsset(x.result_design?.backgroundAssetId||'');setMobileLayoutDraft(x.page_design?.mobile||{});loadedDesignRevision.current=validDesignRevision(x.design_revision)?x.design_revision:1;setPageConflict(false);setMergeCandidate(null);setMergeChoices({});setAutoSaveBlockedSignature('');setPageSaveError('');savedPageDraft.current=serializePageDraft(pageDraftFromActivity(x))}
async function deleteCanvasPage(a:Activity){
 if(designActivity===a.id&&!confirmPageNavigation())return;
 if(!window.confirm(`Eliminare definitivamente la pagina "${a.title}" e le eventuali risposte associate?`))return;
 try{
  await request(`/sessions/${selected}/pages/${a.id}`,'DELETE');
  const updated=await request<Snapshot>(`/sessions/${selected}`);setSnap(updated);
  if(designActivity===a.id){const next=updated.activities[0];if(next)beginPageDesign(next);else setDesignActivity('')}
  setNotice('Pagina eliminata');
 }catch(e){notify(e)}
}
async function duplicatePage(activityId:string){if(!confirmPageNavigation())return;try{
  const previousIds=new Set(snap?.activities.map(a=>a.id)||[]);
  await request(`/sessions/${selected}/activities/${activityId}/duplicate`,'POST');
  let updated=await request<Snapshot>(`/sessions/${selected}`);
  const copy=updated.activities.find(a=>!previousIds.has(a.id));
  if(copy){const ids=updated.activities.map(a=>a.id).filter(id=>id!==copy.id);const at=ids.indexOf(activityId);if(at!==-1){ids.splice(at+1,0,copy.id);await request(`/sessions/${selected}/pages/order`,'PUT',{activity_ids:ids});updated=await request<Snapshot>(`/sessions/${selected}`)}}
  setSnap(updated);
  if(copy)beginPageDesign(updated.activities.find(a=>a.id===copy.id)||copy);
  else setNotice('Pagina duplicata: seleziona la copia dalla barra laterale.');
 }catch(e){notify(e)}}
const selectedSessionRef=useRef(selected);
selectedSessionRef.current=selected;
const pageOrderRequestInFlight=useRef(false);
const [pageOrderPending,setPageOrderPending]=useState(false);
const [pageOrderAnnouncement,setPageOrderAnnouncement]=useState('');
async function persistPageOrder(activityIds:string[]){
 if(pageOrderRequestInFlight.current)return;
 pageOrderRequestInFlight.current=true;
 setPageOrderPending(true);
 setPageOrderAnnouncement('Riordino delle pagine in corso');
 const sessionId=selected;
 try{
  const outcome=await commitAndReconcilePageOrder(
   activityIds,
   ()=>request(`/sessions/${sessionId}/pages/order`,'PUT',{activity_ids:activityIds}),
   ()=>request<Snapshot>(`/sessions/${sessionId}`),
   snapshot=>snapshot.activities.map(activity=>activity.id),
  );
  // A response for a former session must never overwrite the active session.
  if(selectedSessionRef.current===sessionId){
   setSnap(outcome.snapshot);
   setPageOrderAnnouncement(({saved:'Ordine delle pagine salvato',recovered:'Ordine salvato e recuperato dal server',
    rejected:'Riordino non applicato: mostrato l’ordine effettivo del server',
    concurrent:'Ordine modificato contemporaneamente: mostrato l’ordine del server'} as const)[outcome.state]);
  }
 }catch(e){
  // PUT may have COMMITTED despite a lost response; never claim the old order was preserved.
  if(selectedSessionRef.current===sessionId)setPageOrderAnnouncement('Esito del riordino non verificabile: ricarica la sessione prima di spostare altre pagine');
  notify(e);
 }finally{pageOrderRequestInFlight.current=false;setPageOrderPending(false)}
}
async function dropPage(sourceId:string,targetId:string){
 if(!snap||snap.session.status==='closed'||sourceId===targetId||!confirmPageNavigation()||pageOrderRequestInFlight.current)return;
 try{
  const activity_ids=movePageId(snap.activities.map(a=>a.id),sourceId,targetId);
  await persistPageOrder(activity_ids);
 }catch(e){notify(e)}
}
async function movePage(index:number,to:number){
 if(!snap||index<0||index>=snap.activities.length||to<0||to>=snap.activities.length||snap.session.status==='closed'||!confirmPageNavigation()||pageOrderRequestInFlight.current)return;
 const ids=snap.activities.map(a=>a.id);[ids[index],ids[to]]=[ids[to],ids[index]];
 await persistPageOrder(ids);
}
async function importEditablePowerPoint(file:File|undefined){
 if(!file)return;
 if(!file.name.toLowerCase().endsWith('.pptx')||file.size>50*1024*1024){setError('Seleziona un PPTX fino a 50 MiB');return}
 setAssetBusy(true);
 try{
  const response=await fetch('/api/presentations/import-editable',{method:'POST',credentials:'include',headers:{'Content-Type':'application/vnd.openxmlformats-officedocument.presentationml.presentation'},body:file});
  const result=await response.json();if(!response.ok)throw Error(result.error||`HTTP ${response.status}`);
  await load();setSelected(result.id);setSnap(null);setDashboardPage('session');
  setNotice(`${result.pages} pagine modificabili importate. Verifica font, immagini e layout: conversione parziale.`);
 }catch(e){notify(e)}finally{setAssetBusy(false)}
}
async function importPresentationFile(file:File|undefined){
 if(!file||!selected)return;
 if(file.size>100*1024*1024){setError('File superiore a 100 MiB');return}
 const pdf=file.name.toLowerCase().endsWith('.pdf'),pptx=file.name.toLowerCase().endsWith('.pptx');
 if(!pdf&&!pptx){setError('Seleziona PDF o PPTX');return}
 setAssetBusy(true);
 try{
  const response=await fetch(`/api/sessions/${selected}/presentation-import`,{method:'POST',credentials:'include',headers:{'Content-Type':pdf?'application/pdf':'application/vnd.openxmlformats-officedocument.presentationml.presentation'},body:file});
  const result=await response.json();if(!response.ok)throw Error(result.error||`HTTP ${response.status}`);
  setSnap(await request<Snapshot>(`/sessions/${selected}`));await refreshAssets();setNotice(`${result.created} pagine importate`);
 }catch(e){notify(e)}finally{setAssetBusy(false)}
}
async function importSlideImages(files:FileList|null){if(!files?.length||!selected)return;if(files.length>100){setError('Massimo 100 immagini per importazione');return}setAssetBusy(true);try{let created=0;for(const [index,file] of Array.from(files).entries()){
const mime=mediaUploadMime(file,'image');
if(!mime||!['image/png','image/jpeg','image/webp'].includes(mime)||file.size>100*1024*1024)throw Error(`Formato o dimensione non validi: ${file.name}`);
const r=await fetch(`/api/sessions/${selected}/assets`,{method:'POST',credentials:'include',headers:{'Content-Type':mime},body:file});
if(!r.ok)throw Error(`Upload pagina ${index+1}: HTTP ${r.status}`);
const asset=await r.json();const title=file.name.replace(/\.[^.]+$/,'').slice(0,240)||`Slide ${index+1}`;
await request(`/sessions/${selected}/slides`,'POST',{asset_id:asset.id,title});created++;
}
setSnap(await request<Snapshot>(`/sessions/${selected}`));await refreshAssets();setNotice(`${created} pagine slide aggiunte alla sequenza`);
}catch(e){notify(e)}finally{setAssetBusy(false)}}
async function addSlide(asset:{id:string;mime_type:string}){const title=window.prompt('Titolo della nuova pagina',`Slide ${snap?.activities.length||1}`);if(!title?.trim())return;try{await request(`/sessions/${selected}/slides`,'POST',{asset_id:asset.id,title:title.trim()});setSnap(await request<Snapshot>(`/sessions/${selected}`));setNotice('Pagina slide aggiunta alla sequenza')}catch(e){notify(e)}}
async function renameCanvasPage(page:Activity){
 if(!selected||snap?.session.status==='closed')return;
 const proposal=window.prompt('Nuovo nome della pagina',page.title);
 if(proposal===null)return;
 const title=proposal.trim();
 if(!title||title.length>240||/[\x00-\x1f\x7f]/.test(title)){setNotice('Il nome della pagina deve contenere da 1 a 240 caratteri, senza caratteri di controllo.');return}
 if(title===page.title)return;
 try{
  const renamed=await request<{id:string;title:string}>(`/sessions/${selected}/pages/${page.id}/title`,'PATCH',{title});
  // Preserve an unsaved in-memory canvas draft: title-only edits never reload its design.
  setSnap(old=>old?{...old,activities:old.activities.map(a=>a.id===renamed.id?{...a,title:renamed.title}:a)}:old);
  setNotice(`Pagina rinominata: ${renamed.title}`);
 }catch(e){notify(e)}
}
function renameCurrentCanvasPage(){const page=snap?.activities.find(a=>a.id===designActivity);if(page)void renameCanvasPage(page)}
function createCanvasPage(){return createCanvasPageAt()}
async function createCanvasPageAt(anchorId?:string,where:'before'|'after'='after'){
 if(!confirmPageNavigation())return;
 const name=window.prompt('Titolo della nuova pagina',`Pagina ${(snap?.activities.length||0)+1}`);
 if(!name?.trim())return;
 try{const created=await request<{id:string}>(`/sessions/${selected}/pages`,'POST',{title:name.trim()});
 let updated=await request<Snapshot>(`/sessions/${selected}`);
 if(anchorId){const ids=updated.activities.map(a=>a.id).filter(id=>id!==created.id);const at=ids.indexOf(anchorId);if(at!==-1){ids.splice(at+(where==='after'?1:0),0,created.id);await request(`/sessions/${selected}/pages/order`,'PUT',{activity_ids:ids});updated=await request<Snapshot>(`/sessions/${selected}`)}}
 setSnap(updated);setSessionTab('pages');
 const page=updated.activities.find(a=>a.id===created.id);
 if(page){beginPageDesign(page);setNotice('Pagina creata. Inserisci i widget dal canvas, quindi salva il layout.')}
 }catch(e){notify(e)}
}
async function createInteractivePage(template:'poll'|'quiz'|'timed_quiz'){
 const titles={poll:'Nuovo sondaggio',quiz:'Nuovo quiz',timed_quiz:'Nuovo quiz a tempo'};
 const name=window.prompt('Titolo della pagina',titles[template]);
 if(!name?.trim())return;
 try{
  const opts=[{id:'option-1',label:'Opzione 1'},{id:'option-2',label:'Opzione 2'}];
  const created=await request<Activity>(`/sessions/${selected}/activities`,'POST',{
   type:template,title:name.trim(),options:opts,answer_mode:'single',answer_required:true,
   correct_option_id:template==='poll'?null:'option-1',
   duration_seconds:template==='timed_quiz'?30:null
  });
  const updated=await request<Snapshot>(`/sessions/${selected}`);
  setSnap(updated);setSessionTab('pages');
  const page=updated.activities.find(a=>a.id===created.id);
  if(page){beginPageDesign(page);setNotice('Pagina interattiva creata. Configura opzioni, risposte e durata nel widget e salva il layout.');}
 }catch(e){notify(e)}
}
async function addActivity(){try{const opts=(answerMode==='text'||answerMode==='file')?[]:options.split('\n').map(x=>x.trim()).filter(Boolean).map((label,i)=>({id:`option-${i+1}`,label}));const created=await request<Activity>(`/sessions/${selected}/activities`,'POST',{type:kind,title,options:opts,answer_mode:answerMode,answer_required:answerRequired,correct_option_id:(kind==='quiz'||kind==='timed_quiz')&&answerMode==='single'?opts[correct]?.id:null,correct_option_ids:answerMode==='multiple'?opts.filter((_,i)=>multipleAnswers.includes(String(i))).map(x=>x.id):[],duration_seconds:kind==='timed_quiz'?30:null});setTitle('');const updated=await request<Snapshot>(`/sessions/${selected}`);setSnap(updated);setSessionTab('pages');const newPage=updated.activities.find(a=>a.id===created.id);if(newPage){beginPageDesign(newPage);setNotice('Pagina creata: ora puoi inserire e configurare i widget sul canvas. Salva il layout per pubblicare le modifiche.')}}catch(e){notify(e)}}
async function resetSessionToReady(){if(!selected||!window.confirm('Riportare la sessione a non avviata? Tutti i partecipanti, le risposte, i voti e le statistiche saranno cancellati definitivamente; le pagine, i widget e le impostazioni resteranno.'))return;try{await request(`/sessions/${selected}/reset-to-ready`,'POST',{confirmation:'RESET_SESSION_RESULTS'});setSnap(await request<Snapshot>(`/sessions/${selected}`));await load();setNotice('Sessione non avviata: risultati e partecipanti cancellati, configurazione conservata. Il link pubblico è stato rigenerato.')}catch(e){notify(e)}}
async function restartPageTimer(a:Activity){const clearResponses=window.confirm('Riavviare il timer E AZZERARE le risposte precedenti?\nOK: azzera.\nAnnulla: scegli se mantenerle.');if(!clearResponses&&!window.confirm('Riavviare il timer MANTENENDO le risposte precedenti?'))return;try{await request(`/sessions/${selected}/activities/${a.id}/restart-timer`,'POST',{confirmation:'RESTART_PAGE_TIMER',clear_responses:clearResponses});setSnap(await request<Snapshot>(`/sessions/${selected}`));setNotice('Countdown riavviato: i partecipanti possono rispondere di nuovo.')}catch(e){notify(e)}}
async function changeStatus(status:string){try{await request(`/sessions/${selected}/status`,'POST',{status});await request<Snapshot>(`/sessions/${selected}`).then(setSnap);load()}catch(e){notify(e)}}
async function updateRetention(days:number){try{await request(`/sessions/${selected}/retention`,'PATCH',{retention_days:days});setSnap(await request<Snapshot>(`/sessions/${selected}`));}catch(e){notify(e)}}
async function revokeSession(){if(!window.confirm(lang==='it'?'Revocare tutti gli accessi e chiudere la sessione?':'Revoke every access link and close the session?'))return;try{await request(`/sessions/${selected}/revoke`,'POST');setSnap(await request<Snapshot>(`/sessions/${selected}`));await load()}catch(e){notify(e)}}
async function deleteSession(){if(!window.confirm(lang==='it'?'Eliminare definitivamente la sessione e tutte le risposte?':'Permanently delete this session and all responses?'))return;try{await fetch(`/api/sessions/${selected}`,{method:'DELETE',credentials:'include'}).then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`)});setSelected('');setDashboardPage('open');setSnap(null);await load()}catch(e){notify(e)}}
async function activate(a:Activity){try{await request(`/sessions/${selected}/activities/${a.id}/open`,'POST');await request<Snapshot>(`/sessions/${selected}`).then(setSnap)}catch(e){notify(e)}}
async function closeActivity(a:Activity){try{await request(`/sessions/${selected}/activities/${a.id}/close`,'POST');await request<Snapshot>(`/sessions/${selected}`).then(setSnap)}catch(e){notify(e)}}
async function join(){
 if(joining.current)return;
 joining.current=true;setJoinPending(true);
 try{if(!consent)throw Error('Functional cookies are required');await request(`/join/${encodeURIComponent(joinCode)}`,'POST',{pseudonym:pseudonym.trim()});localStorage.setItem('quorivio_pseudonym',pseudonym.trim());setJoined(true);setParticipantReady(true)}
 catch(e){notify(e)}finally{joining.current=false;setJoinPending(false)}
}
async function saveSlideMaster(){if(!selected||!snap)return;try{const current=snap.session.theme||{};const next={...current,master:{...(current.master||{}),titleStyle:slideMasterDraft}};await request(`/sessions/${selected}/design`,'PATCH',{theme:next});const latest=await request<Snapshot>(`/sessions/${selected}`);setSnap(latest);setNotice('Schema Titolo salvato per tutte le pagine della sessione')}catch(e){notify(e)}}
async function saveDesign(){try{const theme={...(snap?.session.theme||{}),...(pageBackground?{backgroundUrl:pageBackground}:{}),...(pageLogo?{logos:[pageLogo]}:{})};await request(`/sessions/${selected}/design`,'PATCH',{theme});if(current){const page_design={...(mediaUrl?{media:[{kind:mediaKind,url:mediaUrl}]}:{})};await request(`/sessions/${selected}/activities/${current.id}/design`,'PATCH',{page_design,result_design:page_design})}setSnap(await request(`/sessions/${selected}`))}catch(e){notify(e)}}
async function vote(){
 if(votePending||sent||!entry?.activity||!joined)return;
 const activityId=entry.activity.id;
 const mode=entry.activity.answer_mode||'single';
 if(!canSubmitParticipantAnswer(mode,entry.activity.answer_required!==false,{answer,multipleAnswers,freeText}))return;
 setVotePending(true);
 try{
  const payload:any={activity_id:activityId};
  if(mode==='single')payload.option_id=answer;
  else if(mode==='multiple')payload.option_ids=multipleAnswers;
  else if(mode==='text')payload.text=freeText.trim();
  else payload.asset_id=answer;
  await request(`/join/${encodeURIComponent(joinCode)}/respond`,'POST',payload);
  setSent(true);
 }catch(e){notify(e)}finally{setVotePending(false)}
}
async function react(emoji:string){try{const result=await request(`/join/${encodeURIComponent(joinCode)}/reactions`,'POST',{activity_id:entry.activity.id,emoji});setSelectedReaction(emoji);if(result.already_reacted)setNotice('Reazione già selezionata')}catch(e){notify(e)}}
async function ratePage(score:number,widgetId:string){
  const key=entry.activity.id+':'+widgetId;
  if(pendingRatingVotes.current.has(key))return;
  pendingRatingVotes.current.add(key);setRatingPending(old=>[...new Set([...old,widgetId])]);
  try{
   const data=await request(`/join/${encodeURIComponent(joinCode)}/ratings`,'POST',{activity_id:entry.activity.id,score,widget_id:widgetId,comment:ratingComments[widgetId]||''});
   setRatingSent(old=>[...new Set([...old,widgetId])]);
   setRatingVotes(old=>({...old,[key]:String(score)}));
   if(data.already_rated)setNotice('Questo voto era già stato registrato');
   else setNotice('Voto registrato. Puoi modificarlo finché la pagina rimane aperta.');
  }catch(e){notify(e)}finally{pendingRatingVotes.current.delete(key);setRatingPending(old=>old.filter(id=>id!==widgetId))}
 }
async function loadRatingStats(){try{setRatingStats(await request(`/sessions/${selected}/ratings/stats`))}catch(e){notify(e)}}
async function loadReactions(){try{setReactions(await request(`/sessions/${selected}/reactions/stats`))}catch(e){notify(e)}}
useEffect(()=>{setRatingSent([]);setRatingComments({});setSelectedReaction('');setMultipleAnswers([]);setAnswer('');setFreeText('');setSent(false);setVotePending(false)},[entry?.activity?.id,entry?.activity?.opened_at]);const current= snap?.activities.find(a=>a.id===snap.session.current_activity_id);const showResults=(s:Snapshot,a:Activity,mode="bars")=>{const rows=a.options.map(o=>({...o,count:s.results.find(r=>r.activity_id===a.id&&r.option_id===o.id)?.count||0}));const total=rows.reduce((n,r)=>n+r.count,0);return <div className="results">{mode==="pie"&&total>0&&<div className="result-pie" role="img" aria-label="Distribuzione percentuale delle risposte" style={{background:`conic-gradient(${rows.map((r,i)=>`hsl(${(i*137.5)%360} 62% 53%) ${rows.slice(0,i).reduce((n,x)=>n+x.count,0)/total*100}% ${rows.slice(0,i+1).reduce((n,x)=>n+x.count,0)/total*100}%`).join(",")})`}}/>}{rows.map(r=><div className="result" key={r.id}><div className="result-heading"><span>{r.label}</span><strong>{r.count} · {total?Math.round(r.count/total*100):0}%</strong></div>{mode==="bars"&&<div className="bar-track"><div className="bar" style={{width:`${total?r.count/total*100:0}%`}}/></div>}</div>)}<p className="muted">{total} risposte</p></div>};
return <div className="app"><a className="skip-link" href="#main-content">{pc.skip}</a><header><a className="brand" href="/"><img src="/editor-quorivio-logo.svg" alt="Quorivio" style={{height:35,maxWidth:172}}/></a><nav><a href={`/docs/manuals/user-guide.${lang}.pdf`} target="_blank" rel="noreferrer">{lang==='it'?'Manuale utente':'User guide'}</a>{me&&<a href={`/docs/manuals/presenter-guide.${lang}.pdf`} target="_blank" rel="noreferrer">{lang==='it'?'Manuale presentatore':'Presenter guide'}</a>}{me&&<a href={`/docs/manuals/admin-guide.${lang}.pdf`} target="_blank" rel="noreferrer">{lang==='it'?'Manuale amministratore':'Administrator guide'}</a>}<span className="version">0.1.0-dev</span><button className="small ghost" onClick={()=>setLang(lang==='it'?'en':'it')}>{lang.toUpperCase()} ↔</button>{me&&!joinPath&&<button className="small ghost" onClick={async()=>{await request('/auth/logout','POST');writeWorkspaceLocation({sessionId:'',section:'workspace',tab:'overview',pageId:''});setMe(null);setSelected('');setSnap(null);setDesignActivity('');setDashboardPage('workspace')}}><LogOut size={16}/> Logout</button>}</nav></header>{notice&&<div role="status" className="alert" onClick={()=>setNotice('')}>{notice} <button className="small outline" type="button" onClick={e=>{e.stopPropagation();setNotice('')}} aria-label="Chiudi messaggio">×</button></div>}{error&&<div role="alert" className="alert" onClick={()=>setError('')}>{error} <button className="small outline" type="button" onClick={e=>{e.stopPropagation();setError('')}} aria-label="Chiudi errore">×</button></div>}{!cookieAcknowledged&&createPortal(<dialog ref={node=>{if(node&&!node.open)node.showModal()}} aria-label="Informativa cookie funzionali" className="panel functional-cookie-dialog" onCancel={event=>event.preventDefault()}><h3>Cookie funzionali</h3><p>Quorivio utilizza cookie tecnici necessari per autenticazione, sessioni e sicurezza. Non sono utilizzati cookie di profilazione da questa funzione.</p><button className="primary small" onClick={()=>{document.cookie='q_cookie_notice=ack; Max-Age=31536000; Path=/; SameSite=Lax'+(location.protocol==='https:'?'; Secure':'');setCookieAcknowledged(true)}}>Ho capito</button></dialog>,document.body)}
{joinPath?<main id="main-content" className="narrow" style={window.matchMedia('(max-width:700px)').matches?{backgroundColor:'#ffffff',backgroundImage:'none'}:entry?.activity?.page_design?.backgroundAssetId?{backgroundImage:`url(/api/join/${encodeURIComponent(joinCode)}/activities/${entry.activity.id}/media/${entry.activity.page_design.backgroundAssetId})`,backgroundSize:"cover",backgroundPosition:"center"}:entry?.activity?.page_design?.backgroundUrl?{backgroundImage:`url(${entry.activity.page_design.backgroundUrl})`,backgroundSize:"cover"}:entry?.theme?.backgroundUrl?{backgroundImage:`url(${entry.theme.backgroundUrl})`,backgroundSize:"cover"}:undefined}>{(entry?.theme?.logos||[]).map((url:string,i:number)=><img key={i} src={url} alt="Logo organizzazione" style={{maxHeight:72,maxWidth:210,marginRight:12}}/>)}<div className="eyebrow"><Radio size={17}/> LIVE SESSION</div><h1>{entry?.session?.title||'Sessione non disponibile'}</h1>{resolveSlideMasterWidgets(entry?.activity?.page_design?.widgets||[],entry?.theme?.master?.widgets).some((w:any)=>w.kind==='title')&&<div className="participant-slide-title" aria-label="Titolo pagina attiva">{resolveSlideMasterWidgets(entry.activity.page_design?.widgets||[],entry?.theme?.master?.widgets).filter((w:any)=>w.kind==='title').map((w:any)=><h2 key={w.id} hidden={w.showTitle===false} style={widgetDisplay(w,{pageTitle:entry.activity.title,masterTitleStyle:entry.theme?.master?.titleStyle}).style as React.CSSProperties}>{widgetDisplay(w,{pageTitle:entry.activity.title}).title}</h2>)}</div>}{joinStatus==='loading'?<section className="panel centered" role="status">{pc.loading}</section>:joinStatus==='unavailable'?<section className="panel centered" role="alert"><h2>{pc.unavailable}</h2><p>{pc.unavailableHelp}</p><button type="button" onClick={()=>void refreshPublicEntry()}>{pc.retry}</button><a href="/">{pc.another}</a></section>:!participantReady?<section className="panel centered" role="status">{pc.checking}</section>:entry?.session&&(!joined?<section className="panel centered"><Users size={42} className="accent"/><h2>Partecipa alla sessione</h2><p>Puoi accedere senza account scegliendo uno pseudonimo, se il presentatore abilita gli anonimi. I cookie funzionali sono necessari per ritrovare la partecipazione dopo la riapertura del browser.</p><label>Pseudonimo<input autoComplete="nickname" value={pseudonym} maxLength={40} onChange={e=>setPseudonym(e.target.value)}/></label><label><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/> Accetto i cookie funzionali necessari al servizio</label>{entry.allow_anonymous===false?<p>Accesso anonimo disabilitato: effettua l’accesso con un account approvato.</p>:<button type="button" className="primary" disabled={joinPending||!consent||pseudonym.trim().length<2} onClick={()=>void join()}>{joinPending?pc.joining:t.enter} <ArrowRight size={18}/></button>}</section>:entry?.session?.status!=='active'?<section className="panel centered" role="status"><h2>{pc.paused}</h2><p>{pc.pausedHelp}</p></section>:entry?.activity?<section className="panel"><p className="participant-connection" role="status" aria-live="polite">{liveConnection==='connected'?pc.connected:liveConnection==='connecting'?pc.connecting:liveConnection==='blocked'?pc.blocked:pc.disconnected}</p><span className="pill">{entry.activity.type==='slide'?'Slide':entry.activity.type==='timed_quiz'?'Quiz a tempo':entry.activity.type==='quiz'?'Quiz':'Sondaggio'}</span>{!resolveSlideMasterWidgets(entry.activity.page_design?.widgets||[],entry?.theme?.master?.widgets).length&&<h2>{entry.activity.page_design?.header||entry.activity.title}</h2>}{entry.activity.type==='timed_quiz'&&<PageTimer openedAt={entry.activity.opened_at} duration={entry.activity.duration_seconds} label="Quiz a tempo"/>}{(entry.activity.page_design?.media||[]).map((m:any,i:number)=>m.kind==='image'?<img key={i} src={m.url} alt={m.alt||'Media'} style={{maxWidth:'100%'}}/>:m.kind==='video'?<video key={i} controls src={m.url} style={{maxWidth:'100%'}}/>:<a key={i} href={m.url} target="_blank" rel="noreferrer">Apri documento PDF</a>)}<div className="audience-layout-controls" role="group" aria-label="Visualizzazione della pagina"><button type="button" aria-pressed={!participantReadingMode} onClick={()=>setParticipantReadingMode(false)}>Diapositiva 16:9</button><button type="button" aria-pressed={participantReadingMode} onClick={()=>setParticipantReadingMode(true)}>Lettura accessibile</button></div><div className="audience-stage-scroll" role="region" aria-label="Contenuto della diapositiva" tabIndex={0}><div ref={element=>{if(element)element.inert=audienceTimerExpired}} className={'audience-widget-layout'+(audiencePortrait?' stage-phone':participantReadingMode?' stage-reading':resolveSlideMasterWidgets(entry.activity.page_design?.widgets||[],entry?.theme?.master?.widgets).some((w:any)=>w.position)?' stage-fidelity':' stage-legacy')} style={{position:'relative',...(audiencePortrait?{height:mobileStageHeight(resolveSlideMasterWidgets(entry.activity.page_design?.widgets||[],entry?.theme?.master?.widgets)),backgroundImage:entry.activity.page_design?.mobile?.backgroundAssetId?`url(/api/join/${encodeURIComponent(joinCode)}/activities/${encodeURIComponent(entry.activity.id)}/media/${encodeURIComponent(entry.activity.page_design.mobile.backgroundAssetId)})`:'none',backgroundColor:entry.activity.page_design?.mobile?.backgroundColor||'#ffffff',backgroundSize:'cover',backgroundPosition:'center'}:entry.activity.page_design?.backgroundAssetId?{backgroundImage:`url(/api/join/${encodeURIComponent(joinCode)}/activities/${encodeURIComponent(entry.activity.id)}/media/${encodeURIComponent(entry.activity.page_design.backgroundAssetId)})`,backgroundSize:'cover',backgroundPosition:'center'}:{})}}>{(audiencePortrait?mobilePageWidgets(resolveSlideMasterWidgets(entry.activity.page_design?.widgets||[],entry?.theme?.master?.widgets),entry.activity.page_design?.mobile):resolveSlideMasterWidgets(entry.activity.page_design?.widgets||[],entry?.theme?.master?.widgets)).filter((w:any)=>w.kind!=='participant-count').map((w:any)=><div key={w.id} data-widget-kind={w.kind} className={`page-widget widget-${w.style?.animation||'none'}`} data-show-title={w.showTitle!==false} {...widgetArtData(w.style)} style={{...(w.position?widgetGeometryStyle(w.position):{}),...(w.position?{'--stage-x':w.position.x+'%','--stage-y':w.position.y+'%','--stage-width':w.position.width+'%','--stage-height':(w.position.height??24)+'%','--stage-rotation':(w.position.rotation??0)+'deg'}:{}),...widgetAppearanceStyle(w.style,w.style?.fillImageAssetId?`/api/join/${encodeURIComponent(joinCode)}/activities/${entry.activity.id}/media/${w.style.fillImageAssetId}`:undefined),...widgetTypographyStyle(w.style),'--authored-widget-font-size':widgetTypographyStyle(w.style).fontSize,...(audiencePortrait?{'--mobile-widget-font-size':`${w.style?.fontSize||16}px`,fontSize:`${w.style?.fontSize||16}px`}:{})} as React.CSSProperties}>{w.kind!=='shape'&&<WidgetShapeOutline style={w.style}/>}<WidgetGraphic kind={w.kind} style={w.style}/><WidgetContentFit>{w.kind==='rating'?<>{w.showTitle!==false&&<strong>{w.label||'Indice di gradimento'}</strong>}{w.description&&<p>{w.description}</p>}<label>Commento facoltativo<textarea maxLength={1000} rows={2} value={ratingComments[w.id]||''} onChange={e=>setRatingComments(old=>({...old,[w.id]:e.target.value}))}/></label><p className="muted tiny">0 = gradimento minimo · 9 = gradimento massimo</p><RatingChoices view={w.style?.ratingView} disabled={ratingPending.includes(w.id)} selected={ratingVotes[entry.activity.id+':'+w.id]} onSelect={n=>void ratePage(n,w.id)}/></>:w.kind==='profile'?<PresenterProfileWidget code={joinCode} presenterId={w.presenterId} label={w.label} showEmail={w.showEmail===true}/>:['image','logo'].includes(w.kind)&&w.assetId?<CroppedImage className="projection-media" src={`/api/join/${encodeURIComponent(joinCode)}/activities/${encodeURIComponent(entry.activity.id)}/media/${encodeURIComponent(w.assetId)}`} crop={w.crop} alt={w.label||'Immagine'}/>:w.kind==='pdf'&&w.assetId?<a href={`/api/join/${encodeURIComponent(joinCode)}/activities/${entry.activity.id}/media/${w.assetId}`} target="_blank" rel="noopener noreferrer">Apri PDF</a>:w.kind==='video'&&w.assetId?<video controls preload="metadata" style={{maxWidth:'100%'}} src={`/api/join/${encodeURIComponent(joinCode)}/activities/${entry.activity.id}/media/${w.assetId}`}/>:w.kind==='postit'?<div className="rehearsal-postit" style={{whiteSpace:'pre-wrap',backgroundColor:w.style?.fillNone?'transparent':w.style?.fillColor||undefined,textAlign:w.style?.textAlign||undefined}}>{w.description&&w.description.startsWith(w.label||'')?<WidgetStyledText text={w.description} widget={w} field="description"/>:<><WidgetStyledText text={w.label||'Nota'} widget={w} field="label"/>{w.description&&<> {'\n'}<WidgetStyledText text={w.description} widget={w} field="description"/></>}</>}</div>:w.kind==='text'?<p style={{whiteSpace:'pre-wrap',textAlign:w.style?.textAlign||undefined}}>{w.description&&w.description.startsWith(w.label||'')?<WidgetStyledText text={w.description} widget={w} field="description"/>:<><WidgetStyledText text={w.label||''} widget={w} field="label"/>{w.description&&<> {'\n'}<WidgetStyledText text={w.description} widget={w} field="description"/></>}</>}</p>:w.kind==='divider'?<hr/>:w.kind==='footer'?<div className="projection-slide-footer" style={widgetDisplay(w,{sessionTitle:entry.session?.title,pageNumber:Number(entry.activity.position)+1}).style as React.CSSProperties}><span className="slide-footer-center">{w.showTitle===false?'':widgetDisplay(w,{sessionTitle:entry.session?.title,pageNumber:Number(entry.activity.position)+1}).center}</span></div>:w.kind==='timer'?<PageTimer openedAt={entry.activity.opened_at} duration={entry.activity.duration_seconds} label={w.label} face={widgetTimerFace(w.style)}/>:w.kind==='qr'?<ParticipantAccessQr sessionId={entry.session.id} joinCode={joinCode} publicAccess widget={w}/>:w.kind==='question'?<QuestionWidget key={`${entry.activity.id}:${entry.activity.opened_at}:${w.id}`} code={joinCode} activityId={entry.activity.id} widget={w}/>:w.kind==='timed-quiz'?<><PageTimer openedAt={entry.activity.opened_at} duration={w.durationSeconds||30} label={w.label||'Quiz a tempo'} face={widgetTimerFace(w.style)}/><QuestionWidget key={`${entry.activity.id}:${entry.activity.opened_at}:${w.id}`} code={joinCode} activityId={entry.activity.id} widget={w}/></>:w.kind==='results-button'?null:w.kind==='topic-question'?<TopicQuestionWidget code={joinCode} activityId={entry.activity.id} widget={w}/>:w.kind==='reactions'?<div className="projection-sample-reactions">{w.showTitle!==false&&<strong><WidgetStyledText text={w.label||'Reazioni'} widget={w} field="label"/></strong>}<ReactionChoices size={w.reactionIconSize||32} selected={selectedReaction} onSelect={emoji=>void react(emoji)}/></div>:(w.kind==='shape'||w.kind==='line')?(w.showTitle===false?null:<span className="widget-graphic-label">{w.label||(w.kind==='shape'?'Forma':'Linea')}</span>):w.kind==='participant-count'?<div className="widget-live-count"><strong>{w.label||'Partecipanti connessi'}</strong><span>{entry.activity.connected_participants??0}</span></div>:null}</WidgetContentFit></div>)}<SlideCanvasNumber widgets={resolveSlideMasterWidgets(entry.activity.page_design?.widgets||[],entry?.theme?.master?.widgets)} pageNumber={Number(entry.activity.position)+1}/></div></div>{audienceTimerExpired?<p role="status" className="notice">Tempo scaduto: le interazioni con i widget sono terminate.</p>:<AudienceExtensions key={entry.activity.id} joinCode={joinCode} activityId={entry.activity.id} joined={joined}/>} {!audienceTimerExpired&&!(entry.activity.page_design?.widgets||[]).some((w:any)=>w.kind==='reactions')&&<div className="reaction-bar" aria-label="Reazioni alla pagina"><span>Reagisci:</span>{['👍','❤️','😂','😮','👏','🎉','🤔','😕'].map(emoji=><button key={emoji} className="small outline" aria-pressed={selectedReaction===emoji} onClick={()=>react(emoji)} aria-label={'Reazione '+emoji}>{emoji}</button>)}</div>}{liveResults.length>0&&<section className="panel"><h3>Risultati live</h3>{entry.activity.options.map((o:any)=><p key={o.id}>{o.label}: {liveResults.find((r:any)=>r.option_id===o.id)?.count||0}</p>)}</section>}{entry.activity.type==='slide'?<p className="muted">Pagina informativa: nessuna risposta richiesta.</p>:sent?<div className="success" role="status" aria-live="polite"><ShieldCheck size={36}/><h3>{t.thankyou}</h3><p>Attendi la prossima attività.</p></div>:entry.activity.status!=='open'?<p>Questa attività è chiusa.</p>:<>{(entry.activity.answer_mode==='text')?<textarea aria-label="La tua risposta" rows={5} maxLength={5000} value={freeText} onChange={e=>setFreeText(e.target.value)} placeholder="Scrivi la tua risposta"/>:(entry.activity.answer_mode==='file')?<p>Carica un allegato usando l'upload della sessione e indica il suo identificativo.<input value={answer} onChange={e=>setAnswer(e.target.value)} placeholder="UUID allegato"/></p>:<div className="choices" role="group" aria-label="Opzioni di risposta">{entry.activity.options.map((o:any)=><button type="button" aria-pressed={entry.activity.answer_mode==='multiple'?multipleAnswers.includes(o.id):answer===o.id} disabled={votePending} className={(entry.activity.answer_mode==='multiple'?multipleAnswers.includes(o.id):answer===o.id)?'choice active':'choice'} key={o.id} onClick={()=>entry.activity.answer_mode==='multiple'?setMultipleAnswers(prev=>prev.includes(o.id)?prev.filter(x=>x!==o.id):[...prev,o.id]):setAnswer(o.id)}>{o.label}</button>)}</div>}<button type="button" disabled={votePending||!canSubmitParticipantAnswer(entry.activity.answer_mode||'single',entry.activity.answer_required!==false,{answer,multipleAnswers,freeText})} className="primary" onClick={()=>void vote()}>{votePending?pc.sending:t.vote} <ArrowRight size={18}/></button></>}</section>:<section className="panel centered"><Wifi size={36}/><h2>Sei connesso</h2><p>Il presentatore avvierà presto un’attività.</p></section>)}</main>:
publicPath?<PresenterLiveScreen sessionId={publicId} renderResults={showResults}/>:
me===undefined?<main id="main-content" className="narrow">Caricamento...</main>:me?.must_change_password?<main id="main-content" className="narrow"><section className="panel"><h1>Modifica obbligatoria della password</h1><p>Prima di utilizzare Quorivio, imposta una password personale di almeno 12 caratteri.</p><label>Nuova password<input type="password" autoComplete="new-password" value={newPassword} onChange={e=>setNewPassword(e.target.value)}/></label><label>Conferma nuova password<input type="password" autoComplete="new-password" value={confirmNewPassword} onChange={e=>setConfirmNewPassword(e.target.value)}/></label><button className="primary" disabled={newPassword.length<12||newPassword!==confirmNewPassword} onClick={async()=>{try{await request('/auth/change-password','POST',{current_password:password,new_password:newPassword});setMe(null);setSelected('');setNewPassword('');setConfirmNewPassword('');setPassword('');setError('');setNotice('Password aggiornata: accedi nuovamente con la nuova password.')}catch(e){notify(e)}}}>Aggiorna password</button></section></main>:!me&&resetToken?<main id="main-content" className="narrow"><form className="panel" aria-labelledby="reset-password-title" onSubmit={e=>{e.preventDefault();void confirmPasswordRecovery()}}><h1 id="reset-password-title">Recupero password / Password reset</h1><label>Nuova password / New password<input type="password" autoComplete="new-password" minLength={12} maxLength={256} value={resetPassword} onChange={e=>setResetPassword(e.target.value)}/></label><label>Conferma nuova password / Confirm new password<input type="password" autoComplete="new-password" minLength={12} maxLength={256} value={resetPasswordConfirmation} onChange={e=>setResetPasswordConfirmation(e.target.value)}/></label>{resetPasswordConfirmation&&resetPassword!==resetPasswordConfirmation&&<p role="status" className="muted tiny">Le password non coincidono. / Passwords do not match.</p>}<button className="primary" disabled={resetSubmitPending||!resetToken||resetPassword.length<12||resetPassword!==resetPasswordConfirmation} type="submit">{resetSubmitPending?"Verifica in corso… / Verifying…":"Conferma / Confirm"}</button><p className="muted tiny">L’autenticazione a due fattori resta attiva. / MFA remains enabled.</p></form></main>:!me?<main id="main-content" className="hero"><div><div className="eyebrow"><span className="live-dot"/> INTERACTIVE PRESENTATIONS, REIMAGINED</div><h1>Ogni voce<br/>conta<span className="brand-dot">.</span></h1><p className="lead">{t.subtitle}. Crea esperienze live con sondaggi, quiz e risultati istantanei.</p><div className="join-by-code"><input aria-label="Codice sessione" placeholder="Codice sessione" value={code} onChange={e=>setCode(normalizeJoinCode(e.target.value))}/><button className="outline" disabled={!code.trim()} onClick={()=>location.assign(`/join/${encodeURIComponent(code.trim())}`)}>Partecipa <ArrowRight size={16}/></button></div><div className="features"><span><Radio size={17}/> Live polls</span><span><Users size={17}/> Audience first</span><span><BarChart3 size={17}/> Real-time insights</span></div></div>{emailChallenge&&<section className="panel login" aria-label="Secondo fattore"><h3>Verifica secondo fattore / Second factor</h3><div className="downloads">{mfaMethods.map(method=><button type="button" key={method} className={mfaMethod===method?'primary small':'outline small'} onClick={()=>void chooseMfaMethod(method)}>{method==='email'?'Email':'Authenticator TOTP'}</button>)}</div>{mfaMethod==='email'?<label>Codice email<input inputMode="numeric" autoComplete="one-time-code" value={emailCode} maxLength={6} onChange={e=>setEmailCode(e.target.value.replace(/\D/g,''))}/></label>:<>{showRecovery?<label>Codice di recupero<input autoComplete="off" value={recoveryCode} onChange={e=>setRecoveryCode(e.target.value)}/></label>:<label>Codice autenticatore<input inputMode="numeric" autoComplete="one-time-code" value={totpCode} maxLength={6} onChange={e=>setTotpCode(e.target.value.replace(/\D/g,''))}/></label>}<button className="small outline" onClick={()=>setShowRecovery(v=>!v)}>{showRecovery?'Usa autenticatore':'Usa codice di recupero'}</button></>}<div className="downloads"><button type="button" disabled={mfaMethod==='email'?emailCode.length!==6:showRecovery?!recoveryCode:totpCode.length!==6} onClick={verifyEmailLogin}>Verifica / Verify</button><button type="button" className="outline small" onClick={()=>{setEmailChallenge('');setEmailCode('')}}>Annulla</button></div></section>}{!emailChallenge&&<form className="panel login" onSubmit={e=>{if(registerMode){e.preventDefault();register()}else handleLogin(e)}}><div className="eyebrow">PRESENTER STUDIO</div><h2>{registerMode?"Registrazione nuovo utente":t.login}</h2><label>{registerMode?t.email:"Email o nickname"}<input type={registerMode?"email":"text"} autoComplete="username" required value={email} onChange={e=>setEmail(e.target.value)}/></label><label>{t.password}<input type="password" required value={password} onChange={e=>setPassword(e.target.value)}/></label><button className="primary">{registerMode?"Invia richiesta di registrazione":"Accedi"} <ArrowRight size={18}/></button><button type="button" className="outline small" onClick={()=>setRegisterMode(!registerMode)}>{registerMode?"Torna al login":"Registrati"}</button><p className="muted tiny">Accesso locale · Configurazione amministratore</p><p className="muted tiny">Nuovi account soggetti all'approvazione dell'amministratore.</p><button type="button" className="outline small" onClick={requestPasswordRecovery} disabled={!email.includes('@')}>Password dimenticata? / Forgot password?</button>{oidcProviders.length>0&&<div className="oidc-options"><p>SSO / Federated sign-in</p>{oidcProviders.map(p=><a key={p.id} className="button outline small" href={'/api/auth/'+(['github','facebook'].includes(p.id)?'social':'oidc')+'/'+encodeURIComponent(p.id)+'/start'}>Accedi con {p.label||p.id.toUpperCase()}</a>)}</div>}</form>}</main>:
<main id="main-content" className="dashboard"><div className="aside"><section className="panel" aria-label="Navigazione funzionalità"><h3>Sezioni</h3>{([['new','Nuova sessione'],['open','Apri sessione'],['calendar','Calendario'],['profile','Profilo presentatore'],['mfa','Sicurezza / MFA'],['sso','SSO / Identità'],...(me?.role==='platform_admin'?([['users','Gestione utenti'],['settings','Impostazioni server']] as const):[])] as const).map(([key,label])=><button key={key} className={dashboardPage===key?'session selected':'session'} style={{width:'100%',marginBottom:7}} onClick={()=>navigateDashboard(key)}>{label}</button>)}</section>{selected&&snap&&<section className="panel" aria-label="Modelli della sessione"><button type="button" className="small outline dashboard-schemes-shortcut" onClick={openSchemaEditor} disabled={sidebarBusy} aria-label="Apri editor degli schemi della sessione">▤ Editor degli schemi</button><p className="muted tiny">Titolo, footer e modelli globali</p></section>}{selected&&dashboardPage==='session'&&snap&&<section className="panel current-session-actions" aria-label="Azioni della sessione corrente">
  <h3>Sessione aperta</h3><strong className="current-session-name">{snap.session.title}</strong>
  <p className="muted tiny">Stato: {snap.session.status}</p>
  <button type="button" className="small outline" onClick={leaveCurrentSession} disabled={sidebarBusy}>Torna alle sessioni</button>
  {snap.session.status!=='closed'&&<button type="button" className="small outline" disabled={sidebarBusy} onClick={()=>void closeSidebarSession()}>Chiudi sessione</button>}
  <button type="button" className="small outline" disabled={sidebarBusy} onClick={()=>void duplicateSelected()}>Duplica sessione</button>
  {snap.session.status!=='closed'&&<button type="button" className="small outline" disabled={sidebarBusy} onClick={()=>setSidebarRename(snap.session.title)}>Rinomina sessione</button>}
  {sidebarRename!==null&&<form onSubmit={e=>{e.preventDefault();void renameSidebarSession()}} aria-label="Rinomina sessione corrente">
    <label>Nuovo nome<input autoFocus maxLength={160} required value={sidebarRename} onChange={e=>setSidebarRename(e.target.value)}/></label>
    <div className="downloads"><button type="submit" className="small primary" disabled={sidebarBusy||!sidebarRename.trim()}>Conferma nome</button><button type="button" className="small outline" disabled={sidebarBusy} onClick={()=>setSidebarRename(null)}>Annulla</button></div>
  </form>}
  {selectedSessionRole==='owner'&&<button type="button" className="small outline danger-action" disabled={sidebarBusy} onClick={()=>void deleteSession()}>Elimina sessione</button>}
  <button type="button" className="small outline" onClick={openSchemaEditor} disabled={sidebarBusy}>Modifica schemi</button>
 </section>}</div><div className="workspace">{dashboardPage==='master'&&snap&&selected&&<section className="panel slide-scheme-workspace" aria-label="Editor degli schemi PowerPoint">
 <header className="slide-scheme-header"><div><h2>Editor degli schemi</h2><p className="muted tiny">Schema globale della sessione · elementi ereditati dalle pagine, personalizzabili localmente</p></div>
  <button type="button" className="slide-scheme-exit outline" onClick={()=>navigateDashboard('session')}>Esci dagli schemi</button>
 </header>
 <div className="slide-scheme-ribbon" role="toolbar" aria-label="Barra multifunzione schemi">
   <div className="slide-scheme-ribbon-group"><strong>Inserisci</strong><div className="slide-scheme-ribbon-actions"><button type="button" disabled={schemaSaving||schemaWidgets.some(w=>w.kind==='title')} onClick={()=>insertSchemaWidget('title')}>Titolo</button><button type="button" disabled={schemaSaving||schemaWidgets.some(w=>w.kind==='footer')} onClick={()=>insertSchemaWidget('footer')}>Footer</button></div></div>
   <div className="slide-scheme-ribbon-group"><strong>Allinea</strong><div className="slide-scheme-ribbon-actions">{([['left','Sinistra'],['center-x','Centro'],['right','Destra'],['top','In alto'],['center-y','Metà'],['bottom','In basso']] as const).map(([mode,label])=><button type="button" key={mode} disabled={!schemaSelected.length} onClick={()=>arrangeSchema(mode as ArrangeMode)}>{label}</button>)}</div></div>
   <div className="slide-scheme-ribbon-group"><strong>Distribuisci</strong><div className="slide-scheme-ribbon-actions">{([['distribute-x','Orizzontale'],['distribute-y','Verticale']] as const).map(([mode,label])=><button type="button" key={mode} disabled={schemaSelected.length<3} onClick={()=>arrangeSchema(mode as ArrangeMode)}>{label}</button>)}</div></div>
   <div className="slide-scheme-ribbon-group slide-scheme-ribbon-save"><strong>Schema</strong><div className="slide-scheme-ribbon-actions"><button type="button" className="primary" disabled={schemaSaving||snap.session.status==='closed'} onClick={()=>void saveSchemaEditor()}>Salva schema</button><span className="muted tiny" role="status">{JSON.stringify(schemaWidgets)!==schemaBaseline.current?'Modifiche non salvate':'Sincronizzato'}</span></div></div>
 </div>
 <div className="slide-scheme-widget-rail" aria-label="Aggiungi widget allo schema"><strong>Widget</strong><div className="slide-scheme-widget-options">{schemaWidgetKinds.map(kind=><button type="button" key={kind} disabled={schemaSaving||schemaWidgets.length>=16||(['title','footer'].includes(kind)&&schemaWidgets.some(w=>w.kind===kind))||(['image','video','logo','pdf'].includes(kind)&&!schemaMediaAssets(kind).length)} title={['image','video','logo','pdf'].includes(kind)&&!schemaMediaAssets(kind).length?'Carica un allegato compatibile nella libreria della sessione':''} onClick={()=>insertSchemaWidget(kind)} aria-label={'Aggiungi widget allo schema: '+editorWidgetNames[kind]}><EditorWidgetIcon kind={kind}/><span>{editorWidgetNames[kind]}</span></button>)}</div></div>
 <div className="slide-scheme-layout"><div className="slide-scheme-canvas"><WidgetCanvas key={`${selected}:master`} widgets={schemaWidgets} onChange={next=>setSchemaWidgets(masterWidgetTemplate(next))} onSelectionChange={ids=>{setSchemaSelected(ids);setSchemaInspected(ids[0]||'')}} onInspectWidget={setSchemaInspected} assets={assets} sessionId={selected} joinCode={snap.session.join_code} pageTitle="Titolo della pagina" sessionTitle={snap.session.title} pageNumber={1} masterTitleStyle={snap.session.theme?.master?.titleStyle}/></div>
 <aside className="panel slide-scheme-inspector" aria-label="Proprietà schema selezionato"><h3>Proprietà dello schema</h3>
 {schemaWidgets.filter(w=>w.id===schemaInspected).map(w=><div key={w.id} className="slide-scheme-properties">
 <h4>{editorWidgetNames[w.kind]||w.kind}</h4>
 {['image','video','logo','pdf'].includes(w.kind)&&<label>Allegato dello schema<select value={w.assetId||''} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,assetId:e.target.value}:x))}>{schemaMediaAssets(w.kind).map(a=><option key={a.id} value={a.id}>{a.mime_type} · {a.id.slice(0,8)}</option>)}</select></label>}
 <label><input type="checkbox" checked={w.showTitle!==false} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,showTitle:e.target.checked}:x))}/>Mostra nome/titolo</label>
 {w.kind!=='title'&&w.kind!=='footer'&&<label>Testo widget<input maxLength={240} value={w.label||''} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,label:e.target.value}:x))}/></label>}
 {w.kind==='title'&&<><label><input type="checkbox" checked={w.titleFollowPage!==false} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,titleFollowPage:e.target.checked}:x))}/> Segui il titolo della pagina</label>{w.titleFollowPage===false&&<label>Testo personalizzato<input maxLength={240} value={w.label||''} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,label:e.target.value}:x))}/></label>}</>}
 {w.kind==='footer'&&<><label><input type="checkbox" checked={w.footerShowSessionTitle!==false} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,footerShowSessionTitle:e.target.checked}:x))}/> Mostra nome della sessione</label><label><input type="checkbox" checked={w.footerShowPageNumber!==false} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,footerShowPageNumber:e.target.checked}:x))}/> Numero pagina (10 px dal bordo del canvas)</label><label><input type="checkbox" checked={w.footerSeparator!==false} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,footerSeparator:e.target.checked}:x))}/> Separatore superiore</label>{w.footerSeparator!==false&&<label>Colore separatore<input type="color" value={w.footerSeparatorColor||'#9ca3af'} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,footerSeparatorColor:e.target.value}:x))}/></label>}
 {w.footerShowSessionTitle===false&&<label>Testo centrale<input maxLength={240} value={w.label||''} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,label:e.target.value}:x))}/></label>}
 <fieldset className="slide-scheme-number-controls" disabled={w.footerShowPageNumber===false}><legend>Posizione numero pagina</legend><p className="muted tiny">Percentuali all'interno del Footer. Senza personalizzazione: 10 px dal bordo inferiore e destro della pagina.</p>
 {([['footerNumberX','Orizzontale (%)'],['footerNumberY','Verticale (%)']] as const).map(([field,label])=><label key={field}>{label}<input type="number" min={0} max={100} step={1} value={w[field]??100} onChange={e=>{const value=Number(e.target.value);if(Number.isFinite(value)&&value>=0&&value<=100)setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,[field]:value}:x))}}/></label>)}
 <button type="button" className="outline small" onClick={()=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,footerNumberX:undefined,footerNumberY:undefined}:x))}>Ripristina numero in basso a destra</button></fieldset></>}
 <label>Colore del testo<input type="color" value={w.style?.color|| (w.kind==='title'?'#000000':'#26364a')} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,color:e.target.value}}:x))}/></label>
  <label>Carattere<select value={w.style?.fontFamily||'Arial'} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,fontFamily:e.target.value}}:x))}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(font=><option key={font}>{font}</option>)}</select></label>
 <div className="slide-scheme-typography"><label><input type="checkbox" checked={w.style?.bold===true} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,bold:e.target.checked}}:x))}/> Grassetto</label><label><input type="checkbox" checked={w.style?.italic===true} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,italic:e.target.checked}}:x))}/> Corsivo</label><label><input type="checkbox" checked={w.style?.underline===true} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,underline:e.target.checked}}:x))}/> Sottolineato</label></div>
<label>Dimensione testo (px)<input type="number" min={8} max={120} value={w.style?.fontSize||(w.kind==='title'?24:14)} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=8&&n<=120)setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,fontSize:n}}:x))}}/></label>
 <button type="button" className="outline small danger-action" onClick={()=>{if(window.confirm('Eliminare il widget dallo schema globale?')){setSchemaWidgets(items=>items.filter(x=>x.id!==w.id));setSchemaInspected('')}}}>Rimuovi dallo schema</button>
 </div>)}
 {!schemaWidgets.some(w=>w.id===schemaInspected)&&<p className="muted tiny">Seleziona un widget e apri Proprietà widget dal menu contestuale, dalla palette o con doppio clic sul widget.</p>}
 </aside></div>
 <p className="muted tiny">Le pagine ereditano i widget globali; Titolo/Footer locali prevalgono sui relativi tipi. Il numero pagina è dinamico e può essere posizionato oppure nascosto.</p>
 </section>}{dashboardPage==='calendar'  &&<section className="panel"><CalendarAgenda date={calendarMonth} setDate={setCalendarMonth} view={calendarView} setView={setCalendarView} entries={globalAppointments} onSelect={(id:string)=>{setSelected(id);setSnap(null);setDashboardPage('session')}}/></section>}{dashboardPage==='open'&&<section className="panel"><h2>Apri sessione</h2><label>Ricerca sessioni<input value={sessionSearch} placeholder="Nome, codice, stato, ruolo" onChange={e=>{setSessionSearch(e.target.value);setSessionPage(1)}}/></label><label>Sessioni per pagina<select value={sessionPageSize} onChange={e=>{setSessionPageSize(Number(e.target.value));setSessionPage(1)}}>{[10,20,50,100].map(n=><option key={n} value={n}>{n}</option>)}</select></label><div className="activity-row"><button className="small outline" disabled={sessionPage===1} onClick={()=>setSessionPage(n=>n-1)}>Precedente</button><span>Pagina {sessionPage}</span><button className="small outline" disabled={sessionTotal<=sessionPage*sessionPageSize} onClick={()=>setSessionPage(n=>n+1)}>Successiva</button></div>{sessions.map(s=><details key={s.id} className="panel" style={{margin:'8px 0',padding:12}}><summary><strong style={{color:(s as any).access_role==='collaborator'?'#37b5a5':'#8064d5'}}>{s.title}</strong> · {(s as any).access_role==='collaborator'?'Collaboratore':'Owner'} · {s.status}</summary><p>Codice: {s.join_code}</p><button className="small primary" onClick={()=>{setSelected(s.id);setSnap(null);setDashboardPage('session')}}>Apri sessione</button> <button type="button" className="small outline" onClick={()=>void duplicateSessionFrom(s.id)} aria-label={`Duplica sessione ${s.title} senza risposte`}>Duplica senza dati {s.status==='closed'?'(terminata)':''}</button></details>)}</section>}{dashboardPage==='new'&&<section className="panel"><h2>Nuova sessione</h2><p className="muted">Crea una sessione e aggiungi le date e gli orari nella sua dashboard.</p><label>Nome della sessione<input maxLength={160} value={newTitle} onChange={e=>setNewTitle(e.target.value)} placeholder="Workshop"/></label><button className="primary" disabled={!newTitle.trim()} onClick={createSession}><Plus size={18}/> Crea sessione</button></section>}{dashboardPage==='sso'&&<FederatedIdentities providers={oidcProviders} onMessage={setNotice}/>}{dashboardPage==='mfa'&&<section className="panel"><h3>Autenticazione a due fattori: email e TOTP</h3><div className="notice"><strong>Email MFA / Secondo fattore email:</strong> {me?.email_mfa_enabled?'Attivo / Enabled':'Disattivo / Disabled'}<p>Email e TOTP sono indipendenti. L'attivazione email richiede SMTP e conferma del codice ricevuto; la disattivazione richiede la password. / Email and TOTP are independent; email setup requires OTP confirmation.</p><label>Password corrente / Current password<input type="password" autoComplete="current-password" value={emailMfaPassword} onChange={e=>setEmailMfaPassword(e.target.value)}/></label><button className="small outline" disabled={!emailMfaPassword} onClick={async()=>{try{const result=await request<any>('/auth/email-mfa/settings','POST',{enabled:!me?.email_mfa_enabled,password:emailMfaPassword});if(result.pending_confirmation){setEmailEnrollmentId(result.challenge_id);setEmailEnrollmentCode('');setNotice('Controlla la tua email e inserisci il codice entro 10 minuti / Check your email for a code valid for 10 minutes')}else{setMe(null);setEmailEnrollmentId('');setEmailMfaPassword('');setNotice('Impostazione aggiornata; accedi di nuovo / Setting updated; sign in again')}}catch(e){notify(e)}}}>{me?.email_mfa_enabled?'Disattiva email MFA / Disable':'Invia codice di attivazione / Send enrollment code'}</button>{emailEnrollmentId&&!me?.email_mfa_enabled&&<div className="panel"><p>Inserisci il codice di verifica ricevuto via email. / Enter the code received by email.</p><label>Codice email / Email code<input inputMode="numeric" autoComplete="one-time-code" maxLength={6} value={emailEnrollmentCode} onChange={e=>setEmailEnrollmentCode(e.target.value.replace(/\D/g,'').slice(0,6))}/></label><button className="small primary" disabled={!/^\d{6}$/.test(emailEnrollmentCode)} onClick={async()=>{try{await request('/auth/email-mfa/enrollment/confirm','POST',{challenge_id:emailEnrollmentId,code:emailEnrollmentCode});setEmailEnrollmentId('');setEmailEnrollmentCode('');setEmailMfaPassword('');setMe(null);setNotice('MFA email attivata: esegui nuovamente l’accesso / Email MFA enabled: sign in again')}catch(e){notify(e)}}}>Conferma e attiva MFA email / Confirm and enable</button></div>}</div><p>Stato: {me?.totp_enabled?'Attivata':'Disattivata'}</p>{!me?.totp_enabled?<><button className="small outline" onClick={async()=>{try{setEnrollment(await request('/auth/mfa/setup','POST'))}catch(e){notify(e)}}}>Configura MFA</button>{enrollment&&<><p>Inserisci questo segreto nella tua app di autenticazione:</p><code style={{overflowWrap:'anywhere'}}>{enrollment.secret}</code><p>URI completo per l'app autenticatore:</p><code style={{overflowWrap:'anywhere'}}>{enrollment.otpauth_url}</code><p>QR da scansionare con l'autenticatore:</p><img alt="QR configurazione TOTP" width={180} height={180} src={'/api/auth/mfa/qr'} /><p>Oppure usa il collegamento otpauth: <a href={enrollment.otpauth_url}>Apri app autenticatore</a></p><label>Codice di conferma<input inputMode="numeric" value={mfaAdminCode} onChange={e=>setMfaAdminCode(e.target.value.slice(0,6))}/></label><button className="small" onClick={async()=>{try{const confirmed=await request('/auth/mfa/confirm','POST',{code:mfaAdminCode});setRecoveryCodes(confirmed.recovery_codes||[]);setMe(await request('/auth/me'));setEnrollment(null);setMfaAdminCode('')}catch(e){notify(e)}}}>Attiva MFA</button></>}</>:<><label>Codice MFA per disattivare<input inputMode="numeric" value={mfaAdminCode} onChange={e=>setMfaAdminCode(e.target.value.slice(0,6))}/></label><label>Password corrente<input type="password" value={password} onChange={e=>setPassword(e.target.value)}/></label><button className="small outline" onClick={async()=>{try{await request('/auth/mfa/disable','POST',{code:mfaAdminCode,password});setMe(await request('/auth/me'));setMfaAdminCode('');setPassword('');setRecoveryCodes([])}catch(e){notify(e)}}}>Disattiva MFA</button></>}{recoveryCodes.length>0&&<div className="notice"><strong>Salva i codici di recupero: vengono mostrati solo ora.</strong><pre style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>{recoveryCodes.join('\n')}</pre><button className="small outline" onClick={()=>{void navigator.clipboard.writeText(recoveryCodes.join('\n'))}}>Copia codici</button><button className="small outline" onClick={()=>setRecoveryCodes([])}>Li ho salvati</button></div>}{me?.totp_enabled&&<button className="small outline" onClick={async()=>{try{const answer=await request('/auth/mfa/recovery-codes/rotate','POST',{password,code:mfaAdminCode});setRecoveryCodes(answer.recovery_codes||[]);setMfaAdminCode('')}catch(e){notify(e)}}}>Rigenera codici di recupero (password e TOTP richiesti)</button>}</section>}{me?.role==='platform_admin'&&dashboardPage==='settings'&&<section className="panel"><h3>SMTP/SMTPS</h3><p>Configurazione SMTP cifrata. Scegli TLS implicito (di norma porta 465) oppure STARTTLS obbligatorio (di norma porta 587): la password è cifrata nel database e non viene mai restituita dal server.</p><label>Server SMTP<input value={smtpForm.host} onChange={e=>setSmtpForm(v=>({...v,host:e.target.value}))}/></label><label>Porta SMTP<input type="number" value={smtpForm.port} onChange={e=>setSmtpForm(v=>({...v,port:Number(e.target.value)}))}/></label><label>Utente SMTP<input value={smtpForm.user} onChange={e=>setSmtpForm(v=>({...v,user:e.target.value}))}/></label><label>Password SMTP (lasciare vuota per conservare quella precedente)<input type="password" autoComplete="new-password" value={smtpForm.password} onChange={e=>setSmtpForm(v=>({...v,password:e.target.value}))}/></label><label>Email mittente (indirizzo email valido)<input type="email" value={smtpForm.from} onChange={e=>setSmtpForm(v=>({...v,from:e.target.value}))}/></label><label>Trasporto<select value={smtpForm.secure?'tls':'starttls'} onChange={e=>setSmtpForm(v=>({...v,secure:e.target.value==='tls',port:e.target.value==='tls'?465:587}))}><option value="tls">SMTPS - TLS implicito</option><option value="starttls">SMTP - STARTTLS obbligatorio</option></select></label><label>Nome del mittente<input maxLength={120} value={smtpForm.senderName} onChange={e=>setSmtpForm(v=>({...v,senderName:e.target.value}))}/></label><button className="small primary" onClick={async()=>{try{const r=await request('/admin/smtp','PUT',{...smtpForm});setSmtpStatus(r);setSmtpForm(v=>({...v,password:''}));setNotice('Configurazione SMTPS salvata')}catch(e){notify(e)}}}>Salva configurazione SMTP</button><button className="small outline" onClick={async()=>{try{const c=await request('/admin/smtp');setSmtpStatus(c);setNotice(c.configured?'Configurazione SMTP verificata: '+c.transport:'SMTP non configurato');setSmtpForm(v=>({...v,host:c.host||'',port:Number(c.port||465),user:c.user||'',from:c.from||'',senderName:c.senderName||'',secure:c.transport!=='starttls',password:''}))}catch(e){notify(e)}}}>Verifica configurazione</button>{smtpStatus&&<p>{smtpStatus.configured?`SMTPS: ${smtpStatus.host}:${smtpStatus.port} — ${smtpStatus.from}`:smtpStatus.error||'Non configurato'}</p>}<label>Destinatario email di prova<input type="email" value={smtpRecipient} onChange={e=>setSmtpRecipient(e.target.value)}/></label><button className="small" onClick={async()=>{try{await request('/admin/smtp/test','POST',{recipient:smtpRecipient});setNotice('Email di test inviata')}catch(e){notify(e)}}}>Invia email di prova</button></section>}{me?.role==='platform_admin'&&dashboardPage==='users'&&<section className="panel"><h3>Gestione utenti</h3><label>Nuovo utente (email)<input type="email" value={newUserEmail} onChange={e=>setNewUserEmail(e.target.value)}/></label><label>Nickname facoltativo<input maxLength={32} value={newUserNickname} onChange={e=>setNewUserNickname(e.target.value)}/></label><label>Password temporanea (almeno 12 caratteri)<input type="password" value={newUserTemporaryPassword} onChange={e=>setNewUserTemporaryPassword(e.target.value)}/></label><button className="small" disabled={!newUserEmail||newUserTemporaryPassword.length<12} onClick={async()=>{try{await request('/admin/users','POST',{email:newUserEmail,temporary_password:newUserTemporaryPassword,nickname:newUserNickname||null,role:'user'});setNewUserEmail('');setNewUserNickname('');setNewUserTemporaryPassword('');setAdminUsers((await request<{items:any[]}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`)).items)}catch(e){notify(e)}}}>Crea utente</button><button className="outline small" onClick={async()=>{try{setAdminUsers((await request<{items:any[]}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`)).items);const cfg=await request('/admin/settings');setAdminUrl(cfg.public_base_url||'');setAdminRetention(Number(cfg.closed_session_retention_days||60))}catch(e){notify(e)}}}>Carica utenti e impostazioni</button><div className="activity-row"><label>Ricerca email, nickname o stato<input placeholder="Email, nickname, approvato, non approvato" value={userSearch} onChange={e=>{setUserSearch(e.target.value);setUserPage(1)}}/></label><label>Utenti per pagina<select value={userPageSize} onChange={e=>{setUserPageSize(Number(e.target.value));setUserPage(1)}}>{[10,20,50,100].map(n=><option key={n} value={n}>{n}</option>)}</select></label></div><div className="activity-row"><button className="small outline" disabled={userPage<=1} onClick={()=>setUserPage(x=>x-1)}>← Precedente</button><span>Pagina {userPage}</span><button className="small outline" disabled={userTotal<=userPage*userPageSize} onClick={()=>setUserPage(x=>x+1)}>Successiva →</button></div>{adminUsers.map((u:any)=><details key={u.id} className="panel" style={{margin:'8px 0',padding:12}}><summary style={{cursor:'pointer'}}><strong>{u.nickname||u.email}</strong> · {u.email} · <span style={{color:u.approved?'#29b96f':'#e35353'}}>{u.approved?'Approvato':'Non approvato'}</span></summary><div className="activity-row"><span>MFA TOTP: <strong>{u.totp_enabled?'Attiva':'Disattiva'}</strong></span><button type="button" className="outline small" disabled={!u.totp_enabled||!!u.is_primary_admin||u.id===me?.id} onClick={async()=>{if(!window.confirm('Ripristinare la MFA di questo utente? I codici di recupero esistenti saranno revocati.'))return;const admin_password=window.prompt('Conferma la tua password amministratore');if(!admin_password)return;const admin_totp_code=window.prompt('Codice TOTP amministratore (se attivato)')||'';try{await request(`/admin/users/${u.id}/mfa/reset`,'POST',{admin_password,admin_totp_code,confirm:true});setAdminUsers(old=>old.map(x=>x.id===u.id?{...x,totp_enabled:false}:x));setNotice('MFA azzerata. L’utente dovrà configurarla nuovamente.')}catch(e){notify(e)}}}>Azzera MFA utente</button></div><label>Nickname<input value={u.nickname||''} disabled={!!u.is_primary_admin} onChange={e=>setAdminUsers(old=>old.map(x=>x.id===u.id?{...x,nickname:e.target.value}:x))}/></label>{u.is_primary_admin&&<button className="outline small" onClick={async()=>{const next=window.prompt('Nuova email admin principale',u.email);if(!next||next===u.email)return;try{await request(`/admin/users/${u.id}/identity`,'PATCH',{email:next});setAdminUsers((await request<{items:any[]}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`)).items)}catch(e){notify(e)}}}>Cambia email principale</button>}<select disabled={!!u.is_primary_admin} value={u.role} onChange={e=>setAdminUsers(old=>old.map(x=>x.id===u.id?{...x,role:e.target.value}:x))}><option value="user">user</option><option value="presenter">presenter</option><option value="moderator">moderator</option><option value="org_admin">org_admin</option><option value="platform_admin">platform_admin</option></select><button type="button" className="small" disabled={!!u.is_primary_admin} aria-label={`Stato approvazione di ${u.email}: ${u.approved?'approvato':'non approvato'}`} style={{background:u.approved?'#166534':'#991b1b',color:'#fff',borderRadius:9,padding:'8px 14px'}} onClick={()=>setAdminUsers(old=>old.map(x=>x.id===u.id?{...x,approved:!x.approved}:x))}>{u.approved?'Approvato · clicca per revocare':'Non approvato · clicca per approvare'}</button><button className="small" disabled={!!u.is_primary_admin||!!adminSavingId} onClick={async()=>{if(adminSavingId)return;setAdminSavingId(u.id);try{await request(`/admin/users/${u.id}`,'PATCH',{nickname:u.nickname||null,role:u.role,approved:u.approved});setAdminUsers((await request<{items:any[]}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`)).items);setNotice('Utente salvato')}catch(e){notify(e)}finally{setAdminSavingId('')}}}>{adminSavingId===u.id?'Salvataggio…':'Salva utente'}</button><button className="small outline" disabled={!!u.is_primary_admin} onClick={async()=>{if(!window.confirm('Eliminare l’account?'))return;try{const r=await fetch(`/api/admin/users/${u.id}`,{method:'DELETE',credentials:'include'});if(!r.ok)throw Error(`HTTP ${r.status}`);setAdminUsers((await request<{items:any[]}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`)).items)}catch(e){notify(e)}}}>Elimina</button></details>)}</section>}{me?.role==='platform_admin'&&dashboardPage==='settings'&&<section className="panel"><h3>Configurazione server</h3><label>URL esterna HTTPS<input value={adminUrl} onChange={e=>setAdminUrl(e.target.value)}/></label><label>Giorni conservazione sessioni chiuse<input type="number" min="1" max="3650" value={adminRetention} onChange={e=>setAdminRetention(Number(e.target.value))}/></label><label>Limite upload (MB, 1–1024)<input type="number" min="1" max="1024" value={adminUploadMb} onChange={e=>setAdminUploadMb(Number(e.target.value))}/></label><p className="muted tiny">Dopo una modifica del limite rigenera e applica i manifest Ingress Kubernetes.</p><button className="small" onClick={async()=>{try{await request('/admin/settings','PATCH',{public_base_url:adminUrl,closed_session_retention_days:adminRetention,max_upload_mb:adminUploadMb})}catch(e){notify(e)}}}>Salva impostazioni</button></section>}{dashboardPage==='profile'&&<section className="panel"><h3>Profilo utente e presentatore</h3><p>Account: {me?.email} · nickname: {me?.nickname||'non impostato'}</p><label>Nickname (univoco)<input maxLength={32} placeholder="nickname" value={nickname} onChange={e=>setNickname(e.target.value)}/></label><p className="muted tiny">Nome e foto visibili nei widget profilo delle sessioni.</p><label>Nome visualizzato<input maxLength={100} value={profileName} onChange={e=>setProfileName(e.target.value)}/></label><section className="gravatar-profile-settings" aria-label="Gravatar del tuo account"><label><input type="checkbox" aria-label="Usa Gravatar per la foto profilo" checked={!!myProfile?.gravatar_enabled} disabled={photoBusy||profileSaving} onChange={async e=>{const enabled=e.target.checked;setPhotoBusy(true);try{const data=await request<any>('/auth/profile/gravatar','PUT',{enabled});setMyProfile((old:any)=>({...old,...data}));setProfilePhoto(data.profile_photo_url||'');setPhotoVersion(v=>v+1);setNotice(enabled?(data.sync==='unavailable'?'Gravatar attivato; riprova la sincronizzazione più tardi':data.sync==='missing'?'Gravatar attivato: nessuna foto trovata per la tua email':'Foto Gravatar sincronizzata'):'Sincronizzazione Gravatar disattivata')}catch(error){notify(error)}finally{setPhotoBusy(false)}}}/>Usa Gravatar per la foto del mio account</label><p className="muted tiny">È una scelta facoltativa. La foto viene importata nel server Quorivio usando la tua email registrata e verificata a ogni accesso; non viene caricata direttamente da Gravatar nei browser dei partecipanti.</p><div className="downloads"><a className="outline asbutton small" target="_blank" rel="noopener noreferrer" href="https://gravatar.com/">Aggiungi o modifica una foto su Gravatar</a>{myProfile?.gravatar_enabled&&<button type="button" className="outline small" disabled={photoBusy||profileSaving} onClick={async()=>{setPhotoBusy(true);try{const data=await request<any>('/auth/profile/gravatar','PUT',{enabled:true});setMyProfile((old:any)=>({...old,...data}));setProfilePhoto(data.profile_photo_url||'');setPhotoVersion(v=>v+1);setNotice(data.sync==='imported'?'Foto Gravatar importata':data.sync==='unchanged'?'Gravatar già aggiornato':data.sync==='missing'?'Nessun Gravatar associato alla email':'Servizio Gravatar momentaneamente non disponibile')}catch(error){notify(error)}finally{setPhotoBusy(false)}}}>Importa / aggiorna Gravatar</button>}</div></section><label>Foto del profilo (PNG, JPEG o WebP, massimo 5 MB, lato massimo 4096 px)<input type="file" accept="image/png,image/jpeg,image/webp" disabled={photoBusy||profileSaving} aria-label="Carica foto del profilo" onChange={async e=>{const file=e.target.files?.[0];e.target.value='';if(!file||photoBusy||profileSaving)return;setPhotoBusy(true);try{if(!['image/png','image/jpeg','image/webp'].includes(file.type)||file.size===0||file.size>5*1024*1024)throw Error('Immagine non valida o troppo grande');const response=await fetch('/api/auth/profile/photo',{method:'POST',credentials:'include',headers:{'Content-Type':file.type},body:file});const result=await response.json();if(!response.ok)throw Error(result.error||'Caricamento fallito');setProfilePhoto(result.profile_photo_url);setMyProfile((old:any)=>({...old,profile_photo_url:result.profile_photo_url}));setPhotoVersion(v=>v+1);setNotice('Foto aggiornata')}catch(err){notify(err)}finally{setPhotoBusy(false)}}}/></label><button type="button" className="outline small" disabled={photoBusy||profileSaving||!myProfile?.profile_photo_url} onClick={async()=>{if(photoBusy||profileSaving)return;setPhotoBusy(true);try{await request('/auth/profile/photo','DELETE');setProfilePhoto('');setMyProfile((old:any)=>({...old,profile_photo_url:null}));setPhotoVersion(v=>v+1);setNotice('Foto rimossa')}catch(err){notify(err)}finally{setPhotoBusy(false)}}}>Elimina foto</button><div className="downloads"><button className="outline small" disabled={!myProfile||photoBusy||profileSaving||profileName.trim().length<2||profileName.trim().length>100} onClick={async()=>{if(profileSaving||photoBusy)return;setProfileSaving(true);try{const p=await request<any>('/auth/profile','PATCH',{nickname:nickname||null,display_name:profileName});setMyProfile((old:any)=>({...old,...p}));setMe(await request('/auth/me'));setNotice('Profilo salvato')}catch(e){notify(e)}finally{setProfileSaving(false)}}}>{profileSaving?'Salvataggio in corso…':'Salva profilo'}</button></div>{photoBusy&&<p role="status" aria-live="polite">Aggiornamento foto in corso…</p>}{myProfile?.profile_photo_url&&<img src={`${myProfile.profile_photo_url}?v=${photoVersion}`} alt="Foto profilo" style={{maxHeight:72,maxWidth:72,objectFit:'cover',borderRadius:'50%'}}/>}</section>}{dashboardPage!=='session'?(['new','open','calendar'].includes(dashboardPage)?null:<div className="welcome"><h1>{dashboardPage==='users'?'Gestione utenti':dashboardPage==='settings'?'Impostazioni server':dashboardPage==='mfa'?'Autenticazione a due fattori':dashboardPage==='sso'?'Identità federate':'Profilo presentatore'}</h1><p>Gestisci questa funzionalità dal pannello dedicato a sinistra.</p></div>):!snap?<div className="welcome"><div className="orb"><BarChart3 size={55}/></div><h1>Le idee prendono vita.</h1><p>Seleziona una sessione o creane una nuova.</p></div>:<><div className="workspace-head"><div><div className="eyebrow">PRESENTER CONTROL ROOM</div><h1>{snap.session.title}</h1><div className="subline"><span className="pill">{snap.session.status}</span><span>Codice: <strong>{snap.session.join_code}</strong></span></div></div><div className="actions">{snap.session.status==='active'&&!snap.session.current_activity_id&&<span role="status" className="muted tiny">Sessione avviata: pubblica una pagina da «Pagine e contenuti» per mostrarla sullo schermo.</span>}{snap.session.status==='paused'&&<span role="status" className="muted tiny">Sessione in pausa: i partecipanti non possono inviare nuove risposte.</span>}{snap.session.status!=='closed'&&snap.session.status!=='active'&&<button className="primary" onClick={()=>changeStatus('active')}><Play size={16}/> Avvia</button>}{snap.session.status==='active'&&<button className="outline" onClick={()=>changeStatus('paused')}>Pausa</button>}{snap.session.status==='paused'&&<button className="primary" onClick={()=>changeStatus('active')}>Riprendi</button>}{snap.session.status==='active'&&snap.activities.find(a=>a.id===snap.session.current_activity_id)?.page_design?.widgets?.some((w:any)=>w.kind==='timer')&&<button type="button" className="primary" title="Riavvia manualmente il timer della pagina e cancella i risultati precedenti" onClick={()=>{const a=snap.activities.find(a=>a.id===snap.session.current_activity_id);if(a)void restartPageTimer(a)}}><Timer size={19}/> Riavvia countdown</button>}{(snap.session.status==='active'||snap.session.status==='paused')&&<button type="button" className="outline" title="Ritorna a non avviata: elimina partecipanti, voti e risultati, conserva pagine e configurazioni" onClick={()=>void resetSessionToReady()}>↺ Riporta a non avviata</button>}{(snap.session.status==='active'||snap.session.status==='paused')&&<button className="outline" onClick={()=>changeStatus('closed')}><Square size={16}/> Termina</button>}</div></div>{presenterLive==='disconnected'&&<div className="live-stale-warning" role="status">{liveFallback?'WebSocket in riconnessione; dati della dashboard aggiornati tramite HTTP.':'Connessione live interrotta: riconnessione in corso.'}</div>}<div className="rehearsal-launch">{(snap.session.status==='active'||snap.session.status==='paused')?<div className="session-live-access" aria-label="Accesso alla sessione live"><div className="session-live-qr"><img src={`/api/sessions/${selected}/qr?format=svg`} alt="QR per il pubblico"/><div><strong>Partecipanti</strong><a href={snap.session.join_url||`/join/${snap.session.join_code}`} target="_blank" rel="noreferrer">Apri URL partecipanti</a><small>Codice: {snap.session.join_code}</small></div></div><div className="session-live-presenter"><img className="session-presenter-qr" src={`/api/sessions/${selected}/presenter-qr`} alt="QR presentatore (richiede autenticazione)"/><strong>Presentatore</strong><a href={`/screen/${selected}`} target="_blank" rel="noopener noreferrer" title="Apri lo schermo presentatore live"><Presentation size={22}/> Apri schermo presentatore</a><a href={`${location.origin}/screen/${selected}`} target="_blank" rel="noopener noreferrer" title="Collegamento diretto autenticato del presentatore">URL presentatore</a></div></div>:null}<div className="rehearsal-launch-actions" role="group" aria-label={snap.session.status==='active'||snap.session.status==='paused'?'Accessi reali alla sessione':'Anteprime della sessione'}>{!(snap.session.status==='active'||snap.session.status==='paused')&&(['presenter','participant','mobile','both'] as RehearsalMode[]).map(m=><button type="button" key={m} className="primary" title={m==='presenter'?'Apri anteprima presentatore':m==='participant'?'Apri anteprima partecipante':m==='mobile'?'Apri anteprima smartphone':'Apri anteprime affiancate'} onClick={()=>{setRehearsalMode(m);setRehearsalOpen(true)}}>{m==='presenter'?<><Presentation size={22}/> Anteprima presentatore</>:m==='participant'?<><Users size={22}/> Anteprima partecipante</>:m==='mobile'?<><Users size={22}/> Anteprima smartphone</>:<><Square size={22}/> Anteprime affiancate</>}</button>)}</div>{!(snap.session.status==='active'||snap.session.status==='paused')&&<small>Le risposte della prova non incidono sulle statistiche.</small>}</div>{rehearsalOpen&&!designActivity&&<RehearsalErrorBoundary onClose={()=>setRehearsalOpen(false)}><SessionRehearsal initialMode={rehearsalMode} snapshot={snap} onClose={()=>setRehearsalOpen(false)}/></RehearsalErrorBoundary>}<button className="primary" onClick={()=>{setSessionTab('pages');if(snap.activities.length)beginPageDesign(snap.activities.find(a=>a.id===designActivity)||snap.activities[0]);else void createCanvasPage()}}>✎ Modifica le pagine</button><nav className="session-tabs" aria-label="Sezioni della sessione">{([['overview','Impostazioni e monitoraggio'],['pages','Pagine e contenuti']] as const).map(([id,label])=><button key={id} className={sessionTab===id?'primary':'outline'} aria-pressed={sessionTab===id} onClick={()=>setSessionTab(id)}>{label}</button>)}</nav><div className={`session-detail-layout session-tab-${sessionTab}`}><div><section className="panel"><h3>Metadati della sessione</h3><label>Nome<input placeholder={snap.session.title} value={sessionTitleEdit} onChange={e=>setSessionTitleEdit(e.target.value)}/></label><button className="outline small" disabled={snap.session.status==='closed'} onClick={updateSessionMetadata}>Salva nome</button><h4>Date della sessione</h4><p className="muted tiny">Ogni data comprende ora di inizio, durata e fuso orario IANA. Le modifiche vengono applicate dopo «Salva date della sessione».</p><div className="activity-row"><label>Data<input type="date" value={appointmentDate} onChange={e=>setAppointmentDate(e.target.value)}/></label><label>Ora di inizio<input type="time" value={appointmentTime} onChange={e=>setAppointmentTime(e.target.value)}/></label><label>Durata (min)<input type="number" min={5} max={1440} value={appointmentMinutes} onChange={e=>setAppointmentMinutes(Number(e.target.value))}/></label><label>Fuso orario IANA<input aria-label="Fuso orario della data" list="session-time-zones" value={appointmentZone} onChange={e=>setAppointmentZone(e.target.value)} placeholder="Europe/Rome"/><datalist id="session-time-zones"><option value="Europe/Rome"/><option value="Europe/Paris"/><option value="Europe/London"/><option value="UTC"/><option value="America/New_York"/><option value="Asia/Tokyo"/></datalist></label><button className="outline small" disabled={!appointmentDate||!/^([01]\d|2[0-3]):[0-5]\d$/.test(appointmentTime)||!Number.isInteger(appointmentMinutes)||appointmentMinutes<5||appointmentMinutes>1440||!appointmentZone||(()=>{try{new Intl.DateTimeFormat('en',{timeZone:appointmentZone});return false}catch{return true}})()} onClick={()=>setAppointments(a=>a.some(x=>x.date===appointmentDate&&x.start_time===appointmentTime&&x.time_zone===appointmentZone)?a:[...a,{date:appointmentDate,start_time:appointmentTime,duration_minutes:appointmentMinutes,time_zone:appointmentZone}].sort((x,y)=>`${x.date}T${x.start_time}`.localeCompare(`${y.date}T${y.start_time}`)))}>Aggiungi data</button></div>{appointments.length===0&&<p className="muted tiny">Non sono ancora state inserite date con orario.</p>}{appointments.map((a,i)=><div className="activity-row" key={`${a.date}-${a.start_time}-${a.time_zone}-${i}`}><span>{a.date} · {a.start_time} · {a.duration_minutes} min · {a.time_zone}</span><button className="outline small" aria-label={`Rimuovi data ${a.date} ${a.start_time}`} onClick={()=>setAppointments(v=>v.filter((_,n)=>n!==i))}>Rimuovi</button></div>)}<button className="primary small" onClick={async()=>{try{await request(`/sessions/${selected}/appointments`,'PUT',{appointments});setAppointments(await request(`/sessions/${selected}/appointments`));setNotice('Date della sessione salvate')}catch(e){notify(e)}}}>Salva date della sessione</button>{scheduleDates.length>0&&<details><summary>Importa date dal calendario precedente ({scheduleDates.length})</summary><p className="muted tiny">Le date precedenti non contengono l'ora. Imposta l'ora, la durata e il fuso qui sopra, poi importa e salva. Il vecchio calendario non viene eliminato automaticamente.</p><button className="outline small" onClick={()=>{setAppointments(v=>[...v,...scheduleDates.filter(d=>!v.some(x=>x.date===d&&x.start_time===appointmentTime&&x.time_zone===appointmentZone)).map(d=>({date:d,start_time:appointmentTime,duration_minutes:appointmentMinutes,time_zone:appointmentZone}))].sort((a,b)=>`${a.date}T${a.start_time}`.localeCompare(`${b.date}T${b.start_time}`)));setNotice('Date precedenti importate nella bozza: salva per confermare')}} disabled={!appointmentZone||!Number.isInteger(appointmentMinutes)||appointmentMinutes<5||appointmentMinutes>1440}>Importa date precedenti</button></details>}</section><section className="panel invitation-panel"><h3><Radio size={19}/> Invito alla sessione</h3><p>Inserisci questo QR code in qualsiasi PowerPoint o PDF.</p><div className="qr-layout"><img className="qr" src={`/api/sessions/${selected}/qr?format=svg`} alt="QR code della sessione"/><div><p className="muted">Codice sessione</p><div className="join-code">{snap.session.join_code}</div><a href={snap.session.join_url} target="_blank" rel="noreferrer">Link partecipanti <ExternalLink size={14}/></a><div className="downloads"><a href={`/api/sessions/${selected}/qr?format=png`}><Download size={15}/> PNG</a><a href={`/api/sessions/${selected}/qr?format=svg`}><Download size={15}/> SVG</a></div></div></div></section><section className="panel"><h3><Plus size={19}/> Crea contenuti con i widget</h3><p className="muted">Apri l’editor grafico per creare o duplicare pagine, scegliere lo sfondo, aggiungere widget e configurare domande, sondaggi e quiz. La pagina si apre direttamente nell’editor, dove puoi modificarla subito.</p><p className="muted tiny">Seleziona una miniatura nell’editor. Usa il clic destro (pressione prolungata su mobile) per le azioni contestuali.</p><button type="button" className="primary" onClick={()=>{setSessionTab('pages');if(!designActivity&&snap.activities.length)beginPageDesign(snap.activities[0]);else if(!snap.activities.length)void createCanvasPage()}}>✎ Modifica le pagine</button></section></div><div><details className="panel live-stats-tools" aria-label="Statistiche delle interazioni live">
 <summary>Statistiche live e monitoraggio</summary>
 <div className="title-row"><h3><BarChart3 size={19}/> Statistiche dei widget</h3>
  <button type="button" className="small outline" onClick={loadReactions}>Reazioni ricevute</button>
  <button type="button" className="small outline" onClick={loadRatingStats}>Risultati valutazioni</button>
  <a href={`/screen/${selected}`} target="_blank" rel="noreferrer">Schermo pubblico <ExternalLink size={14}/></a>
 </div>
 {ratingStats?.by_widget&&<p>Per widget: {ratingStats.by_widget.map((w:any)=>`${w.target_kind} / ${w.widget_id}: ${w.mean??'—'} (${w.responses})`).join(' · ')}</p>}
 {ratingStats&&<p>Gradimento medio: {ratingStats.overall?.mean??'—'} / 9 · {ratingStats.overall?.responses||0} valutazioni</p>}
 {reactions&&<section className="panel"><h4>Reazioni per sessione</h4><p>{Object.entries(reactions.by_session||{}).map(([e,c])=>`${e}: ${c}`).join(' · ')}</p>
 <h4>Per pagina</h4>{(reactions.by_page||[]).map((v:any,i:number)=><p key={i}>{v.title}: {v.emoji} {v.count}</p>)}
 <h4>Per partecipante</h4>{(reactions.by_user||[]).map((v:any,i:number)=><p key={i}>{v.pseudonym||v.id}: {v.count}</p>)}</section>}
 </details>{designActivity&&<section className="panel powerpoint-editor editor-ux-v2" id="quorivio-slide-editor" aria-label="Editor grafico delle pagine" onPointerDown={e=>{if(e.pointerType==='mouse')return;const button=(e.target as HTMLElement).closest('button');if(button&&!button.classList.contains('editor-icon-tool'))setEditorTouchHint(button.title||button.getAttribute('aria-label')||button.textContent?.trim()||'')}}>
<header className="editor-mock-header"><div className="editor-mock-brand"><img src="/editor-quorivio-logo.svg" alt="Quorivio"/><span>{snap.session.title}</span><div className="editor-presenter-identities" aria-label="Proprietario e collaboratori della sessione"><span className="editor-owner-chip" title="Proprietario primario">Owner: {availablePresenters.find(p=>p.is_owner)?.name||'Proprietario'}</span>{availablePresenters.filter(p=>!p.is_owner).map(p=><span key={p.id} className="editor-collaborator-chip" title="Collaboratore della sessione">{p.name}</span>)}</div></div><div className="editor-mock-actions"><span role="status" aria-live="polite" className={'editor-autosave-indicator'+((pageSaveError||pageConflict)?' has-error':'')}>{pageConflict?'Conflitto di revisione':pageSaveError?'Errore salvataggio: '+pageSaveError:pageSavePending?'Salvataggio automatico…':pageHasUnsavedChanges?'Modifiche in attesa…':'Salvato automaticamente'}</span><button type="button" className="editor-preview-open editor-schemes-open" title="Apri l'editor degli schemi (titoli e footer)" onClick={()=>{if(confirmPageNavigation()){setRehearsalOpen(false);setInspectedWidget('');openSchemaEditor()}}}>▤ Schemi</button>{(['presenter','participant','mobile','both'] as RehearsalMode[]).map(m=><button key={m} type="button" className={'editor-preview-open preview-'+m} aria-haspopup="dialog" aria-expanded={rehearsalOpen&&rehearsalMode===m} onClick={()=>{setRehearsalMode(m);setRehearsalOpen(true)}}>{m==='presenter'?'▶ Presentatore':m==='participant'?'▶ Partecipante':m==='mobile'?'▯ Smartphone':'▣ Affiancate'}</button>)}<button type="button" className="editor-exit" onClick={()=>void exitPageEditor()}>Esci</button></div></header>
{rehearsalOpen&&<RehearsalErrorBoundary onClose={()=>setRehearsalOpen(false)}><SessionRehearsal initialMode={rehearsalMode} initialPageId={designActivity} snapshot={{...snap,activities:snap.activities.map(a=>a.id===designActivity?{...a,page_design:{...((a as any).page_design||{}),widgets:pageWidgets,mobile:mobileLayoutDraft,backgroundColor:questionBackgroundColor,backgroundUrl:questionBackground,backgroundAssetId:questionBackgroundAsset,header:questionHeader}}:a)}} onClose={()=>setRehearsalOpen(false)}/></RehearsalErrorBoundary>}
<aside className="page-editor-sidebar" aria-label="Miniature delle pagine">
  <header><strong>Pagine</strong><button type="button" className="outline small" title="Apri editor schemi: Titolo, footer e stili della sessione" onClick={()=>{if(confirmPageNavigation()){setInspectedWidget('');openSchemaEditor()}}}>Modifica schemi</button><span aria-label={`Totale ${snap.activities.length} pagine`}>{snap.activities.length}</span></header>
  <p className="page-editor-order-status" role="status" aria-live="polite">{pageOrderAnnouncement}</p>
  <div className="page-editor-thumbnails" aria-busy={pageOrderPending}>
   {snap.activities.map((a,i)=><div className={'page-editor-thumb-row'+(designActivity===a.id?' is-active':'')} key={a.id}
      draggable={snap.session.status!=='closed'&&!pageOrderPending}
      onDragStart={e=>{e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('application/x-quorivio-page',a.id)}}
      onDragOver={e=>{if(e.dataTransfer.types.includes('application/x-quorivio-page'))e.preventDefault()}}
      onDrop={e=>{e.preventDefault();const dragged=e.dataTransfer.getData('application/x-quorivio-page');if(dragged)void dropPage(dragged,a.id)}}
      onContextMenu={e=>{e.preventDefault();setPageExportError('');setPageThumbMenu(a.id)}}>
     <button type="button" className="page-editor-thumb" aria-current={designActivity===a.id?'page':undefined}
       aria-label={`Mostra pagina ${i+1}: ${a.title}; Alt+Freccia su/giù per riordinare`} 
       aria-keyshortcuts="Alt+ArrowUp Alt+ArrowDown"
       onClick={()=>beginPageDesign(a)} onKeyDown={e=>{if(!['ArrowUp','ArrowDown','Home','End'].includes(e.key))return;e.preventDefault();const pages=snap.activities;const to=e.key==='Home'?0:e.key==='End'?pages.length-1:Math.max(0,Math.min(pages.length-1,i+(e.key==='ArrowDown'?1:-1)));if(e.altKey){if((e.key==='ArrowUp'||e.key==='ArrowDown')&&to!==i)void dropPage(a.id,pages[to].id);return}if(pages[to]){beginPageDesign(pages[to]);requestAnimationFrame(()=>document.querySelectorAll<HTMLButtonElement>('.page-editor-thumb')[to]?.focus())}}}>
       <span className="page-editor-thumb-number" aria-hidden="true">{String(i+1).padStart(2,'0')}</span>
       <span className="page-editor-preview" aria-hidden="true" style={{backgroundImage:(a as any).page_design?.backgroundAssetId?`url(${assets.find(x=>x.id===(a as any).page_design.backgroundAssetId)?.url||''})`:(a as any).page_design?.backgroundUrl?`url(${(a as any).page_design.backgroundUrl})`:undefined,backgroundSize:'cover',backgroundPosition:'center'}}><span className="page-editor-preview-title">{(a as any).page_design?.header||a.title}</span>{((a as any).page_design?.widgets||[]).slice(0,24).map((w:any,i:number)=>{const p=w.position||{x:(i%2)*50,y:Math.floor(i/2)*14,width:48,height:24};return <span key={w.id||i} className="page-editor-preview-widget" style={{left:`${Math.max(0,Math.min(100,Number(p.x)||0))}%`,top:`${Math.max(0,Math.min(100,Number(p.y)||0))}%`,width:`${Math.max(1,Math.min(100,Number(p.width)||20))}%`,height:`${Math.max(1,Math.min(100,Number(p.height)||15))}%`,transform:`rotate(${Number(p.rotation)||0}deg)`,backgroundColor:w.style?.fillNone?'transparent':w.style?.fillColor||'#e7e8f4',...widgetAppearanceStyle(w.style)}} title={w.label||w.kind}>{w.kind!=='shape'&&<WidgetShapeOutline style={w.style}/>}{w.label||w.kind}</span>})}</span>
     </button>
     <span className="page-editor-thumbnail-caption" aria-label={`Numero pagina ${i+1}`}>{i+1}</span>
     <button type="button" className="page-editor-thumb-menu-trigger"  aria-label={`Menu pagina ${i+1}: crea, duplica, elimina, sposta`}
       aria-expanded={pageThumbMenu===a.id} onClick={()=>{setPageExportError('');setPageThumbMenu(v=>v===a.id?'':a.id)}}><MoreVertical size={19}/></button>
     {pageThumbMenu===a.id&&<div className="page-editor-thumb-menu" role="group" aria-label={`Azioni pagina ${i+1}`} onKeyDown={e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();setPageThumbMenu('');const trigger=e.currentTarget.previousElementSibling as HTMLButtonElement|null;requestAnimationFrame(()=>trigger?.focus())}}}>
       <button type="button" title="Mostra questa pagina nell'editor" onClick={()=>{beginPageDesign(a);setPageThumbMenu('')}}>Apri pagina</button>
       {snap.session.status!=='closed'&&<button type="button" title="Rinomina questa pagina senza modificare i widget o le risposte" onClick={()=>{setPageThumbMenu('');void renameCanvasPage(a)}}>Rinomina pagina</button>}
       {snap.session.status!=='closed'&&<>
       <button type="button" title="Inserisce una pagina prima di questa" onClick={()=>{setPageThumbMenu('');void createCanvasPageAt(a.id,'before')}}>Nuova pagina prima</button>
       <button type="button" title="Inserisce una pagina dopo questa" onClick={()=>{setPageThumbMenu('');void createCanvasPageAt(a.id,'after')}}>Nuova pagina dopo</button>
       <button type="button" title="Duplica questa pagina subito dopo" onClick={()=>{setPageThumbMenu('');void duplicatePage(a.id)}}>Duplica pagina</button>
       <button type="button" title="Sposta la pagina prima della precedente" disabled={pageOrderPending||i===0} onClick={()=>{setPageThumbMenu('');void movePage(i,i-1)}}>Sposta su</button>
       <button type="button" title="Sposta la pagina dopo la successiva" disabled={pageOrderPending||i===snap.activities.length-1} onClick={()=>{setPageThumbMenu('');void movePage(i,i+1)}}>Sposta giù</button>
        <button type="button" title="Esporta layout di questa pagina in JSON" onClick={()=>{try{downloadPageDraftFor(a);setPageExportError('');setPageThumbMenu('')}catch(e){setPageExportError('Esportazione non riuscita: '+(e instanceof Error?e.message:String(e)))}}}>Esporta layout JSON</button>{pageExportError&&<p className="page-editor-export-error" role="alert">{pageExportError}</p>}
        <label className="editor-thumb-import">Importa layout JSON<input type="file" accept=".json,application/json" onChange={e=>{const f=e.target.files?.[0];e.target.value='';setPageThumbMenu('');openImportDraftFor(a,f)}}/></label>
       <button type="button" className="editor-delete-action" title="Elimina definitivamente questa pagina" onClick={()=>{setPageThumbMenu('');void deleteCanvasPage(a)}}>Elimina pagina</button>
       </>}
     </div>}
    </div>)}
  </div>
  {!snap.activities.length&&<EditorIconTool label="Crea la prima pagina" onClick={()=>void createCanvasPage()}><Plus size={22}/></EditorIconTool>}
</aside>
<div className="editor-stage" data-editor-device={canvasDevice}>
 <div className="editor-device-switch" role="group" aria-label="Layout da modificare"><button type="button" aria-pressed={canvasDevice==='desktop'} onClick={()=>setCanvasDevice('desktop')}>Desktop 16:9</button><button type="button" aria-pressed={canvasDevice==='phone'} onClick={()=>setCanvasDevice('phone')}>Smartphone 390px</button><small>{canvasDevice==='phone'?'Posizioni e sfondo indipendenti dal desktop; la pagina può scorrere verticalmente.':'Layout proiettore e desktop.'}</small></div>
 <div className="editor-canvas-slot">
  <WidgetCanvas key={`${selected}:${designActivity}:${canvasDevice}`} widgets={canvasDevice==='phone'?mobilePageWidgets(pageWidgets,mobileLayoutDraft):pageWidgets} mobileMode={canvasDevice==='phone'} mobileHeight={mobileStageHeight(pageWidgets)} mobileBackgroundColor={mobileLayoutDraft.backgroundColor} pageTitle={snap.activities.find(a=>a.id===designActivity)?.title||""} sessionTitle={snap.session.title} pageNumber={slidePageNumber(snap.activities,designActivity)} masterTitleStyle={snap.session.theme?.master?.titleStyle} onChange={changeCanvasWidgets} onAutoFit={canvasDevice==='phone'?undefined:reconcilePageAutoFit}
    onBeginGesture={beginPageWidgetGesture} onEndGesture={endPageWidgetGesture}
    assets={assets} backgrounds={backgrounds} sessionId={selected} joinCode={snap.session.join_code} onUpload={uploadWidgetMedia} assetBusy={assetBusy}
    backgroundAssetId={canvasDevice==='phone'?mobileLayoutDraft.backgroundAssetId||'':questionBackgroundAsset} onBackgroundSelect={id=>{if(canvasDevice==='phone'){if(id)void selectLibraryBackground(id,false,true);else setMobileLayoutDraft(old=>({...old,backgroundAssetId:undefined}));}else if(id)void selectLibraryBackground(id,false);else setQuestionBackgroundAsset('')}}
    onBackgroundUpload={file=>uploadBackground(file,false,canvasDevice==='phone')} onBackgroundColorChange={color=>setMobileLayoutDraft(old=>({...old,backgroundColor:color,backgroundAssetId:undefined}))}
    onRenamePage={renameCurrentCanvasPage}
    onContextOpen={()=>{setPageContextOpen(false);setInspectedWidget('');setPageThumbMenu('')}} dismissContextMenus={!!pageThumbMenu} suspendFormattingRibbon={pageConflict} onSaveRequested={()=>void updatePageDesign()} onOpenPageSettings={()=>{setInspectedWidget('');setPageContextOpen(true)}} onInspectWidget={id=>{setPageContextOpen(false);setInspectedWidget(id)}}/>
  {pageContextOpen&&<EditorFloatingWindow portal placement="page" className="editor-context-drawer" ariaLabel="Impostazioni contestuali pagina">
    <div className="editor-drawer-heading"><strong>Impostazioni pagina e risultati</strong><button type="button" className="editor-drawer-close" aria-label="Chiudi impostazioni pagina" onClick={()=>setPageContextOpen(false)}>×</button></div>
     <section className="slide-master-editor" aria-label="Editor schemi Titolo e Footer"><h4>Editor schema · Titolo sessione</h4><p className="muted tiny">Come lo schema diapositiva di PowerPoint: queste impostazioni si applicano a tutti i Titoli che usano lo schema. I titoli locali possono invece essere personalizzati.</p>
       <label>Font dello schema<select value={slideMasterDraft.fontFamily||'Arial'} onChange={e=>setSlideMasterDraft({...slideMasterDraft,fontFamily:e.target.value})}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(name=><option key={name} value={name}>{name}</option>)}</select></label>
       <label>Dimensione (pt)<input type="number" min={10} max={96} value={slideMasterDraft.fontSize||24} onChange={e=>setSlideMasterDraft({...slideMasterDraft,fontSize:Math.min(96,Math.max(10,Number(e.target.value)||24))})}/></label>
       <label>Colore<input type="color" value={slideMasterDraft.color||'#000000'} onChange={e=>setSlideMasterDraft({...slideMasterDraft,color:e.target.value})}/></label>
       <label><input type="checkbox" checked={slideMasterDraft.bold!==false} onChange={e=>setSlideMasterDraft({...slideMasterDraft,bold:e.target.checked})}/> Grassetto</label>
       <button type="button" className="primary small" onClick={()=>void saveSlideMaster()}>Applica schema a tutta la sessione</button>
       <div className="slide-master-sample" style={{fontFamily:slideMasterDraft.fontFamily||'Arial',fontSize:slideMasterDraft.fontSize||24,color:slideMasterDraft.color||'#000000',fontWeight:slideMasterDraft.bold!==false?'bold':'normal'}}>Titolo della diapositiva</div>
     </section>
     <button type="button" className="outline small" onClick={adoptSchemaOnCurrentPage}>Applica schema Titolo/Footer alla pagina corrente</button>
     <section className="slide-master-editor" aria-label="Schema footer della pagina"><h4>Editor schema · Footer</h4>
       <p className="muted tiny">Inserisci e configura il footer della pagina corrente. Il numero pagina rimane dinamico anche dopo il riordinamento.</p>
       {pageWidgets.filter((w:any)=>w.kind==='footer').map((w:any)=><div key={w.id} className="schema-footer-controls">
         <label><input type="checkbox" checked={w.footerShowSessionTitle!==false} onChange={e=>setPageWidgets(old=>old.map(item=>item.id===w.id?{...item,footerShowSessionTitle:e.target.checked}:item))}/>Mostra titolo della sessione</label>
         <label><input type="checkbox" checked={w.footerShowPageNumber!==false} onChange={e=>setPageWidgets(old=>old.map(item=>item.id===w.id?{...item,footerShowPageNumber:e.target.checked}:item))}/>Mostra numero pagina</label>
         <label>Colore del testo footer<input type="color" value={w.style?.color||'#e0e5f2'} onChange={e=>setPageWidgets(old=>old.map(item=>item.id===w.id?{...item,style:{...item.style,color:e.target.value}}:item))}/></label>
         <label>Dimensione del footer (pt)<input type="number" min={10} max={96} value={w.style?.fontSize||14} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=10&&n<=96)setPageWidgets(old=>old.map(item=>item.id===w.id?{...item,style:{...item.style,fontSize:n}}:item))}}/></label>
         <button type="button" className="outline small" onClick={()=>setInspectedWidget(w.id)}>Posizione, rotazione e altre proprietà</button>
       </div>)}
       {!pageWidgets.some((w:any)=>w.kind==='footer')&&<button type="button" className="outline small" onClick={()=>setPageWidgets(old=>[...old,newFooterWidget(crypto.randomUUID())])} disabled={pageWidgets.length>=16}>Inserisci footer nella pagina</button>}
     </section>
     <p className="muted">Gli sfondi sono immagini caricate dai presentatori nella propria libreria. Gli sfondi dei collaboratori sono copiati nella tua libreria quando li utilizzi.</p>
     <label>Testo sopra la domanda<input value={questionHeader} onChange={e=>setQuestionHeader(e.target.value)}/></label>
     <label>Colore di fondo della pagina<input type="color" value={questionBackgroundColor||'#ffffff'} onChange={e=>setQuestionBackgroundColor(e.target.value)}/></label>
     <p>{questionBackgroundAsset?'Sfondo della pagina applicato':'Nessuna immagine di sfondo applicata'}</p>
     <label>Sfondo della pagina<select aria-label="Seleziona sfondo pagina dalla libreria" value="" disabled={assetBusy} onChange={e=>{if(e.target.value)void selectLibraryBackground(e.target.value,false)}}><option value="">Scegli dalla libreria dei presentatori</option>{backgrounds.map(a=><option key={a.id} value={a.id}>{a.mine?'Il mio sfondo':'Sfondo collaboratore'} · {a.id.slice(0,8)}</option>)}</select></label>
     <label>Carica un nuovo sfondo<input type="file" accept="image/png,image/jpeg,image/gif,image/webp" disabled={assetBusy} onChange={e=>{void uploadBackground(e.target.files?.[0],false).catch(()=>{});e.target.value=''}}/></label>
     <button type="button" className="outline small" onClick={()=>{setQuestionBackgroundAsset('');setQuestionBackground('')}}>Rimuovi sfondo pagina</button>
     <label>Testo sopra i risultati<input value={resultHeader} onChange={e=>setResultHeader(e.target.value)}/></label>
     <label>Colore sfondo risultati<input type="color" value={resultBackgroundColor||'#ffffff'} onChange={e=>setResultBackgroundColor(e.target.value)}/></label>
     <p>{resultBackgroundAsset?'Sfondo dei risultati applicato':'Nessuna immagine di sfondo risultati applicata'}</p>
     <label>Sfondo risultati<select aria-label="Seleziona sfondo risultati dalla libreria" value="" disabled={assetBusy} onChange={e=>{if(e.target.value)void selectLibraryBackground(e.target.value,true)}}><option value="">Scegli dalla libreria dei presentatori</option>{backgrounds.map(a=><option key={a.id} value={a.id}>{a.mine?'Il mio sfondo':'Sfondo collaboratore'} · {a.id.slice(0,8)}</option>)}</select></label>
     <label>Carica sfondo risultati<input type="file" accept="image/png,image/jpeg,image/gif,image/webp" disabled={assetBusy} onChange={e=>{void uploadBackground(e.target.files?.[0],true).catch(()=>{});e.target.value=''}}/></label>
     <button type="button" className="outline small" onClick={()=>{setResultBackgroundAsset('');setResultBackground('')}}>Rimuovi sfondo risultati</button>
   </EditorFloatingWindow>}
  {inspectedWidget&&<EditorFloatingWindow portal placement="properties" className="editor-context-drawer editor-widget-drawer" ariaLabel="Proprietà widget selezionato">
   <div className="editor-drawer-heading"><strong>Proprietà widget</strong><button type="button" className="editor-drawer-close" aria-label="Chiudi proprietà widget" onClick={()=>setInspectedWidget('')}>×</button></div>
   {pageWidgets.filter(w=>w.id===inspectedWidget).map(w=><div key={w.id} className="slide-master-widget-settings" onPointerDown={e=>{if((e.target as HTMLElement).closest('input,textarea,[contenteditable=true]'))e.stopPropagation()}}>
    {w.kind==='title'&&<><h4>Titolo della pagina</h4><label><input type="checkbox" checked={w.titleFollowPage!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,titleFollowPage:e.target.checked}:z))}/> Usa il nome corrente della pagina</label><label><input type="checkbox" checked={w.titleUseMaster!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,titleUseMaster:e.target.checked}:z))}/> Usa lo schema del titolo della sessione</label>{w.titleFollowPage===false&&<label>Testo personalizzato<input maxLength={240} value={w.label||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,label:e.target.value}:z))}/></label>}<small>Disattivando lo schema, il widget usa la propria formattazione.</small></>}
    <label><input type="checkbox" checked={w.showTitle!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,showTitle:e.target.checked}:z))}/>Mostra nome/titolo del widget</label>
    {w.kind!=='footer'&&<label className="widget-auto-fit-setting"><input type="checkbox" checked={w.autoFit!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,autoFit:e.target.checked}:z))}/> Adatta automaticamente l'altezza al contenuto</label>}
   {requiresAnswerSubmit(w.kind)&&<section className="widget-answer-typography" aria-label="Formattazione delle risposte e invio"><h4>Risposte e pulsante invio</h4>
    <label>Font risposta<select aria-label="Font campo risposta" value={w.style?.answerFontFamily||'Arial'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerFontFamily:e.target.value}}:z))}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(f=><option key={f}>{f}</option>)}</select></label>
    <label>Dimensione carattere risposta (px)<input type="number" min={10} max={96} value={w.style?.answerFontSize||16} onChange={e=>{const v=Number(e.target.value);if(Number.isInteger(v)&&v>=10&&v<=96)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerFontSize:v}}:z))}}/></label>
    <label>Colore testo risposta<input type="color" value={w.style?.answerColor||'#152236'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerColor:e.target.value}}:z))}/></label>
    <label><input type="checkbox" checked={!!w.style?.answerBold} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerBold:e.target.checked}}:z))}/> Risposta in grassetto</label>
    <label><input type="checkbox" checked={!!w.style?.answerItalic} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerItalic:e.target.checked}}:z))}/> Risposta in corsivo</label>
     <label>Larghezza casella risposta libera (%)<input type="number" aria-label="Larghezza casella risposta libera" min={25} max={100} step={5} value={w.style?.answerFieldWidth||100} onChange={e=>{const v=Number(e.target.value);if(Number.isInteger(v)&&v>=25&&v<=100)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerFieldWidth:v}}:z))}}/></label>
     <label>Altezza casella risposta libera (px)<input type="number" aria-label="Altezza casella risposta libera" min={48} max={400} step={8} value={w.style?.answerFieldHeight||96} onChange={e=>{const v=Number(e.target.value);if(Number.isInteger(v)&&v>=48&&v<=400)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerFieldHeight:v}}:z))}}/></label>
    <label>Dimensione pulsante invio (px)<input type="number" aria-label="Dimensione pulsante invio" min={12} max={40} value={w.style?.submitButtonSize||16} onChange={e=>{const v=Number(e.target.value);if(Number.isInteger(v)&&v>=12&&v<=40)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,submitButtonSize:v}}:z))}}/></label>
    <p className="muted tiny">Le opzioni di scelta supportano anche la formattazione dei singoli caratteri tramite la palette.</p>
   </section>}
 {w.kind==='footer'&&<><h4>Footer della pagina</h4><label><input type="checkbox" checked={w.footerShowSessionTitle!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,footerShowSessionTitle:e.target.checked}:z))}/> Mostra il nome della sessione al centro</label><label><input type="checkbox" checked={w.footerShowPageNumber!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,footerShowPageNumber:e.target.checked}:z))}/> Mostra il numero della pagina a destra</label>{w.footerShowSessionTitle===false&&<label>Testo centrale personalizzato<input maxLength={240} value={w.label||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,label:e.target.value}:z))}/></label>}<small>La numerazione si aggiorna automaticamente al riordino delle diapositive.</small></>}
   </div>)}
   <ol className="widget-list">{pageWidgets.map((w,i)=>({w,i})).filter(x=>x.w.id===inspectedWidget).map(({w,i})=><li key={w.id} draggable onDragStart={e=>e.dataTransfer.setData('text/plain',String(i))} onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();const from=Number(e.dataTransfer.getData('text/plain'));if(Number.isInteger(from)&&from>=0&&from<pageWidgets.length)setPageWidgets(old=>{const next=[...old];const [m]=next.splice(from,1);next.splice(i,0,m);return next})}}><span aria-label="Trascina">⠿ {w.kind}</span>{eligibleStatisticSources(pageWidgets).some(source=>source.id===w.id)&&<label>Grafico risultati del widget<select aria-label={'Grafico risultati '+w.id} value={(w as any).resultsView||'bars'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,resultsView:e.target.value}:z))}><option value="bars">Barre</option><option value="pie">Torta</option><option value="table">Tabella</option><option value="cloud">Nuvola</option></select></label>}{w.kind==='results-button'&&<label className="widget-results-top-setting">Risultati principali da mostrare<input type="number" aria-label="Numero risultati principali" min={1} max={20} step={1} value={w.resultTopCount??5} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=1&&n<=20)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,resultTopCount:n}:z))}}/><small>Default 5 · tutte le voci selezionate saranno mostrate per intero, riscalandole se necessario.</small></label>}
     {w.kind==='results-button'&&<label className="widget-results-only-setting"><input type="checkbox" aria-label="Mostra soltanto i risultati" checked={w.resultsOnly===true} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,resultsOnly:e.target.checked}:z))}/> Solo risultati (nascondi titolo e testo della domanda)<small>Disattivata per impostazione predefinita. I conteggi restano visibili soltanto al presentatore.</small></label>}{w.kind==='results-button'&&<label className="widget-auto-fit-setting"><input type="checkbox" aria-label="Ridimensionamento automatico contenuto risultati" checked={w.autoFit!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,autoFit:e.target.checked}:z))}/> Adatta automaticamente il contenuto dei risultati<small>Disattiva per modificare liberamente l'altezza del riquadro senza ridimensionare testi e grafici. L'eventuale eccedenza scorre nel widget.</small></label>}{w.kind==='results-button'&&<label>Widget sorgente delle statistiche<select aria-label="Widget sorgente statistiche" value={(w as any).targetWidgetId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,targetWidgetId:e.target.value||undefined,targetQuestionId:undefined}:z))}><option value="">Seleziona un widget della pagina</option>{eligibleStatisticSources(pageWidgets,w.id).map(source=><option key={source.id} value={source.id}>{source.label||editorWidgetNames[source.kind]||source.kind}</option>)}</select><small>Solo il presentatore vede i risultati; ogni istanza è indipendente.</small></label>}{w.kind==='results-button'&&pageWidgets.find(z=>z.id===w.targetWidgetId)?.questions?.length&&<label>Domanda da visualizzare<select aria-label="Domanda sorgente delle statistiche" value={(w as any).targetQuestionId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,targetQuestionId:e.target.value||undefined}:z))}><option value="">Domanda principale</option>{(pageWidgets.find(z=>z.id===w.targetWidgetId)?.questions||[]).map((q:any)=><option key={q.id} value={q.id}>{q.label}</option>)}</select></label>}{w.kind==='profile'&&<label>Testo aggiuntivo del presentatore<textarea aria-label="Testo opzionale profilo presentatore" maxLength={500} rows={3} value={w.description||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,description:e.target.value}:z))}/></label>}{w.kind==='reactions'&&<label>Dimensione icone delle reazioni (px)<input type="range" aria-label="Dimensione icone reazioni" min={16} max={96} step={2} value={w.reactionIconSize||32} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,reactionIconSize:Number(e.target.value)}:z))}/><output>{w.reactionIconSize||32}px</output></label>}{w.kind==='timer'&&<label>Durata massima countdown (secondi)<input type="number" aria-label="Durata massima countdown del widget" min={1} max={3600} step={1} value={w.durationSeconds??60} onChange={e=>{const value=Number(e.target.value);if(Number.isInteger(value)&&value>=1&&value<=3600)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,durationSeconds:value}:z))}}/><small>Da 1 secondo a 60 minuti. Allo scadere, tutte le interazioni della pagina vengono bloccate.</small></label>}{w.kind==='profile'&&<select aria-label="Presentatore da mostrare" value={(w as any).presenterId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,presenterId:e.target.value||undefined}:z))}><option value="">Autore della sessione</option>{availablePresenters.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select>}{['question','timed-quiz'].includes(w.kind)&&<label><input type="checkbox" checked={w.allowAnswerChange===true} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,allowAnswerChange:e.target.checked}:z))}/>Consenti al partecipante di modificare la risposta inviata (durante la finestra di voto)</label>}{w.kind==='profile'&&<label><input type="checkbox" checked={w.showEmail===true} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,showEmail:e.target.checked}:z))}/>Pubblica l'e-mail del presentatore nella pagina (visibile a tutti i partecipanti)</label>}{w.kind==='rating'&&<p className="muted tiny">0 = gradimento minimo · 9 = gradimento massimo</p>}{w.kind==='rating'&&<select aria-label="Oggetto del gradimento" value={(w as any).targetKind||'question'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,targetKind:e.target.value}:z))}><option value="question">Domanda</option><option value="quiz">Quiz</option><option value="session">Sessione</option><option value="presenter">Presentatore</option></select>}{w.kind==='rating'&&(w as any).targetKind==='presenter'&&<select aria-label="Presentatore valutato" value={(w as any).targetId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,targetId:e.target.value||undefined}:z))}><option value="">Seleziona presentatore</option>{availablePresenters.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select>}<input aria-label="Titolo widget" title="Clicca per posizionare il cursore; trascina per selezionare il testo" onPointerDown={e=>e.stopPropagation()} value={w.label||''} maxLength={240} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,label:e.target.value}:z))}/>{['rating','question','text','postit'].includes(w.kind)&&<textarea aria-label="Descrizione o commento opzionale" rows={2} maxLength={500} value={w.description||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,description:e.target.value}:z))}/>} {w.kind==='topic-question'&&<label><input type="checkbox" checked={!!(w as any).showNames} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,showNames:e.target.checked}:z))}/>Mostra nickname al presentatore</label>}{w.kind==='question'&&<label><input type="checkbox" checked={w.required!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,required:e.target.checked}:z))}/>Obbligatoria</label>}{['question','timed-quiz'].includes(w.kind)&&<WidgetSubquestionEditor widget={w} onPatch={changes=>setPageWidgets(old=>old.map(z=>{if(z.id!==w.id)return z;let marks:TextMark[]=z.textMarks||[];if(Array.isArray(changes.questions)){const next=changes.questions as any[];for(const q of z.questions||[]){const changed=next.find(n=>n.id===q.id);if(!changed){marks=marks.filter(m=>!m.field.startsWith('question:'+q.id+':'));continue}if(changed.label!==q.label)marks=remapMarks(marks,'question:'+q.id+':label',q.label||'',changed.label||'');if(changed.description!==q.description)marks=remapMarks(marks,'question:'+q.id+':description',q.description||'',changed.description||'');for(const option of q.options||[]){const target=(changed.options||[]).find((o:any)=>o.id===option.id);const f='question:'+q.id+':option:'+option.id;if(!target)marks=marks.filter(m=>m.field!==f);else if(target.label!==option.label)marks=remapMarks(marks,f,option.label||'',target.label||'')}}}return {...z,...changes,textMarks:marks}}))}/>}{['question','timed-quiz'].includes(w.kind)&&<WidgetChoiceEditor widget={w} onPatch={changes=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,...changes}:z))}/>}{['image','video','logo','pdf'].includes(w.kind)&&<label>File multimediale caricato<select aria-label={'Allegato '+w.kind} value={w.assetId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,assetId:e.target.value}:z))}><option value="">Seleziona file</option>{assets.filter(a=>w.kind==='pdf'?a.mime_type==='application/pdf':w.kind==='logo'?a.mime_type.startsWith('image/'):a.mime_type.startsWith(w.kind+'/')).map(a=><option key={a.id} value={a.id}>{a.mime_type} · {a.id.slice(0,8)}</option>)}</select><input type="file" aria-label={"Carica media "+w.kind} accept={w.kind==='pdf'?'application/pdf':w.kind==='video'?'video/mp4,video/webm':'image/png,image/jpeg,image/gif,image/webp'} disabled={assetBusy} onChange={e=>{void uploadWidgetMedia(w.id,e.target.files?.[0],w.kind);e.target.value=''}}/><small>Seleziona oppure carica un file e salva il layout prima di pubblicare.</small></label>}{['shape','line'].includes(w.kind)&&<section className="widget-graphic-settings" aria-label="Formato elementi grafici"><h4>Forma e linea</h4>{w.kind==='shape'&&<label>Tipo di forma<select aria-label="Tipo forma grafica" value={w.style?.shapeType||'rectangle'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,shapeType:e.target.value as WidgetTextStyle['shapeType']}}:z))}>{['rectangle','rounded-rectangle','circle','ellipse','triangle','diamond','hexagon','pentagon','star','arrow','heart','cloud','speech'].map(t=><option key={t} value={t}>{t}</option>)}</select></label>}{w.kind==='line'&&<label>Direzione linea<select aria-label="Direzione linea" value={w.style?.lineDirection||'horizontal'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,lineDirection:e.target.value as WidgetTextStyle['lineDirection']}}:z))}>{['horizontal','vertical','diagonal','reverse'].map(t=><option key={t} value={t}>{t}</option>)}</select></label>}<label>Spessore (pt)<input type="number" min={0} max={12} step={0.5} value={w.style?.strokeWidth??2} onChange={e=>{const n=Number(e.target.value);if(n>=0&&n<=12)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,strokeWidth:n}}:z))}}/></label><label>Colore<input type="color" value={w.style?.strokeColor||'#334155'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,strokeColor:e.target.value}}:z))}/></label><label>Tratto<select value={w.style?.strokeDash||'solid'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,strokeDash:e.target.value as WidgetTextStyle['strokeDash']}}:z))}>{['solid','dash','dot'].map(t=><option key={t} value={t}>{t}</option>)}</select></label></section>}<WidgetAppearanceEditor widget={w} onPatch={style=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,...style}}:z))}/>{w.style?.fillMode==='image'&&<label>Immagine di riempimento del widget<select aria-label="Immagine di riempimento del widget" value={w.style?.fillImageAssetId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,fillImageAssetId:e.target.value||undefined}}:z))}><option value="">Seleziona immagine</option>{assets.filter(a=>a.mime_type?.startsWith('image/')).map(a=><option key={a.id} value={a.id}>{a.id.slice(0,8)} · {a.mime_type}</option>)}</select></label>}{w.style?.fillMode==='image'&&<label>Carica immagine di riempimento<input type="file" accept="image/png,image/jpeg,image/gif,image/webp" disabled={assetBusy} onChange={e=>{void uploadWidgetFillImage(w.id,e.target.files?.[0]);e.target.value=''}}/></label>}<details className="widget-options"><summary>Stile e animazioni</summary><div className="widget-style"><label>Font<select value={w.style?.fontFamily||'Arial'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,fontFamily:e.target.value}}:z))}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(x=><option key={x}>{x}</option>)}</select></label><label>Dimensione<input type="number" min="10" max="96" value={w.style?.fontSize||18} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,fontSize:Number(e.target.value)}}:z))}/></label><label>Allineamento testo<select aria-label="Allineamento testo widget" value={w.style?.textAlign||"left"} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,textAlign:e.target.value as WidgetTextStyle['textAlign']}}:z))}><option value="left">Sinistra</option><option value="center">Centro</option><option value="right">Destra</option></select></label><label>Allineamento verticale<select aria-label="Allineamento verticale widget" value={w.style?.verticalAlign||"top"} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,verticalAlign:e.target.value as WidgetTextStyle['verticalAlign']}}:z))}><option value="top">Alto</option><option value="middle">Centro</option><option value="bottom">Basso</option></select></label><label>Colore<input type="color" value={w.style?.color||'#1f2937'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,color:e.target.value}}:z))}/></label>{(['bold','italic','underline','strikethrough'] as const).map(k=><label key={k}><input type="checkbox" checked={!!w.style?.[k]} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,[k]:e.target.checked}}:z))}/>{k}</label>)}<label>Animazione<select value={w.style?.animation||'none'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,animation:e.target.value as WidgetTextStyle['animation']}}:z))}><option>none</option><option>fade</option><option>slide</option></select></label></div></details><button className="outline small" onClick={()=>{if(!window.confirm('Eliminare questo widget dal canvas?'))return;setPageWidgets(old=>old.filter(z=>z.id!==w.id))}}>Rimuovi</button><button className="outline small" disabled={i===0} onClick={()=>setPageWidgets(old=>{const n=[...old];[n[i-1],n[i]]=[n[i],n[i-1]];return n})}>↑</button><button className="outline small" disabled={i===pageWidgets.length-1} onClick={()=>setPageWidgets(old=>{const n=[...old];[n[i+1],n[i]]=[n[i],n[i+1]];return n})}>↓</button></li>)}</ol>
  </EditorFloatingWindow>}
 </div>
  {pageConflict&&<div className="editor-secondary-workflow" aria-label="Esportazione, salvataggio e risoluzione conflitti"><div className="editor-save-feedback" role="status" aria-live="polite">{notice|| (pageHasUnsavedChanges?"Modifiche da salvare":"Nessuna modifica in sospeso")}</div><div className="downloads">{pageHasUnsavedChanges&&<span role="status" className="muted tiny">● Modifiche non salvate</span>}{pageConflict&&<div role="alert" className="notice">Un altro presentatore ha salvato questa pagina. La tua bozza è ancora disponibile, ma non può sovrascrivere la versione più recente.</div>}{pageConflict&&<><button className="outline small" disabled={pageSavePending || !!mergeCandidate?.local} onClick={()=>void inspectPageConflict()}>Confronta e riconcilia le modifiche</button><button className="outline small" disabled={pageSavePending} onClick={async()=>{if(!window.confirm('Scartare le modifiche locali e ricaricare il layout aggiornato dal server?'))return;try{const latest=await request<Snapshot>(`/sessions/${selected}`);const page=latest.activities.find(a=>a.id===designActivity);if(!page){setNotice('La pagina non esiste più');return}setSnap(latest);beginPageDesign(page);setNotice('Layout aggiornato dal server')}catch(e){notify(e)}}}>Ricarica layout dal server</button></>}{pageConflict&&mergeCandidate&&mergePreview&&<section className="page-merge-panel" aria-label="Riconciliazione delle modifiche"><h4>Riconciliazione con la versione server {mergeCandidate.revision}</h4><p className="muted tiny">Le modifiche indipendenti sono combinate senza sovrascrivere il server. Per ogni conflitto scegli esplicitamente quale valore conservare. La sincronizzazione automatica riprende dopo la risoluzione esplicita dei conflitti.</p>{mergePreview.conflicts.length===0&&<p role="status">Nessun conflitto sui singoli campi: le modifiche sono combinabili.</p>}{mergePreview.conflicts.map(c=><label key={c.path} className="page-merge-choice">{c.label}<select aria-label={'Risolvi '+c.label} value={mergeChoices[c.path]||''} onChange={e=>setMergeChoices(old=>({...old,[c.path]:e.target.value as MergeChoice}))}><option value="">Scegli una versione</option><option value="local">Conserva la mia modifica</option><option value="remote">Conserva la modifica del server</option></select><div className="page-merge-diff"><span><strong>La mia versione:</strong> <code>{describeMergeValue(c.local)}</code></span><span><strong>Versione server:</strong> <code>{describeMergeValue(c.remote)}</code></span></div></label>)}<div className="downloads"><button type="button" className="outline small" disabled={!mergePreview.conflicts.length} onClick={()=>setMergeChoices(Object.fromEntries(mergePreview.conflicts.map(c=>[c.path,'local' as MergeChoice])))}>Scegli la mia versione per tutti</button><button type="button" className="outline small" disabled={!mergePreview.conflicts.length} onClick={()=>setMergeChoices(Object.fromEntries(mergePreview.conflicts.map(c=>[c.path,'remote' as MergeChoice])))}>Scegli la versione server per tutti</button></div><p className="muted tiny" role="status">{unresolvedMergeConflicts.length} conflitti ancora da risolvere. Le modifiche non vengono pubblicate finché non premi Salva layout.</p><div className="downloads"><button className="primary small" disabled={unresolvedMergeConflicts.length>0||pageSavePending} onClick={()=>void applyPageRebase()}>Applica riconciliazione alla bozza</button><button className="outline small" onClick={()=>{if(mergeCandidate?.local)setPageConflict(false);setMergeCandidate(null);setMergeChoices({})}}>Annulla confronto</button></div></section>}<button className="primary small" onClick={updatePageDesign} disabled={!pageHasUnsavedChanges||pageSavePending||pageConflict}>Salva layout</button><button className="outline small" onClick={()=>{if(confirmPageNavigation())setDesignActivity('')}}>Chiudi</button></div></div>}
</div>
<aside className="editor-widget-rail" aria-label="Aggiungi widget">
 <header><strong>Widget</strong><span className="muted tiny">Trascina o tocca</span></header>
 <div className="editor-widget-grid">{editorWidgetKinds.map(k=><EditorIconTool key={k} kind={k} label={`Aggiungi widget: ${editorWidgetNames[k]}`} draggable onDragStart={e=>{e.dataTransfer.setData('application/x-quorivio-widget',k);e.dataTransfer.effectAllowed='copy'}} onClick={()=>{setInspectedWidget('');setPageContextOpen(false);setPageWidgets(old=>{if(old.length>=16){setNotice('Massimo 16 widget per pagina.');return old}const i=old.length;const position=k==='footer'?newFooterWidget('new').position:freeWidgetPosition(old,{x:4+(i%4)*24,y:4+Math.floor(i/4)*24},22,20);if(!position){setNotice('Non c’è spazio per un altro widget su questa pagina.');return old}return [...old,{...(k==='footer'?newFooterWidget(crypto.randomUUID()):{}),id:crypto.randomUUID(),kind:k,...(k==='results-button'&&eligibleStatisticSources(old).length?{targetWidgetId:eligibleStatisticSources(old)[0].id}:{}),style:{...(k==='footer'?newFooterWidget('new').style:{}),fillNone:k!=='shape',shapeType:'rectangle',...(k==='shape'||k==='line'?{strokeColor:'#334155',strokeWidth:2,strokeDash:'solid',lineDirection:'horizontal',fillColor:k==='shape'?'#dbeafe':'#ffffff'}:{})},label:k==='footer'?'':k==='rating'?'Quanto hai gradito?':k==='question'?'Nuova domanda':k==='timed-quiz'?'Quiz a tempo':k==='results-button'?'Risultati':k==='participant-count'?'Partecipanti connessi':editorWidgetNames[k],position:{...position,rotation:0}}]})}}><EditorWidgetIcon kind={k}/><span className="editor-icon-caption" aria-hidden="true">{editorWidgetNames[k]}</span></EditorIconTool>)}</div>
 </aside>
{editorTouchHint&&<div className="editor-touch-assist" role="status" aria-live="polite">{editorTouchHint}</div>}
</section>}{selected&&<section className="panel"><h3>Schermo presentatore</h3><p>Apri la vista di presentazione e le statistiche live in una finestra separata.</p><a className="outline asbutton" target="_blank" rel="noopener noreferrer" href={'/screen/'+encodeURIComponent(selected)}>Apri schermo presentatore ↗</a><details className="presenter-preview"><summary>Mostra anteprima della schermata di proiezione</summary><iframe title="Anteprima presentatore e risultati live" loading="lazy" src={'/screen/'+encodeURIComponent(selected)}/></details></section>}{selected&&(presenterLive==='disconnected'||presenterLive==='blocked')&&<div className="live-stale-warning" role="status" aria-live="polite">{presenterLive==='blocked'?'Accesso live revocato: i dati potrebbero non essere aggiornati.':'Connessione live interrotta: le statistiche potrebbero essere obsolete. Riconnessione in corso…'}</div>}{current&&<section className="panel live-panel"><div className="eyebrow"><span className="live-dot"/> {t.results}</div><h2>{current.title}</h2>{showResults(snap,current)}</section>}{current&&(current as any).page_design?.widgets?.filter((w:any)=>w.kind==='topic-question').map((w:any)=><TopicPresenterList key={w.id} sessionId={selected} activityId={current.id} widget={w}/>)}{current&&<PresenterAudienceExtensions key={current.id} sessionId={selected} activityId={current.id}/>}<section className="panel"><h3><ShieldCheck size={19}/> {lang==='it'?'Privacy e ciclo di vita':'Privacy and lifecycle'}</h3><button type="button" className="binary-toggle" aria-pressed={snap.session.allow_anonymous!==false} onClick={()=>setAnonymous(!(snap.session.allow_anonymous!==false))}>Consenti partecipazione anonima: {snap.session.allow_anonymous!==false?'SÌ':'NO'}</button><button type="button" className="binary-toggle" aria-pressed={!!snap.session.show_results} onClick={()=>setResultsVisibility(!(!!snap.session.show_results))}>Pubblica risultati live ai partecipanti: {!!snap.session.show_results?'SÌ':'NO'}</button><label htmlFor="retention-days">{lang==='it'?'Conservazione risposte (giorni)':'Response retention (days)'}</label><div className="downloads"><input id="retention-days" type="number" min="1" max="3650" defaultValue={snap.session.retention_days??60} key={selected+String(snap.session.retention_days)} onBlur={e=>{const days=Number(e.target.value);if(Number.isInteger(days)&&days>=1&&days<=3650&&days!==snap.session.retention_days)updateRetention(days)}} aria-label="Retention days"/></div><p className="muted tiny">{lang==='it'?'Per salvare, modifica il valore e sposta il focus. La cancellazione programmata riguarda sessioni chiuse o scadute.':'Change the value and leave the field to save. Scheduled purging applies to closed or expired sessions.'}</p><div className="downloads"><button className="outline small" onClick={revokeSession} disabled={snap.session.status==='closed'}>{lang==='it'?'Revoca accessi':'Revoke access'}</button></div></section><section className="panel"><h3>Allegati della sessione</h3><label>Importa PowerPoint modificabile in una nuova sessione (conversione parziale)<input type="file" accept=".pptx,application/vnd.openxmlformats-officedocument.presentationml.presentation" disabled={assetBusy} onChange={e=>{void importEditablePowerPoint(e.target.files?.[0]);e.target.value=''}}/></label><p className="muted tiny">Testi, immagini PNG/JPEG e alcune forme semplici diventano widget modificabili. Grafici, SmartArt, animazioni e temi complessi possono perdere fedeltà: per preservare l’aspetto originale usa anche l’importazione grafica.</p><label>Importa direttamente PDF/PPTX (richiede worker di conversione configurato)<input type="file" accept=".pdf,.pptx,application/pdf,application/vnd.openxmlformats-officedocument.presentationml.presentation" disabled={assetBusy||snap.session.status==='closed'} onChange={e=>{void importPresentationFile(e.target.files?.[0]);e.target.value=''}}/></label><label>Importa pagine convertite (PNG/JPEG/WebP, in ordine alfabetico)<input type="file" accept="image/png,image/jpeg,image/webp" multiple disabled={assetBusy||snap.session.status==='closed'} onChange={e=>{void importSlideImages(e.target.files);e.target.value=''}}/></label><p className="muted tiny">Puoi importare direttamente PDF/PPTX quando il convertitore è configurato. In alternativa usa tools/import_presentation.py e seleziona le immagini convertite.</p><p className="muted tiny">PNG, JPEG, GIF, WebP, PDF, MP4, WebM. Limite predefinito 100 MB, modificabile dall’amministratore. I file sono privati e scaricabili solo dai presentatori autorizzati.</p><label>Carica un file<input type="file" accept="image/png,image/jpeg,image/gif,image/webp,application/pdf,video/mp4,video/webm" disabled={assetBusy||snap.session.status==='closed'} onChange={e=>{void uploadAsset(e.target.files?.[0]);e.target.value=''}}/></label><div className="downloads"><button className="outline small" onClick={refreshAssets}>Aggiorna allegati</button></div>{assets.map(a=><div className="activity-row" key={a.id}><div><small>{a.mime_type} · {Math.ceil(Number(a.byte_size)/1024)} KiB</small><div className="muted tiny">{a.id}</div></div><div className="activity-actions"><a className="outline asbutton" href={a.url} target="_blank" rel="noreferrer">Apri</a>{a.mime_type.startsWith('image/')&&snap.session.status!=='closed'&&<button className="outline small" onClick={()=>addSlide(a)}>Crea pagina slide</button>}{snap.session.status!=='closed'&&<button className="outline small" onClick={()=>deleteAsset(a.id)}>Elimina</button>}</div></div>)}</section><section className="panel"><h3>Portabilità e collaborazione</h3><p className="muted tiny">Il formato .quorivio include definizione e allegati utilizzati, ma non risposte, credenziali o dati dei partecipanti. I formati legacy restano importabili tramite gli strumenti amministrativi di migrazione. La duplicazione genera un nuovo codice QR.</p><div className="downloads"><button className="outline small" onClick={duplicateSelected}>Duplica sessione</button><a className="outline asbutton" href={`/api/sessions/${selected}/export.quorivio`} download>Esporta archivio Quorivio completo</a><a className="outline asbutton" href={`/api/sessions/${selected}/export.pptx`} download>Esporta PowerPoint (contenuti supportati)</a></div><label>Importa archivio Quorivio con allegati (.quorivio)<input type="file" accept=".quorivio,application/vnd.quorivio.session+zip" onChange={e=>{void importQuorivioBundle(e.target.files?.[0]);e.target.value=''}}/></label><hr/><label>Email co-presentatore approvato<input type="email" value={coEmail} onChange={e=>setCoEmail(e.target.value)}/></label><div className="downloads"><button className="outline small" onClick={addCollaborator} disabled={!coEmail.includes('@')}>Aggiungi presentatore</button><button className="outline small" onClick={refreshCollaborators}>Mostra collaboratori</button></div>{coPresenters.map(x=><div className="activity-row" key={x.id}><span>{x.email}</span><button className="small outline" onClick={()=>removeCollaborator(x.id)}>Rimuovi</button></div>)}</section><section className="panel"><h3><Download size={19}/> Dati della sessione</h3><p className="muted">Scarica le risposte confermate in CSV.</p><a className="outline asbutton" href={`/api/sessions/${selected}/report.json`} download>Report JSON aggregato e audit</a><a className="outline asbutton" href={`/api/sessions/${selected}/export.csv`}><Download size={16}/> Esporta CSV</a></section></div></div></>}</div></main>}
<footer>QUORIVIO · Open infrastructure for interactive experiences</footer></div>}
createRoot(document.getElementById('root')!).render(<App/>);
