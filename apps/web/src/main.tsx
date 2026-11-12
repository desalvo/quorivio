import {thumbnailWidgetModel} from './thumbnail-widget-content.js';
import {resultPieLayout,resultPieSize,resultPiePercent,resultPieViewport} from './result-pie-layout.js';
import {createLiveResultPoller} from './live-result-poller.js';
import {answerFieldHeight,answerFieldHeightForKey} from './answer-field-resize.js';
import {readWorkspaceLocation,writeWorkspaceLocation} from './workspace-recovery';
import {LOCAL_SESSION_ARCHIVE_MIME,LOCAL_SESSION_ARCHIVE_MAX_BYTES,localSessionArchiveFilename,localSessionImportError,isLocalSessionArchiveMime} from './session-local-transfer.js';
import {DEFAULT_TITLE_STYLE,newTitleWidget,newFooterWidget,widgetDisplay,slidePageNumber,footerPageNumber} from './slide-master';
import {choosePageIds,orderedSelectedPageIds,duplicatePageOrder,thumbnailShortcut} from './page-thumbnail-selection';
import {canResetListedSession,canDeleteListedSession} from './session-list-management';
import {resolveSlideMasterWidgets,masterWidgetTemplate,normalizeLegacyFooter} from './master-widget-utils';
import {participantVisibleWidgets,participantPhoneLayout,widgetTitleVisible} from './live-slide-policy';
import {defaultParticipantPhoneMode} from './participant-device-default';
import {participantPhoneLayoutEnabled,participantStaticWidescreenPage} from './participant-widescreen-policy';
import {participantReadingWidgets} from './live-slide-policy';
import {stageWidgetTypography} from './stage-widget-typography';
import {consumeRecoveryTokenFromUrl} from './password-recovery-url';
import {validPageDesign} from '../../api/src/domain';
import {setChoiceTruth,clearChoiceTruth,gradeChoiceAnswer} from '../../api/src/widget-answer-key';
import type {AnswerFeedback} from '../../api/src/widget-answer-key';
import type {PageDesign,WidgetTextStyle,WidgetInlineMark,WidgetSubquestion} from '../../api/src/domain';
import {pageDraftSignature as serializePageDraft,pageDraftFromActivity,validDesignRevision,type EditablePageDraft} from './page-draft';
import {autosaveRecoveryDecision,recoverableAutosaveTransportError,retryAutosaveDelay} from './page-autosave';
import {widgetAppearanceStyle,widgetTypographyStyle} from './widget-appearance.js';
import {widgetArtData,widgetTimerFace,type WidgetTimerFace} from './widget-art.js';
import {styledSegments,inlineMarkCss,formatTextRange,remapMarks,changedRegion,inlineKeys,applySelectionInlineStyle,selectionUniformValue,scaleWidgetFont,scaleAllWidgetTypography,formatSelectedOrEntireField,applyAllWidgetTypeface,type InlineStyle,type TextMark} from './widget-text-marks.js';
import {RichWidgetText,restoreDomTextRange} from './widget-rich-editor.js';
import {explicitWidgetFontFamily,widgetTextDefaults,initialWidgetTextStyle} from './widget-typography-defaults.js';
import {RatingChoices,RatingCommentField} from './rating-choices.js';
import {ReactionChoices} from './reaction-choices.js';
import {eligibleStatisticSources,linkedStatisticSource,linkedResultQuestion,resultSourceTitleVisible,resultSourceAnswersVisible,linkedStatisticContext,effectiveResultView,sampleStatisticRows,rehearsalFreeTextRows,rowsFromWidgetAnswerDetail,topicQuestionRows,REHEARSAL_EMOJIS,type StatRow,gaugeModel,gaugeColor,reactionBubbles,fitReactionBubbleLayout} from './widget-results.js';
import {resultTextCss,resultHasAnswerKey,resultElementKey} from './result-text-style.js';
import {answerTruthVerdict,feedbackOptionVerdict,truthVerdictClass,truthVerdictSymbol} from './answer-truth-presentation.js';
import {ResultFormatControls} from './result-format-controls.js';
import {rehearsalPresenterPages,rehearsalAudiencePage,rehearsalStartIndex} from './rehearsal-page-routing.js';
import {rejectWidgetCollisions,moveWidgetsToCollisionLimit,resizeWidgetToCollisionLimit,magneticSnapWithGuides,snapWidgetGroupDelta,freeWidgetPosition} from './widget-placement.js';
import {widgetGeometryStyle} from './widget-geometry';
import {mediaUploadMime} from './widget-asset-upload';
import {backgroundUploadError} from './background-upload-error';
import {answerInputStyle,answerOptionStyle,answerSubmitStyle,requiresAnswerSubmit} from './widget-answer-style';
import {cloudRankColor,rankCloudItems} from './word-cloud-rank';
import {sortedResultBars,visibleResultBars,resultBarWidth,splitResultLabel} from './result-top-rows';
import {phoneStageScale} from './rehearsal-phone-scale';
import {MOBILE_PAGE_WIDTH,mobileStageHeight,mobilePageWidgets,mergeMobilePositionEdits,pruneMobilePageLayout} from './mobile-page-layout';
import type {MobilePageLayout} from '../../api/src/domain';
import {proportionalWidgetScale,predictedResultsHeight} from './widget-content-scale';
import {canvasWidgetAtPoint} from './editor-context-hit';
import {startsWidgetSelectionOnPointerDown} from './editor-context-input';
import {activateRehearsalDialog} from './rehearsal-dialog';
import {questionModeOptions,invalidPageWidgetReason} from './editor-save-safety';
import {contextMenuCoordinates,floatingWidgetMenuPosition} from './editor-context-menu';
import {boundFloatingPosition,boundFloatingSize,floatingLogicalViewport} from './editor-floating-geometry';
import {thumbnailMenuPosition} from './thumbnail-menu-layout';
import {WidgetShapeOutline} from './widget-shape-outline';
import {WidgetGraphic} from './widget-graphic';
import {GRAPHIC_PRESETS,graphicStyle,type GraphicKind,type GraphicPreset} from './graphic-presets';
import {slideBackgroundCss,slideBackground} from './master-background';
import {canSubmitRehearsalAnswer,commitRehearsalAnswer,changeRehearsalReaction,changeRehearsalRating,REHEARSAL_REACTION_PREFIX} from './rehearsal-responses';
import {rehearsalDurationSeconds,rehearsalExpired,maySubmitTimedRehearsal,pageCountdownSeconds,pageInteractionExpired} from './rehearsal-timer';
import {mergePageDrafts,type MergeChoice} from './page-merge';
import {createPageDraftBackup,parsePageDraftBackup,planPageDraftRecovery} from './page-draft-recovery';
import {arrangeWidgets,type ArrangeMode} from './widget-arrange';
import {resultBarGradient} from './result-bar-gradient.js';
import {normalizeJoinCode,canSubmitParticipantAnswer,publicActivityFromSnapshot} from './participant-state';
import {moveWidgetGroup,pasteWidgetGroup} from './widget-group';
import {createLiveConnection} from './live-connection';
import {EMPTY_QR_TARGET,visibleQrTarget,updateQrTarget,type SyncedQrTarget} from './session-qr-state';
import {isOwnerSessionSnapshot,normalizeOwnerSessionSnapshot,sessionFailureForStatus} from './session-load-recovery';
import {reorderWidgetLayers,type LayerAction} from './widget-layer';
import {existingWidgetIds,deleteWidgetSelection,insertWidgetGroupInFreeSpace,nudgeWidgetSelection} from './widget-selection';
import {pasteWidget} from './widget-clipboard';
import {saveEditorWidgetClipboard,readEditorWidgetClipboard} from './editor-cross-page-clipboard';
import {newWidgetHistory,editWidgets,reconcileWidgetAutoFit,beginWidgetGesture,endWidgetGesture,undoWidgets,redoWidgets} from './widget-history';
import {AuthBackendSettingsPanel} from './admin-auth-backends.js';
import {activateUiLanguage,preferredUiLanguage,translateUiText,type UiLanguage} from './ui-locale.js';
import {EditableNumberField} from './editable-number-field.js';
import {GLOBAL_ZOOM_STORAGE_KEY,GLOBAL_ZOOM_MIN,GLOBAL_ZOOM_MAX,GLOBAL_ZOOM_CSS_VARIABLE,normalizeGlobalZoom,nextGlobalZoom,zoomStyleValue,isUnscaledPublicSurface} from './global-page-zoom.js';
import {movePageId,movePageToSlot} from './page-order';
import {rehearsalPageDirection} from './rehearsal-navigation';
import {presenterPageIndex,presenterAdjacentPage,presenterKeyboardDirection,presenterVisiblePages} from './presenter-navigation';
import {commitAndReconcilePageOrder} from './page-order-recovery';
import React,{useEffect,useState,useRef} from 'react';import{createPortal}from'react-dom';import{createRoot}from'react-dom/client';import{ArrowRight,BarChart3,Download,ExternalLink,LogOut,Play,Plus,Radio,ShieldCheck,Square,Users,Wifi,Type,Image as ImageIcon,Clock3,MessageCircle,FileText,Minus,MoreVertical,Settings2,Undo2,Redo2,Save,Maximize2,Star,Smile,StickyNote,UserCircle,Video,QrCode,Timer,MessageSquareText,BadgeCheck,Gauge,Heading1,PanelBottom,Presentation,BarChartHorizontal,FileQuestion,Vote,Hash,BookImage,Bold as BoldIcon,Italic as ItalicIcon,Underline as UnderlineIcon,Strikethrough as StrikethroughIcon,AlignLeft,AlignCenter,AlignRight,PaintBucket,Palette as PaletteIcon,SlidersHorizontal,X,MoveHorizontal,MoveVertical,Scissors,Copy,ClipboardPaste,Info,Upload}from'lucide-react';import './style.css';
// RC266: title-bar docking stays reachable at the bottom and right of the
// editor; a separate corner handle resizes format and widget properties windows.
function EditorFloatingWindow({children,className,ariaLabel,role='region',placement='properties',portal=false,onMouseDownCapture}:{children:React.ReactNode;className:string;ariaLabel:string;role?:'toolbar'|'region';placement?:'palette'|'properties'|'page';portal?:boolean;onMouseDownCapture?:React.MouseEventHandler<HTMLDivElement>}){
 const panel=useRef<HTMLDivElement|null>(null);
 // The studio applies CSS zoom on <html>: fixed offsets are in logical
 // pixels, but window.innerWidth/Height remain physical. Root clientWidth can
 // also be physical with overflow rules, so divide by the computed CSS zoom.
 const viewport=()=>floatingLogicalViewport(window.innerWidth,window.innerHeight,Number.parseFloat(getComputedStyle(document.documentElement).zoom));
 const pointer=useRef<{id:number;kind:'move'|'resize';startX:number;startY:number;left:number;top:number;width:number;height:number}|null>(null);
 const [size,setSize]=useState<{width:number;height:number}|null>(null);
 const [point,setPoint]=useState<{left:number;top:number}>(()=>{
  const vp=typeof document==='undefined'?{width:1440,height:900}:viewport();
  const vw=vp.width,vh=vp.height;
  if(placement==='palette')return {left:Math.max(12,Math.round((vw-Math.min(850,vw-24))/2)),top:Math.max(12,Math.round(vh-Math.min(190,vh/3)-22))};
  return {left:Math.max(12,vw-Math.min(440,vw-24)-28),top:Math.max(12,Math.min(110,vh/8))};
 });
 const bound=(left:number,top:number)=>{
  const vp=viewport();
  return boundFloatingPosition(left,top,panel.current?.offsetWidth||Math.min(850,vp.width-24),panel.current?.offsetHeight||180,vp.width,vp.height);
 };
 useEffect(()=>{
  const constrain=()=>{
   setPoint(previous=>{const next=bound(previous.left,previous.top);return next.left===previous.left&&next.top===previous.top?previous:next});
   const vp=viewport();
   setSize(previous=>{if(!previous)return previous;const next=boundFloatingSize(previous.width,previous.height,vp.width,vp.height,placement);return previous.width===next.width&&previous.height===next.height?previous:next});
  };
  constrain();window.addEventListener('resize',constrain);
  const observer=typeof ResizeObserver==='undefined'?null:new ResizeObserver(constrain);
  if(panel.current)observer?.observe(panel.current);
  observer?.observe(document.documentElement); // react to global CSS zoom without a window resize
  return ()=>{window.removeEventListener('resize',constrain);observer?.disconnect()};
 },[placement]);
 const start=(e:React.PointerEvent<HTMLDivElement>)=>{
  if(e.button!==0)return;
  const target=e.target as HTMLElement;
  const resize=!!target.closest('.editor-floating-resize-handle');
  if(!resize&&!target.closest('.palette-ribbon-head,.editor-drawer-heading'))return;
  if(!resize&&target.closest('button,input,textarea,select,a,[contenteditable=true]'))return;
  pointer.current={id:e.pointerId,kind:resize?'resize':'move',startX:e.clientX,startY:e.clientY,left:point.left,top:point.top,width:panel.current?.offsetWidth||360,height:panel.current?.offsetHeight||240};
  e.currentTarget.setPointerCapture(e.pointerId);
  e.preventDefault();
 };
 const move=(e:React.PointerEvent<HTMLDivElement>)=>{
  const drag=pointer.current;if(!drag||drag.id!==e.pointerId)return;
  const dx=e.clientX-drag.startX,dy=e.clientY-drag.startY;
  if(drag.kind==='resize'){const vp=viewport();setSize(boundFloatingSize(drag.width+dx,drag.height+dy,vp.width,vp.height,placement));}
  else setPoint(bound(drag.left+dx,drag.top+dy));
 };
 const stop=(e:React.PointerEvent<HTMLDivElement>)=>{if(pointer.current?.id===e.pointerId){pointer.current=null;if(e.currentTarget.hasPointerCapture(e.pointerId))e.currentTarget.releasePointerCapture(e.pointerId)}};
 const resizeWithKeyboard=(e:React.KeyboardEvent<HTMLButtonElement>)=>{
  if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(e.key))return;
  e.preventDefault();e.stopPropagation();
  const step=e.shiftKey?48:16;
  const base=size||{width:panel.current?.offsetWidth||360,height:panel.current?.offsetHeight||240};
  const vp=viewport();
  setSize(boundFloatingSize(base.width+(e.key==='ArrowRight'?step:e.key==='ArrowLeft'?-step:0),base.height+(e.key==='ArrowDown'?step:e.key==='ArrowUp'?-step:0),vp.width,vp.height,placement));
 };
 const customSize=size?({'--editor-floating-width':size.width+'px','--editor-floating-height':size.height+'px'} as React.CSSProperties):{};
 const content=<div ref={panel} className={className+' editor-floating-panel'} data-floating-editor={placement} role={role} aria-label={ariaLabel} style={{left:point.left,top:point.top,...customSize}} onMouseDownCapture={onMouseDownCapture} onKeyDownCapture={e=>{if((e.target as HTMLElement).closest('input,select,textarea,[contenteditable=true]'))e.stopPropagation()}} onPointerDown={start} onPointerMove={move} onPointerUp={stop} onPointerCancel={stop} onLostPointerCapture={stop}>{children}<button type="button" className="editor-floating-resize-handle" aria-label={'Ridimensiona '+ariaLabel+' (trascina o usa le frecce)'} title="Ridimensiona: trascina l’angolo o usa le frecce; Maiusc per passi più grandi" onKeyDown={resizeWithKeyboard} /></div>;
 return portal?createPortal(placement==='palette'?content:<div className="editor-ux-v2 editor-floating-scope">{content}</div>,document.body):content;
}

/** Scale only rendered content, never resize the author-defined widget or its handles.
 * The frame uses native layout dimensions and reports when it was downscaled.
 * The same component is used for editor, presenter and rehearsal surfaces. */
function WidgetContentFit({children,editor=false,allowScale=true,minScale=.005,textStyle}:{children:React.ReactNode;editor?:boolean;allowScale?:boolean;minScale?:number;textStyle?:React.CSSProperties}){
 const frame=useRef<HTMLDivElement>(null),body=useRef<HTMLDivElement>(null);
 const [factor,setFactor]=useState(1);
 useEffect(()=>{
  let raf=0;
  const measure=()=>{
   cancelAnimationFrame(raf);
   raf=requestAnimationFrame(()=>{
    const a=frame.current,b=body.current;if(!a||!b||!a.clientWidth||!a.clientHeight)return;
    if(!allowScale){setFactor(1);return}
    // Keep the entire text/chart/legend/percentage/answer subtree under ONE transform.
    // Result rows are all rendered in the source option order (even before votes);
    // reserve the tallest row including the potential true/false badge.
    const results=b.querySelector<HTMLElement>('.linked-results');
    const rows=results?.querySelector<HTMLElement>('.linked-results-items');
    const actualRows=Array.from(rows?.querySelectorAll<HTMLElement>('.linked-results-row')||[]);
    const chartHasRows=Boolean(results&&['bars','pie','table','cloud'].includes(results.dataset.fitPredictedChart||''));
    const configuredRows=chartHasRows?Number(results?.dataset.fitPredictedRows??actualRows.length):0;
    const tallestRow=Math.max(22,...actualRows.map(row=>row.offsetHeight));
    const otherHeight=results?Math.max(0,results.scrollHeight-(rows?.scrollHeight||0)):0;
    const predicted=results&&chartHasRows&&configuredRows>actualRows.length?predictedResultsHeight({
     rows:Math.max(actualRows.length,configuredRows||0),
     maxRowHeight:tallestRow,
     otherHeight:b.scrollHeight-results.scrollHeight+otherHeight,
     truthBadge:results.dataset.answerKeyEnabled==='true'
    }):0;
    const next=proportionalWidgetScale({
     frameWidth:a.clientWidth,frameHeight:a.clientHeight,
     contentWidth:Math.max(b.scrollWidth,b.clientWidth),
     contentHeight:Math.max(b.scrollHeight,b.clientHeight),
     predictedHeight:predicted,minScale
    });
    // Always shrink when the content grows: the previous scale may now overflow.
    setFactor(previous=>next<previous?next:Math.abs(previous-next)<.0001?previous:next);
   });
  };
  measure();const resize=new ResizeObserver(measure);
  if(frame.current)resize.observe(frame.current);
  if(body.current)resize.observe(body.current);
  const changes=new MutationObserver(measure);
  if(body.current)changes.observe(body.current,{childList:true,characterData:true,subtree:true,attributes:true,attributeFilter:['class','style','hidden','data-answer-verdict']});
  document.fonts?.ready.then(measure).catch(()=>{});
  return()=>{cancelAnimationFrame(raf);resize.disconnect();changes.disconnect()};
 },[children,allowScale,minScale]);
 return <><div className="widget-fit-frame" ref={frame} data-scaled={allowScale&&Math.abs(factor-1)>.015} data-fit-mode={allowScale?'scale':'scroll'}>
  <div className="widget-fit-content" ref={body} style={{...textStyle,'--widget-fit-scale':allowScale?factor:1,transform:allowScale&&Math.abs(factor-1)>.015?`scale(${factor})`:undefined} as React.CSSProperties}>{children}</div>
 </div>{editor&&allowScale&&factor<.985&&<span className="widget-rescale-indicator" role="status" title={`Contenuto ridotto al ${Math.round(factor*100)}% per entrare nel widget`} aria-label={`Contenuto ridotto al ${Math.round(factor*100)}%`}>↘ {Math.round(factor*100)}%</span>}</>;
}

type DiskVolumeStatus={status:'ok'|'warning'|'unavailable';usedBytes:number|null;totalBytes:number|null;availableBytes:number|null;usedPercent:number|null;observedAt:string|null;reason?:string};
type DiskStatus={thresholdPercent:number;recoveryPercent:number;checkedAt:string;emailNotificationsConfigured:boolean;application:DiskVolumeStatus;conversion:DiskVolumeStatus;database:DiskVolumeStatus;logicalDatabaseBytes:number};
function diskGigabytes(bytes:number|null|undefined){return bytes===null||bytes===undefined?'—':(bytes/(1024**3)).toLocaleString('it-IT',{maximumFractionDigits:2})+' GiB'}
type Session={id:string;owner_id?:string;access_role?:'owner'|'collaborator';title:string;reference_date?:string;join_code:string;join_url:string;status:string;current_activity_id:string|null;presenter_activity_id?:string|null;expires_at:string;retention_days?:number;allow_anonymous?:boolean;show_results?:boolean;theme?:any};type Activity={id:string;type:'poll'|'quiz'|'timed_quiz'|'slide';title:string;options:{id:string;label:string}[];correct_option_id?:string;status:string;duration_seconds:number|null;opened_at?:string;answer_mode?:'single'|'multiple'|'text'|'file';answer_required?:boolean;page_design?:any};type Snapshot={connected_participants?:number;session:Session;activities:Activity[];results:{activity_id:string;option_id:string;count:number}[];totals:{activity_id:string;count:number}[]};
/** Expired/revoked presenter credentials redirect to the login screen without a manual reload.
 * Public audience and initial login/MFA requests must never trigger a redirect loop. */
let reauthenticationRedirecting=false;
function redirectExpiredPresenterAuth(url:string,status:number,apiError?:string):boolean{
 const shouldRedirect=(status===401&&['authentication_required','session_revoked'].includes(apiError||''))
  &&!url.startsWith('/join/')
  &&!['/auth/me','/auth/login','/auth/ldap/login','/auth/ldap/status','/auth/oidc/providers'].includes(url)
  &&!url.startsWith('/auth/oidc/')&&!url.startsWith('/auth/mfa/challenge/');
 if(shouldRedirect&&!reauthenticationRedirecting){
  reauthenticationRedirecting=true;
  // No full document navigation: repeated 401s must not cause a reload/rate-limit storm.
  window.history.replaceState(window.history.state,'','/?reauthentication_required=1');
  window.dispatchEvent(new Event('quorivio:authentication-expired'));
 }
 return shouldRedirect;
}
/** Multipart transfers and downloads bypass the JSON request helper but still
 * use the same reauthentication behavior when their presenter cookie expires. */
async function authenticatedFetch(input:RequestInfo|URL,init?:RequestInit):Promise<Response>{
 const url=typeof input==='string'?input:input instanceof URL?input.pathname:input.url;
 const apiPath=url.startsWith('/api/')?url.slice(4):'';
 // Suppress stale multipart/download requests after the first expired-auth 401.
 // A local response prevents background polling from hitting server rate limits.
 // Anonymous join and sign-in calls must remain available.
 if(reauthenticationRedirecting&&apiPath&&!apiPath.startsWith('/auth/')&&!apiPath.startsWith('/join/')){
  return new Response(JSON.stringify({error:'authentication_required'}),{status:401,headers:{'Content-Type':'application/json'}});
 }
 const response=await fetch(input,init);
 if(response.status===401){
  if(url.startsWith('/api/')&&!url.startsWith('/api/join/')){
   const info=await response.clone().json().catch(()=>({}));
   redirectExpiredPresenterAuth(url.slice(4),response.status,info?.error);
  }
 }
 return response;
}
async function request<T=any>(url:string,method='GET',body?:unknown,options?:{signal?:AbortSignal;cache?:RequestCache}):Promise<T>{
 // After expiry, suppress stale background calls; allow login/MFA and identity discovery.
 const authRoute=url.startsWith('/auth/');
 const guestRoute=url.startsWith('/join/');
 if(reauthenticationRedirecting&&!authRoute&&!guestRoute){const error=Object.assign(new Error('authentication_required'),{status:401});return Promise.reject(error)}
 const res=await fetch('/api'+url,{method,credentials:'include',headers:{'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body),signal:options?.signal,cache:options?.cache});if(!res.ok){let info:any={};try{info=await res.json()}catch{}redirectExpiredPresenterAuth(url,res.status,info.error);const e=new Error(res.status===429&&info.error==='rate_limited'?'Limite temporaneo di richieste raggiunto: riprova tra poco.':info.error||`HTTP ${res.status}`) as Error&{status:number};e.status=res.status;throw e}if(authRoute&&res.ok&&(url==='/auth/me'||url==='/auth/login'||url==='/auth/ldap/login'||url.startsWith('/auth/mfa/'))){reauthenticationRedirecting=false;}
 return res.status===204||res.status===205?undefined as T:res.json()}
/** A stalled request must never keep a restored session on a blank page indefinitely. */
function sessionSnapshotRequest(sessionId:string,signal?:AbortSignal):Promise<Snapshot>{
 return request<Snapshot>(`/sessions/${encodeURIComponent(sessionId)}`,'GET',undefined,{signal,cache:'no-store'});
}
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
 useEffect(()=>{let alive=true;const load=()=>authenticatedFetch(`/api/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(activityId)}/timed-leaderboard?page=${page}`,{credentials:'same-origin'}).then(r=>r.ok?r.json():null).then(v=>{if(alive)setData(v)}).catch(()=>{});void load();const timer=setInterval(load,2000);return()=>{alive=false;clearInterval(timer)}},[sessionId,activityId,page]);
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
 // Legacy question statistics cannot render reaction-only bubbles.
 const mode=['bars','pie','table','cloud','gauge'].includes(widget.resultsView)?widget.resultsView:'bars';
 return <section className="panel" aria-label={`Risultati ${widget.label||'domanda'}`}><h4>{widget.label||'Domanda'} · {mode==='bars'?'Barre':mode==='pie'?'Torta':mode==='cloud'?'Nuvola':mode==='gauge'?'Gauge':'Tabella'}</h4>{!data?<p>Caricamento risultati…</p>:data.revisions?.length?data.revisions.map((rev:any)=><div key={rev.revision}><p>Revisione {rev.revision} · {rev.responses} risposte · {rev.texts||0} testi · {rev.attachments||0} allegati</p>{Object.keys(rev.options||{}).length>0&&<div className={'widget-results-'+mode}>{mode==='gauge'&&<ResultGauge widget={widget} rows={Object.entries(rev.options||{}).map(([id,count])=>({id,label:widget.options?.find((o:any)=>o.id===id)?.label||id,count:Number(count)||0}))} sourceKind={widget.kind}/>}{mode==='pie'&&<div role="img" aria-label="Distribuzione risposte" style={{width:110,height:110,borderRadius:'50%',margin:'12px auto',background:`conic-gradient(${Object.values(rev.options).map((v:any,i:number,all:any[])=>{const start=all.slice(0,i).reduce((a:number,b:any)=>a+Number(b),0)/Math.max(1,all.reduce((a:number,b:any)=>a+Number(b),0))*100;const end=(all.slice(0,i+1).reduce((a:number,b:any)=>a+Number(b),0))/Math.max(1,all.reduce((a:number,b:any)=>a+Number(b),0))*100;return `${['#536fd7','#40a8a0','#e4a84b','#9b71c7','#d76d84'][i%5]} ${start}% ${end}%`}).join(',')})`}}/>}{(mode==='gauge'?[]:mode==='cloud'?rankCloudItems(Object.entries(rev.options),entry=>Number(entry[1]),entry=>entry[0]):Object.entries(rev.options)).map(([key,value],index)=>{const count=Number(value),total=Math.max(1,Object.values(rev.options).reduce((a:number,b:any)=>a+Number(b),0));const label=widget.options?.find((o:any)=>o.id===key)?.label||key;return mode==='cloud'?<span key={key} className="result-cloud-word" style={{fontSize:`${Math.round(14+26*count/total)}px`,color:cloudRankColor(index)}} title={`${label}: ${count}`}><span>{label}</span><small> [{count}]</small></span>:<div key={key} className={mode==='bars'?'widget-results-bar-row':undefined}><div className="widget-results-bar-caption"><span>{label}</span><strong aria-label={`${count} risposte`}>{count}</strong></div>{mode==='bars'&&<progress max={total} value={count} aria-label={`${label}: ${count} su ${total}`}/>}</div>})}</div>}</div>):<p>Nessuna risposta per questo widget.</p>}</section>
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
/** A result-specific text override wins over the formatting of the linked source. */
function ResultCopyText({value,source,field,result,formatKey}:{value:string;source:any;field:string;result:any;formatKey:string}){
 return result.resultTextStyles?.[formatKey]?<>{value}</>:<WidgetStyledText text={value} widget={source} field={field}/>;
}
/** One rating widget across editor, presenter, rehearsal and public participation.
 * In particular the optional comment, authored description, legend and button
 * size must not drift depending on which view is rendering the same page. */
function RatingStageContent({widget,readOnly=false,disabled=false,comment='',onCommentChange,selected,onSelect}:{widget:any;readOnly?:boolean;disabled?:boolean;comment?:string;onCommentChange?:(comment:string)=>void;selected?:string;onSelect?:(score:number)=>void}){
 return <div className="projection-sample-rating" data-rating-parity="true">
  {widgetTitleVisible(widget)&&<strong><WidgetStyledText text={widget.label||'Gradimento'} widget={widget} field="label"/></strong>}
  {widget.description&&<p><WidgetStyledText text={widget.description} widget={widget} field="description"/></p>}
  <RatingCommentField value={comment} readOnly={readOnly} disabled={disabled} onChange={onCommentChange}/>
  <p className="rating-range-hint muted tiny">0 = gradimento minimo · 9 = gradimento massimo</p>
  <RatingChoices view={widget.style?.ratingView} size={widget.style?.ratingButtonSize} readOnly={readOnly} disabled={disabled} selected={selected} onSelect={onSelect}/>
 </div>;
}
/** Optional source copy inherits the originating question font, answer styling
 * and per-field rich marks. Rendered above, not inside, the statistic rows. */
/** Independent source-title and answer toggles; the old combined flag is read
 * for existing sessions. Source choices never expose grading keys. */
function LinkedResultSourceQuestion({result,source,rankedRows=[]}:{result:any;source:any;rankedRows?:StatRow[]}){
 const selected=result.resultsOnly?undefined:linkedResultQuestion(result,source);if(!selected)return null;
 const {part,questionId}=selected;
 const showSourceTitle=resultSourceTitleVisible(result);
 const showSourceAnswers=resultSourceAnswersVisible(result);
 const field=(key:string)=>questionId?'question:'+questionId+':'+key:key;
 const format=widgetTextDefaults(source.kind,source.style)||{};
 const sourceStyle:React.CSSProperties={
  fontFamily:format.fontFamily||undefined,
  fontSize:`${Math.max(10,Math.min(96,Number(format.fontSize)||22))}px`,
  textAlign:format.textAlign||undefined
 };
 const choices=source.kind==='rating'?Array.from({length:10},(_,i)=>({id:String(i),label:String(i)})):
  source.kind==='reactions'?['👍','❤️','😂','😮','👏','🎉','🤔','😕'].map(v=>({id:v,label:v})):(part.options||[]);
 return <section className="linked-source-question" data-source-widget-id={source.id} data-source-question-id={questionId} aria-label="Domanda sorgente" style={sourceStyle}>
  {showSourceTitle&&<strong className="linked-source-question-title" data-result-custom={result.resultTextStyles?.sourceTitle?"true":undefined} style={resultTextCss(result.resultTextStyles,"sourceTitle")}><ResultCopyText value={source.label||part.label||''} source={source} field="label" result={result} formatKey="sourceTitle"/></strong>}
  {showSourceAnswers&&<>
   {['question','timed-quiz','topic-question'].includes(source.kind)&&<div className="linked-source-question-prompt" data-result-custom={result.resultTextStyles?.[`question:${questionId||"main"}`]?"true":undefined} style={resultTextCss(result.resultTextStyles,`question:${questionId||"main"}`,{color:result.style?.sourceQuestionColor||'#2563eb'})}><span aria-hidden="true">• </span><ResultCopyText value={part.label||source.label||''} source={source} field={field('label')} result={result} formatKey={`question:${questionId||"main"}`}/></div>}
   {part.description&&<p><WidgetStyledText text={part.description} widget={source} field={field('description')}/></p>}
   {choices.length>0&&<div className="linked-source-answers" role="list" aria-label="Risposte possibili">
    {sortedResultBars(choices.map((opt:any)=>({opt,count:rankedRows.find(r=>r.id===opt.id)?.count||0})),result.resultSortOrder).map(({opt}:any)=>{const optionIndex=choices.findIndex((candidate:any)=>candidate.id===opt.id);const verdict=answerTruthVerdict(source,questionId,opt.id,result.showCorrectAnswers===true);return <div key={opt.id} role="listitem" data-answer-verdict={verdict||undefined} data-correct={verdict==='correct'?'true':undefined} className={'widget-answer-option linked-source-answer'+truthVerdictClass(verdict)} data-result-custom={result.resultTextStyles?.[resultElementKey('option',questionId,opt.id)]?'true':undefined} style={{...answerOptionStyle(format),...resultTextCss(result.resultTextStyles,resultElementKey('option',questionId,opt.id),{bold:true})}}><span aria-hidden="true">{result.pieShowOptionNumbers===true&&result.resultsView==='pie'?`${optionIndex+1}. `:'• '} </span><strong style={{fontWeight:'inherit'}}><ResultCopyText value={opt.label} source={source} field={field('option:'+opt.id)} result={result} formatKey={resultElementKey('option',questionId,opt.id)}/></strong>{verdict&&<span className="answer-verdict-icon" aria-label={verdict==='correct'?'Risposta vera':'Risposta falsa'}>{truthVerdictSymbol(verdict)}</span>}</div>})}
   </div>}
  </>}
 </section>;
}
/** RC316: shared, accessible, responsive dial with needle, graduated scale and glow. */
function ResultGauge({widget,rows,sourceKind='question'}:{widget:any;rows:StatRow[];sourceKind?:string}){
 const model=gaugeModel(rows,widget,sourceKind),uid=React.useId().replace(/:/g,'');
 const color=gaugeColor(widget.gaugeColor),minColor=gaugeColor(widget.gaugeMinColor,'#11e98b'),maxColor=gaugeColor(widget.gaugeMaxColor,'#ff4263');
 const showValue=widget.gaugeShowValue!==false,gradient=widget.gaugeGradient!==false;
 const label=model.value===null?'—':Number(model.value.toFixed(2)).toLocaleString('it-IT',{maximumFractionDigits:2});
 const fmt=(v:number)=>Number(v.toFixed(2)).toLocaleString('it-IT',{maximumFractionDigits:2});
 const point=(part:number,radius:number)=>({x:180-Math.cos(Math.PI*part)*radius,y:183-Math.sin(Math.PI*part)*radius});
 const tip=point(model.percent/100,116),ticks=Array.from({length:51},(_,i)=>{
  const t=i/50,major=i%5===0;return {i,major,inside:point(t,major?108:116),outside:point(t,124),label:major?point(t,91):null};
 });
 const arc="M 46 183 A 134 134 0 0 1 314 183",arcColor=gradient?`url(#gauge-arc-${uid})`:color;
 return <svg className="linked-results-gauge" viewBox="0 0 360 286" role="img" aria-label={`Gauge semicircolare: ${model.value===null?'nessun dato':label}; minimo ${model.min}; massimo ${model.max}; aggregazione ${model.aggregation}`} preserveAspectRatio="xMidYMid meet" data-gauge-needle={model.value===null?'empty':'active'}>
  <title>{`Gauge ${model.aggregation}: ${label}, intervallo ${model.min}–${model.max}`}</title>
  <defs>
   <linearGradient id={`gauge-arc-${uid}`} x1="0%" y1="0%" x2="100%" y2="0%"><stop offset="0%" stopColor={minColor}/><stop offset="48%" stopColor="#ffe944"/><stop offset="100%" stopColor={maxColor}/></linearGradient>
   <linearGradient id={`gauge-needle-${uid}`} x1="0%" y1="100%" x2="100%" y2="0%"><stop offset="0%" stopColor="#1d3555"/><stop offset="48%" stopColor="#4e709a"/><stop offset="100%" stopColor="#172c48"/></linearGradient>
   <filter id={`gauge-glow-${uid}`} x="-30%" y="-50%" width="160%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>
  </defs>
  <path className="linked-results-gauge-halo" d={arc} stroke={arcColor} filter={`url(#gauge-glow-${uid})`}/>
  <path className="linked-results-gauge-track" d={arc}/>
  <path className="linked-results-gauge-fill" d={arc} stroke={arcColor}/>
  {ticks.map(t=><g key={t.i} className={t.major?'linked-results-gauge-major':'linked-results-gauge-minor'}>
   <line x1={t.inside.x} y1={t.inside.y} x2={t.outside.x} y2={t.outside.y}/>
   {t.label&&<text x={t.label.x} y={t.label.y} dominantBaseline="middle" textAnchor="middle">{fmt(model.min+t.i/50*(model.max-model.min))}</text>}
  </g>)}
  {model.value!==null&&<g className="linked-results-gauge-needle">
   <path d={`M 174 188 L ${tip.x} ${tip.y} L 186 178 Z`} fill={`url(#gauge-needle-${uid})`}/>
   <circle cx="180" cy="183" r="15" fill="#25345e" stroke="#a9b9ff" strokeWidth="3"/>
   <circle cx="176" cy="179" r="7" fill="#d0d9ff" opacity=".8"/>
  </g>}
  {showValue&&<text className="linked-results-gauge-value" x="180" y="245" textAnchor="middle">{label}</text>}
  <text className="linked-results-gauge-caption" x="180" y="273" textAnchor="middle">{widget.label||'Risultati'}</text>
 </svg>;
}


/** Shared responsive emoji layout for editor, preview and presenter: measured
 * using the chart's own frame, with a scrollable opt-out for legacy layouts. */
function ResponsiveReactionBubbles({widget,rows,total,fit}:{widget:any;rows:StatRow[];total:number;fit:boolean}){
 const items=total>0?reactionBubbles(rows,widget.resultTopCount??5,widget.resultSortOrder):[];
 const container=useRef<HTMLDivElement>(null);
 const [viewport,setViewport]=useState({width:360,height:220});
 useEffect(()=>{
  if(!fit||!container.current)return;
  const el=container.current;let raf=0;
  const measure=()=>{cancelAnimationFrame(raf);raf=requestAnimationFrame(()=>{
   const width=el.clientWidth,height=el.clientHeight;
   setViewport(old=>Math.abs(old.width-width)<1&&Math.abs(old.height-height)<1?old:{width,height});
  })};
  const observer=new ResizeObserver(measure);
  observer.observe(el);measure();
  return()=>{cancelAnimationFrame(raf);observer.disconnect()};
 },[fit]);
 const layout=fitReactionBubbleLayout(items,viewport.width,viewport.height);
 const presentation=fit?({
  '--bubble-columns':String(layout.columns),'--bubble-rows':String(layout.rows),
  '--bubble-gap':layout.gap+'px','--bubble-padding':layout.padding+'px',
  '--bubble-meta-font':layout.metaFont+'px','--bubble-emoji-font':layout.emojiFont+'px'
 } as React.CSSProperties):undefined;
 return <div ref={container} className="linked-results-bubbles" data-bubble-mode={fit?'fit':'scroll'} style={presentation} role="list" aria-label="Reazioni più frequenti">
  {items.map((r,i)=><div className="linked-results-bubble-item" key={r.id} role="listitem" aria-label={`${r.label}: ${r.count} reazioni, ${r.percent.toFixed(1)}%`}>
   <span className="linked-results-bubble-orb" style={{'--reaction-bubble-size':`${fit?layout.diameters[i]:r.size}px`,'--reaction-bubble-hue':String((i*53+210)%360)} as React.CSSProperties}><span aria-hidden="true">{r.label}</span></span>
   <strong className="linked-results-bubble-count">{r.count}</strong>
   <small className="linked-results-bubble-percent">{r.percent.toLocaleString('it-IT',{maximumFractionDigits:1})}%</small>
  </div>)}
  {total===0&&<span className="linked-results-no-data" role="status">Nessuna reazione ancora registrata.</span>}
 </div>;
}

/** The exact same chart is used in editor, both rehearsals and presenter projection. */
function LinkedResultChart({widget,widgets,rows,emptyLabel}:{widget:any;widgets:any[];rows?:StatRow[];emptyLabel?:string}){
 const source=linkedStatisticSource(widget,widgets);
 const chart=effectiveResultView(widget,widgets);
 const [truthVisible,setTruthVisible]=useState(widget.showCorrectAnswers===true);
 useEffect(()=>setTruthVisible(widget.showCorrectAnswers===true),[widget.id,widget.targetWidgetId,widget.targetQuestionId,widget.showCorrectAnswers]);
 const hasKey=resultHasAnswerKey(source,widget.targetQuestionId||'');
 const viewWidget={...widget,showCorrectAnswers:hasKey&&truthVisible};
 if(!source)return <div className="linked-results linked-results-unconfigured" role="status">{widget.showTitle!==false&&!widget.resultsOnly&&<strong>{widget.label||'Risultati'}</strong>}<small>Collega un widget statistico dalle proprietà, anche da un’altra pagina.</small></div>;
 const sourceRows=rows||sampleStatisticRows(source,1,{},widget.targetQuestionId||'');
 const data=sortedResultBars(sourceRows,widget.resultSortOrder);
 const displayRows=visibleResultBars(sourceRows,widget.resultSortOrder,widget.resultTopCount);
 const maxBarCount=Math.max(0,...displayRows.map(r=>Number.isFinite(r.count)?r.count:0));
 const total=data.reduce((n,r)=>n+r.count,0);
 const pieColors=data.map(r=>{
  const originalIndex=Math.max(0,sourceRows.findIndex(item=>item.id===r.id));
  const key=resultElementKey('row',widget.targetQuestionId||'',r.id);
  const option=resultElementKey('option',widget.targetQuestionId||'',r.id);
  const chosen=widget.resultTextStyles?.[key]?.color||widget.resultTextStyles?.[option]?.color;
  return /^#[0-9a-f]{6}$/i.test(chosen||'')?chosen:['#277fd1','#e87947','#51a580','#a477ca','#d35482','#b5a337'][originalIndex%6];
 });
 const pieSegments=resultPieLayout(data.map(r=>r.count),widget.pieSize,widget.pieShowPercentages===true,widget.pieShowOptionNumbers===true,data.map(r=>sourceRows.findIndex(item=>item.id===r.id)+1));
 const pieViewport=resultPieViewport(pieSegments,widget.pieSize);
 return <section className={'linked-results result-view-'+chart} data-answer-key-enabled={String(hasKey)} data-fit-predicted-rows={displayRows.length} data-fit-predicted-chart={chart} data-result-source-kind={source.kind} data-gauge-transparent={chart==='gauge'&&((widget.gaugeTransparent??source.gaugeTransparent)===true)?'true':undefined} data-bubbles-fit={chart==='bubbles'&&((widget.bubbleNoScroll??source.bubbleNoScroll)!==false)?'true':'false'} aria-label={'Risultati '+(source.label||source.kind)}>
  {hasKey&&<button type="button" className={'result-answer-key-toggle'+(truthVisible?' is-active':'')} aria-label={truthVisible?'Nascondi risposte vere e false':'Evidenzia risposte vere e false'} aria-pressed={truthVisible} title={truthVisible?'Nascondi evidenziazione delle risposte':'Mostra risposte vere e false'} onPointerDown={e=>e.stopPropagation()} onClick={e=>{e.stopPropagation();setTruthVisible(v=>!v)}}>R</button>}
  <LinkedResultSourceQuestion result={viewWidget} source={source} rankedRows={data}/>
  {!widget.resultsOnly&&<>{widget.showTitle!==false&&<strong><WidgetStyledText text={widget.label||'Risultati'} widget={widget} field="label"/></strong>}{!resultSourceTitleVisible(widget)&&!resultSourceAnswersVisible(widget)&&<small>{source.label||source.kind} · {total} risposte{emptyLabel?' · '+emptyLabel:''}</small>}</>}
  {(resultSourceTitleVisible(widget)||resultSourceAnswersVisible(widget))&&<small>{total} risposte{emptyLabel?' · '+emptyLabel:''}</small>}
  {chart==='gauge'&&<ResultGauge widget={{...source,...widget}} rows={sourceRows} sourceKind={source.kind}/>}
  {chart==='bubbles'&&<ResponsiveReactionBubbles widget={widget} rows={sourceRows} total={total} fit={(widget.bubbleNoScroll??source.bubbleNoScroll)!==false}/>}
  {chart==='pie'&&<svg className="linked-results-pie linked-results-pie-chart" role="img" aria-label={widget.pieShowPercentages===true?"Distribuzione percentuale delle risposte. Legenda accessibile con conteggi e percentuali.":"Distribuzione delle risposte."} viewBox={`0 ${pieViewport.y} ${pieViewport.width} ${pieViewport.height}`} style={{'--pie-chart-ratio':`${pieViewport.width} / ${pieViewport.height}`} as React.CSSProperties} data-pie-viewport-height={pieViewport.height} data-pie-size={resultPieSize(widget.pieSize)} data-mobile-percent-labels={widget.pieShowPercentages===true?'true':'false'} preserveAspectRatio="xMidYMid meet">
   <title>{widget.pieShowPercentages===true?"Distribuzione percentuale delle risposte":"Distribuzione delle risposte"}</title>
   {total===0&&<circle className="linked-results-pie-empty" cx={250} cy={160} r={116*resultPieSize(widget.pieSize)/100} fill="#e9eff5" stroke="#9aaec2" strokeWidth="2" aria-label="Torta vuota: nessuna risposta"/>}
   {pieSegments.map(r=><path key={'slice-'+r.index} d={r.path} fill={pieColors[r.index-1]} stroke="#fff" strokeWidth="1.5"><title>{`${data[r.index-1]?.label||('Opzione '+r.index)}: ${r.count} ${r.count===1?'risposta':'risposte'}${widget.pieShowPercentages===true?', '+resultPiePercent(r.share):''}`}</title></path>)}
   {pieSegments.filter(r=>r.label).map(r=><g className="linked-results-pie-callout" key={'label-'+r.index}>
    <polyline points={r.leader} fill="none" stroke={pieColors[r.index-1]} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
    <text x={r.labelX} y={r.labelY} textAnchor={r.side==='left'?'end':'start'} dominantBaseline="middle">{r.label}</text>
   </g>)}
  </svg>}
  {chart==='pie'&&total>0&&widget.pieShowPercentages===true&&<div className="linked-results-pie-mobile-legend" role="list" aria-label="Percentuali delle risposte">
   {pieSegments.map(r=><div key={'pie-mobile-'+r.index} className="linked-results-pie-mobile-item" role="listitem" aria-label={`${data[r.index-1]?.label||('Opzione '+r.index)}: ${r.count} ${r.count===1?'risposta':'risposte'}, ${resultPiePercent(r.share)}`}>
    <span className="linked-results-pie-mobile-swatch" aria-hidden="true" style={{backgroundColor:pieColors[r.index-1]}}/>
    <span className="linked-results-pie-mobile-name" title={data[r.index-1]?.label||('Opzione '+r.index)}>{widget.pieShowOptionNumbers===true?(r.index+'. '):''}{data[r.index-1]?.label||('Opzione '+r.index)}</span>
    <strong className="linked-results-pie-mobile-percent">{resultPiePercent(r.share)}</strong>
   </div>)}
  </div>}
  {emptyLabel==='live'&&total===0&&<small className="linked-results-no-data" role="status">Nessuna risposta ancora registrata per questa sorgente.</small>}
  {chart!=='gauge'&&chart!=='bubbles'&&<div className="linked-results-items">{displayRows.map((r,i)=>{const verdict=answerTruthVerdict(source,widget.targetQuestionId||'',r.id,viewWidget.showCorrectAnswers===true);return <div className={"linked-results-row"+truthVerdictClass(verdict)} data-answer-verdict={verdict||undefined} key={r.id} style={chart==='cloud'?{fontSize:`${Math.round(14+24*r.count/Math.max(1,total))}px`,color:cloudRankColor(i)}:undefined}><span className="linked-result-pair" data-result-custom={widget.resultTextStyles?.[resultElementKey('row',widget.targetQuestionId||'',r.id)]?"true":undefined} style={{...resultTextCss(widget.resultTextStyles,resultElementKey('row',widget.targetQuestionId||'',r.id)),...(chart==='pie'?{color:pieColors[data.findIndex(x=>x.id===r.id)]}: {})}}><span className="linked-result-label">{chart==='pie'&&widget.pieShowOptionNumbers===true?`${sourceRows.findIndex(x=>x.id===r.id)+1}. `:''}{splitResultLabel(r.label).prefix}</span><span className="linked-result-final">{splitResultLabel(r.label).last}<output>{chart==='cloud'?`[${r.count}]`:r.count}</output>{verdict&&<small className="answer-verdict-icon" aria-label={verdict==='correct'?'Risposta vera':'Risposta falsa'}>{truthVerdictSymbol(verdict)}</small>}</span></span>{chart==='bars'&&<div className="linked-results-track"><div style={{width:resultBarWidth(r.count,maxBarCount)+'%',...(widget.barHitGradient===true?{background:resultBarGradient(widget.barGradientStartColor,widget.barGradientEndColor,r.count/Math.max(1,maxBarCount))}: {})}}/></div>}</div>})}</div>}
 </section>;
}

/** A malformed live statistics widget must never crash the dashboard or reset
 * a running session. Errors stay local to one chart with an explicit retry. */
class ResultsWidgetErrorBoundary extends React.Component<
 React.PropsWithChildren<{widgetId:string}>,
 {failed:boolean;generation:number}
>{
 state={failed:false,generation:0};
 static getDerivedStateFromError(){return {failed:true};}
 componentDidCatch(error:Error){console.error('[quorivio-results-widget]',this.props.widgetId,error.message);}
 render(){
  if(this.state.failed)return <div className="results-widget-failure" role="alert">
   <p>Risultati temporaneamente non disponibili. La sessione e la dashboard restano operative.</p>
   <button type="button" onClick={()=>this.setState(s=>({failed:false,generation:s.generation+1}))}>Riprova grafico</button>
  </div>;
  return <React.Fragment key={this.state.generation}>{this.props.children}</React.Fragment>;
 }
}

/** Authenticated, source-scoped live results. Never leak statistics to participant projection. */
function PresenterLinkedResult({sessionId,activity,widget,widgets,activities}:{sessionId:string;activity:any;widget:any;widgets:any[];activities:any[]}){
 const context=linkedStatisticContext(widget,activity,activities,widgets);
 const sourceWidgets=context?.widgets||[];
 const source=context?.source;
 const sourceActivityId=context?.activity.id||activity.id;
 const [rows,setRows]=useState<StatRow[]>([]);
 const [loadFailed,setLoadFailed]=useState(false);
 useEffect(()=>{
  setRows([]);setLoadFailed(false);
  if(!source)return;
  const poller=createLiveResultPoller(async()=>{
   let next:StatRow[]=[];
    if(source.kind==='question'){
     const data=await request<any>(`/sessions/${encodeURIComponent(sessionId)}/widget-answers/detail?activity_id=${encodeURIComponent(sourceActivityId)}&widget_id=${encodeURIComponent(source.id)}&question_id=${encodeURIComponent(widget.targetQuestionId||'')}`);
     next=rowsFromWidgetAnswerDetail(source,data,widget.targetQuestionId||'');
    }else if(source.kind==='rating'){
     const data=await request<any>(`/sessions/${encodeURIComponent(sessionId)}/ratings/stats`);
     // The owner-only endpoint returns a source-widget scoped 0–9 histogram.
     // No participant selection or comment is projected on the presenter.
     next=Array.from({length:10},(_,score)=>({id:String(score),label:String(score),count:(data.by_widget_score||[])
      .filter((x:any)=>x.widget_id===source.id&&x.activity_id===sourceActivityId&&Number(x.score)===score)
      .reduce((sum:number,x:any)=>sum+Number(x.count||0),0)}));
    }else if(source.kind==='reactions'){
     const data=await request<any>(`/sessions/${encodeURIComponent(sessionId)}/reactions/stats`);
     next=REHEARSAL_EMOJIS.map(emoji=>({id:emoji,label:emoji,count:(data.by_page||[]).filter((x:any)=>x.activity_id===sourceActivityId&&x.emoji===emoji).reduce((n:number,x:any)=>n+Number(x.count),0)}));
    }else if(source.kind==='timed-quiz'){
     const data=await request<any>(`/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(sourceActivityId)}/widgets/${encodeURIComponent(source.id)}/timed-leaderboard?page=1`);
     next=[{id:'correct',label:'Corrette',count:Number(data.correct||0)},{id:'answers',label:'Totale',count:Number(data.answers||0)}];
    }else if(source.kind==='topic-question'){
     // Presenter-authorized, source/page-scoped PostgreSQL total. Never send
     // the free-text questions or their authors to participant projections.
     const data=await request<any>(`/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(sourceActivityId)}/topic-widgets/${encodeURIComponent(source.id)}/stats`);
     next=topicQuestionRows(data.total);
    }
   return next;
  },next=>{setRows(next);setLoadFailed(false)},()=>setLoadFailed(true));
  // Live snapshots can arrive faster than an HTTP response. Do NOT depend on
  // the entire snapshot object: doing so cancels every in-flight request while
  // participants vote, leaving a permanently empty result chart.
  void poller.refresh();const timer=window.setInterval(()=>void poller.refresh(),3000);return()=>{poller.stop();window.clearInterval(timer)};
 },[sessionId,sourceActivityId,source?.id,source?.kind,widget.targetQuestionId]);
 return <div className="presenter-linked-results" data-source-activity-id={context?.activity.id||''}>
  <LinkedResultChart widget={widget} widgets={sourceWidgets} rows={rows} emptyLabel="live"/>
  {loadFailed&&<small className="live-stale-warning" role="status">Risultati temporaneamente non disponibili. Nuovo tentativo automatico in corso.</small>}
 </div>;
}

/** Guidance is intentionally independent of the grading key; it never reveals correct options. */
function ChoiceSubmissionHint({part,kind}:{part:any;kind:string}){
 const mode=part.answerMode||(kind==='timed-quiz'?'single':'text');
 if(!['single','multiple'].includes(mode)||!(part.answerKeyEnabled===true||kind==='timed-quiz'))return null;
 return <small className="widget-truth-hint">{mode==='multiple'?'Selezionare solo le risposte vere':'Selezionare solo una risposta'}</small>;
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
  <button type="button" className="outline small projection-readonly-submit" disabled tabIndex={-1} style={answerSubmitStyle(widget.style)}>Invia risposta</button><ChoiceSubmissionHint part={part} kind={widget.kind}/>
 </section>;
}
function SlideCanvasNumber({widgets,pageNumber}:{widgets:any[];pageNumber:number}){
 const item=footerPageNumber(widgets,pageNumber);
 if(!item)return null;
 return <span className="slide-canvas-page-number" data-custom-number={'x' in item?'true':'false'} aria-label={`Numero pagina ${item.text}`}
  style={{fontFamily:item.fontFamily,fontSize:`${(item.fontSize/12.8).toFixed(5)}cqw`,color:item.color,fontWeight:item.bold?'bold':'normal',fontStyle:item.italic?'italic':'normal',textDecoration:[item.underline?'underline':'',item.strikethrough?'line-through':''].filter(Boolean).join(' ')||'none','--footer-pad-right':`${(item.paddingRight/12.8).toFixed(5)}cqw`,'--footer-pad-bottom':`${(item.paddingBottom/12.8).toFixed(5)}cqw`,'--phone-footer-number-font-size':`${item.fontSize}px`,'--phone-footer-pad-right':`${item.paddingRight}px`,'--phone-footer-pad-bottom':`${item.paddingBottom}px`,...('x' in item?{'--footer-number-x':`${item.x}%`,'--footer-number-y':`${item.y}%`,right:'auto',bottom:'auto',transform:'translate(-100%,-100%)'}:{})} as React.CSSProperties}>{item.text}</span>;
}
/** The same authoritative QR target drives the dashboard and projected widgets.
 * A reset or revocation is pushed through the presenter WebSocket, while polling
 * and focus recovery also detect changed public-origin settings or lost events.
 * Never synthesize the public URL from a join code or the browser origin. */
function useSynchronizedParticipantQr(sessionId:string|undefined,joinCode:string|undefined,publicAccess=false){
 const accessKey=publicAccess?joinCode:sessionId;
 const base=publicAccess?`/api/join/${encodeURIComponent(joinCode||'')}`:`/api/sessions/${encodeURIComponent(sessionId||'')}`;
 const sourceKey=accessKey?`${publicAccess?'public':'owner'}:${base}:${joinCode||''}`:'';
 const [target,setTarget]=useState<SyncedQrTarget>(EMPTY_QR_TARGET);
 useEffect(()=>{
  const controller=new AbortController();
  if(!sourceKey)return()=>controller.abort();
  let pending=false;
  // Both JSON endpoints are the same source of truth used for QR SVG/PNG.
  const endpoint=publicAccess?`${base}/qr-url`:`${base}/qr?format=json`;
  const refresh=async()=>{
   if(pending||controller.signal.aborted)return;
   pending=true;
   const attempt=new AbortController();
   const onStop=()=>attempt.abort();
   controller.signal.addEventListener('abort',onStop,{once:true});
   const limit=window.setTimeout(()=>attempt.abort(),9000);
   try{
    const response=await fetch(endpoint,{credentials:'same-origin',cache:'no-store',signal:attempt.signal,headers:{Accept:'application/json'}});
    if(!response.ok)throw Error('qr_link_unavailable');
    const value=await response.json();
    if(typeof value?.url!=='string'||!/^https?:\/\/[^\s]+$/.test(value.url))throw Error('invalid_qr_url');
    if(!controller.signal.aborted)setTarget(old=>updateQrTarget(old,sourceKey,value.url));
   }catch{
    // An invalidated public token must never leave a stale scannable QR visible.
    if(!controller.signal.aborted)setTarget(old=>updateQrTarget(old,sourceKey,null));
   }finally{window.clearTimeout(limit);controller.signal.removeEventListener('abort',onStop);pending=false}
  };
  void refresh();
  const timer=window.setInterval(()=>void refresh(),12000);
  const focus=()=>void refresh();
  const online=()=>void refresh();
  const visible=()=>{if(document.visibilityState==='visible')void refresh()};
  window.addEventListener('focus',focus);
  window.addEventListener('online',online);
  document.addEventListener('visibilitychange',visible);
  return()=>{controller.abort();window.clearInterval(timer);window.removeEventListener('focus',focus);window.removeEventListener('online',online);document.removeEventListener('visibilitychange',visible)};
 },[sourceKey,base,publicAccess]);
 // A session switch hides the former session's link in the same render, before
 // its effect starts. URL revisions force <img> remounts to drop old QR pixels.
 const shown=visibleQrTarget(target,sourceKey);
 const url=shown?.url||'';
 const revision=shown?.revision||0;
 const failed=shown?.failed||false;
 const imageSrc=url?(publicAccess?`${base}/qr.svg?revision=${revision}`:`${base}/qr?format=svg&revision=${revision}`):'';
 return {url,revision,failed,imageSrc,loading:!!sourceKey&&!url&&!failed};
}
/** QR widget: owner preview and real public view observe the same URL source. */
function ParticipantAccessQr({sessionId,joinCode,publicAccess=false,widget}:{sessionId:string;joinCode?:string;publicAccess?:boolean;widget:any}){
 const {url,revision,failed,imageSrc}=useSynchronizedParticipantQr(sessionId,joinCode,publicAccess);
 return <div className="projection-sample-qr participant-access-qr" style={{'--qr-url-font-size':`${Math.max(10,Math.min(96,Number(widget.qrUrlFontSize)||15))}px`,'--qr-url-extra-width':`${Math.max(0,Number(widget.qrUrlWidthExtra)||0)}px`,'--qr-image-size':Number.isFinite(widget.qrImagePixels)&&widget.qrImagePixels>=16?`${widget.qrImagePixels}px`:'100%'} as React.CSSProperties} data-qr-target="participants" data-qr-show-url={widget.showQrUrl!==false} data-qr-show-title={widget.showTitle===true} aria-label="Accesso dei partecipanti">
  {widget.showTitle===true&&<strong><WidgetStyledText text={widget.label||'Accesso partecipanti'} widget={widget} field="label"/></strong>}
  {url?<><img key={revision} src={imageSrc} alt="Scansiona il QR per accedere come partecipante" loading="lazy"/>{widget.showQrUrl!==false&&<a className="participant-qr-url" href={url} title={url} target="_blank" rel="noopener noreferrer" aria-label="URL di accesso dei partecipanti">{url}</a>}</>:
   <small className="participant-qr-unavailable" role="status">{failed?'Link partecipanti non disponibile':'Caricamento QR partecipanti…'}</small>}
 </div>;
}
function ProjectionWidgetContent({sessionId,widget,activity,peerWidgets=[],joinCode,usePrivateProfile=false,sessionTitle="",pageNumber=1,masterTitleStyle}:{sessionId:string;widget:any;activity:any;peerWidgets?:any[];joinCode?:string;usePrivateProfile?:boolean;sessionTitle?:string;pageNumber?:number;masterTitleStyle?:any}){
 const kind=widget.kind;
 const display=widgetDisplay(widget,{pageTitle:activity?.title,sessionTitle,pageNumber,masterTitleStyle});
 if(kind==='shape'||kind==='line')return null;
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
 if(kind==='rating')return <RatingStageContent widget={widget} readOnly/>;
 if(kind==='reactions')return <div className="projection-sample-reactions">{widget.showTitle!==false&&<strong><WidgetStyledText text={widget.label||'Reazioni'} widget={widget} field="label"/></strong>}<ReactionChoices size={widget.reactionIconSize||32} readOnly/></div>;
 if(kind==='qr')return <ParticipantAccessQr sessionId={sessionId} joinCode={joinCode} widget={widget}/>;
 if(kind==='results-button')return <LinkedResultChart widget={widget} widgets={peerWidgets} rows={linkedStatisticSource(widget,peerWidgets)?sampleStatisticRows(linkedStatisticSource(widget,peerWidgets)!,42):undefined} emptyLabel="simulazione"/>;
 if(kind==='profile'){
  const profileProps={presenterId:widget.presenterId,label:widget.label,description:widget.description,showEmail:widget.showEmail===true,showProfilePhoto:widget.showProfilePhoto,showProfileName:widget.showProfileName,showProfileDescription:widget.showProfileDescription};
  return <div className="projection-sample-profile">{joinCode&&!usePrivateProfile?<PresenterProfileWidget code={joinCode} {...profileProps}/>:<EditorPresenterProfileWidget sessionId={sessionId} {...profileProps}/>}</div>;
 }
 if(kind==='topic-question')return <div className="projection-sample-topic" data-readonly-preview="true"><strong><WidgetStyledText text={widget.label||'Domande del pubblico'} widget={widget} field="label"/></strong><textarea className="widget-free-answer-field" style={answerInputStyle(widget.style)} readOnly disabled tabIndex={-1} aria-label="Casella per la domanda, sola anteprima presentatore" placeholder="Scrivi una domanda…"/><button type="button" className="outline small projection-readonly-submit" disabled tabIndex={-1} style={answerSubmitStyle(widget.style)}>Invia domanda</button></div>;
 const textStyle={fontFamily:explicitWidgetFontFamily(widget.style?.fontFamily),fontSize:undefined,color:widget.style?.color||undefined,fontWeight:widget.style?.bold?'bold':undefined,fontStyle:widget.style?.italic?'italic':undefined,textDecoration:[widget.style?.underline?'underline':'',widget.style?.strikethrough?'line-through':''].filter(Boolean).join(' ')||undefined};
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
 const widgets=activity.page_design?.suppressMaster?(activity.page_design?.widgets||[]):resolveSlideMasterWidgets(activity.page_design?.widgets||[],snapshot.session.theme?.master?.widgets);
 const control=widgets.find((w:any)=>w.kind==='results-button');
 return <>
 <div className="projection-page-content" aria-label="Pagina del presentatore" style={slideBackgroundCss(activity.page_design,snapshot.session.theme,id=>`/api/sessions/${sessionId}/assets/${id}`)}>
 {widgets.map((w:any)=><div key={w.id} className="projection-widget" data-widget-kind={w.kind} data-vertical-align={w.style?.verticalAlign||'top'} data-show-title={widgetTitleVisible(w)} data-footer-separator={w.kind==='footer'?String(w.footerSeparator!==false):undefined} {...widgetArtData(w.style)} style={{...(w.kind==='footer'?{'--footer-divider-color':w.footerSeparatorColor||'#9ca3af'} as React.CSSProperties:{}),...(w.position?widgetGeometryStyle(w.position):{}),...widgetAppearanceStyle(w.style,w.style?.fillImageAssetId?`/api/sessions/${sessionId}/assets/${w.style.fillImageAssetId}`:undefined),...stageWidgetTypography(w,{pageTitle:activity.title,masterTitleStyle:snapshot.session.theme?.master?.titleStyle})}}>{w.kind!=='shape'&&<WidgetShapeOutline style={w.style}/> }<WidgetGraphic kind={w.kind} style={w.style}/>{w.kind==='timer'&&canControlTimer&&<div className="presenter-timer-controls"><button type="button" disabled={restartBusy} onClick={()=>void restart()} title="Riavvia manualmente il countdown e consenti nuove risposte"><Timer size={17}/> Riavvia timer</button>{restartMessage&&<small role="status">{restartMessage}</small>}</div>}<ResultsWidgetErrorBoundary widgetId={w.id}><WidgetContentFit allowScale={w.autoFit!==false&&!['qr','participant-count'].includes(w.kind)} minScale={w.kind==='results-button'?.005:.08}>{w.kind==='results-button'?<PresenterLinkedResult sessionId={sessionId} activity={activity} widget={w} widgets={widgets} activities={snapshot.activities}/>:<ProjectionWidgetContent sessionId={sessionId} widget={w} activity={activity} joinCode={snapshot.session.join_code} sessionTitle={snapshot.session.title} pageNumber={slidePageNumber(snapshot.activities,activity.id)} masterTitleStyle={snapshot.session.theme?.master?.titleStyle}/>}</WidgetContentFit></ResultsWidgetErrorBoundary></div>)}
  <SlideCanvasNumber widgets={widgets} pageNumber={slidePageNumber(snapshot.activities,activity.id)}/>
 </div>
 {<button type="button" className="primary presenter-results-button" onClick={()=>setVisible(v=>!v)} aria-expanded={visible} aria-controls="presenter-page-results">Risultati</button>}
 {visible&&<ResultsWidgetErrorBoundary key={'statistics-'+activity.id} widgetId={'statistics-'+activity.id}><div id="presenter-page-results" role="region" aria-label="Risultati della pagina" className="presenter-page-results" style={activity.result_design?.backgroundAssetId?{backgroundImage:`url(/api/sessions/${sessionId}/assets/${activity.result_design.backgroundAssetId})`,backgroundSize:"cover",backgroundPosition:"center"}:activity.result_design?.backgroundColor?{backgroundColor:activity.result_design.backgroundColor}:undefined}>{renderResults(snapshot,activity,control?effectiveResultView(control,widgets):'bars')}{activity.type==='timed_quiz'&&<TimedLeaderboard sessionId={sessionId} activityId={activity.id}/>}{widgets.filter((w:any)=>w.kind==='timed-quiz').map((w:any)=><WidgetTimedLeaderboard key={w.id} sessionId={sessionId} activityId={activity.id} widget={w}/>)}{widgets.filter((w:any)=>w.kind==='question').flatMap((w:any)=>[<WidgetResults key={w.id} sessionId={sessionId} activityId={activity.id} widget={w}/>,...(w.questions||[]).map((q:any)=><WidgetResults key={w.id+':'+q.id} sessionId={sessionId} activityId={activity.id} questionId={q.id} widget={{...q,id:w.id,resultsView:w.resultsView}}/>)])}{widgets.filter((w:any)=>w.kind==='topic-question').map((w:any)=><TopicPresenterList key={w.id} sessionId={sessionId} activityId={activity.id} widget={w}/>)}</div></ResultsWidgetErrorBoundary>}
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
type PresenterProfileVisibility={showEmail?:boolean;showProfilePhoto?:boolean;showProfileName?:boolean;showProfileDescription?:boolean};
type PresenterProfileProps=PresenterProfileVisibility&{presenterId?:string;label?:string;description?:string};
function PresenterProfileCard({profile,photoUrl,label,description,showEmail,showProfilePhoto,showProfileName,showProfileDescription}:PresenterProfileProps&{profile:any|null;photoUrl?:string}){
 const photo=photoUrl;
 return <div className="page-widget presenter-profile-card" data-widget-kind="profile">
  {!profile?<strong>{label||'Profilo presentatore'}</strong>:<div className="presenter-profile-identity">
   {showProfilePhoto!==false&&photo&&<img src={photo} alt={`Foto di ${profile.name||'presentatore'}`} className="presenter-profile-avatar" loading="lazy"/>}
   <div className="presenter-profile-details">
    {showProfileName!==false&&<strong className="presenter-profile-name">{profile.name||'Presentatore'}</strong>}
    {showEmail===true&&profile.email&&<a className="presenter-profile-email" href={'mailto:'+profile.email}>{profile.email}</a>}
   </div>
  </div>}
  {showProfileDescription!==false&&description?.trim()&&<p className="presenter-profile-custom-text">{description}</p>}
 </div>;
}
function PresenterProfileWidget({code,...settings}:PresenterProfileProps&{code:string}){
 const [profiles,setProfiles]=useState<any[]>([]);
 useEffect(()=>{let active=true;fetch(`/api/join/${encodeURIComponent(code)}/presenter-profiles`).then(r=>r.ok?r.json():[]).then((data:any)=>{if(active)setProfiles(Array.isArray(data)?data:[])}).catch(()=>{if(active)setProfiles([])});return()=>{active=false}},[code]);
 const p=settings.presenterId?profiles.find(p=>p.id===settings.presenterId):profiles[0];
 // Only the public, session-scoped photo URL may reach anonymous projections.
 return <PresenterProfileCard {...settings} profile={p||null} photoUrl={p?p.photo_url:undefined}/>;
}
/** Editor and private rehearsal must use the authenticated session endpoint, even for draft pages. */
function EditorPresenterProfileWidget({sessionId,...settings}:PresenterProfileProps&{sessionId:string}){
 const [profiles,setProfiles]=useState<any[]>([]);
 useEffect(()=>{let active=true;if(!sessionId){setProfiles([]);return}request<any[]>(`/sessions/${encodeURIComponent(sessionId)}/presenter-profiles`).then(data=>{if(active)setProfiles(Array.isArray(data)?data:[])}).catch(()=>{if(active)setProfiles([])});return()=>{active=false}},[sessionId]);
 const chosen=settings.presenterId?profiles.find(p=>p.id===settings.presenterId):profiles.find(p=>p.is_owner)||profiles[0];
 return <PresenterProfileCard {...settings} profile={chosen||null} photoUrl={chosen?.profile_photo_url}/>
}
function QuestionWidget({code,activityId,widget}:{code:string;activityId:string;widget:any}){
 return <div className="widget-question-group" aria-label={widget.label||'Gruppo di domande'}>
  <QuestionWidgetSingle key={widget.id+':primary'} code={code} activityId={activityId} widget={widget} questionId="" marks={widget}/>
  {(widget.questions||[]).map((question:any)=><QuestionWidgetSingle key={widget.id+':'+question.id} code={code} activityId={activityId} widget={{...question,id:widget.id,kind:widget.kind,durationSeconds:widget.durationSeconds,allowAnswerChange:question.allowAnswerChange===true}} questionId={question.id} marks={widget}/>)}
 </div>;
}
function QuestionWidgetSingle({code,activityId,widget,questionId,marks}:{code:string;activityId:string;widget:any;questionId:string;marks:any}){
 const [choice,setChoice]=useState('');const [many,setMany]=useState<string[]>([]);const [body,setBody]=useState('');const [attachment,setAttachment]=useState('');const [status,setStatus]=useState('');const [busy,setBusy]=useState(false),[submitted,setSubmitted]=useState(false);const [feedback,setFeedback]=useState<AnswerFeedback|null>(null);
 useEffect(()=>{setChoice('');setMany([]);setBody('');setAttachment('');setStatus('');setBusy(false);setSubmitted(false);setFeedback(null)},[activityId,widget.id,questionId]);
 const mode=widget.kind==='timed-quiz'?(widget.answerMode==='multiple'?'multiple':'single'):(widget.answerMode||'text');const options=widget.options||[];
 const uploadParticipantFile=async(file:File|undefined)=>{if(!file)return;setStatus('Caricamento...');try{const response=await fetch(`/api/join/${encodeURIComponent(code)}/activities/${encodeURIComponent(activityId)}/widgets/${encodeURIComponent(widget.id)}/upload?question_id=${encodeURIComponent(questionId)}`,{method:'POST',credentials:'include',headers:{'Content-Type':file.type,'X-Quorivio-Filename':encodeURIComponent(file.name)},body:file});const result=await response.json();if(!response.ok)throw Error(result.error||'Upload non riuscito');setAttachment(result.asset_id);setStatus('Allegato caricato, puoi inviare la risposta')}catch(e){setStatus(e instanceof Error?e.message:String(e))}};
 const submit=async()=>{
  if(busy||(submitted&&widget.allowAnswerChange!==true))return;
  setBusy(true);setStatus('Invio in corso…');
  try{
   const payload={...(mode==='single'?{option_id:choice}:mode==='multiple'?{option_ids:many}:mode==='file'?{asset_id:attachment}:{text:body}),question_id:questionId};
   const r=await request<any>(`/join/${encodeURIComponent(code)}/activities/${encodeURIComponent(activityId)}/widgets/${encodeURIComponent(widget.id)}/respond`,'POST',payload);
   setSubmitted(true);setFeedback(r.feedback||null);setStatus(r.already_submitted?'Risposta già registrata':r.changed?'Risposta aggiornata':'Risposta registrata');
  }catch(e){
   const message=e instanceof Error?e.message:String(e);
   setStatus(message.includes('timer_elapsed')?'Tempo scaduto: la risposta non è stata registrata':message);
  }finally{setBusy(false)}
 };
 return <section className="widget-question" aria-label={widget.label||'Domanda aggiuntiva'}><strong><WidgetStyledText text={widget.label||'Domanda'} widget={marks} field={questionId?`question:${questionId}:label`:"label"}/></strong>{widget.description&&<p><WidgetStyledText text={widget.description} widget={marks} field={questionId?`question:${questionId}:description`:'description'}/></p>}{(mode==='single'||mode==='multiple')?options.map((o:any)=>{const verdict=submitted?feedbackOptionVerdict(feedback,o.id):null;return <label className={'widget-answer-option'+truthVerdictClass(verdict)} data-answer-verdict={verdict||undefined} style={answerOptionStyle(marks.style)} key={o.id}><input type={mode==='single'?'radio':'checkbox'} disabled={busy||(submitted&&widget.allowAnswerChange!==true)} name={`widget-${widget.id}-${questionId}`} checked={mode==='single'?choice===o.id:many.includes(o.id)} onChange={()=>{setFeedback(null);mode==='single'?setChoice(o.id):setMany(old=>old.includes(o.id)?old.filter(x=>x!==o.id):[...old,o.id])}}/><WidgetStyledText text={o.label} widget={marks} field={questionId?`question:${questionId}:option:${o.id}`:'option:'+o.id}/>{verdict&&<span className="answer-verdict-icon" aria-label={verdict==='correct'?'Risposta vera':'Risposta falsa'}>{truthVerdictSymbol(verdict)}</span>}</label>}):mode==='text'?<textarea className="widget-free-answer-field" style={answerInputStyle(marks.style)} rows={3} maxLength={5000} disabled={busy||(submitted&&widget.allowAnswerChange!==true)} value={body} onChange={e=>setBody(e.target.value)}/>:<label>Carica un allegato (PNG, JPEG, GIF, WebP, PDF, MP4 o WebM)<input type="file" accept="image/png,image/jpeg,image/gif,image/webp,application/pdf,video/mp4,video/webm" disabled={busy||(submitted&&widget.allowAnswerChange!==true)} onChange={e=>{void uploadParticipantFile(e.target.files?.[0])}}/>{attachment&&<small>Allegato pronto: {attachment}</small>}</label>}<button type="button" className="outline small" style={answerSubmitStyle(marks.style)} onClick={()=>void submit()} disabled={busy||(submitted&&widget.allowAnswerChange!==true)||(mode==='single'&&!choice)||(mode==='multiple'&&many.length===0)||(mode==='text'&&!body.trim())||(mode==='file'&&!attachment)} aria-busy={busy}>Invia risposta</button><ChoiceSubmissionHint part={widget} kind={widget.kind}/><p role="status" aria-live="polite">{status}</p>{submitted&&feedback&&<div className="widget-answer-feedback" role="status" aria-live="polite" data-answer-correct={String(feedback.is_correct)}><strong>{feedback.is_correct?'✓ Risposta corretta!':'✕ Risposta sbagliata.'}</strong></div>}</section>
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
/** Single and side-by-side rehearsals use one logical 1280×720 slide.
 * Scaling the entire slide prevents widget auto-fit and text wrapping from
 * changing simply because another preview pane is opened alongside it. */
function DesktopRehearsalStage({children,immersive=false}:{children:React.ReactNode;immersive?:boolean}){
 const viewport=useRef<HTMLDivElement>(null);
 const [scale,setScale]=useState(1);
 useEffect(()=>{
  const measure=()=>{const width=viewport.current?.clientWidth||1280;const height=immersive?(viewport.current?.clientHeight||720):0;setScale(Math.max(0.1,Math.min(width/1280,immersive?height/720:1)))};
  measure();const observer=new ResizeObserver(measure);
  if(viewport.current)observer.observe(viewport.current);
  return()=>observer.disconnect();
 },[immersive]);
 return <div className={'rehearsal-desktop-viewport'+(immersive?' immersive':'')} ref={viewport}>
  <div className="rehearsal-desktop-sizer" style={{height:720*scale,width:1280*scale}}>
   <div className="rehearsal-desktop-stage" style={{width:1280,height:720,transform:`scale(${scale})`}}>{children}</div>
  </div>
 </div>;
}
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
 const [page,setPage]=useState(()=>rehearsalStartIndex(snapshot.activities,initialPageId));
 const [responses,setResponses]=useState<Record<string,string|string[]>>({});
 const [demoRatingComments,setDemoRatingComments]=useState<Record<string,string>>({});
 // Draft edits never change presenter statistics until an explicit local submit.
 const [submittedAnswers,setSubmittedAnswers]=useState<Record<string,string|string[]>>({});
 // Presenter controls never reflect the participant's draft or submitted choices.
 const [demoResultsVisible,setDemoResultsVisible]=useState(false);
 // Page-scoped local counts: rehearsal is intentionally disconnected from POST APIs.
 const [topicSubmissions,setTopicSubmissions]=useState<Record<string,number>>({});
 const [seed,setSeed]=useState(()=>Math.floor(Math.random()*0x7fffffff));
 const [pageStartedAt,setPageStartedAt]=useState(()=>Date.now());
 const [rehearsalNow,setRehearsalNow]=useState(()=>Date.now());
 const activities=snapshot.activities||[];
 const presenterPages=rehearsalPresenterPages(activities);
 const activity=presenterPages[page] as any;
 const audienceActivity=rehearsalAudiencePage(activity,activities) as any;
 // The presenter walks only visible pages. Participant content always follows
 // that presenter's configured audience page, including hidden question slides.
 // The audience timer must NOT restart when the presenter changes a result page.
 useEffect(()=>{const instant=Date.now();setPageStartedAt(instant);setRehearsalNow(instant);setDemoResultsVisible(false)},[audienceActivity?.id,seed]);
 useEffect(()=>{const timer=window.setInterval(()=>setRehearsalNow(Date.now()),1000);return()=>window.clearInterval(timer)},[]);
 const presenterWidgets=activity?.page_design?.suppressMaster?((activity?.page_design?.widgets||[]) as any[]):resolveSlideMasterWidgets((activity?.page_design?.widgets||[]) as any[],snapshot.session.theme?.master?.widgets);
 const widgets=audienceActivity?.page_design?.suppressMaster?((audienceActivity?.page_design?.widgets||[]) as any[]):resolveSlideMasterWidgets((audienceActivity?.page_design?.widgets||[]) as any[],snapshot.session.theme?.master?.widgets);
 const pageExpired=pageInteractionExpired(widgets,pageStartedAt,rehearsalNow);
 const [fullScreen,setFullScreen]=useState(false);const shellRef=useRef<HTMLDivElement>(null);

 const closeRef=useRef(onClose);closeRef.current=onClose;
 useEffect(()=>{const root=shellRef.current;return root?activateRehearsalDialog(root,()=>closeRef.current()):undefined},[]);
 useEffect(()=>{const handler=()=>setFullScreen(document.fullscreenElement===shellRef.current);document.addEventListener('fullscreenchange',handler);return()=>document.removeEventListener('fullscreenchange',handler)},[]);
 // Studio chrome normally runs at 80% zoom. A native fullscreen canvas must
 // use physical viewport pixels, then restore the user's studio preference.
 useEffect(()=>{if(!fullScreen)return;const root=document.documentElement;const previous=root.style.zoom;root.style.zoom='100%';return()=>{root.style.zoom=previous}},[fullScreen]);
 useEffect(()=>{const key=(event:KeyboardEvent)=>{if(event.defaultPrevented)return;const direction=rehearsalPageDirection(event);if(!direction)return;event.preventDefault();setPage(index=>Math.max(0,Math.min(presenterPages.length-1,index+direction)));};document.addEventListener('keydown',key);return()=>document.removeEventListener('keydown',key)},[presenterPages.length]);
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
    const pageKey=REHEARSAL_REACTION_PREFIX+audienceActivity.id;
    return changeRehearsalReaction(previous,pageKey,widgetId,value);
   }
   return changeRehearsalRating(previous,widgetId,value);
  });
 };
 const submitDemoTopic=(widgetId:string)=>{
  const draft=responses[widgetId];const clean=typeof draft==='string'?draft.trim():'';
  const key=audienceActivity?.id+':'+widgetId;
  if(pageInteractionExpired(widgets,pageStartedAt,Date.now())||clean.length<5||clean.length>2000||(topicSubmissions[key]||0)>=10)return;
  setTopicSubmissions(previous=>(previous[key]||0)>=10?previous:{...previous,[key]:(previous[key]||0)+1});
  setResponses(previous=>({...previous,[widgetId]:''}));
 };
 const renderSlide=(viewer:'presenter'|'participant',mobile=false)=>{
  const viewActivity=viewer==='presenter'?activity:audienceActivity;
  const viewWidgets=viewer==='presenter'?presenterWidgets:widgets;
  const viewPageNumber=slidePageNumber(activities,activity.id);
  return <section className="rehearsal-slide" aria-label={viewer==='presenter'?'Pagina del presentatore':'Pagina del partecipante'} style={mobile&&!viewActivity?.page_design?.importedImageFit?{backgroundImage:viewActivity?.page_design?.mobile?.backgroundAssetId?`url(/api/sessions/${snapshot.session.id}/assets/${viewActivity.page_design.mobile.backgroundAssetId})`:'none',backgroundColor:viewActivity?.page_design?.mobile?.backgroundColor||'#ffffff',backgroundSize:'cover',backgroundPosition:'center'}:slideBackgroundCss(viewActivity?.page_design,snapshot.session.theme,id=>`/api/sessions/${snapshot.session.id}/assets/${id}`)}>
  {!viewWidgets.length&&!viewActivity?.page_design?.importedImageFit&&<h2 className="rehearsal-empty-title">{viewActivity?.page_design?.header||viewActivity?.title}</h2>}
  {pageExpired&&<div className="rehearsal-page-expired" role="status">Tempo scaduto · interazioni della pagina disabilitate</div>}
   <div className="rehearsal-widgets">{(viewer==='presenter'?(mobile?mobilePageWidgets(viewWidgets,viewActivity?.page_design?.mobile):viewWidgets):(mobile?participantPhoneLayout(viewWidgets,viewActivity?.page_design?.mobile).widgets:participantVisibleWidgets(viewWidgets))).map(w=>{
   const answer=viewer==='participant'?responses[w.id]:undefined;const isMulti=w.answerMode==='multiple';
   const style={...{'--stage-x':`${w.position?.x??0}%`,'--stage-y':`${w.position?.y??0}%`,'--stage-width':`${w.position?.width??45}%`,'--stage-height':`${w.position?.height??24}%`},left:`${w.position?.x??0}%`,top:`${w.position?.y??0}%`,width:`${w.position?.width??45}%`,height:`${w.position?.height??24}%`,transform:`rotate(${w.position?.rotation||0}deg)`,...widgetAppearanceStyle(w.style,w.style?.fillImageAssetId?`/api/sessions/${snapshot.session.id}/assets/${w.style.fillImageAssetId}`:undefined),...stageWidgetTypography(w,{pageTitle:viewActivity.title,masterTitleStyle:snapshot.session.theme?.master?.titleStyle},mobile)} as React.CSSProperties;
   const kind=w.kind;
   return <div key={w.id} data-widget-kind={kind} data-vertical-align={w.style?.verticalAlign||'top'} className={'rehearsal-widget rehearsal-'+kind} data-show-title={widgetTitleVisible(w)} data-footer-separator={kind==='footer'?String(w.footerSeparator!==false):undefined} {...widgetArtData(w.style)} style={{...style,...(kind==='footer'?{'--footer-divider-color':w.footerSeparatorColor||'#9ca3af'} as React.CSSProperties:{})}}>{w.kind!=='shape'&&<WidgetShapeOutline style={w.style}/>}<WidgetGraphic kind={w.kind} style={w.style}/><WidgetContentFit allowScale={w.autoFit!==false&&!['qr','participant-count'].includes(kind)} minScale={kind==='results-button'?.005:.08}>
    {kind==='results-button'?(()=>{
      const context=linkedStatisticContext(w,viewActivity,activities,viewWidgets);
      const source=context?.source;
      const sourceWidgets=context?.widgets||[];
      const actual=source?rehearsalFreeTextRows(source,submittedAnswers,w.targetQuestionId||''):[];
      const rows=source?(actual.length?actual:sampleStatisticRows(source,seed,submittedAnswers,w.targetQuestionId||'',{[source.id]:topicSubmissions[context!.activity.id+':'+source.id]||0})):undefined;
      return <LinkedResultChart widget={w} widgets={sourceWidgets} rows={rows} emptyLabel="simulazione"/>;
     })():
    kind==='reactions'&&viewer==='presenter'?<ProjectionWidgetContent sessionId={snapshot.session.id} widget={w} activity={viewActivity} joinCode={snapshot.session.join_code} usePrivateProfile={true} sessionTitle={snapshot.session.title} pageNumber={viewPageNumber} masterTitleStyle={snapshot.session.theme?.master?.titleStyle}/>:kind==='reactions'?<div className="projection-sample-reactions">{w.showTitle!==false&&<strong><WidgetStyledText text={w.label||'Reazioni'} widget={w} field="label"/></strong>}<ReactionChoices size={w.reactionIconSize||32} selected={typeof submittedAnswers[w.id]==='string'?submittedAnswers[w.id] as string:undefined} disabled={pageExpired} onSelect={emoji=>submitDemoDirect(w.id,'reactions',emoji)}/></div>:
    kind==='rating'?<RatingStageContent widget={w} readOnly={viewer==='presenter'} disabled={pageExpired} comment={viewer==='participant'?demoRatingComments[w.id]||'':''} onCommentChange={comment=>setDemoRatingComments(old=>({...old,[w.id]:comment}))} selected={viewer==='participant'&&typeof submittedAnswers[w.id]==='string'?submittedAnswers[w.id] as string:undefined} onSelect={viewer==='participant'?n=>submitDemoDirect(w.id,'rating',String(n)):undefined}/>:
    (kind==='question'||kind==='timed-quiz')?<div className="projection-question-group" aria-label="Domande interattive di prova">
     {[{...w,_questionId:''},...(w.questions||[]).map((q:any)=>({...q,_questionId:q.id}))].map((q:any)=>{
      const questionId=q._questionId as string;const key=questionId?`${w.id}:${questionId}`:w.id;const current=viewer==='participant'?responses[key]:undefined;const sent=viewer==='participant'&&submittedAnswers[key]!==undefined;const multiple=q.answerMode==='multiple';const answerMode=q.answerMode||(kind==='timed-quiz'?'single':'text');const field=(key:string)=>questionId?'question:'+questionId+':'+key:key;const timedSeconds=kind==='timed-quiz'?rehearsalDurationSeconds(w.durationSeconds,viewActivity?.duration_seconds):undefined;const mayChange=q.allowAnswerChange===true;const canInteract=viewer==='participant'&&!pageExpired&&(timedSeconds===undefined||maySubmitTimedRehearsal(pageStartedAt,timedSeconds,rehearsalNow,mayChange?false:sent))&&(!sent||mayChange);const chosen=submittedAnswers[key];const demoFeedback=sent?gradeChoiceAnswer({...q,answerMode},kind,Array.isArray(chosen)?chosen:typeof chosen==='string'?[chosen]:[]):null;
      return <section className="projection-interactive-widget" data-question-id={questionId} key={key}><strong><WidgetStyledText text={q.label||'Domanda'} widget={w} field={field('label')}/></strong>{q.description&&<p><WidgetStyledText text={q.description} widget={w} field={field('description')}/></p>}
       {['single','multiple'].includes(answerMode)?(q.options||[]).map((o:any)=>{const verdict=feedbackOptionVerdict(demoFeedback,o.id);return <label className={'widget-answer-option'+truthVerdictClass(verdict)} data-answer-verdict={verdict||undefined} style={answerOptionStyle(w.style)} key={o.id}><input type={multiple?'checkbox':'radio'} disabled={!canInteract} name={'rehearsal-'+key} checked={Array.isArray(current)?current.includes(o.id):current===o.id} onChange={()=>choose(key,o.id,multiple)}/><WidgetStyledText text={o.label} widget={w} field={field('option:'+o.id)}/>{verdict&&<span className="answer-verdict-icon" aria-label={verdict==='correct'?'Risposta vera':'Risposta falsa'}>{truthVerdictSymbol(verdict)}</span>}</label>}):answerMode==='file'?<label>Allegato di prova (non caricato)<input type="file" accept="image/png,image/jpeg,image/gif,image/webp,application/pdf,video/mp4,video/webm" disabled={!canInteract} onChange={e=>choose(key,e.target.files?.[0]?.name||'')}/></label>:<textarea className="widget-free-answer-field" style={answerInputStyle(w.style)} aria-label={'Risposta simulata '+key} maxLength={5000} disabled={!canInteract} readOnly={viewer==='presenter'} value={typeof current==='string'?current:''} placeholder="Scrivi una risposta di prova" onChange={e=>choose(key,e.target.value)}/>}{<button type="button" className="outline small" disabled={!canInteract||!canSubmitRehearsalAnswer(answerMode,current)} style={answerSubmitStyle(w.style)} onClick={()=>submitDemoAnswer(key,answerMode,timedSeconds)}>{viewer==='presenter'?'Invia risposta':'Invia risposta di prova'}</button>}<ChoiceSubmissionHint part={q} kind={w.kind}/>{sent&&<small role="status" aria-live="polite">{demoFeedback?(demoFeedback.is_correct?'✓ Risposta corretta!':'✕ Risposta sbagliata.'):'Risposta simulata inviata'}{q.allowAnswerChange===true?' · modificabile':''} · nessun dato salvato</small>}{timedSeconds!==undefined&&rehearsalExpired(pageStartedAt,timedSeconds,rehearsalNow)&&!sent&&<small role="status" aria-live="polite">Tempo scaduto: risposta di prova non più inviabile</small>}</section>;
     })}{kind==='timed-quiz'&&<PageTimer openedAt={new Date(pageStartedAt).toISOString()} duration={rehearsalDurationSeconds(w.durationSeconds,viewActivity?.duration_seconds)} label="Tempo rimanente nella prova" face={widgetTimerFace(w.style)}/>}</div>:
    kind==='participant-count'?<div className="projection-participant-count"><strong><WidgetStyledText text={w.label||'Partecipanti connessi'} widget={w} field="label"/></strong><span data-simulated-participants="true">{(seed%37)+12}</span><small>Dati di simulazione</small></div>:
    kind==='timer'?<div className="projection-sample-timer"><strong><WidgetStyledText text={w.label||'Timer'} widget={w} field="label"/></strong><PageTimer openedAt={new Date(pageStartedAt).toISOString()} duration={w.durationSeconds??60} label="Tempo rimanente nella prova" face={widgetTimerFace(w.style)}/></div>:
    kind==='topic-question'&&viewer==='participant'?<div className="projection-sample-topic"><strong><WidgetStyledText text={w.label||'Domande del pubblico'} widget={w} field="label"/></strong><textarea className="widget-free-answer-field" style={answerInputStyle(w.style)} aria-label={'Domanda simulata '+w.id} disabled={pageExpired} maxLength={2000} value={typeof answer==='string'?answer:''} onChange={e=>choose(w.id,e.target.value)}/><button type="button" disabled={pageExpired||typeof answer!=='string'||answer.trim().length<5||(topicSubmissions[viewActivity.id+':'+w.id]||0)>=10} style={answerSubmitStyle(w.style)} onClick={()=>submitDemoTopic(w.id)}>Invia domanda di prova</button><small>{topicSubmissions[viewActivity.id+':'+w.id]||0} / 10 domande simulate inviate, non salvate</small></div>:
    kind==='topic-question'&&viewer==='presenter'?<ProjectionWidgetContent sessionId={snapshot.session.id} widget={w} activity={viewActivity} usePrivateProfile={true} sessionTitle={snapshot.session.title} pageNumber={viewPageNumber} masterTitleStyle={snapshot.session.theme?.master?.titleStyle}/>:
    <ProjectionWidgetContent sessionId={snapshot.session.id} widget={w} activity={viewActivity} joinCode={snapshot.session.join_code} usePrivateProfile={true} sessionTitle={snapshot.session.title} pageNumber={viewPageNumber} masterTitleStyle={snapshot.session.theme?.master?.titleStyle}/>}
</WidgetContentFit>   </div>;
  })}<SlideCanvasNumber widgets={viewWidgets} pageNumber={viewPageNumber}/></div>
 </section>;
 };
 // Render the modal at document.body. When it is nested inside editor/dashboard,
 // an ancestor can become inert or aria-hidden during focus/background isolation,
 // leaving a visually correct dialog invisible to the accessibility tree.
 return createPortal(<div className="rehearsal-backdrop" onClick={e=>{if(e.target===e.currentTarget)onClose()}} role="dialog" aria-modal="true" aria-label="Anteprima interattiva della sessione"><div ref={shellRef} tabIndex={-1} className={'rehearsal-shell rehearsal-mode-'+mode+(fullScreen?' rehearsal-immersive':'')}>
  <header className="rehearsal-toolbar"><strong>ANTEPRIMA · {snapshot.session.title}</strong><span>Nessuna risposta di prova viene salvata</span><div className="rehearsal-mode-switch" role="group" aria-label="Modalità anteprima"><button type="button" aria-pressed={mode==='presenter'} onClick={()=>setMode('presenter')}>Presentatore</button><button type="button" aria-pressed={mode==='participant'} onClick={()=>setMode('participant')}>Partecipante</button><button type="button" aria-pressed={mode==='both'} onClick={()=>setMode('both')}>Affiancate</button><button type="button" aria-pressed={mode==='mobile'} onClick={()=>setMode('mobile')}>Smartphone</button></div>{mode==='both'&&<div className="rehearsal-device-switch" role="group" aria-label="Dispositivo partecipante"><button type="button" aria-pressed={participantDevice==='desktop'} onClick={()=>setParticipantDevice('desktop')}>Desktop</button><button type="button" aria-pressed={participantDevice==='phone'} onClick={()=>setParticipantDevice('phone')}>Smartphone</button></div>}<button type="button" onClick={()=>{void(document.fullscreenElement?document.exitFullscreen():shellRef.current?.requestFullscreen())?.catch(()=>setFullScreen(false))}} aria-pressed={fullScreen} aria-label="Visualizza anteprima a tutto schermo">{fullScreen?'Riduci':'⛶ Tutto schermo'}</button><button type="button" onClick={onClose} aria-label="Chiudi anteprima">× Chiudi</button></header>
  <div className="rehearsal-stage">{activity?<div className="rehearsal-panes">{(mode==='presenter'||mode==='both')&&<div className="rehearsal-pane"><strong className="rehearsal-pane-heading">Presentatore · {activity?.title||'Pagina'} · statistiche simulate</strong><DesktopRehearsalStage immersive={fullScreen}>{renderSlide('presenter')}</DesktopRehearsalStage>{demoResultsVisible&&<section id="rehearsal-simulated-results" className="rehearsal-statistics" aria-label="Statistiche della simulazione">{presenterWidgets.filter(w=>w.kind==='results-button').map(w=>{const context=linkedStatisticContext(w,activity,activities,presenterWidgets);const source=context?.source;const rows=source?rehearsalFreeTextRows(source,submittedAnswers,w.targetQuestionId||''):[];return <LinkedResultChart key={w.id} widget={w} widgets={context?.widgets||[]} rows={source?(rows.length?rows:sampleStatisticRows(source,seed,submittedAnswers,w.targetQuestionId||'',{[source.id]:topicSubmissions[context!.activity.id+':'+source.id]||0})):undefined} emptyLabel="simulazione"/>})}</section>}</div>}{(mode==='participant'||mode==='both'||mode==='mobile')&&<div className={'rehearsal-pane'+(mode==='mobile'||(mode==='both'&&participantDevice==='phone')?' rehearsal-pane-phone':'')}><strong className="rehearsal-pane-heading">Partecipante · {audienceActivity?.title||'Pagina'} · {mode==='mobile'||(mode==='both'&&participantDevice==='phone')?'smartphone':'prova interattiva'}</strong>{mode==='mobile'||(mode==='both'&&participantDevice==='phone')?(participantStaticWidescreenPage(audienceActivity)?<div className="rehearsal-phone-widescreen-frame" aria-label="Pagina statica 16:9 su smartphone"><DesktopRehearsalStage>{renderSlide('participant')}</DesktopRehearsalStage></div>:<PhoneRehearsalStage height={participantPhoneLayout(widgets,audienceActivity?.page_design?.mobile).height}>{renderSlide('participant',true)}</PhoneRehearsalStage>):<DesktopRehearsalStage immersive={fullScreen}>{renderSlide('participant')}</DesktopRehearsalStage>}</div>}</div>:<p>Questa sessione non contiene ancora pagine.</p>}</div>
  {fullScreen&&<div className="rehearsal-fullscreen-controls" role="group" aria-label="Navigazione anteprima a tutto schermo"><button type="button" className="rehearsal-fullscreen-exit" onClick={()=>void document.exitFullscreen().catch(()=>{})} aria-label="Esci da tutto schermo">✕ Esci</button><button type="button" className="rehearsal-fullscreen-prev" disabled={page===0} aria-label="Pagina precedente" onClick={()=>setPage(v=>Math.max(0,v-1))}>‹</button><span className="rehearsal-fullscreen-count" aria-live="polite">{page+1} / {presenterPages.length}</span><button type="button" className="rehearsal-fullscreen-next" disabled={page>=presenterPages.length-1} aria-label="Pagina successiva" onClick={()=>setPage(v=>Math.min(presenterPages.length-1,v+1))}>›</button></div>}
  <footer className="rehearsal-footer"><button type="button" disabled={page===0} onClick={()=>setPage(v=>v-1)}>← Precedente</button><span>{Object.keys(submittedAnswers).filter(key=>!key.startsWith(REHEARSAL_REACTION_PREFIX)).length+Object.values(topicSubmissions).reduce((sum,count)=>sum+count,0)} interazioni simulate · non inviate</span><button type="button" disabled={page>=presenterPages.length-1} onClick={()=>setPage(v=>v+1)}>Successiva →</button><button type="button" onClick={()=>{setResponses({});setSubmittedAnswers({});setTopicSubmissions({});setSeed(Math.floor(Math.random()*0x7fffffff));setPage(0)}}>Ricomincia prova</button></footer>
 </div></div>,document.body);
}

const editorWidgetKinds=['rating','reactions','text','shape','line','timer','qr','profile','question','postit','image','video','logo','pdf','topic-question','timed-quiz','results-button','participant-count','title','footer'] as const;
const editorWidgetNames:Record<string,string>={rating:'Gradimento',reactions:'Reazioni',text:'Testo',divider:'Separatore (legacy)',shape:'Forme',line:'Linee',timer:'Timer',qr:'Codice QR',profile:'Profilo presentatore',question:'Domanda o sondaggio',postit:'Nota adesiva',image:'Immagine',video:'Video',logo:'Logo',pdf:'Documento PDF','topic-question':'Domande sul tema','timed-quiz':'Quiz a tempo','results-button':'Risultati','participant-count':'Partecipanti connessi',title:'Titolo',footer:'Footer'};
/** Compact PowerPoint-like master ribbon: icon, caption, and a complete tooltip. */
function SchemaRibbonButton({label,hint,icon,disabled=false,onClick,primary=false}:{label:string;hint:string;icon:React.ReactNode;disabled?:boolean;onClick:()=>void;primary?:boolean}){
 return <button type="button" className={'slide-scheme-ribbon-tool'+(primary?' primary':'')} title={hint} aria-label={label+': '+hint} disabled={disabled} onClick={onClick}><span className="slide-scheme-ribbon-icon" aria-hidden="true">{icon}</span><span className="slide-scheme-ribbon-caption">{label}</span></button>;
}
const schemaAlignIcons:Partial<Record<ArrangeMode,React.ReactNode>>={left:<AlignLeft size={20}/>, 'center-x':<AlignCenter size={20}/>,right:<AlignRight size={20}/>,top:<MoveVertical size={20}/>, 'center-y':<AlignCenter size={20}/>,bottom:<MoveVertical size={20}/>, 'distribute-x':<MoveHorizontal size={20}/>, 'distribute-y':<MoveVertical size={20}/>};
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
/** Right-click or long-press a palette graphic to insert a precise preset.
 * A simple click still inserts the default. Choices reuse the normal style schema. */
function GraphicInsertTool({kind,onInsert,disabled=false,schema=false}:{kind:GraphicKind;onInsert:(preset?:GraphicPreset,options?:{strokeWidth:number;strokeColor:string;fillColor:string;fillNone:boolean})=>void;disabled?:boolean;schema?:boolean}){
 const [menu,setMenu]=useState<{x:number;y:number}|null>(null);
 const [strokeWidth,setStrokeWidth]=useState(2),[strokeColor,setStrokeColor]=useState('#334155');
 const [fillColor,setFillColor]=useState('#dbeafe'),[fillNone,setFillNone]=useState(false);
 const hold=useRef<ReturnType<typeof setTimeout>|null>(null),suppressClick=useRef(false),button=useRef<HTMLButtonElement>(null);
 const clearHold=()=>{if(hold.current!==null){clearTimeout(hold.current);hold.current=null}};
 const show=(x:number,y:number)=>{clearHold();const width=Math.min(340,window.innerWidth-16),height=Math.min(570,window.innerHeight*.8);setMenu({x:Math.max(8,Math.min(x,window.innerWidth-width-8)),y:Math.max(8,Math.min(y,window.innerHeight-height-8))});};
 useEffect(()=>{if(!menu)return;const key=(e:KeyboardEvent)=>{if(e.key==='Escape')setMenu(null)};const outside=(e:PointerEvent)=>{if(!(e.target as Element)?.closest?.('.graphic-preset-popup')&&!(e.target as Element)?.closest?.('[data-graphic-palette]'))setMenu(null)};document.addEventListener('keydown',key);document.addEventListener('pointerdown',outside);return()=>{document.removeEventListener('keydown',key);document.removeEventListener('pointerdown',outside)}},[menu]);
 useEffect(()=>()=>clearHold(),[]);
 const insert=(preset?:GraphicPreset)=>{suppressClick.current=false;onInsert(preset,{strokeWidth,strokeColor,fillColor,fillNone});setMenu(null)};
 const label=kind==='line'?'Linee':'Forme';
 const trigger=<button ref={button} type="button" className={schema?'slide-scheme-graphic-trigger':'editor-icon-tool'} data-widget-kind={kind} data-graphic-palette={kind} aria-label={'Aggiungi widget: '+label} title={'Clic: inserisci '+label.toLowerCase()+' · tasto destro o pressione lunga: scegli il tipo'} disabled={disabled} draggable={!schema} onDragStart={e=>{if(schema)return;e.dataTransfer.setData('application/x-quorivio-widget',kind);e.dataTransfer.effectAllowed='copy'}} onClick={()=>{if(suppressClick.current){suppressClick.current=false;return}insert()}} onContextMenu={e=>{e.preventDefault();suppressClick.current=false;show(e.clientX,e.clientY)}} onPointerDown={e=>{if(e.pointerType==='mouse')return;clearHold();hold.current=setTimeout(()=>{suppressClick.current=true;show(e.clientX,e.clientY)},560)}} onPointerUp={clearHold} onPointerCancel={clearHold} onPointerLeave={clearHold} onKeyDown={e=>{if(e.key==='ContextMenu'||e.key==='F10'&&e.shiftKey){e.preventDefault();const r=button.current?.getBoundingClientRect();show((r?.left||20)+12,(r?.bottom||30)+5)}}}>{schema?<><EditorWidgetIcon kind={kind}/><span>{label}</span></>:<><EditorWidgetIcon kind={kind}/><span className="editor-icon-caption" aria-hidden="true">{label}</span></>}</button>;
 return <>{schema?trigger:<span className="editor-icon-wrapper editor-graphic-wrapper">{trigger}<button type="button" className="editor-graphic-options" disabled={disabled} aria-label={'Scegli tipo e formato: '+label} title={'Apri il menu per scegliere '+label.toLowerCase()} onClick={e=>{e.preventDefault();e.stopPropagation();const r=button.current?.getBoundingClientRect();show((r?.left||8)+10,(r?.bottom||8)+4)}}>⋯</button></span>}
 {menu&&createPortal(<div className="graphic-preset-popup" role="dialog" aria-label={'Scegli '+label.toLowerCase()+' da inserire'} style={{left:menu.x,top:menu.y}} onContextMenu={e=>e.preventDefault()}>
  <header><strong>Inserisci {label.toLowerCase()}</strong><button type="button" className="outline small" onClick={()=>setMenu(null)} aria-label="Chiudi opzioni grafiche">×</button></header>
  <label>Spessore linea o bordo (pt)<input type="number" min="0" max="12" step="0.5" value={strokeWidth} onChange={e=>setStrokeWidth(Math.max(0,Math.min(12,Number(e.target.value)||0)))}/></label>
  <label>Colore linea o bordo<input type="color" value={strokeColor} onChange={e=>setStrokeColor(e.target.value)}/></label>
  {kind==='shape'&&<><label>Colore riempimento<input type="color" value={fillColor} disabled={fillNone} onChange={e=>setFillColor(e.target.value)}/></label><label><input type="checkbox" checked={fillNone} onChange={e=>setFillNone(e.target.checked)}/> Nessun riempimento</label></>}
  <div className="graphic-preset-choices">{GRAPHIC_PRESETS[kind].map(preset=><button type="button" key={preset.id} onClick={()=>insert(preset)}>{preset.label}</button>)}</div>
 </div>,document.body)}</>;
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
 {widget.kind==='line'&&<>
  <label>Direzione della linea<select aria-label="Direzione della linea" value={style.lineDirection||'horizontal'} onChange={e=>onPatch({lineDirection:e.target.value})}><option value="horizontal">Orizzontale</option><option value="vertical">Verticale</option><option value="diagonal">Diagonale ↘</option><option value="reverse">Diagonale ↙</option></select></label>
  <label>Frecce della linea<select aria-label="Frecce della linea" value={style.lineArrow||'none'} onChange={e=>onPatch({lineArrow:e.target.value})}><option value="none">Senza frecce</option><option value="start">Freccia iniziale</option><option value="end">Freccia finale</option><option value="both">Entrambe le frecce</option></select></label>
 </>}
 {widget.kind==='shape'&&<label>Preset di forma<select aria-label="Preset di forma" value={style.shapeType||'rectangle'} onChange={e=>onPatch({shapeType:e.target.value})}>{GRAPHIC_PRESETS.shape.map(p=><option value={p.id} key={p.id}>{p.label}</option>)}</select></label>}
 <label>Tipo riempimento<select aria-label="Tipo riempimento" value={style.fillMode||'solid'} onChange={e=>onPatch({fillMode:e.target.value,fillNone:false})}><option value="solid">Solido</option><option value="gradient">Gradiente</option><option value="image">Immagine della libreria</option></select></label>
 <label>Trasparenza riempimento (%)<input type="range" aria-label="Trasparenza riempimento" min={0} max={100} value={Math.round((1-(style.fillOpacity??1))*100)} onChange={e=>onPatch({fillOpacity:1-Number(e.target.value)/100})}/><output>{Math.round((1-(style.fillOpacity??1))*100)}%</output></label>
 {style.fillMode==='gradient'&&<label>Secondo colore del gradiente<input type="color" aria-label="Secondo colore del gradiente" value={style.gradientEndColor||'#57a6f8'} onChange={e=>onPatch({gradientEndColor:e.target.value})}/></label>}
 {style.fillMode==='image'&&<p className="muted tiny">Scegli un'immagine privata della sessione dal selettore nel pannello proprietà. Ogni widget può avere la sua immagine.</p>}
 
 </fieldset>;
}

/** Grading is opt-in for ordinary questions. One explicit choice state means every
 * other option is implicitly false; single-choice questions have at most one true. */
function ChoiceTruthEditor({question,kind,onPatch,context=false}:{question:any;kind:string;onPatch:(patch:Record<string,unknown>)=>void;context?:boolean}){
 const mode=question.answerMode||(kind==='timed-quiz'?'single':'text');
 if(!['single','multiple'].includes(mode))return null;
 const enabled=kind==='timed-quiz'||question.answerKeyEnabled===true;
 const options:Array<{id:string;label:string}>=question.options||[];
 const selected=mode==='multiple'?(question.correctOptionIds||[]):question.correctOptionId?[question.correctOptionId]:(question.correctOptionIds||[]);
 return <fieldset className={context?'widget-truth-context':'widget-truth-properties'} aria-label={context?'Risposte vere e false dal menu contestuale':'Risposte vere e false'}>
  <legend>{context?'V/F':'Verifica delle risposte'}</legend>
  {kind!=='timed-quiz'&&<label><input type="checkbox" checked={enabled} aria-label="Attiva valutazione vero o falso" onChange={e=>onPatch(e.target.checked?{answerKeyEnabled:true,correctOptionId:undefined,correctOptionIds:[]}:clearChoiceTruth())}/> {context?'Abilita V/F':"Assegna vero/falso alle opzioni e mostra il risultato dopo l'invio"}</label>}
  {enabled&&<>{!context&&<small>Una volta assegnato uno stato, tutte le opzioni sono false per impostazione predefinita. {mode==='single'?'Può esserci una sola risposta vera.':'Possono esserci più risposte vere.'}</small>}
   {options.map((o,i)=><label key={o.id} title={o.label}>{context?`#${i+1} ${String(o.label||'').slice(0,16)}${String(o.label||'').length>16?'…':''}`:`Risposta ${i+1}: ${o.label}`}
    <select aria-label={'Stato vero falso opzione '+(i+1)} value={selected.includes(o.id)?'true':'false'} onChange={e=>{if(kind==='timed-quiz'&&selected.includes(o.id)&&selected.length===1&&e.target.value==='false')return;onPatch(setChoiceTruth({...question,kind,answerMode:mode},o.id,e.target.value==='true'))}}>{/* The timed scorer requires one or more true choices. */}
     <option value="false">{context?'F':'Falso'}</option><option value="true">{context?'V':'Vero'}</option>
    </select></label>)}
   {kind==='timed-quiz'&&!context&&<small>Il quiz a tempo richiede almeno una risposta vera.</small>}
   {kind!=='timed-quiz'&&<button type="button" className="outline small" onClick={()=>onPatch(clearChoiceTruth())}>{context?'Azzera V/F':'Resetta stati vero/falso'}</button>}
  </>}
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
  <label>Tipo di risposta<select aria-label="Tipo risposta" value={mode} onChange={e=>onPatch({answerMode:e.target.value,options:questionModeOptions(choices,e.target.value),answerKeyEnabled:false,correctOptionId:undefined,correctOptionIds:[]})}><option value="single">Scelta singola</option><option value="multiple">Scelta multipla</option>{!quiz&&<><option value="text">Testo libero</option><option value="file">Allegato</option></>}</select></label>
  <ChoiceTruthEditor question={widget} kind={widget.kind} onPatch={onPatch}/>
  {selectionMode&&<div className="widget-choice-list"><strong>Opzioni di risposta (massimo 12)</strong><p className="widget-choice-caption">Le opzioni vengono mostrate sotto al testo della domanda, nel canvas e ai partecipanti. Il simbolo di scelta è sempre a sinistra della risposta.</p>
   {choices.map((o:any,i:number)=><div className="widget-choice-editor-row" key={o.id}>
     <label className="widget-choice-text">Opzione {i+1}<input aria-label={'Testo opzione '+(i+1)} maxLength={255} value={o.label||''} onChange={e=>onPatch({options:choices.map((c:any)=>c.id===o.id?{...c,label:e.target.value}:c),textMarks:remapMarks(widget.textMarks||[],'option:'+o.id,o.label||'',e.target.value)})}/></label>
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
   <label>Modalità risposta<select aria-label={'Modalità domanda indipendente '+(index+2)} value={q.answerMode||'text'} onChange={e=>update(q.id,{answerMode:e.target.value,options:['single','multiple'].includes(e.target.value)&&(!q.options||q.options.length<2)?[{id:'opt_a',label:'Opzione A'},{id:'opt_b',label:'Opzione B'}]:q.options||[],answerKeyEnabled:false,correctOptionId:undefined,correctOptionIds:[]})}><option value="text">Testo libero</option><option value="single">Scelta singola</option><option value="multiple">Scelta multipla</option>{widget.kind!=='timed-quiz'&&<option value="file">Allegato</option>}</select></label>
   <ChoiceTruthEditor question={q} kind={widget.kind} onPatch={changes=>update(q.id,changes)}/>
   {['single','multiple'].includes(q.answerMode)&&<div className="widget-subquestion-choices">{(q.options||[]).map((o:any,i:number)=><label key={o.id}>Risposta {i+1}<input maxLength={255} aria-label={'Opzione '+(i+1)+' domanda '+(index+2)} value={o.label} onChange={e=>update(q.id,{options:q.options.map((old:any)=>old.id===o.id?{...old,label:e.target.value}:old)})}/><button type="button" disabled={q.options.length<=2} aria-label={'Rimuovi opzione '+(i+1)+' domanda '+(index+2)} onClick={()=>onPatch({questions:questions.map((item:any)=>item.id===q.id?{...item,options:item.options.filter((v:any)=>v.id!==o.id),correctOptionIds:(item.correctOptionIds||[]).filter((id:string)=>id!==o.id),correctOptionId:item.correctOptionId===o.id?undefined:item.correctOptionId}:item),textMarks:(widget.textMarks||[]).filter((mark:TextMark)=>mark.field!==`question:${q.id}:option:${o.id}`)})}>×</button>{widget.kind==='timed-quiz'&&<input type={q.answerMode==='multiple'?'checkbox':'radio'} aria-label={'Corretta opzione '+(i+1)+' domanda '+(index+2)} name={'correct-question-'+q.id} checked={q.answerMode==='multiple'?(q.correctOptionIds||[]).includes(o.id):q.correctOptionId===o.id} onChange={e=>update(q.id,q.answerMode==='multiple'?{correctOptionIds:e.target.checked?[...(q.correctOptionIds||[]).filter((x:string)=>x!==o.id),o.id]:(q.correctOptionIds||[]).filter((x:string)=>x!==o.id)}:{correctOptionId:o.id,correctOptionIds:[o.id]})}/>}</label>)}<button type="button" disabled={(q.options||[]).length>=12} onClick={()=>update(q.id,{options:[...(q.options||[]),{id:'opt_'+crypto.randomUUID().replace(/-/g,'').slice(0,20),label:'Nuova risposta'}]})}>+ Opzione</button></div>}
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
/** Editable font size with explicit, browser-independent step arrows.
 * Keep the temporary string until Enter/blur: clearing "16" to enter "24"
 * must not instantly force the old value back into the controlled input. */
function WidgetFontSizeControl({size,onApply}:{size:number;onApply:(size:number)=>void}){
 const [draft,setDraft]=useState(String(size));
 const focused=useRef(false);
 useEffect(()=>{if(!focused.current)setDraft(String(size))},[size]);
 const valid=(value:string)=>{const parsed=Number(value);return value.trim()!==''&&Number.isInteger(parsed)&&parsed>=10&&parsed<=96?parsed:null};
 const commit=()=>{const next=valid(draft);if(next===null){setDraft(String(size));return}setDraft(String(next));if(next!==size)onApply(next)};
 const step=(delta:number)=>{const next=Math.max(10,Math.min(96,(valid(draft)??size)+delta));setDraft(String(next));onApply(next)};
 return <span className="palette-ribbon-font-size" role="group" aria-label="Dimensione carattere">
  <input type="number" min={10} max={96} step={1} inputMode="numeric" value={draft} title="Dimensione carattere (10–96)" aria-label="Dimensione del testo selezionato" onFocus={e=>{focused.current=true;e.currentTarget.select()}} onBlur={()=>{focused.current=false;commit()}} onChange={e=>{const value=e.currentTarget.value;setDraft(value);const next=valid(value);if(next!==null&&next!==size)onApply(next)}} onKeyDown={e=>{e.stopPropagation();if(e.key==='Enter'){e.preventDefault();e.currentTarget.blur()}else if(e.key==='Escape'){e.preventDefault();setDraft(String(size));e.currentTarget.blur()}}}/>
  <span className="palette-ribbon-font-stepper">
   <button type="button" aria-label="Aumenta dimensione carattere di 1" title="Aumenta di 1" onMouseDown={e=>e.preventDefault()} onClick={()=>step(1)}>▲</button>
   <button type="button" aria-label="Diminuisci dimensione carattere di 1" title="Diminuisci di 1" onMouseDown={e=>e.preventDefault()} onClick={()=>step(-1)}>▼</button>
  </span>
 </span>;
}

function WidgetCanvas({widgets,numberingWidgets,onChange,pageTitle="",sessionTitle="",pageNumber=1,masterTitleStyle,assets=[],backgrounds=[],sessionId="",joinCode,onUpload,assetBusy=false,backgroundAssetId="",importedImageFit,onBackgroundSelect,onBackgroundUpload,onBackgroundColorChange,onRenameLibraryImage,onDeleteLibraryImage,mobileMode=false,mobileHeight=720,mobileBackgroundColor,onBeginGesture,onEndGesture,onAutoFit,onInspectWidget,onSelectionChange,onOpenPageSettings,onRenamePage,onSaveRequested,onContextOpen,pageAudienceId="",onPageAudienceChange,pagePresenterHidden=false,onPagePresenterHiddenChange,pageOptions=[],sourceActivities=[],currentActivityId="",dismissContextMenus=false,suspendFormattingRibbon=false,toolbarCommand,onToolbarClipboardChange}: {widgets:any[];numberingWidgets?:any[];pageTitle?:string;sessionTitle?:string;pageNumber?:number;masterTitleStyle?:any;onChange:(items:any[])=>void;onBeginGesture?:()=>void;onEndGesture?:()=>void;onAutoFit?:(base:any[],fitted:any[])=>void;assets?:any[];backgrounds?:any[];sessionId?:string;joinCode?:string;onUpload?:(widgetId:string,file:File|undefined,kind:string)=>Promise<void>;assetBusy?:boolean;backgroundAssetId?:string;importedImageFit?:'contain'|'cover'|'fill';onBackgroundSelect?:(id:string)=>void;onBackgroundUpload?:(file:File|undefined)=>Promise<boolean>;onRenameLibraryImage?:(id:string)=>Promise<void>;onDeleteLibraryImage?:(id:string)=>Promise<void>;onBackgroundColorChange?:(value:string)=>void;mobileMode?:boolean;mobileHeight?:number;mobileBackgroundColor?:string;onInspectWidget?:(id:string)=>void;onSelectionChange?:(ids:string[])=>void;onOpenPageSettings?:()=>void;onRenamePage?:()=>void;onSaveRequested?:()=>void;onContextOpen?:()=>void;pageAudienceId?:string;onPageAudienceChange?:(id:string)=>void;pagePresenterHidden?:boolean;onPagePresenterHiddenChange?:(value:boolean)=>void;pageOptions?:{id:string;title:string}[];sourceActivities?:Activity[];currentActivityId?:string;dismissContextMenus?:boolean;suspendFormattingRibbon?:boolean;toolbarCommand?:{action:'copy'|'cut'|'paste';token:number};onToolbarClipboardChange?:(available:boolean)=>void}){
 const ref=useRef<HTMLDivElement>(null);
 const contextHold=useRef<ReturnType<typeof setTimeout>|null>(null);
 const widgetHold=useRef<ReturnType<typeof setTimeout>|null>(null);
 const clearWidgetHold=()=>{if(widgetHold.current){clearTimeout(widgetHold.current);widgetHold.current=null}};
 const clearContextHold=()=>{if(contextHold.current!==null){clearTimeout(contextHold.current);contextHold.current=null}};
 const gesture=useRef<{id:string;pointerId:number;mode:'move'|'resize'|'rotate';edge:string;qrBasePixels?:number;startX:number;startY:number;pos:{x:number;y:number;width:number;height:number;rotation?:number};startAngle?:number;groupBase?:any[];groupIds?:string[]}|null>(null);
 const [active,setActive]=useState<string|null>(null);
 const [selectedWidgets,setSelectedWidgets]=useState<string[]>([]);
 const [ribbonDismissed,setRibbonDismissed]=useState(true);
 const [formatTab,setFormatTab]=useState<'text'|'border'|'effects'|'content'|'links'>('text');
 useEffect(()=>{onSelectionChange?.(selectedWidgets)},[selectedWidgets]);
 const toggleSelection=(id:string,extend=false)=>{setRibbonDismissed(true);setFormatScope('widget');setToolbarRange(null);textSelection.current=null;pendingTextStyle.current=null;setEditing(null);setActive(id);setSelectedWidgets(old=>extend?(old.includes(id)?old.filter(x=>x!==id):[...old,id]):[id])};
 const arrangeSelected=(mode:ArrangeMode)=>{const ids=selectedWidgets.length?selectedWidgets:active?[active]:[];onChange(rejectWidgetCollisions(widgets,arrangeWidgets(widgets,ids,mode),ids))};
 const [editing,setEditing]=useState<string|null>(null);
 const textSelection=useRef<{id:string;field:string;start:number;end:number}|null>(null);
 const [toolbarRange,setToolbarRange]=useState<{id:string;field:string;start:number;end:number}|null>(null);
 const [formatScope,setFormatScope]=useState<'widget'|'label'|'description'|'answers'|'submit'|'page-number'>('widget');
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
  const dismissOnViewportChange=(event:Event)=>{if(event.type==='scroll'&&event.target instanceof Element&&event.target.closest('.canvas-context-menu'))return;setContextWidget(null)};
  window.addEventListener('scroll',dismissOnViewportChange,true);
  window.addEventListener('resize',dismissOnViewportChange);
  return()=>{document.removeEventListener('pointerdown',dismiss,true);document.removeEventListener('keydown',onEscape,true);window.removeEventListener('scroll',dismissOnViewportChange,true);window.removeEventListener('resize',dismissOnViewportChange)};
 },[contextWidget]);
 const [backgroundMenu,setBackgroundMenu]=useState(false);const [libraryImageId,setLibraryImageId]=useState('');
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
  setRibbonDismissed(true);setActive(widgetId);onContextOpen?.();
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
 const copySelectedWidget=()=>{const items=clipboardSelection();if(items.length){saveEditorWidgetClipboard(sessionId,items);setClipboardAvailable(true);onToolbarClipboardChange?.(true);pasteCount.current=0}};
 const pasteCopiedWidget=()=>{const source=readEditorWidgetClipboard(sessionId);if(!source.length)return;if(widgets.length+source.length>16){window.alert('Massimo 16 widget per pagina.');return}pasteCount.current++;const result=insertWidgetGroupInFreeSpace(widgets,source,source.map(w=>crypto.randomUUID()),Math.min(5*pasteCount.current,40));if(!result){window.alert('Impossibile incollare i widget: controlla la geometria.');return}onChange(result.widgets);setSelectedWidgets(result.selected);setActive(result.selected[0])};
 const cutSelectedWidget=()=>{const items=clipboardSelection();if(!items.length||!window.confirm(`Tagliare e rimuovere ${items.length} widget?`))return;saveEditorWidgetClipboard(sessionId,items);setClipboardAvailable(true);onToolbarClipboardChange?.(true);pasteCount.current=0;onChange(deleteWidgetSelection(widgets,items.map(w=>w.id)));setSelectedWidgets([]);setActive(null)};
 const processedToolbarCommand=useRef<number|null>(toolbarCommand?.token??null);
 useEffect(()=>{
  if(!toolbarCommand||processedToolbarCommand.current===toolbarCommand.token)return;
  processedToolbarCommand.current=toolbarCommand.token;
  if(toolbarCommand.action==='copy')copySelectedWidget();
  else if(toolbarCommand.action==='cut')cutSelectedWidget();
  else if(toolbarCommand.action==='paste')pasteCopiedWidget();
 },[toolbarCommand]);
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
 // RC326: autoFit is a content-fit preference, NEVER a widget geometry edit.
  // Dragging/resizing the border or editing fonts must not disable it or grow
  // the widget into its neighbours. One proportional transform handles overflow.
  void onAutoFit;
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
  const qrMeasured=w.kind==='qr'&&edge?((e.currentTarget.querySelector('.participant-access-qr>img') as HTMLImageElement|null)?.offsetWidth||undefined):undefined;
  gesture.current={id:w.id,pointerId:e.pointerId,mode:rotate?'rotate':edge?'resize':'move',edge,qrBasePixels:w.kind==='qr'&&edge?(Number(w.qrImagePixels)||qrMeasured||120):undefined,startX:e.clientX,startY:e.clientY,pos:{x:p.x,y:p.y,width:p.width,height:p.height??24,rotation:p.rotation??0},groupIds,groupBase:structuredClone(widgets)};
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
  const resized=resizeWidgetToCollisionLimit(base,g.id,nextPos);
  const original=base.find(w=>w.id===g.id);
  if(original?.kind==='qr'&&g.qrBasePixels){
   const actual=resized.find(w=>w.id===g.id)?.position||nextPos;
   const corner=['nw','ne','sw','se'].includes(g.edge);
   const ratio=corner?Math.min(actual.width/Math.max(.01,g.pos.width),actual.height/Math.max(.01,g.pos.height)):1;
   const pixels=Math.max(16,Math.min(4096,Math.round(g.qrBasePixels*ratio)));
   onChange(resized.map(w=>w.id===g.id?{...w,qrImagePixels:pixels}:w));
  }else onChange(resized);
 }
 function keyboardGeometry(e:React.KeyboardEvent<HTMLDivElement>,w:any){
  if((e.target as HTMLElement).closest('input,textarea,button,select,[contenteditable=true]'))return;
  if(e.key==='Delete'||e.key==='Backspace'){
   e.preventDefault();e.stopPropagation();
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
 <label>Modalità di risposta<select aria-label="Modalità risposta widget" value={selectedQuestion.answerMode||(selectedQuestion.kind==='timed-quiz'?'single':'text')} onChange={e=>patch(selectedQuestion.id,{answerMode:e.target.value,options:questionModeOptions(selectedQuestion.options||[],e.target.value),answerKeyEnabled:false,correctOptionId:undefined,correctOptionIds:[]})}><option value="single">Una scelta</option><option value="multiple">Scelta multipla</option>{selectedQuestion.kind==='question'&&<><option value="text">Testo libero</option><option value="file">File</option></>}</select></label>
 <ChoiceTruthEditor question={selectedQuestion} kind={selectedQuestion.kind} onPatch={changes=>patch(selectedQuestion.id,changes)}/>
 {['single','multiple'].includes(selectedQuestion.answerMode||(selectedQuestion.kind==='timed-quiz'?'single':'text'))&&<div className="widget-answer-options"><strong>Opzioni (massimo 12)</strong>{(selectedQuestion.options||[]).map((option:any,i:number)=><div className="widget-option-row" key={option.id}><input aria-label={'Opzione '+(i+1)} maxLength={255} value={option.label} onChange={e=>patch(selectedQuestion.id,{options:selectedQuestion.options.map((o:any)=>o.id===option.id?{...o,label:e.target.value}:o)})}/>{selectedQuestion.kind==='timed-quiz'&&<label><input type={selectedQuestion.answerMode==='multiple'?'checkbox':'radio'} name={'correct-'+selectedQuestion.id} checked={((selectedQuestion.correctOptionIds?.length?selectedQuestion.correctOptionIds:[selectedQuestion.correctOptionId])).includes(option.id)} onChange={e=>{const current=(selectedQuestion.correctOptionIds?.length?selectedQuestion.correctOptionIds:[selectedQuestion.correctOptionId]).filter(Boolean);const ids=selectedQuestion.answerMode==='multiple'?(e.target.checked?[...new Set([...current,option.id])]:current.filter((id:string)=>id!==option.id)):(e.target.checked?[option.id]:[]);patch(selectedQuestion.id,{correctOptionId:ids[0]||undefined,correctOptionIds:ids})}}/> Corretta</label>}<button type="button" aria-label={'Rimuovi opzione '+(i+1)} onClick={()=>{const options=selectedQuestion.options.filter((o:any)=>o.id!==option.id);patch(selectedQuestion.id,{options,correctOptionIds:(selectedQuestion.correctOptionIds||[]).filter((id:string)=>id!==option.id),correctOptionId:selectedQuestion.correctOptionId===option.id?undefined:selectedQuestion.correctOptionId})}}>×</button></div>)}<button type="button" disabled={(selectedQuestion.options||[]).length>=12} onClick={()=>patch(selectedQuestion.id,{options:[...(selectedQuestion.options||[]),{id:'opt_'+crypto.randomUUID().replace(/-/g,'').slice(0,24),label:'Nuova opzione'}]})}>Aggiungi opzione</button></div>}
 <label>Visualizzazione risultati<select aria-label="Visualizzazione risultati della domanda" value={selectedQuestion.resultsView||'bars'} onChange={e=>patch(selectedQuestion.id,{resultsView:e.target.value})}><option value="bars">Barre</option><option value="pie">Torta</option><option value="table">Tabella</option><option value="cloud">Nuvola animata</option><option value="gauge">Gauge semicircolare</option></select></label>
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
}}>{snapGrid&&<div className="widget-snap-grid" aria-hidden="true"/>}{alignmentGuides.length>0&&<div className="widget-alignment-guides" aria-hidden="true">{alignmentGuides.map(g=><span key={g.axis} className={"widget-alignment-guide axis-"+g.axis} data-guide-source={g.source} style={g.axis==='x'?{left:g.at+'%'}:{top:g.at+'%'}}/>)}</div>}{onBackgroundUpload&&<input ref={backgroundFileRef} style={{display:"none"}} aria-hidden="true" tabIndex={-1} type="file" accept="image/png,image/jpeg,image/gif,image/webp" disabled={assetBusy||backgroundUploading} onChange={e=>{const file=e.currentTarget.files?.[0];e.currentTarget.value="";if(!file)return;setBackgroundMenu(true);setBackgroundUploading(true);setBackgroundUploadStatus('Caricamento dello sfondo e applicazione alla pagina…');void onBackgroundUpload(file).then(applied=>{if(applied){setBackgroundUploadStatus('Sfondo caricato e applicato.');setBackgroundMenu(false)}else setBackgroundUploadStatus('Caricamento annullato: nessuna immagine applicata.')}).catch(error=>{setBackgroundUploadStatus('Caricamento non riuscito: '+(error instanceof Error?error.message:String(error)))}).finally(()=>setBackgroundUploading(false))}}/>} {contextWidget&&!onInspectWidget&&<div className="canvas-context-properties">{questionEditor}{cropEditor}{shapePaintEditor}</div>}<div className="canvas-editor-tools"><label><input type="checkbox" checked={snapGrid} onChange={e=>setSnapGrid(e.target.checked)}/> Aggancia alla griglia (5%)</label><button type="button" className="outline small" disabled={!active} onClick={copySelectedWidget}>Copia selezione</button><button type="button" className="outline small" disabled={!active} onClick={cutSelectedWidget}>Taglia selezione</button><button type="button" className="outline small" disabled={!clipboardAvailable} onClick={pasteCopiedWidget}>Incolla selezione</button><button type="button" className="outline small" disabled={!groupSelection().length} onClick={duplicateSelected}>Duplica selezione</button><button type="button" className="outline small" disabled={!groupSelection().length} onClick={deleteSelected}>Elimina selezione</button><span>Ctrl/Cmd+A seleziona tutti · Maiusc+clic seleziona più widget · trascina la selezione insieme · Ctrl/Cmd+C, X, V, D</span></div><div className="canvas-editor-tools" role="group" aria-label="Allineamento widget selezionati"><strong>{selectedWidgets.length} selezionati</strong>{([['left','Sinistra'],['center-x','Centro orizzontale'],['right','Destra'],['top','Alto'],['center-y','Centro verticale'],['bottom','Basso'],['same-width','Stessa larghezza'],['same-height','Stessa altezza'],['distribute-x','Distribuisci orizzontalmente'],['distribute-y','Distribuisci verticalmente'],['space-x','Spazi orizzontali uguali'],['space-y','Spazi verticali uguali'],['canvas-center-x','Centra selezione nel canvas orizzontalmente'],['canvas-center-y','Centra selezione nel canvas verticalmente'],['canvas-left','Allinea al bordo sinistro della pagina'],['canvas-right','Allinea al bordo destro della pagina'],['canvas-top','Allinea al bordo alto della pagina'],['canvas-bottom','Allinea al bordo basso della pagina']] as [ArrangeMode,string][]).map(([mode,label])=><button key={mode} type="button" className="outline small" disabled={selectedWidgets.length<(mode.startsWith('canvas-')?1:mode.startsWith('distribute')||mode.startsWith('space')?3:2)} onClick={()=>arrangeSelected(mode)}>{label}</button>)}<button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>{setSelectedWidgets([]);setActive(null)}}>Deseleziona</button><div className="canvas-editor-tools" role="group" aria-label="Ordine e spostamento widget selezionati"><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>layerSelected('front')}>Porta selezione davanti</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>layerSelected('back')}>Porta selezione dietro</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>layerSelected('forward')}>Un livello avanti</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>layerSelected('backward')}>Un livello indietro</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>nudgeSelected(-1,0)} aria-label="Sposta selezione a sinistra">←</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>nudgeSelected(1,0)} aria-label="Sposta selezione a destra">→</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>nudgeSelected(0,-1)} aria-label="Sposta selezione in alto">↑</button><button type="button" className="outline small" disabled={!selectedWidgets.length} onClick={()=>nudgeSelected(0,1)} aria-label="Sposta selezione in basso">↓</button></div></div><div className="canvas-with-rulers"><div className="canvas-ruler-horizontal" aria-hidden="true">{Array.from({length:11},(_,i)=><span key={i}>{i*10}</span>)}</div><div className="canvas-ruler-vertical" aria-hidden="true">{Array.from({length:11},(_,i)=><span key={i}>{i*10}</span>)}</div><div className="widget-canvas" ref={ref} role="group" aria-label={mobileMode?"Canvas grafico smartphone":"Canvas grafico widget"} style={{"--editor-page-background":backgroundAssetId&&sessionId?`url(/api/sessions/${sessionId}/assets/${backgroundAssetId})`:"none",'--editor-page-background-size':importedImageFit==='fill'?'100% 100%':importedImageFit||'cover',...(mobileMode?{'--editor-phone-background-color':mobileBackgroundColor||'#ffffff'}:{})} as React.CSSProperties} onClick={e=>{if(e.target===e.currentTarget){setSelectedWidgets([]);setActive(null);setEditing(null);setContextWidget(null)}}} onContextMenuCapture={handleCanvasContext} onPointerDownCapture={e=>{
  contextPointer.current=null;
  if(e.button!==2)return;
  const canvas=e.currentTarget;
  const direct=(e.target as Element).closest('.widget-canvas-item') as HTMLElement|null;
  const widget=direct&&canvas.contains(direct)?direct:canvasWidgetAtPoint(canvas,e.clientX,e.clientY);
  const id=widget?.dataset.widgetId;
  if(id&&widgets.some(w=>w.id===id))contextPointer.current={id,x:e.clientX,y:e.clientY,at:performance.now()};
 }} onPointerDown={e=>{if(e.pointerType!=="mouse"&&!(e.target as HTMLElement).closest("button,input,select,textarea,.widget-canvas-item")){clearContextHold();contextHold.current=setTimeout(openBlankMenu,580)}}} onPointerUp={clearContextHold} onPointerCancel={clearContextHold} onPointerLeave={clearContextHold} onDragOver={e=>{if(e.dataTransfer.types.includes('application/x-quorivio-widget'))e.preventDefault()}} onDrop={e=>{const kind=e.dataTransfer.getData('application/x-quorivio-widget');if(!kind||!['rating','reactions','text','shape','line','timer','qr','profile','question','postit','image','video','logo','pdf','topic-question','timed-quiz','results-button','participant-count','title','footer'].includes(kind))return;e.preventDefault();const b=ref.current?.getBoundingClientRect();const x=b?clamp((e.clientX-b.left)/b.width*100,0,72):0;const y=b?clamp((e.clientY-b.top)/b.height*100,0,76):0;{const position=kind==='footer'?newFooterWidget('new').position:freeWidgetPosition(widgets,{x,y},28,20);if(!position){window.alert('Non c’è spazio disponibile sul canvas per aggiungere questo widget.');return}onChange([...widgets,{...(kind==='footer'?newFooterWidget(crypto.randomUUID()):kind==='title'?newTitleWidget(pageTitle||'Titolo'):{}),id:crypto.randomUUID(),kind,...(kind==='qr'?{showTitle:false,showQrUrl:true}:{}),...(['shape','line'].includes(kind)?{label:kind==='shape'?'Forma':'Linea',style:graphicStyle(kind as GraphicKind)}:kind==='title'||kind==='footer'?{}:{style:initialWidgetTextStyle(kind)}),...(kind==='results-button'&&eligibleStatisticSources(widgets).length?{targetWidgetId:eligibleStatisticSources(widgets)[0].id}:{}),label:['shape','line','footer'].includes(kind)?'':kind==='qr'?'Accesso partecipanti':kind==='question'?'Nuova domanda':kind==='topic-question'?'Domande sul tema':kind,position:{...position,rotation:0}}])}}}>{backgroundMenu&&onBackgroundSelect&&createPortal(<div className="canvas-background-context canvas-background-context-floating" role="group" aria-label="Menu contestuale sfondo canvas" onContextMenu={e=>e.preventDefault()}><strong>Menu della pagina</strong>{onRenamePage&&<button type="button" onClick={()=>{setBackgroundMenu(false);onRenamePage()}}>Rinomina pagina</button>}<button type="button" onMouseDown={e=>e.stopPropagation()} onClick={()=>{setBackgroundMenu(false);setArrangeMenu(true)}}>Strumenti di selezione e allineamento</button><button type="button" title="Configurazione completa della pagina" onClick={()=>{onOpenPageSettings?.();setBackgroundMenu(false)}}>Impostazioni pagina e risultati</button><strong>Proiezioni indipendenti</strong><label>Pagina per i partecipanti<select aria-label="Pagina partecipanti dal menu canvas" value={pageAudienceId} onChange={e=>onPageAudienceChange?.(e.target.value)}><option value="">Questa stessa pagina</option>{pageOptions.map((page,i)=><option key={page.id} value={page.id}>{i+1}. {page.title}</option>)}</select></label><label><input type="checkbox" aria-label="Nascondi al presentatore dal menu canvas" checked={pagePresenterHidden} onChange={e=>onPagePresenterHiddenChange?.(e.target.checked)}/> Salta sullo schermo presentatore</label><strong>{mobileMode?'Sfondo smartphone (indipendente dal desktop)':'Sfondo della pagina'}</strong>{mobileMode&&<label>Colore di sfondo smartphone<input type="color" aria-label="Colore sfondo smartphone" value={mobileBackgroundColor||'#ffffff'} onChange={e=>onBackgroundColorChange?.(e.target.value)}/></label>}<div><strong>Sfondi dei presentatori</strong>{backgroundAssetId&&<small>Immagine applicata a questa pagina</small>}<BackgroundGallery items={backgrounds} disabled={assetBusy} label="Scegli sfondo canvas" onSelect={id=>onBackgroundSelect?.(id)}/></div>{onBackgroundUpload&&<button type="button" disabled={assetBusy||backgroundUploading} onClick={()=>{setBackgroundUploadStatus('');backgroundFileRef.current?.click()}}>Carica immagine nello sfondo e nella libreria…</button>}<details className="canvas-library-manager"><summary>Gestisci immagini della libreria (rinomina / elimina)</summary><div><strong>Immagine da gestire</strong><BackgroundGallery items={backgrounds.filter(a=>a.mine)} selectedId={libraryImageId} label="Immagine da gestire nella libreria" onSelect={setLibraryImageId}/></div><div className="canvas-library-actions"><button type="button" disabled={!libraryImageId||assetBusy} onClick={()=>void onRenameLibraryImage?.(libraryImageId)}>Rinomina immagine</button><button type="button" disabled={!libraryImageId||assetBusy} onClick={()=>{void (async()=>{if(onDeleteLibraryImage){await onDeleteLibraryImage(libraryImageId);setLibraryImageId('')}})()}}>Elimina immagine inutilizzata</button></div><small>Si possono eliminare solo le immagini non utilizzate da pagine, widget, schemi o sfondi.</small></details>{backgroundUploadStatus&&<p className="canvas-background-upload-status" role="status" aria-live="polite">{backgroundUploadStatus}</p>}<button type="button" onClick={()=>{onBackgroundSelect("");setBackgroundMenu(false)}}>Rimuovi sfondo</button><button type="button" onClick={()=>{onSaveRequested?.();setBackgroundMenu(false)}}>Salva ora</button><button type="button" onClick={()=>setBackgroundMenu(false)}>Chiudi menu</button><small>Le modifiche vengono salvate automaticamente.</small></div>,document.body)}{widgets.map((w,i)=>{const pos=w.position||{x:4+(i%4)*24,y:4+Math.floor(i/4)*24,width:22,height:20,rotation:0};return <div key={w.id} className={'widget-canvas-item '+(selectedWidgets.includes(w.id)?'dragging':'')} data-widget-kind={w.kind} data-vertical-align={w.style?.verticalAlign||'top'} data-show-title={widgetTitleVisible(w)} data-footer-separator={w.kind==='footer'?String(w.footerSeparator!==false):undefined} data-widget-id={w.id} {...widgetArtData(w.style)} onFocus={e=>{if(e.target===e.currentTarget)setActive(w.id)}} onClick={e=>{if(e.detail===0&&!(e.target as HTMLElement).closest('button,input,select,textarea'))toggleSelection(w.id,e.shiftKey)}} onContextMenu={e=>{e.preventDefault();e.stopPropagation();openWidgetContextMenu(w.id,e.currentTarget,e.clientX,e.clientY)}} onTouchStart={e=>{if((e.target as HTMLElement).closest("button,input,textarea,select"))return;const widgetElement=e.currentTarget;clearWidgetHold();widgetHold.current=setTimeout(()=>{positionMenu(widgetElement);setActive(w.id);setBackgroundMenu(false);setArrangeMenu(false);onContextOpen?.();setContextWidget(w.id)},600)}} onTouchMove={clearWidgetHold} onTouchEnd={clearWidgetHold} onTouchCancel={clearWidgetHold} style={{...widgetGeometryStyle(pos),...widgetAppearanceStyle(w.style,w.style?.fillImageAssetId&&sessionId?`/api/sessions/${sessionId}/assets/${w.style.fillImageAssetId}`:undefined),...stageWidgetTypography(w,{pageTitle,masterTitleStyle},mobileMode),...(mobileMode?{fontSize:`${widgetTextDefaults(w.kind,w.style)?.fontSize??16}px`,'--mobile-widget-font-size':`${widgetTextDefaults(w.kind,w.style)?.fontSize??16}px`}:{}),...(w.kind==='footer'?{'--footer-divider-color':w.footerSeparatorColor||'#9ca3af'} as React.CSSProperties:{})}} tabIndex={0} role="group" data-selected={selectedWidgets.includes(w.id)} onKeyDown={e=>{if(e.key==='ContextMenu'||(e.shiftKey&&e.key==='F10')){e.preventDefault();positionMenu(e.currentTarget);setContextWidget(w.id);setActive(w.id);onContextOpen?.();return}keyboardGeometry(e,w)}} aria-keyshortcuts="ArrowLeft ArrowRight ArrowUp ArrowDown Shift+ArrowRight Shift+ArrowDown Alt+ArrowRight Alt+ArrowDown Delete Backspace Escape" onPointerDown={e=>{if(!startsWidgetSelectionOnPointerDown(e.button))return;if(e.shiftKey){e.stopPropagation();toggleSelection(w.id,true);return}if(!selectedWidgets.includes(w.id))toggleSelection(w.id);down(e,w)}} onPointerMove={move} onPointerUp={end} onPointerCancel={cancelGesture} onLostPointerCapture={cancelGesture} onDoubleClick={e=>{if((e.target as HTMLElement).closest('[contenteditable=true]'))return;const targetField=(e.target as HTMLElement).closest('[data-widget-text-field]')?.getAttribute('data-widget-text-field')||'label';const root=e.currentTarget;setActive(w.id);setSelectedWidgets([w.id]);setRibbonDismissed(true);setContextWidget(null);setBackgroundMenu(false);setArrangeMenu(false);setEditing(w.id);setFormatScope(targetField.includes('option:')?'answers':targetField.endsWith('description')?'description':'label');requestAnimationFrame(()=>{const field=Array.from(root.querySelectorAll<HTMLElement>('[data-widget-text-field]')).find(node=>node.getAttribute('data-widget-text-field')===targetField)||root.querySelector<HTMLElement>('[contenteditable=true]');field?.focus()})}} aria-label={`Widget ${w.kind}; frecce spostano, Maiusc più frecce ridimensionano, Alt più frecce ruotano, Canc elimina`}>{w.kind!=='shape'&&<WidgetShapeOutline style={w.style}/>}<WidgetGraphic kind={w.kind} style={w.style}/><WidgetContentFit editor textStyle={stageWidgetTypography(w,{pageTitle,masterTitleStyle},mobileMode) as React.CSSProperties} allowScale={w.autoFit!==false&&!['qr','participant-count'].includes(w.kind)&&editing!==w.id} minScale={w.kind==='results-button'?.005:.08}>{(w.kind==='qr'?false:w.showTitle!==false)&&!['line','shape'].includes(w.kind)&&!(w.kind==='results-button'&&(w.resultsOnly===true||editing!==w.id))&&!(w.kind==='rating'&&editing!==w.id)&&<RichWidgetText value={w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).title:w.kind==='footer'?widgetDisplay(w,{sessionTitle,pageNumber}).center:w.label||''} marks={w.textMarks} field="label" active={editing===w.id} ariaLabel={'Titolo '+w.kind} maxLength={240} onSelection={r=>recordTextSelection(w.id,'label',r)} onChange={value=>editContent(w,'label',w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).title:w.kind==='footer'?widgetDisplay(w,{sessionTitle,pageNumber}).center:w.label||'',value,{label:value,...(w.kind==='title'?{titleFollowPage:false}:w.kind==='footer'?{footerShowSessionTitle:false}:{})})} onFinish={()=>setEditing(null)}/>}
 
 {(['question','timed-quiz'].includes(w.kind)&&(editing===w.id||!!w.description)||['text','postit'].includes(w.kind)&&editing===w.id)&&<RichWidgetText value={w.description||''} marks={w.textMarks} field="description" active={editing===w.id} ariaLabel={'Contenuto '+w.kind} maxLength={500} onSelection={r=>recordTextSelection(w.id,'description',r)} onChange={value=>editContent(w,'description',w.description||'',value,{description:value})} onFinish={()=>setEditing(null)}/>}
 {['question','timed-quiz'].includes(w.kind)&&['single','multiple'].includes(w.answerMode||(w.kind==='timed-quiz'?'single':'text'))&&Array.isArray(w.options)&&w.options.length>0&&<div className="canvas-widget-answer-preview" data-answer-mode={w.answerMode||'single'} style={answerOptionStyle(widgetTextDefaults(w.kind,w.style))} aria-label="Opzioni di risposta del widget">{w.options.slice(0,12).map((o:any)=><label className="widget-answer-option" key={o.id||o.label}><input type={w.answerMode==='multiple'?'checkbox':'radio'} name={'editor-option-'+w.id} disabled tabIndex={-1} aria-hidden="true"/><RichWidgetText value={o.label} marks={w.textMarks} field={'option:'+o.id} active={editing===w.id} ariaLabel={'Modifica opzione '+o.label} maxLength={255} onSelection={r=>recordTextSelection(w.id,'option:'+o.id,r)} onChange={value=>editContent(w,'option:'+o.id,o.label,value,{options:w.options.map((item:any)=>item.id===o.id?{...item,label:value}:item)})} onFinish={()=>setEditing(null)}/></label>)}</div>}{['question','timed-quiz'].includes(w.kind)&&(w.questions||[]).map((q:any)=><div className="canvas-subquestion" data-question-id={q.id} key={q.id}>
  <RichWidgetText value={q.label} marks={w.textMarks} field={'question:'+q.id+':label'} active={editing===w.id} ariaLabel={'Domanda indipendente '+q.id} maxLength={240} onSelection={r=>recordTextSelection(w.id,'question:'+q.id+':label',r)} onChange={value=>{const updated=w.questions.map((item:any)=>item.id===q.id?{...item,label:value}:item);editContent(w,'question:'+q.id+':label',q.label,value,{questions:updated})}} onFinish={()=>setEditing(null)}/>
  {(editing===w.id||!!q.description)&&<RichWidgetText value={q.description||''} marks={w.textMarks} field={'question:'+q.id+':description'} active={editing===w.id} ariaLabel={'Descrizione domanda '+q.id} maxLength={500} onSelection={r=>recordTextSelection(w.id,'question:'+q.id+':description',r)} onChange={value=>{const updated=w.questions.map((item:any)=>item.id===q.id?{...item,description:value}:item);editContent(w,'question:'+q.id+':description',q.description||'',value,{questions:updated})}} onFinish={()=>setEditing(null)}/>}
  {['single','multiple'].includes(q.answerMode||'text')?(q.options||[]).map((o:any)=><div key={o.id} className="canvas-subquestion-option" style={answerOptionStyle(widgetTextDefaults(w.kind,w.style))}><input type={(q.answerMode==='multiple'?'checkbox':'radio')} disabled tabIndex={-1} aria-hidden="true"/><RichWidgetText value={o.label} marks={w.textMarks} field={'question:'+q.id+':option:'+o.id} active={editing===w.id} ariaLabel={'Opzione '+q.id+' '+o.id} maxLength={255} onSelection={r=>recordTextSelection(w.id,'question:'+q.id+':option:'+o.id,r)} onChange={value=>{const updated=w.questions.map((item:any)=>item.id===q.id?{...item,options:item.options.map((x:any)=>x.id===o.id?{...x,label:value}:x)}:item);editContent(w,'question:'+q.id+':option:'+o.id,o.label,value,{questions:updated})}} onFinish={()=>setEditing(null)}/></div>):q.answerMode==='file'?<small>Risposta con allegato</small>:<EditorAnswerFieldPreview style={w.style} canvasRef={ref} onBeginGesture={onBeginGesture} onEndGesture={onEndGesture} onHeightChange={height=>patch(w.id,{style:{...w.style,answerFieldHeight:height}})}/>}
 <button type="button" className="canvas-widget-submit-preview" style={answerSubmitStyle(w.style)} disabled aria-label="Anteprima invio risposta della domanda">Invia risposta</button><ChoiceSubmissionHint part={q} kind={w.kind}/></div>)}{w.kind==='profile'&&w.showProfileDescription!==false&&w.description?.trim()&&<RichWidgetText value={w.description} marks={w.textMarks} field="description" active={editing===w.id} ariaLabel="Descrizione presentatore" maxLength={500} onSelection={r=>recordTextSelection(w.id,'description',r)} onChange={value=>editContent(w,'description',w.description||'',value,{description:value})} onFinish={()=>setEditing(null)}/>}{w.kind==='timer'&&<div className="widget-timer-design-preview" data-timer-face={widgetTimerFace(w.style)} role="img" aria-label="Anteprima artistica timer"><span className="widget-timer-design-hourglass" aria-hidden="true">{widgetTimerFace(w.style)==='dial'?'◷':widgetTimerFace(w.style)==='digital'?'▣':'⌛'}</span><span>{Math.floor((w.durationSeconds||60)/60)}:{String((w.durationSeconds||60)%60).padStart(2,'0')}</span></div>}{w.kind==='timed-quiz'&&<div className="canvas-widget-time-preview widget-timer-design-preview" data-timer-face={widgetTimerFace(w.style)} aria-label="Timer anteprima quiz"><span aria-hidden="true">{widgetTimerFace(w.style)==='dial'?'◷':widgetTimerFace(w.style)==='digital'?'▣':'⌛'}</span> {w.durationSeconds||30} secondi</div>}{w.kind==='question'&&(!['single','multiple'].includes(w.answerMode||'text')||!w.options?.length)&&<div className="canvas-widget-answer-preview">{w.answerMode==='file'?<span>Allegato da inviare</span>:w.answerMode==='text'||!w.answerMode?<EditorAnswerFieldPreview style={w.style} canvasRef={ref} onBeginGesture={onBeginGesture} onEndGesture={onEndGesture} onHeightChange={height=>patch(w.id,{style:{...w.style,answerFieldHeight:height}})}/>:'Aggiungi opzioni dalla widget'}</div>}{w.kind==='topic-question'&&<div className="canvas-widget-answer-preview"><EditorAnswerFieldPreview questionField style={w.style} canvasRef={ref} onBeginGesture={onBeginGesture} onEndGesture={onEndGesture} onHeightChange={height=>patch(w.id,{style:{...w.style,answerFieldHeight:height}})}/></div>}{requiresAnswerSubmit(w.kind)&&<button type="button" className="canvas-widget-submit-preview" disabled tabIndex={-1} style={answerSubmitStyle(w.style)} aria-label="Anteprima pulsante invio risposte">{w.kind==='topic-question'?'Invia domanda':'Invia risposta'}</button>}{['question','timed-quiz'].includes(w.kind)&&<ChoiceSubmissionHint part={w} kind={w.kind}/>} {!['question','timed-quiz','topic-question','footer','title','shape','line'].includes(w.kind)&&!(editing===w.id&&['text','postit'].includes(w.kind))&&<div className={w.kind==='results-button'?'canvas-widget-results-native':'canvas-widget-body-preview'} aria-label={'Contenuto di prova '+w.kind}><ProjectionWidgetContent sessionId={sessionId} joinCode={joinCode} usePrivateProfile={w.kind==='profile'} widget={['text','postit'].includes(w.kind)?{...w,label:''}:w.kind==='rating'?{...w,showTitle:editing===w.id?false:w.showTitle}:w.kind==='results-button'&&w.targetActivityId&&w.targetActivityId!==currentActivityId?{...w,showTitle:editing===w.id?false:w.showTitle,showSourceQuestion:w.showSourceQuestion??true}:w.kind==='results-button'?{...w,showTitle:editing===w.id?false:w.showTitle}:w.kind==='reactions'?{...w,showTitle:false}:w.kind==='profile'?{...w,description:undefined}:w} activity={{duration_seconds:w.durationSeconds||60}} peerWidgets={w.kind==='results-button'&&w.targetActivityId&&w.targetActivityId!==currentActivityId?(sourceActivities.find(a=>a.id===w.targetActivityId)?.page_design?.widgets||[]):widgets}/></div>}</WidgetContentFit>{contextWidget===w.id&&createPortal(<div className="canvas-context-menu" style={{left:contextPoint.x,top:contextPoint.y}} role="group" tabIndex={-1} aria-label={'Azioni widget '+w.kind} onWheel={e=>e.stopPropagation()} onTouchMove={e=>e.stopPropagation()} onPointerDown={e=>e.stopPropagation()}><button type="button" onClick={()=>{duplicateWidget(w);setContextWidget(null)}}>Duplica</button><button type="button" onClick={()=>{reorderWidget(w.id,'front');setContextWidget(null)}}>Porta avanti</button><button type="button" onClick={()=>{reorderWidget(w.id,'back');setContextWidget(null)}}>Porta indietro</button><button type="button" title="Configura questo widget" onClick={()=>{onInspectWidget?.(w.id);setContextWidget(null)}}>Proprietà widget</button><button type="button" aria-label="Formato widget" onClick={()=>{setActive(w.id);setSelectedWidgets([w.id]);setFormatScope('widget');setFormatTab('text');setRibbonDismissed(false);setContextWidget(null)}}>Formato</button>{(w.kind==='shape'||w.kind==='line')&&<div className="canvas-context-graphic-options" role="group" aria-label={'Formato '+(w.kind==='line'?'linea':'forma')+' selezionata'}>
 <label>Tipo {w.kind==='line'?'di linea':'di forma'}<select aria-label="Preset grafico del widget selezionato" defaultValue="" onChange={e=>{const preset=GRAPHIC_PRESETS[w.kind as GraphicKind].find(p=>p.id===e.target.value);if(preset)patch(w.id,{style:{...w.style,...graphicStyle(w.kind as GraphicKind,preset,{strokeWidth:w.style?.strokeWidth??2,strokeColor:w.style?.strokeColor||'#334155',fillColor:w.style?.fillColor||'#dbeafe',fillNone:w.style?.fillNone??false})}})}}><option value="">Scegli un preset…</option>{GRAPHIC_PRESETS[w.kind as GraphicKind].map(p=><option value={p.id} key={p.id}>{p.label}</option>)}</select></label>
 <label>Spessore (pt)<input type="number" min="0" max="12" step="0.5" aria-label="Spessore grafico nel menu contestuale" value={w.style?.strokeWidth??2} onChange={e=>{const value=Number(e.target.value);if(Number.isFinite(value)&&value>=0&&value<=12)patch(w.id,{style:{...w.style,strokeWidth:value,strokeNone:false}})}}/></label>
 <label>Colore bordo<input type="color" aria-label="Colore linea o bordo nel menu contestuale" value={w.style?.strokeColor||'#334155'} onChange={e=>patch(w.id,{style:{...w.style,strokeColor:e.target.value}})}/></label>
 {w.kind==='shape'&&<><label>Colore riempimento<input type="color" aria-label="Riempimento forma nel menu contestuale" disabled={w.style?.fillNone===true} value={w.style?.fillColor||'#dbeafe'} onChange={e=>patch(w.id,{style:{...w.style,fillColor:e.target.value}})}/></label><label><input type="checkbox" checked={w.style?.fillNone===true} onChange={e=>patch(w.id,{style:{...w.style,fillNone:e.target.checked}})}/> Senza riempimento</label></>}
 </div>}{['question','timed-quiz'].includes(w.kind)&&<ChoiceTruthEditor context question={w} kind={w.kind} onPatch={changes=>patch(w.id,changes)}/>}{['question','timed-quiz'].includes(w.kind)&&(w.questions||[]).map((q:any)=><ChoiceTruthEditor key={q.id} context question={q} kind={w.kind} onPatch={changes=>patch(w.id,{questions:(w.questions||[]).map((part:any)=>part.id===q.id?{...part,...changes}:part)})}/>)}{w.kind!=='line'&&w.kind!=='shape'&&<button type="button" onClick={()=>{setEditing(w.id);setContextWidget(null)}}>Modifica titolo</button>}{['question','timed-quiz'].includes(w.kind)&&<button type="button" disabled={(w.questions||[]).length>=5} onClick={()=>{patch(w.id,{questions:[...(w.questions||[]),newIndependentQuestion(w.kind)]});setEditing(w.id);setContextWidget(null)}}>Aggiungi domanda indipendente</button>}{['question','timed-quiz'].includes(w.kind)&&<button type="button" disabled={(w.options||[]).length>=12} onClick={()=>{patch(w.id,{answerMode:w.answerMode||'single',options:[...(w.options||[]),{id:'opt_'+crypto.randomUUID().replace(/-/g,'').slice(0,24),label:'Nuova opzione'}]});setEditing(w.id);setContextWidget(null)}}>Aggiungi opzione di risposta</button>}{['image','video','logo','pdf'].includes(w.kind)&&<div className="canvas-context-assets"><label htmlFor={'canvas-asset-'+w.id}>Sostituisci file</label><select id={'canvas-asset-'+w.id} aria-label={'Seleziona asset '+w.kind} value={w.assetId||''} onChange={e=>patch(w.id,{assetId:e.target.value})}><option value="">Nessun file</option>{assets.filter(a=>w.kind==='pdf'?a.mime_type==='application/pdf':w.kind==='video'?a.mime_type.startsWith('video/'):a.mime_type.startsWith('image/')).map(a=><option key={a.id} value={a.id}>{a.display_name||a.mime_type+' · '+a.id.slice(0,8)}</option>)}</select>{onUpload&&<label className="canvas-context-upload">Carica nuovo file<input type="file" aria-label={'Carica file '+w.kind} accept={w.kind==='pdf'?'application/pdf':w.kind==='video'?'video/mp4,video/webm':'image/png,image/jpeg,image/gif,image/webp'} disabled={assetBusy} onChange={e=>{void onUpload(w.id,e.target.files?.[0],w.kind);e.target.value=''}}/></label>}<small>Salva il layout per applicare la modifica.</small></div>}<button type="button" onClick={()=>{if(!window.confirm('Eliminare questo widget dal canvas?'))return;onChange(widgets.filter(z=>z.id!==w.id));setActive(null);setContextWidget(null)}}>Elimina</button></div>,document.body)}<button type="button" className="canvas-remove" aria-label={'Rimuovi widget '+w.kind} title="Rimuovi widget" onClick={()=>{if(!window.confirm('Eliminare questo widget dal canvas?'))return;onChange(widgets.filter(z=>z.id!==w.id));setActive(null)}}>×</button><span className="widget-rotate-handle" data-rotate-handle="true" title="Ruota widget" aria-label="Ruota widget"/>{edges.map(edge=><span key={edge} role="presentation" data-resize-edge={edge} className={'widget-resize-edge edge-'+edge}/>)}</div>})}<SlideCanvasNumber widgets={numberingWidgets??widgets} pageNumber={pageNumber}/></div></div>{active&&!ribbonDismissed&&!suspendFormattingRibbon&&widgets.some(w=>w.id===active)&&<EditorFloatingWindow portal placement="palette" className="widget-selection-palette" role="toolbar" ariaLabel="Formattazione rapida widget selezionato" onMouseDownCapture={e=>{if((e.target as HTMLElement).closest("button"))e.preventDefault()}}>
 {(()=>{const w=widgets.find(z=>z.id===active)!;const style=w.style||{};
 const selectedRange=toolbarRange?.id===w.id&&editing===w.id?toolbarRange:null;
 const effectiveScope=formatScope==='widget'?'widget':selectedRange&&selectedRange.end>selectedRange.start?(selectedRange.field.startsWith('option:')||selectedRange.field.includes(':option:')?'answers':selectedRange.field==='description'||selectedRange.field.includes(':description')?'description':'label'):formatScope;
 const activeTextField=effectiveScope==='widget'?null:selectedRange?selectedRange.field:effectiveScope==='label'?'label':effectiveScope==='description'?'description':null;
 const fieldText=(field:string):string=>{
  if(field==='label')return w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).title:w.kind==='footer'?widgetDisplay(w,{sessionTitle,pageNumber}).center:w.label||'';
  if(field==='description')return w.description||'';
  if(field.startsWith('option:'))return w.options?.find((o:any)=>'option:'+o.id===field)?.label||'';
  if(field.startsWith('question:')){const parts=field.split(':');const q=w.questions?.find((o:any)=>o.id===parts[1]);return parts[2]==='label'?q?.label||'':parts[2]==='description'?q?.description||'':q?.options?.find((o:any)=>o.id===parts[3])?.label||''}
  return '';
 };
 const baseline:InlineStyle=w.kind==='title'?widgetDisplay(w,{pageTitle,masterTitleStyle}).style:(widgetTextDefaults(w.kind,style)||style);
 const questionStyle=widgetTextDefaults(w.kind,style)||style;
 const baselineField=effectiveScope==='answers'?{...baseline,fontFamily:questionStyle.answerFontFamily||questionStyle.fontFamily,fontSize:questionStyle.answerFontSize||questionStyle.fontSize,color:questionStyle.answerColor||questionStyle.color,bold:questionStyle.answerBold??false,italic:questionStyle.answerItalic??questionStyle.italic,underline:questionStyle.answerUnderline??questionStyle.underline,strikethrough:questionStyle.answerStrikethrough??questionStyle.strikethrough}:effectiveScope==='submit'?{...baseline,fontFamily:style.submitFontFamily||style.fontFamily||'Arial',fontSize:style.submitButtonSize||16,color:style.submitColor||style.color||'#142c43',bold:style.submitBold??true,italic:style.submitItalic??false,underline:style.submitUnderline??false,strikethrough:style.submitStrikethrough??false}:effectiveScope==='page-number'?{...baseline,fontFamily:style.footerNumberFontFamily||style.fontFamily||'Arial',fontSize:style.footerNumberFontSize||style.fontSize||14,color:style.footerNumberColor||style.color||'#26364a',bold:style.footerNumberBold??false,italic:style.footerNumberItalic??false,underline:style.footerNumberUnderline??false,strikethrough:style.footerNumberStrikethrough??false}:baseline;
 const selectedValue=<K extends keyof InlineStyle>(key:K):InlineStyle[K]|undefined=>{
  if(selectedRange&&effectiveScope!=='widget'){
   const text=fieldText(selectedRange.field);
   const start=selectedRange.end>selectedRange.start?selectedRange.start:0;
   const end=selectedRange.end>selectedRange.start?selectedRange.end:text.length;
   if(end>start){const effective=selectionUniformValue(text,w.textMarks||[],selectedRange.field,start,end,baselineField,key);if(effective!==undefined)return effective;}
  }
  if(activeTextField){const text=fieldText(activeTextField);if(text.length){const effective=selectionUniformValue(text,w.textMarks||[],activeTextField,0,text.length,baselineField,key);if(effective!==undefined)return effective;}}
  return baselineField[key];
 };
 const selectedFlag=(key:'bold'|'italic'|'underline'|'strikethrough')=>selectedValue(key)===true;
 const selectedFont=selectedValue('fontFamily')||baselineField.fontFamily||'Arial';
 const selectedSize=selectedValue('fontSize')||baselineField.fontSize||16;
 const selectedColor=selectedValue('color')||baselineField.color||'#000000';
 const setStyle=(changes:Record<string,unknown>)=>{
  const typographic=Object.keys(changes).every(k=>(inlineKeys as readonly string[]).includes(k));
  if(typographic&&activeTextField){
   const text=fieldText(activeTextField);
   const range=selectedRange?.field===activeTextField?selectedRange:null;
   const next=formatSelectedOrEntireField(w.textMarks||[],activeTextField,text,range,changes as InlineStyle);
   const freeze=w.kind==='title'&&activeTextField==='label'&&w.titleFollowPage!==false?{label:text,titleFollowPage:false}:w.kind==='footer'&&activeTextField==='label'&&w.footerShowSessionTitle!==false?{label:text,footerShowSessionTitle:false}:{};
   patch(w.id,{...freeze,textMarks:next});
   if(range&&range.end>range.start){
    // React and the toolbar may temporarily own focus while the format change
    // re-renders. Return the original highlighted range after the DOM update.
    requestAnimationFrame(()=>{
     const host=Array.from(document.querySelectorAll<HTMLElement>('[data-widget-id]')).find(el=>el.dataset.widgetId===w.id);
     const text=Array.from(host?.querySelectorAll<HTMLElement>('[data-widget-text-field]')||[]).find(el=>el.dataset.widgetTextField===activeTextField);
     if(!text||!text.isContentEditable)return;
     text.focus({preventScroll:true});restoreDomTextRange(text,range);
    });
   }
   return;
  }
  if(typographic&&(effectiveScope==='submit'||effectiveScope==='page-number')){
   const names:Record<string,string>=effectiveScope==='submit'?{fontFamily:'submitFontFamily',fontSize:'submitButtonSize',color:'submitColor',bold:'submitBold',italic:'submitItalic',underline:'submitUnderline',strikethrough:'submitStrikethrough'}:{fontFamily:'footerNumberFontFamily',fontSize:'footerNumberFontSize',color:'footerNumberColor',bold:'footerNumberBold',italic:'footerNumberItalic',underline:'footerNumberUnderline',strikethrough:'footerNumberStrikethrough'};
   const updated={...style};for(const [key,value] of Object.entries(changes))updated[names[key]||key]=value;
   patch(w.id,{style:updated});return;
  }
  if(effectiveScope==='answers'&&typographic){
   const mapping:Record<string,string>={fontFamily:'answerFontFamily',fontSize:'answerFontSize',color:'answerColor',bold:'answerBold',italic:'answerItalic',underline:'answerUnderline',strikethrough:'answerStrikethrough'};
   const updated={...style};for(const [key,val] of Object.entries(changes))updated[mapping[key]||key]=val;
   const marks=(w.textMarks||[]).map((mark:TextMark)=>mark.field.startsWith('option:')||mark.field.includes(':option:')?{...mark,style:{...mark.style,...changes}}:mark);
   patch(w.id,{style:updated,textMarks:marks});return;
  }
  if(typographic){patch(w.id,applyAllWidgetTypeface(w,changes as InlineStyle));return;}
  patch(w.id,{style:{...style,...changes}});
 };
 const setSize=(next:number)=>{
  if(!Number.isInteger(next)||next<(effectiveScope==='submit'?12:effectiveScope==='page-number'?8:10)||next>(effectiveScope==='submit'?40:96))return;
  if(effectiveScope==='widget')patch(w.id,scaleAllWidgetTypography({...w,style:widgetTextDefaults(w.kind,w.style)},next/(widgetTextDefaults(w.kind,w.style)?.fontSize||16)));
  else setStyle({fontSize:next});
 };
 const formatSourceWidgets=w.targetActivityId?(sourceActivities.find(a=>a.id===w.targetActivityId)?.page_design?.widgets||[]):widgets;
 const formatLinkedSource=w.kind==='results-button'?linkedStatisticSource(w,formatSourceWidgets):undefined;
 const formatChart=w.kind==='results-button'?effectiveResultView(w,formatSourceWidgets):(w.resultsView||(w.kind==='reactions'?'bubbles':'bars'));
 return <>
 <div className="palette-ribbon-head">
  <span className="palette-ribbon-context"><Type size={16} aria-hidden="true"/> Formato widget</span>
  <strong className="palette-widget-label" title={w.label||w.kind}>{w.label||w.kind}</strong>
  <span className="palette-ribbon-selection">{selectedRange&&selectedRange.end>selectedRange.start?`${selectedRange.end-selectedRange.start} caratteri selezionati`:'Seleziona del testo per formattarlo'}</span>
  <button type="button" className="palette-ribbon-dismiss" title="Chiudi finestra Formato widget senza deselezionare" aria-label="Chiudi Formato widget" onClick={()=>setRibbonDismissed(true)}><X size={17}/></button>
 </div>
 <div className="widget-format-tabs" role="tablist" aria-label="Schede Formato widget">
  {([['text','Testo'],['border','Bordi'],['effects','Effetti'],['content','Contenuti'],...(w.kind==='results-button'?[['links','Collegamenti']]:[])] as string[][]).map(([id,title])=><button key={id} type="button" role="tab" aria-selected={formatTab===id} onClick={()=>setFormatTab(id as typeof formatTab)}>{title}</button>)}
 </div>
 <div className="palette-ribbon-groups" role="tabpanel" tabIndex={0} aria-label={'Opzioni '+formatTab} data-format-tab={formatTab}>
  {formatTab==='text'&&<><section className="palette-ribbon-group palette-ribbon-target" aria-label="Ambito formattazione">
   <div className="palette-ribbon-controls">
    <label>Applica a<select aria-label="Ambito della formattazione" value={effectiveScope} onChange={e=>{setFormatScope(e.target.value as 'widget'|'label'|'description'|'answers'|'submit'|'page-number');setEditing(null);textSelection.current=null;setToolbarRange(null)}}>
     <option value="widget">Widget intero</option><option value="label">Titolo</option><option value="description">Descrizione</option>
     {['question','timed-quiz','topic-question'].includes(w.kind)&&<><option value="answers">Risposte</option><option value="submit">Pulsante di invio</option></>}
     {w.kind==='footer'&&<option value="page-number">Numero pagina</option>}
    </select></label>
   </div><span className="palette-ribbon-group-title">Ambito</span>
  </section>
  <section className="palette-ribbon-group palette-ribbon-font" aria-label="Carattere">
   <div className="palette-ribbon-controls">
    <div className="palette-ribbon-font-picker">
     <select title="Tipo di carattere" aria-label="Font del testo" value={selectedFont} onChange={e=>setStyle({fontFamily:e.target.value})}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(font=><option key={font} value={font}>{font}</option>)}</select>
     <WidgetFontSizeControl key={`${w.id}:${effectiveScope}:${activeTextField||''}`} size={selectedSize} onApply={setSize}/>
     {effectiveScope==='widget'&&<div className="palette-ribbon-scale" role="group" aria-label="Scala proporzionale di tutti i testi"><button type="button" aria-label="Riduci tutti i testi del widget del 10%" onClick={()=>patch(w.id,scaleAllWidgetTypography(w,0.9))}>A−</button><button type="button" aria-label="Ingrandisci tutti i testi del widget del 10%" onClick={()=>patch(w.id,scaleAllWidgetTypography(w,1.1))}>A+</button></div>}
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
  </>}
  {formatTab==='border'&&<><section className="palette-ribbon-group palette-ribbon-shape" aria-label="Formato forma">
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
  <section className="palette-ribbon-group" aria-label="Bordi avanzati">
   <div className="palette-ribbon-controls widget-format-advanced">
    <label>Spessore (pt)<EditableNumberField ariaLabel="Spessore bordo widget" min={0} max={12} step={0.5} value={style.strokeWidth??0} onCommit={n=>setStyle({strokeWidth:n,strokeNone:n===0})}/></label>
    <label>Stile bordo<select aria-label="Stile bordo widget" value={style.strokeNone?'none':style.strokeDash||'solid'} onChange={e=>setStyle(e.target.value==='none'?{strokeNone:true,strokeWidth:0}:{strokeNone:false,strokeDash:e.target.value,strokeWidth:style.strokeWidth||1})}><option value="none">Nessuno</option><option value="solid">Continuo</option><option value="dash">Tratteggiato</option><option value="dot">Punteggiato</option></select></label>
    <label>Forma<select aria-label="Forma bordo widget" value={style.shapeType||'rectangle'} onChange={e=>setStyle({shapeType:e.target.value})}>{(['rectangle','rounded-rectangle','ellipse','circle','triangle','diamond','cloud','speech','hexagon','pentagon','star','arrow','heart'] as const).map(shape=><option key={shape} value={shape}>{shape}</option>)}</select></label>
    <label>Colore<input type="color" aria-label="Colore bordo widget" value={style.strokeColor||'#334155'} onChange={e=>setStyle({strokeColor:e.target.value,strokeNone:false,strokeWidth:style.strokeWidth||1})}/></label>
    <label><input type="checkbox" checked={style.fillNone===true} onChange={e=>setStyle({fillNone:e.target.checked})}/> Riempimento trasparente</label>
   </div>
  </section></>}
  {formatTab==='effects'&&<section className="palette-ribbon-group" aria-label="Effetti widget"><div className="palette-ribbon-controls widget-format-advanced">
   <label>Tema<select aria-label="Tema grafico widget" value={style.artTheme||'studio'} onChange={e=>setStyle({artTheme:e.target.value})}><option value="studio">Studio</option><option value="glass">Vetro</option><option value="playful">Vivace</option><option value="minimal">Minimale</option></select></label>
   <label>Effetto<select aria-label="Effetto grafico widget" value={style.artEffect||'none'} onChange={e=>setStyle({artEffect:e.target.value})}><option value="none">Nessuno</option><option value="float">Fluttuante</option><option value="glow">Bagliore</option><option value="tilt">Inclinazione</option></select></label>
   <label>Animazione<select aria-label="Animazione widget" value={style.animation||'none'} onChange={e=>setStyle({animation:e.target.value})}><option value="none">Nessuna</option><option value="fade">Dissolvenza</option><option value="slide">Scorrimento</option></select></label>
   <label>Opacità riempimento <input aria-label="Opacità riempimento widget" type="range" min={0} max={100} value={Math.round((style.fillOpacity??1)*100)} onChange={e=>setStyle({fillOpacity:Number(e.target.value)/100})}/><output>{Math.round((style.fillOpacity??1)*100)}%</output></label>
   <label>Riempimento<select aria-label="Modalità riempimento widget" value={style.fillMode||'solid'} onChange={e=>setStyle({fillMode:e.target.value})}><option value="solid">Tinta unita</option><option value="gradient">Gradiente</option><option value="image">Immagine già associata</option></select></label>
   {style.fillMode==='gradient'&&<label>Secondo colore<input type="color" aria-label="Secondo colore gradiente widget" value={style.gradientEndColor||'#57a6f8'} onChange={e=>setStyle({gradientEndColor:e.target.value})}/></label>}
  </div></section>}
  {formatTab==='text'&&<>{requiresAnswerSubmit(w.kind)&&<section className="palette-ribbon-group palette-ribbon-answer-types" aria-label="Testo delle risposte">
    <div className="palette-ribbon-controls">
            <label className="palette-ribbon-answer" title="Larghezza del campo di risposta libera">Campo % <EditableNumberField ariaLabel="Larghezza risposta libera" min={25} max={100} step={5} value={style.answerFieldWidth||100} onCommit={n=>setStyle({answerFieldWidth:n})}/></label>
        <label className="palette-ribbon-answer" title="Altezza del campo di risposta libera">Campo px <EditableNumberField ariaLabel="Altezza risposta libera" min={48} max={400} step={8} value={style.answerFieldHeight||96} onCommit={n=>setStyle({answerFieldHeight:n})}/></label>
    </div><span className="palette-ribbon-group-title">Risposte</span>
  </section>}
  {w.kind==='results-button'&&<section className="palette-ribbon-group result-format-panel" aria-label="Font, dimensione, colore e stile indipendenti per ogni risposta e risultato"><details className="palette-ribbon-advanced" open><summary>Stile indipendente di titoli, opzioni e risultati</summary><ResultFormatControls source={linkedStatisticSource(w,w.targetActivityId?(sourceActivities.find(a=>a.id===w.targetActivityId)?.page_design?.widgets||[]):widgets)} questionId={w.targetQuestionId||''} styles={w.resultTextStyles} onChange={styles=>patch(w.id,{resultTextStyles:styles})}/></details></section>}
  {w.kind==='results-button'&&<section className="palette-ribbon-group" aria-label="Formato testo domanda statistiche"><div className="palette-ribbon-controls"><label>Colore testo domanda <input aria-label="Colore testo domanda nelle statistiche" type="color" value={style.sourceQuestionColor||'#2563eb'} onChange={e=>patch(w.id,{style:{...style,sourceQuestionColor:e.target.value}})}/></label></div><span className="palette-ribbon-group-title">Domande</span></section>}
  {w.kind==='footer'&&<section className="palette-ribbon-group" aria-label="Formato numero pagina">
    <div className="palette-ribbon-controls"><strong>Numero pagina</strong>
     <label>Destra (px)<EditableNumberField ariaLabel="Padding destro numero pagina" min={0} max={80} value={style.footerNumberPaddingRight??5} onCommit={n=>patch(w.id,{style:{...style,footerNumberPaddingRight:n}})}/></label>
     <label>Sotto (px)<EditableNumberField ariaLabel="Padding inferiore numero pagina" min={0} max={80} value={style.footerNumberPaddingBottom??5} onCommit={n=>patch(w.id,{style:{...style,footerNumberPaddingBottom:n}})}/></label>
    </div><span className="palette-ribbon-group-title">Numero pagina</span></section>}
   {w.kind==='reactions'&&<section className="palette-ribbon-group" aria-label="Dimensione reazioni"><label>Dimensione emoji (px)<EditableNumberField ariaLabel="Dimensione emoji reazioni" min={16} max={96} value={w.reactionIconSize??32} onCommit={n=>patch(w.id,{reactionIconSize:n})}/></label></section>}
   {w.kind==='rating'&&<section className="palette-ribbon-group" aria-label="Dimensione pulsanti gradimento"><label>Dimensione voto (px)<EditableNumberField ariaLabel="Dimensione pulsanti gradimento" min={10} max={64} value={style.ratingButtonSize??16} onCommit={n=>patch(w.id,{style:{...style,ratingButtonSize:n}})}/></label></section>}
  </>}
  {formatTab==='content'&&<section className="palette-ribbon-group" aria-label="Visibilità e contenuti widget"><div className="palette-ribbon-controls widget-format-advanced">
   <label><input type="checkbox" checked={w.kind==='qr'?w.showTitle===true:w.showTitle!==false} onChange={e=>patch(w.id,{showTitle:e.target.checked})}/> {['question','timed-quiz','topic-question'].includes(w.kind)?'Mostra testo della domanda':'Mostra titolo widget'}</label>
   {!['qr','participant-count','shape','line'].includes(w.kind)&&<label className="widget-auto-fit-setting"><input type="checkbox" role="switch" aria-label="Adatta automaticamente il contenuto - Formato widget" checked={w.autoFit!==false} onChange={e=>patch(w.id,{autoFit:e.target.checked})}/> Adatta automaticamente il contenuto alla dimensione del widget</label>}
   {w.kind==='profile'&&<>
    <label><input type="checkbox" aria-label="Mostra foto presentatore" checked={w.showProfilePhoto!==false} onChange={e=>patch(w.id,{showProfilePhoto:e.target.checked})}/> Foto del presentatore (se disponibile)</label>
    <label><input type="checkbox" aria-label="Mostra nome presentatore" checked={w.showProfileName!==false} onChange={e=>patch(w.id,{showProfileName:e.target.checked})}/> Nome del presentatore</label>
    <label><input type="checkbox" aria-label="Mostra email presentatore" checked={w.showEmail===true} onChange={e=>patch(w.id,{showEmail:e.target.checked})}/> Email del presentatore (visibile anche al pubblico)</label>
    <label><input type="checkbox" aria-label="Mostra descrizione presentatore" checked={w.showProfileDescription!==false} onChange={e=>patch(w.id,{showProfileDescription:e.target.checked})}/> Descrizione aggiuntiva</label>
   </>}
   {w.kind==='qr'&&<><label><input type="checkbox" checked={w.showQrUrl!==false} onChange={e=>patch(w.id,{showQrUrl:e.target.checked})}/> Mostra URL accesso (riga singola)</label>{w.showQrUrl!==false&&<label>Dimensione font URL (px)<EditableNumberField ariaLabel="Dimensione font URL QRCode" min={10} max={96} value={w.qrUrlFontSize??15} onCommit={next=>{const old=Math.max(10,Math.min(96,Number(w.qrUrlFontSize)||15));const width=Number(w.position?.width)||25;const x=Number(w.position?.x)||0;const delta=Math.max(0,next-old)*0.9;const growth=Math.max(0,Math.min(delta,100-x-width));patch(w.id,{qrUrlFontSize:next,qrUrlWidthExtra:(Number(w.qrUrlWidthExtra)||0)+growth*12.8,position:{...w.position,width:width+growth}})}}/></label>}</>}
   {['question','timed-quiz','rating','reactions','topic-question','results-button'].includes(w.kind)&&<><label>Tipo di grafico risultati<select aria-label="Tipo grafico risultati - Formato widget" value={formatChart} onChange={e=>patch(w.id,{resultsView:e.target.value})}><option value="bars">Barre</option><option value="pie">Torta</option><option value="table">Tabella</option><option value="cloud">Nuvola</option><option value="gauge">Gauge semicircolare</option>{(w.kind==='reactions'||formatLinkedSource?.kind==='reactions')&&<option value="bubbles">Bolle emoji (reazioni)</option>}</select></label>
   {formatChart==='gauge'&&<div className="gauge-format-controls" role="group" aria-label="Opzioni Gauge"><label>Limite minimo<select aria-label="Modalità minimo Gauge" value={w.gaugeMinMode||'auto'} onChange={e=>patch(w.id,{gaugeMinMode:e.target.value})}><option value="auto">Automatico da dati / sorgente</option><option value="manual">Manuale</option></select></label>{w.gaugeMinMode==='manual'&&<label>Minimo<input type="number" aria-label="Minimo Gauge" step="any" min={-1000000} max={1000000} value={w.gaugeMin??0} onChange={e=>{const n=Number(e.target.value);if(Number.isFinite(n)&&Math.abs(n)<=1000000)patch(w.id,{gaugeMin:n})}}/></label>}<label>Limite massimo<select aria-label="Modalità massimo Gauge" value={w.gaugeMaxMode||'auto'} onChange={e=>patch(w.id,{gaugeMaxMode:e.target.value})}><option value="auto">Automatico da dati / sorgente</option><option value="manual">Manuale</option></select></label>{w.gaugeMaxMode==='manual'&&<label>Massimo<input type="number" aria-label="Massimo Gauge" step="any" min={-1000000} max={1000000} value={w.gaugeMax??9} onChange={e=>{const n=Number(e.target.value);if(Number.isFinite(n)&&Math.abs(n)<=1000000)patch(w.id,{gaugeMax:n})}}/></label>}<label>Aggregazione<select aria-label="Aggregazione Gauge" value={w.gaugeAggregation||'mean'} onChange={e=>patch(w.id,{gaugeAggregation:e.target.value})}><option value="min">Minimo</option><option value="max">Massimo</option><option value="mean">Media ponderata</option></select></label><label><input type="checkbox" checked={w.gaugeShowValue!==false} onChange={e=>patch(w.id,{gaugeShowValue:e.target.checked})}/> Mostra indicatore del valore</label><label><input type="checkbox" checked={w.gaugeTransparent===true} onChange={e=>patch(w.id,{gaugeTransparent:e.target.checked})}/> Sfondo trasparente Gauge (predefinito bianco)</label><label>Colore Gauge<input type="color" aria-label="Colore Gauge" value={w.gaugeColor||'#000000'} onChange={e=>patch(w.id,{gaugeColor:e.target.value})}/></label><label><input type="checkbox" checked={w.gaugeGradient!==false} onChange={e=>patch(w.id,{gaugeGradient:e.target.checked})}/> Gradiente minimo/massimo</label>{w.gaugeGradient!==false&&<><label>Colore minimo<input type="color" aria-label="Colore minimo Gauge" value={w.gaugeMinColor||'#d44949'} onChange={e=>patch(w.id,{gaugeMinColor:e.target.value})}/></label><label>Colore massimo<input type="color" aria-label="Colore massimo Gauge" value={w.gaugeMaxColor||'#22ad80'} onChange={e=>patch(w.id,{gaugeMaxColor:e.target.value})}/></label></>}</div>}</>}
   {formatChart==='bubbles'&&<label><input type="checkbox" checked={w.bubbleNoScroll!==false} onChange={e=>patch(w.id,{bubbleNoScroll:e.target.checked})}/> Adatta le bolle al riquadro senza scorrimento (predefinito)</label>}
   {w.kind==='results-button'&&<>
    {formatChart==='pie'&&<><label><input type="checkbox" checked={w.pieShowOptionNumbers===true} onChange={e=>patch(w.id,{pieShowOptionNumbers:e.target.checked})}/> Torta: numera le opzioni nella torta e nella legenda</label><label><input type="checkbox" checked={w.pieShowPercentages===true} onChange={e=>patch(w.id,{pieShowPercentages:e.target.checked})}/> Torta: visualizza percentuale per fetta</label><label className="results-pie-size-control">Dimensione torta <input type="range" aria-label="Dimensione torta risultati" min={25} max={150} step={5} value={resultPieSize(w.pieSize)} onChange={e=>patch(w.id,{pieSize:Number(e.target.value)})}/><output>{resultPieSize(w.pieSize)}%</output></label></>}
    {['bars','pie','table','cloud','bubbles'].includes(formatChart)&&<label>Ordinamento risultati<select aria-label="Ordinamento risultati - Formato widget" value={w.resultSortOrder||'index-asc'} onChange={e=>patch(w.id,{resultSortOrder:e.target.value})}><option value="index-asc">Ordine originale</option><option value="index-desc">Ordine originale inverso</option><option value="count-desc">Più risposte prima</option><option value="count-asc">Meno risposte prima</option></select></label>}
    {['bars','table','cloud','bubbles'].includes(formatChart)&&<label>Numero risultati principali da mostrare <EditableNumberField ariaLabel="Numero risultati principali - Formato widget" min={1} max={20} value={w.resultTopCount??5} onCommit={n=>patch(w.id,{resultTopCount:n})}/></label>}
    {formatChart==='bars'&&<><label><input type="checkbox" checked={w.barHitGradient===true} onChange={e=>patch(w.id,{barHitGradient:e.target.checked})}/> Barre: gradiente proporzionale al numero di risposte</label>{w.barHitGradient===true&&<span className="results-gradient-colors" role="group" aria-label="Colori del gradiente delle barre risultati"><label>Colore iniziale <input type="color" aria-label="Colore iniziale gradiente barre" value={w.barGradientStartColor||'#cbd5e1'} onChange={e=>patch(w.id,{barGradientStartColor:e.target.value})}/></label><label>Colore finale <input type="color" aria-label="Colore finale gradiente barre" value={w.barGradientEndColor||'#1a9e8b'} onChange={e=>patch(w.id,{barGradientEndColor:e.target.value})}/></label></span>}</>}
    <label><input type="checkbox" checked={w.resultsOnly===true} onChange={e=>patch(w.id,{resultsOnly:e.target.checked})}/> Solo risultati</label><label><input type="checkbox" checked={w.showSourceTitle??w.showSourceQuestion===true} onChange={e=>patch(w.id,{showSourceTitle:e.target.checked,showSourceAnswers:w.showSourceAnswers??w.showSourceQuestion===true,resultsOnly:e.target.checked?false:w.resultsOnly})}/> Riporta titolo sorgente</label><label><input type="checkbox" checked={w.showSourceAnswers??w.showSourceQuestion===true} onChange={e=>patch(w.id,{showSourceAnswers:e.target.checked,showSourceTitle:w.showSourceTitle??w.showSourceQuestion===true,resultsOnly:e.target.checked?false:w.resultsOnly})}/> Riporta opzioni sorgente</label>
   </>}
   {w.kind==='footer'&&<><label><input type="checkbox" checked={w.footerShowSessionTitle!==false} onChange={e=>patch(w.id,{footerShowSessionTitle:e.target.checked})}/> Testo della sessione</label><label><input type="checkbox" checked={w.footerShowPageNumber!==false} onChange={e=>patch(w.id,{footerShowPageNumber:e.target.checked})}/> Numero pagina</label><label><input type="checkbox" checked={w.footerSeparator!==false} onChange={e=>patch(w.id,{footerSeparator:e.target.checked})}/> Linea separatrice</label></>}
  </div></section>}
  {formatTab==='links'&&w.kind==='results-button'&&<section className="palette-ribbon-group" aria-label="Collegamenti widget risultati"><div className="palette-ribbon-controls widget-format-advanced">
   <label>Pagina sorgente<select aria-label="Pagina collegata ai risultati" value={w.targetActivityId||''} onChange={e=>patch(w.id,{targetActivityId:e.target.value||undefined,targetWidgetId:undefined,targetQuestionId:undefined})}><option value="">Pagina corrente</option>{sourceActivities.filter(a=>a.id!==currentActivityId).map(a=><option key={a.id} value={a.id}>{a.title}</option>)}</select></label>
   <label>Widget sorgente<select aria-label="Widget collegato ai risultati" value={w.targetWidgetId||''} onChange={e=>patch(w.id,{targetWidgetId:e.target.value||undefined,targetQuestionId:undefined})}><option value="">Seleziona widget</option>{eligibleStatisticSources(w.targetActivityId?(sourceActivities.find(a=>a.id===w.targetActivityId)?.page_design?.widgets||[]):widgets,w.id).map(source=><option key={source.id} value={source.id}>{source.label||source.kind}</option>)}</select></label>
   {(()=>{const source=(w.targetActivityId?(sourceActivities.find(a=>a.id===w.targetActivityId)?.page_design?.widgets||[]):widgets).find((z:any)=>z.id===w.targetWidgetId);return source?.questions?.length?<label>Domanda sorgente<select aria-label="Domanda collegata ai risultati" value={w.targetQuestionId||''} onChange={e=>patch(w.id,{targetQuestionId:e.target.value||undefined})}><option value="">Domanda principale</option>{source.questions.map((q:any)=><option key={q.id} value={q.id}>{q.label}</option>)}</select></label>:null})()}
  </div></section>}
  {formatTab==='content'&&['question','timed-quiz'].includes(w.kind)&&<section className="palette-ribbon-group palette-ribbon-truth" aria-label="Formato widget: risposte vere e false"><ChoiceTruthEditor question={w} kind={w.kind} onPatch={changes=>patch(w.id,changes)}/>{(w.questions||[]).map((q:any)=><ChoiceTruthEditor key={q.id} question={q} kind={w.kind} onPatch={changes=>patch(w.id,{questions:(w.questions||[]).map((part:any)=>part.id===q.id?{...part,...changes}:part)})}/>)}</section>}
  {formatTab==='content'&&<section className="palette-ribbon-group palette-ribbon-arrange" aria-label="Disponi">
   <div className="palette-ribbon-controls">
    <div className="palette-ribbon-buttons" role="group" aria-label="Posizione sul canvas">
     <button type="button" title="Centra il widget orizzontalmente" aria-label="Centra widget nel canvas" onClick={()=>arrangeSelected('canvas-center-x')}><MoveHorizontal size={18}/></button>
     <button type="button" title="Centra il widget verticalmente" aria-label="Centra widget in verticale" onClick={()=>arrangeSelected('canvas-center-y')}><MoveVertical size={18}/></button>
     <button type="button" title="Apri tutte le proprietà" aria-label="Mostra proprietà complete del widget" onClick={()=>onInspectWidget?.(w.id)}><SlidersHorizontal size={18}/></button>
    </div>
    {w.kind==='rating'&&<button type="button" className="palette-ribbon-rating" title="Visualizzazione gradimento" aria-label="Cambia visualizzazione gradimento" onClick={()=>setStyle({ratingView:style.ratingView==='select'?'buttons':'select'})}>0–9 ▾</button>}
   </div>
   <span className="palette-ribbon-group-title">Disponi</span>
  </section>}
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
 // Invalid or audience-only live payloads must never replace the last valid presenter projection.
 useLive(sessionId,s=>{if(isOwnerSessionSnapshot(s,sessionId))setData(normalizeOwnerSessionSnapshot(s))},setConnection);
 const [busy,setBusy]=useState(false);
 const [full,setFull]=useState(false);
 const [mobileControls,setMobileControls]=useState(()=>window.matchMedia('(hover: none), (pointer: coarse)').matches);
 const stageRef=useRef<HTMLElement|null>(null);
 const pending=useRef(false);
 const activities=presenterVisiblePages(data?.activities||[]);
 const currentId=data?.session?.presenter_activity_id||data?.session?.current_activity_id;
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
    if(!isOwnerSessionSnapshot(s,sessionId))throw Error('invalid_presenter_snapshot');
    setVerified(true);setData(normalizeOwnerSessionSnapshot(s));
    if(['active','ready'].includes(s.session.status)&&!s.session.current_activity_id&&s.activities.length){
     await request(`/sessions/${encodeURIComponent(sessionId)}/presentation/ensure-first-page`,'POST');
     const fresh=await request<Snapshot>(`/sessions/${encodeURIComponent(sessionId)}`);
     if(mounted&&isOwnerSessionSnapshot(fresh,sessionId))setData(normalizeOwnerSessionSnapshot(fresh));
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
  const target=presenterAdjacentPage(presenterVisiblePages(data.activities),data.session.presenter_activity_id||data.session.current_activity_id,direction);
  if(!target)return;
  pending.current=true;setBusy(true);setScreenError('');
  try{
   await request(`/sessions/${encodeURIComponent(sessionId)}/activities/${encodeURIComponent(target.id)}/open`,'POST',{expected_current_activity_id:data.session.current_activity_id,expected_presenter_activity_id:data.session.presenter_activity_id||data.session.current_activity_id});
   const refreshed=await request<Snapshot>(`/sessions/${encodeURIComponent(sessionId)}`);
   if(isOwnerSessionSnapshot(refreshed,sessionId))setData(normalizeOwnerSessionSnapshot(refreshed));
   else setScreenError('La pagina partecipanti ha restituito uno snapshot non valido. La pagina presentatore resta disponibile.');
  }catch(e){setScreenError(e instanceof Error?e.message:String(e));
   try{const recovered=await request<Snapshot>(`/sessions/${encodeURIComponent(sessionId)}`);if(isOwnerSessionSnapshot(recovered,sessionId))setData(normalizeOwnerSessionSnapshot(recovered))}catch{}
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
     <ResultsWidgetErrorBoundary key={'page-'+current.id} widgetId={'page-'+current.id}>
      {!current.page_design?.importedImageFit&&!resolveSlideMasterWidgets(current.page_design?.widgets||[],data.session.theme?.master?.widgets).some((w:any)=>w.kind==='title')&&<h2>{current.title}</h2>}
      {current.type==='timed_quiz'&&<PageTimer openedAt={current.opened_at} duration={current.duration_seconds} label="Quiz a tempo"/>}
      <PresenterPageResults sessionId={sessionId} activity={current} snapshot={data} renderResults={renderResults}/>
     </ResultsWidgetErrorBoundary>
    </section>:<section className="panel centered"><h2>In attesa di una pagina</h2><p>Nessuna pagina disponibile per la proiezione.</p></section>}
   {active&&current&&<nav className="presenter-slide-navigation" aria-label="Navigazione pagine del presentatore">
    <div className="presenter-nav-zone previous"><button type="button" className="presenter-nav-arrow" disabled={!previous||busy} aria-label="Pagina precedente" title="Precedente (←)" onClick={()=>void changePage(-1)}>‹</button></div>
    <div className="presenter-nav-zone next"><button type="button" className="presenter-nav-arrow" disabled={!next||busy} aria-label="Pagina successiva" title="Successiva (→)" onClick={()=>void changePage(1)}>›</button></div>
   </nav>}
  </>}
  {screenError&&!verified&&<div role="alert" className="panel">Accesso non autorizzato o schermo non disponibile: {screenError}</div>}
 </main>;
}

/** Lightweight, read-only miniature of authored widget content.
 * Uses the actual current draft and the persisted layout geometry; never
 * issues live requests or manufactures response counts. */
function ThumbnailWidgetContent({widget:w,assetUrl}:{widget:any;assetUrl?:string}){
 const model=thumbnailWidgetModel(w);
 if(model.type==='media')return assetUrl&&model.isImage?<img className="page-editor-preview-real-image" src={assetUrl} alt="" loading="lazy"/>:<span className="thumb-media-label">{model.label}</span>;
 if(model.type==='line')return <span className="thumb-line" style={{borderColor:w.style?.strokeColor||'#334155',borderTopStyle:w.style?.strokeDash==='dash'?'dashed':'solid',transform:`rotate(${Number(w.style?.rotation)||0}deg)`}}/>;
 if(model.type==='shape')return <WidgetShapeOutline style={w.style}/>;
 if(model.type==='choice')return <span className="thumb-content thumb-choice"><strong>{model.label}</strong>{model.options.map((value,i)=><span className="thumb-option" key={i}><i aria-hidden="true">{model.multi?'☐':'○'}</i><span>{value}</span></span>)}</span>;
 if(model.type==='chart')return <span className="thumb-content thumb-chart"><strong>{model.label}</strong><span className="thumb-chart-bars" aria-label="Riquadri grafico segnaposto, non risultati reali"><i/><i/><i/></span></span>;
 if(model.type==='timer')return <span className="thumb-content thumb-timer"><strong>{model.label}</strong><b>{model.timer}</b></span>;
 if(model.type==='rating')return <span className="thumb-content thumb-rating"><strong>{model.label}</strong><span>☆☆☆☆☆</span></span>;
 if(model.type==='reaction')return <span className="thumb-content thumb-reaction"><strong>{model.label}</strong><span>👍 ❤️ 😄</span></span>;
 if(model.type==='qr')return <span className="thumb-content thumb-qr"><span aria-hidden="true">▦</span><small>{model.label}</small></span>;
 return <span className={'thumb-content thumb-'+model.type}>{model.label}{model.description&&<small>{model.description}</small>}</span>;
}

/** Visual picker: thumbnails plus actual filenames, with scrollable keyboard-accessible choices. */
function BackgroundGallery({items,onSelect,disabled=false,selectedId='',label='Immagini della libreria'}:{items:any[];onSelect:(id:string)=>void;disabled?:boolean;selectedId?:string;label?:string}){
 return <div className="background-gallery" role="group" aria-label={label}>
 {items.length===0&&<p className="muted tiny">Nessuna immagine disponibile nella libreria.</p>}
 {items.map(item=><button type="button" className="background-gallery-choice" key={item.id} disabled={disabled} aria-pressed={selectedId===item.id} title={item.display_name||item.name||'Immagine senza nome'} onClick={()=>onSelect(item.id)}>
  <img loading="lazy" src={item.url} alt=""/><span>{item.display_name||item.name||`Immagine ${String(item.id).slice(0,8)}`}</span>
 </button>)}
 </div>;
}
/** Keep the master ribbon compact: open the image library as an accessible
 * dialog instead of rendering every thumbnail directly inside the command strip.
 * This also avoids nesting a scrolling gallery within the horizontal ribbon. */
function SchemaBackgroundTool({items,onSelect,selectedId,disabled,label='Immagine sfondo dello schema'}:{items:any[];onSelect:(id:string)=>void;selectedId:string;disabled:boolean;label?:string}){
 const [open,setOpen]=useState(false);
 const dialogRef=useRef<HTMLDivElement>(null);
 useEffect(()=>{
  if(!open)return;
  const previous=document.activeElement instanceof HTMLElement?document.activeElement:null;
  dialogRef.current?.focus();
  const onKey=(event:KeyboardEvent)=>{
   if(event.key==='Escape'){event.preventDefault();event.stopPropagation();setOpen(false);return;}
   if(event.key!=='Tab'||!dialogRef.current)return;
   const candidates=[...dialogRef.current.querySelectorAll<HTMLElement>('button:not(:disabled),[href],input:not(:disabled),[tabindex]:not([tabindex="-1"])')].filter(node=>node.getClientRects().length>0);
   if(!candidates.length){event.preventDefault();dialogRef.current.focus();return;}
   const first=candidates[0],last=candidates[candidates.length-1];
   if(event.shiftKey&&(document.activeElement===first||document.activeElement===dialogRef.current)){event.preventDefault();last.focus();}
   else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first.focus();}
  };
  document.addEventListener('keydown',onKey,true);
  return()=>{document.removeEventListener('keydown',onKey,true);previous?.focus();};
 },[open]);
 return <>
  <SchemaRibbonButton label="Sfondi" hint="Apri la libreria di sfondi: anteprima, nome e scelta dell'immagine globale" icon={<ImageIcon size={20}/>} disabled={disabled} onClick={()=>setOpen(true)}/>
  {open&&createPortal(<div className="schema-background-modal-backdrop" onMouseDown={e=>{if(e.target===e.currentTarget)setOpen(false)}}>
   <div ref={dialogRef} tabIndex={-1} className="schema-background-modal" role="dialog" aria-modal="true" aria-labelledby="schema-background-modal-title" aria-describedby="schema-background-modal-description">
    <header><div><h2 id="schema-background-modal-title">Sfondi dello schema</h2><p id="schema-background-modal-description">Seleziona una miniatura. Il nome del file è riportato sotto l’immagine.</p></div><button type="button" className="outline" onClick={()=>setOpen(false)} aria-label="Chiudi libreria sfondi">Chiudi</button></header>
    <BackgroundGallery items={items} selectedId={selectedId} disabled={disabled} label={label} onSelect={id=>{onSelect(id);setOpen(false)}}/>
   </div>
  </div>,document.body)}
 </>;
}

/** Server configuration tabs keep inactive components mounted so unsaved provider
 * credentials, backup and SMTP drafts remain available when switching tabs. */
const SERVER_SETTINGS_TABS=[
 {id:'general',label:'Generale'},
 {id:'auth',label:'Autenticazione'},
 {id:'smtp',label:'Posta elettronica'},
 {id:'storage',label:'Spazio disco'},
 {id:'converter',label:'Convertitore'},
 {id:'backup',label:'Backup'},
 {id:'audit',label:'Audit'},
] as const;
type ServerSettingsTab=(typeof SERVER_SETTINGS_TABS)[number]['id'];

/** RC270 platform-only controls: all requests use the same authenticated API path. */
function AdminBackupPanel(){
 const [data,setData]=useState<any>(null),[target,setTarget]=useState<any>({backend:'s3',bucket:'',region:'eu-west-1',prefix:'',directory:'',url:'',username:'',password:'',accessKey:'',secretKey:''});
 const [enabled,setEnabled]=useState(false),[interval,setIntervalHours]=useState(24),[busy,setBusy]=useState(false),[message,setMessage]=useState('');
 const refresh=async()=>{try{const r=await request<any>('/admin/backups');setData(r);setEnabled(r.enabled);setIntervalHours(r.interval_hours);setTarget({backend:r.target?.backend||r.allowed_backends?.[0]||'s3',region:'eu-west-1',directory:'',prefix:'',...r.target,password:'',secretKey:''})}catch(e){setMessage(String(e))}};
 useEffect(()=>{void refresh()},[]);
 const update=(key:string,value:string)=>setTarget((v:any)=>({...v,[key]:value}));
 const save=async()=>{setBusy(true);try{await request('/admin/backups','PUT',{enabled,interval_hours:interval,target});setMessage('Configurazione e pianificazione salvate.');await refresh()}catch(e){setMessage(String(e))}finally{setBusy(false)}};
 const run=async()=>{setBusy(true);try{await request('/admin/backups/run','POST');setMessage('Backup avviato: verifica l’esito nello storico.');await refresh()}catch(e){setMessage(String(e))}finally{setBusy(false)}};
 return <section className="panel" aria-label="Backup completo dell’istanza"><h3>Backup completo: database e file dell’applicazione</h3>
 <p className="muted tiny">Il download browser genera un archivio PostgreSQL + asset persistenti. POSIX/NFS richiedono un volume già montato dal deployment Helm; le credenziali remote vengono cifrate dal server e non sono mostrate dopo il salvataggio.</p>
 {!data?<p>Caricamento destinazioni…</p>:<><label>Backend<select aria-label="Backend backup" value={target.backend||''} onChange={e=>setTarget({backend:e.target.value,region:'eu-west-1',directory:'',prefix:''})}>{(data.allowed_backends||[]).map((x:string)=><option key={x} value={x}>{x.toUpperCase()}</option>)}</select></label>
 {['posix','nfs'].includes(target.backend)&&<label>Sottocartella del volume montato<input aria-label="Sottocartella backup" value={target.directory||''} onChange={e=>update('directory',e.target.value)} placeholder="backups"/></label>}
 {target.backend==='s3'&&<><label>Bucket S3<input value={target.bucket||''} onChange={e=>update('bucket',e.target.value)}/></label><label>Regione<input value={target.region||''} onChange={e=>update('region',e.target.value)}/></label><label>Prefisso oggetti<input value={target.prefix||''} onChange={e=>update('prefix',e.target.value)}/></label><label>Endpoint HTTPS (opzionale)<input value={target.endpoint||''} onChange={e=>update('endpoint',e.target.value)}/></label><label>Access key<input autoComplete="off" value={target.accessKey||''} onChange={e=>update('accessKey',e.target.value)}/></label><label>Secret key (lascia vuoto per conservare quello attuale)<input type="password" autoComplete="new-password" value={target.secretKey||''} onChange={e=>update('secretKey',e.target.value)}/></label></>}
 {target.backend==='webdav'&&<><label>URL cartella WebDAV HTTPS<input type="url" value={target.url||''} onChange={e=>update('url',e.target.value)}/></label><label>Utente WebDAV<input value={target.username||''} onChange={e=>update('username',e.target.value)}/></label><label>Password (lascia vuoto per conservarla)<input type="password" autoComplete="new-password" value={target.password||''} onChange={e=>update('password',e.target.value)}/></label></>}
 <label><input type="checkbox" checked={enabled} onChange={e=>setEnabled(e.target.checked)}/> Esegui backup automatici</label><label>Ripetizione ogni (ore)<input type="number" min={1} max={720} value={interval} onChange={e=>setIntervalHours(Number(e.target.value))}/></label>
 <div className="downloads"><button type="button" disabled={busy} onClick={()=>void save()}>Salva backup e schedule</button><button type="button" className="outline" disabled={busy||!data.target} onClick={()=>void run()}>Esegui ora sul backend</button><a className="button outline" href="/api/admin/backups/download" download>Scarica backup completo via browser</a><button type="button" className="outline" onClick={()=>void refresh()}>Aggiorna esiti</button></div>
 <h4>Ultime esecuzioni</h4>{(data.runs||[]).length===0?<p className="muted tiny">Nessuna esecuzione registrata.</p>:<div className="table-scroll"><table><thead><tr><th>Data</th><th>Destinazione</th><th>Stato</th><th>Dimensione</th></tr></thead><tbody>{data.runs.map((r:any)=><tr key={r.id}><td>{new Date(r.started_at).toLocaleString('it-IT')}</td><td>{r.backend}</td><td>{r.state}{r.error_code?' · '+r.error_code:''}</td><td>{r.bytes?Math.round(Number(r.bytes)/1048576)+' MiB':'—'}</td></tr>)}</tbody></table></div>}</>}
 {message&&<p role="status">{message}</p>}</section>
}
function AdminAuditPanel(){
 const [rows,setRows]=useState<any[]>([]),[term,setTerm]=useState(''),[retention,setRetention]=useState(365),[message,setMessage]=useState('');
 const reload=async()=>{try{const [a,b]=await Promise.all([request<any>('/admin/audit?search='+encodeURIComponent(term)),request<any>('/admin/audit/settings')]);setRows(a.items);setRetention(b.retention_days)}catch(e){setMessage(String(e))}};
 useEffect(()=>{void reload()},[]);
 return <section className="panel" aria-label="Audit amministrativo"><h3>Audit delle operazioni</h3><p className="muted tiny">Operazioni riuscite con attore, tipo di risorsa e data; nessuna password, indirizzo IP o contenuto delle risposte. Le cancellazioni sono gestite dalla retention GDPR.</p><label>Ricerca operazioni / utente<input value={term} onChange={e=>setTerm(e.target.value)}/></label><div className="downloads"><button type="button" className="outline" onClick={()=>void reload()}>Cerca e aggiorna</button><label>Ritenzione (giorni)<input type="number" min={7} max={3650} value={retention} onChange={e=>setRetention(Number(e.target.value))}/></label><button type="button" onClick={()=>void request('/admin/audit/settings','PUT',{retention_days:retention}).then(()=>setMessage('Ritenzione salvata')).catch(e=>setMessage(String(e)))}>Salva ritenzione</button><button type="button" className="outline" onClick={()=>{if(window.confirm(`Eliminare gli audit precedenti a ${retention} giorni?`))void request('/admin/audit/purge','POST',{older_than_days:retention}).then(()=>reload()).catch(e=>setMessage(String(e)))}}>Esegui pulizia manuale</button></div>
 <div className="table-scroll"><table><thead><tr><th>Quando</th><th>Amministratore / utente</th><th>Operazione</th><th>Risorsa</th><th>HTTP</th></tr></thead><tbody>{rows.map(r=><tr key={r.id}><td>{new Date(r.occurred_at).toLocaleString('it-IT')}</td><td>{r.actor_email||'Utente eliminato'}</td><td>{r.action}</td><td>{r.resource_type}</td><td>{r.status}</td></tr>)}</tbody></table></div>{message&&<p role="status">{message}</p>}</section>
}
function AdminLdapPanel(){
 const [query,setQuery]=useState(''),[users,setUsers]=useState<any[]>([]),[subject,setSubject]=useState(''),[role,setRole]=useState('user'),[message,setMessage]=useState('');
 const search=async()=>{try{const r=await request<any>('/admin/ldap/search?q='+encodeURIComponent(query));setUsers(r.items);setSubject(r.items[0]?.subject||'')}catch(e){setMessage(String(e))}};
 const create=async()=>{try{await request('/admin/ldap/users','POST',{query,subject,role});setMessage('Utente LDAP creato e autorizzato. Aggiorna la lista utenti.');setSubject('');setUsers([])}catch(e){setMessage(String(e))}};
 return <section className="panel" aria-label="Creazione utenti LDAP"><h3>Abilita utente da LDAP / Active Directory</h3><p className="muted tiny">Ricerca tramite directory autenticata dal server; scegli esplicitamente ruolo e utente. Non serve conoscere o impostare la password LDAP dell’utente.</p><label>Ricerca nome utente / email<input value={query} onChange={e=>setQuery(e.target.value)}/></label><button className="outline small" disabled={query.length<2} onClick={()=>void search()}>Cerca LDAP</button>{users.length>0&&<><label>Identità verificata<select value={subject} onChange={e=>setSubject(e.target.value)}>{users.map(u=><option key={u.subject} value={u.subject}>{u.email}</option>)}</select></label><label>Ruolo in Quorivio<select value={role} onChange={e=>setRole(e.target.value)}>{['user','presenter','moderator','org_admin','platform_admin'].map(r=><option key={r} value={r}>{r}</option>)}</select></label><button type="button" disabled={!subject} onClick={()=>void create()}>Autorizza utente LDAP</button></>}{message&&<p role="status">{message}</p>}</section>
}
/** Defer legacy dashboard results until inside a local error boundary.
 * Calling showResults() inline while rendering App previously bypassed widget
 * boundaries and could trigger global session-restore on malformed live rows. */
function DashboardLiveResults({snapshot,activity,renderResults}:{snapshot:Snapshot;activity:Activity;renderResults:(s:Snapshot,a:Activity,mode?:string)=>React.ReactNode}){
 return <>{renderResults(snapshot,activity)}</>;
}
function App(){const [statisticsAnonymize,setStatisticsAnonymize]=useState(true);const [lang,setLang]=useState<UiLanguage>(preferredUiLanguage);const t=text[lang];const pc=participantCopy[lang];useEffect(()=>activateUiLanguage(lang),[lang]);const [me,setMe]=useState<any>(undefined);const [ldapStatus,setLdapStatus]=useState<{enabled:boolean;label:string}>({enabled:false,label:'LDAP'});const [loginBackend,setLoginBackend]=useState<'local'|'ldap'>('local');const [ldapLinkLogin,setLdapLinkLogin]=useState('');const [ldapLinkPassword,setLdapLinkPassword]=useState('');const [ldapLinkBusy,setLdapLinkBusy]=useState(false);const [oidcProviders,setOidcProviders]=useState<{id:string;label?:string}[]>([]);useEffect(()=>{void request<{enabled:boolean;label:string}>('/auth/ldap/status').then(setLdapStatus).catch(()=>{})},[]);useEffect(()=>{void request<{providers:{id:string;label?:string}[]}>('/auth/oidc/providers').then(v=>setOidcProviders(v.providers)).catch(()=>{})},[]);const [sessions,setSessions]=useState<Session[]>([]);const [selected,setSelected]=useState<string>(()=>readWorkspaceLocation().sessionId);const [snap,setSnap]=useState<Snapshot|null>(null);const sessionPreviewCache=useRef<Map<string,{snapshot:Snapshot;at:number}>>(new Map());const sessionPreviewPending=useRef<Map<string,Promise<Snapshot|null>>>(new Map());const [error,setError]=useState('');const [email,setEmail]=useState('');const [password,setPassword]=useState('');const [emailChallenge,setEmailChallenge]=useState('');const [mfaMethods,setMfaMethods]=useState<string[]>([]);const [mfaMethod,setMfaMethod]=useState('');const [showRecovery,setShowRecovery]=useState(false);const [emailCode,setEmailCode]=useState('');const [emailMfaPassword,setEmailMfaPassword]=useState('');const [emailEnrollmentId,setEmailEnrollmentId]=useState('');const [emailEnrollmentCode,setEmailEnrollmentCode]=useState('');const [totpCode,setTotpCode]=useState('');const [mfaVerifyPending,setMfaVerifyPending]=useState(false);const mfaVerifyLock=useRef(false);const [recoveryCode,setRecoveryCode]=useState('');const [recoveryCodes,setRecoveryCodes]=useState<string[]>([]);const [resetToken,setResetToken]=useState(()=>consumeRecoveryTokenFromUrl(window.location,window.history));const [resetPassword,setResetPassword]=useState('');const [resetPasswordConfirmation,setResetPasswordConfirmation]=useState('');const [resetSubmitPending,setResetSubmitPending]=useState(false);const resetSubmitLock=useRef(false);const [enrollment,setEnrollment]=useState<any>(null);const [mfaAdminCode,setMfaAdminCode]=useState('');const [smtpStatus,setSmtpStatus]=useState<any>(null);const [diskStatus,setDiskStatus]=useState<DiskStatus|null>(null);const [diskStatusError,setDiskStatusError]=useState('');const [smtpRecipient,setSmtpRecipient]=useState('');const [smtpForm,setSmtpForm]=useState({host:'',port:465,user:'',password:'',from:'',senderName:'',secure:true});const [dashboardPage,setDashboardPage]=useState<'workspace'|'new'|'open'|'calendar'|'session'|'master'|'users'|'settings'|'sso'|'mfa'|'profile'>(readWorkspaceLocation().section);const [serverSettingsTab,setServerSettingsTab]=useState<ServerSettingsTab>('general');const [sidebarRename,setSidebarRename]=useState<string|null>(null);const [sidebarBusy,setSidebarBusy]=useState(false);const localSessionImportRef=useRef<HTMLInputElement|null>(null);const [selectedSessionRole,setSelectedSessionRole]=useState<'owner'|'collaborator'|null>(null);const [schemaWidgets,setSchemaWidgets]=useState<any[]>([]);const [schemaSaving,setSchemaSaving]=useState(false);const [schemaInspected,setSchemaInspected]=useState('');const [schemaSelected,setSchemaSelected]=useState<string[]>([]);const schemaBaseline=useRef('');const [schemaBackgroundAsset,setSchemaBackgroundAsset]=useState('');const schemaBackgroundBaseline=useRef('');const [title,setTitle]=useState('');const [newTitle,setNewTitle]=useState('');const [newReferenceDate,setNewReferenceDate]=useState('');const [sessionTitleEdit,setSessionTitleEdit]=useState('');const [sessionDateEdit,setSessionDateEdit]=useState('');const [scheduleDates,setScheduleDates]=useState<string[]>([]);const [scheduleNewDate,setScheduleNewDate]=useState('');const [appointments,setAppointments]=useState<{date:string;start_time:string;duration_minutes:number;time_zone:string}[]>([]);const [appointmentDate,setAppointmentDate]=useState('');const [appointmentTime,setAppointmentTime]=useState('09:00');const [appointmentMinutes,setAppointmentMinutes]=useState(60);const [appointmentZone,setAppointmentZone]=useState(Intl.DateTimeFormat().resolvedOptions().timeZone||'Europe/Rome');const [calendarMonth,setCalendarMonth]=useState(new Date().toLocaleDateString('en-CA'));const [calendarView,setCalendarView]=useState<'day'|'week'|'month'>('month');const [globalAppointments,setGlobalAppointments]=useState<any[]>([]);const [rehearsalOpen,setRehearsalOpen]=useState(false);const [rehearsalMode,setRehearsalMode]=useState<RehearsalMode>('participant');const [sessionTab,setSessionTab]=useState<'overview'|'pages'|'audience'|'results'>(()=>readWorkspaceLocation().tab);const [designActivity,setDesignActivity]=useState('');
 // Expired presenter session: immediately return to login without reloading the page.
 useEffect(()=>{
  const onExpired=()=>{
   setMe(null);setSnap(null);setSelected('');setDesignActivity('');
   setRehearsalOpen(false);setDashboardPage('workspace');
   writeWorkspaceLocation({sessionId:'',section:'workspace',tab:'overview',pageId:''});
  };
  window.addEventListener('quorivio:authentication-expired',onExpired);
  return()=>window.removeEventListener('quorivio:authentication-expired',onExpired);
 },[]);const [pageThumbMenu,setPageThumbMenu]=useState('');const [selectedPageIds,setSelectedPageIds]=useState<string[]>([]);const [pageMenuPosition,setPageMenuPosition]=useState({left:8,top:8,maxHeight:400,width:270});const [pageBatchBusy,setPageBatchBusy]=useState(false);const [pageOrderPending,setPageOrderPending]=useState(false);
 const sidebarLongPress=useRef<number|undefined>(undefined);const clearSidebarLongPress=()=>{if(sidebarLongPress.current!==undefined)window.clearTimeout(sidebarLongPress.current);sidebarLongPress.current=undefined};const [pageDropSlot,setPageDropSlot]=useState<number|null>(null);const [pageExportError,setPageExportError]=useState('');const [pendingPresentation,setPendingPresentation]=useState<{file:File;afterPageId?:string}|null>(null);const [importImageFit,setImportImageFit]=useState<'contain'|'cover'|'fill'>('cover');const [importHideScheme,setImportHideScheme]=useState(true);const [pageContextOpen,setPageContextOpen]=useState(false);const [inspectedWidget,setInspectedWidget]=useState('');const [editorTouchHint,setEditorTouchHint]=useState('');useEffect(()=>{if(!editorTouchHint)return;const id=window.setTimeout(()=>setEditorTouchHint(''),2400);return()=>window.clearTimeout(id)},[editorTouchHint]);const savedPageDraft=useRef('');const loadedDesignRevision=useRef(1);const [pageConflict,setPageConflict]=useState(false);const [mergeCandidate,setMergeCandidate]=useState<{remote:EditablePageDraft;revision:number;snapshot:Snapshot;base?:EditablePageDraft;local?:EditablePageDraft}|null>(null);const [mergeChoices,setMergeChoices]=useState<Record<string,MergeChoice>>({});type EditorWidgetPermissionFields = Pick<NonNullable<PageDesign['widgets']>[number], 'allowAnswerChange' | 'showEmail' | 'reactionIconSize' | 'titleFollowPage' | 'titleUseMaster' | 'footerShowSessionTitle' | 'footerShowPageNumber' | 'showTitle' | 'showQrUrl' | 'autoFit' | 'resultsOnly' | 'showSourceQuestion' | 'showSourceTitle' | 'showSourceAnswers' | 'showCorrectAnswers' | 'position' | 'resultTopCount'>;
const [pageAudienceId,setPageAudienceId]=useState('');const [pagePresenterHidden,setPagePresenterHidden]=useState(false);
const [widgetHistory,setWidgetHistory]=useState(()=>newWidgetHistory<{id:string;kind:string;label?:string;description?:string;answerMode?:string;options?:{id:string;label:string}[];required?:boolean;durationSeconds?:number;correctOptionId?:string;correctOptionIds?:string[];questions?:WidgetSubquestion[];textMarks?:WidgetInlineMark[];assetId?:string;targetWidgetId?:string;targetActivityId?:string;targetQuestionId?:string;style?:WidgetTextStyle} & EditorWidgetPermissionFields>([]));
const [editorSelectedWidgets,setEditorSelectedWidgets]=useState<string[]>([]);
const [editorToolbarCommand,setEditorToolbarCommand]=useState<{action:'copy'|'cut'|'paste';token:number}|undefined>();
const [editorClipboardReady,setEditorClipboardReady]=useState(false);
const [editorInfoOpen,setEditorInfoOpen]=useState(false);
const issueEditorClipboard=(action:'copy'|'cut'|'paste')=>setEditorToolbarCommand(old=>({action,token:(old?.token||0)+1}));
const pageWidgets=widgetHistory.present;
useEffect(()=>{if(inspectedWidget&&!pageWidgets.some(w=>w.id===inspectedWidget))setInspectedWidget('')},[pageWidgets,inspectedWidget]);
const setPageWidgets:React.Dispatch<React.SetStateAction<typeof pageWidgets>>=(next)=>setWidgetHistory(history=>{const updated=typeof next==='function'?next(history.present):next;const validIds=new Set(updated.map(w=>w.id));return editWidgets(history,updated.map(w=>{if(w.kind!=='results-button'||!w.targetWidgetId||w.targetActivityId)return w;const source=updated.find(s=>s.id===w.targetWidgetId);if(!source)return {...w,targetWidgetId:undefined,targetQuestionId:undefined};if(w.targetQuestionId&&!source.questions?.some(q=>q.id===w.targetQuestionId))return {...w,targetQuestionId:undefined};return w}));});
const reconcilePageAutoFit=React.useCallback((base:typeof pageWidgets, fitted:typeof pageWidgets)=>setWidgetHistory(h=>reconcileWidgetAutoFit(h,base,fitted)),[]);
const resetPageWidgets=(next:typeof pageWidgets)=>setWidgetHistory(newWidgetHistory(next));
const undoPageWidgets=()=>setWidgetHistory(undoWidgets);
const redoPageWidgets=()=>setWidgetHistory(redoWidgets);
const beginPageWidgetGesture=()=>setWidgetHistory(beginWidgetGesture);
const endPageWidgetGesture=()=>setWidgetHistory(endWidgetGesture);const [ratingSent,setRatingSent]=useState<string[]>([]);const [ratingPending,setRatingPending]=useState<string[]>([]);const pendingRatingVotes=useRef(new Set<string>());const [ratingVotes,setRatingVotes]=useState<Record<string,string>>({});const [ratingComments,setRatingComments]=useState<Record<string,string>>({});const [participantReadingMode,setParticipantReadingMode]=useState(false);const [participantPhoneMode,setParticipantPhoneMode]=useState(()=>defaultParticipantPhoneMode(window.innerWidth,window.matchMedia('(pointer: coarse)').matches));const [participantModeExplicit,setParticipantModeExplicit]=useState(false);
useEffect(()=>{
 if(participantModeExplicit)return;
 const pointer=window.matchMedia('(pointer: coarse)');
 const sync=()=>setParticipantPhoneMode(defaultParticipantPhoneMode(window.innerWidth,pointer.matches));
 window.addEventListener('resize',sync);
 pointer.addEventListener('change',sync);
 sync();
 return()=>{window.removeEventListener('resize',sync);pointer.removeEventListener('change',sync)};
},[participantModeExplicit]);const [myProfile,setMyProfile]=useState<any>(null);const [profileName,setProfileName]=useState('');const [nickname,setNickname]=useState('');const [photoBusy,setPhotoBusy]=useState(false);const [profileSaving,setProfileSaving]=useState(false);const [adminSavingId,setAdminSavingId]=useState('');const [photoVersion,setPhotoVersion]=useState(0);const [profilePhoto,setProfilePhoto]=useState('');const [availablePresenters,setAvailablePresenters]=useState<any[]>([]);const [ratingStats,setRatingStats]=useState<any>(null);const [questionHeader,setQuestionHeader]=useState('');const [resultHeader,setResultHeader]=useState('');const [questionBackground,setQuestionBackground]=useState('');const [questionBackgroundColor,setQuestionBackgroundColor]=useState('');const [resultBackground,setResultBackground]=useState('');const [resultBackgroundColor,setResultBackgroundColor]=useState('');const [questionBackgroundAsset,setQuestionBackgroundAsset]=useState('');const [mobileLayoutDraft,setMobileLayoutDraft]=useState<MobilePageLayout>({});const [canvasDevice,setCanvasDevice]=useState<'desktop'|'phone'>('desktop');
useEffect(()=>{setEditorClipboardReady(!!selected&&readEditorWidgetClipboard(selected).length>0);setEditorSelectedWidgets([])},[selected,designActivity,canvasDevice]);const [resultBackgroundAsset,setResultBackgroundAsset]=useState('');const [kind,setKind]=useState<'poll'|'quiz'|'timed_quiz'>('poll');const [options,setOptions]=useState('Sì\nNo');const [correct,setCorrect]=useState(0);const [answerMode,setAnswerMode]=useState<'single'|'multiple'|'text'|'file'>('single');const [answerRequired,setAnswerRequired]=useState(true);const [multipleAnswers,setMultipleAnswers]=useState<string[]>([]);const [freeText,setFreeText]=useState('');const [selectedReaction,setSelectedReaction]=useState('');const [reactions,setReactions]=useState<any>(null);const [code,setCode]=useState('');const [participant,setParticipant]=useState(false);const [answer,setAnswer]=useState('');const [sent,setSent]=useState(false);const [joined,setJoined]=useState(false);const [participantReady,setParticipantReady]=useState(false);const [joinPending,setJoinPending]=useState(false);const [votePending,setVotePending]=useState(false);const [joinStatus,setJoinStatus]=useState<'loading'|'ready'|'unavailable'>('loading');const [liveConnection,setLiveConnection]=useState<'connecting'|'connected'|'disconnected'|'blocked'>('connecting');const joining=useRef(false);const [pseudonym,setPseudonym]=useState(localStorage.getItem('quorivio_pseudonym')||'');const [consent,setConsent]=useState(false);const [newPassword,setNewPassword]=useState('');const [confirmNewPassword,setConfirmNewPassword]=useState('');const [registerMode,setRegisterMode]=useState(false);const [notice,setNotice]=useState('');const [newUserEmail,setNewUserEmail]=useState('');const [newUserNickname,setNewUserNickname]=useState('');const [userSearch,setUserSearch]=useState('');const [userPage,setUserPage]=useState(1);const [userPageSize,setUserPageSize]=useState(10);const [sessionSearch,setSessionSearch]=useState('');const [sessionPage,setSessionPage]=useState(1);const [sessionPageSize,setSessionPageSize]=useState(10);const [sessionTotal,setSessionTotal]=useState(0);const [listSessionBusy,setListSessionBusy]=useState<string|null>(null);const listSessionBusyRef=useRef<string|null>(null);const [userTotal,setUserTotal]=useState(0);const [cookieAcknowledged,setCookieAcknowledged]=useState(document.cookie.split('; ').some(x=>x.startsWith('q_cookie_notice=')));const [newUserTemporaryPassword,setNewUserTemporaryPassword]=useState('');const [adminUsers,setAdminUsers]=useState<any[]>([]);const [adminUrl,setAdminUrl]=useState('');const [adminRetention,setAdminRetention]=useState(60);const [adminUploadMb,setAdminUploadMb]=useState(100);const [converterStatus,setConverterStatus]=useState<{deployment_enabled:boolean;worker_configured:boolean;worker_ready:boolean;admin_enabled:boolean;enabled:boolean;blocker:string|null}|null>(null);const [converterBusy,setConverterBusy]=useState(false);const [slideMasterDraft,setSlideMasterDraft]=useState({...DEFAULT_TITLE_STYLE});const [pageBackground,setPageBackground]=useState('');const [pageLogo,setPageLogo]=useState('');const [mediaUrl,setMediaUrl]=useState('');const [mediaKind,setMediaKind]=useState<'image'|'video'|'pdf'>('image');const [coEmail,setCoEmail]=useState('');const [ownershipTarget,setOwnershipTarget]=useState('');const [ownershipKeepPrevious,setOwnershipKeepPrevious]=useState(true);const [ownershipBusy,setOwnershipBusy]=useState(false);const [coPresenters,setCoPresenters]=useState<any[]>([]);const [assets,setAssets]=useState<any[]>([]);const [backgrounds,setBackgrounds]=useState<any[]>([]);const [assetBusy,setAssetBusy]=useState(false);const [editingActivity,setEditingActivity]=useState<string>('');const [editTitle,setEditTitle]=useState('');const [editOpts,setEditOpts]=useState('');const [editCorrect,setEditCorrect]=useState('');const path=location.pathname;const joinPath=path.startsWith('/join/');const publicPath=path.startsWith('/screen/');const joinCode=joinPath?normalizeJoinCode(path.slice(6)):'';const publicId=publicPath?path.slice(8):'';
useEffect(()=>{if(!notice&&!error)return;const timer=window.setTimeout(()=>{setNotice('');setError('')},7000);return()=>window.clearTimeout(timer)},[notice,error]);const notify=(e:unknown)=>{if(!reauthenticationRedirecting)setError(e instanceof Error?e.message:String(e))};useEffect(()=>{if(dashboardPage!=='profile'||!me)return;let cancelled=false;void request<any>('/auth/profile').then(p=>{if(cancelled)return;setMyProfile(p);setProfileName(p.display_name||'');setProfilePhoto(p.profile_photo_url||'')}).catch(e=>{if(!cancelled)notify(e)});return()=>{cancelled=true}},[dashboardPage,me?.id]);useEffect(()=>{const dismiss=(event:KeyboardEvent)=>{if(event.key==='Escape'){setNotice('');setError('')}};window.addEventListener('keydown',dismiss);return()=>window.removeEventListener('keydown',dismiss)},[]);const load=()=>request<{items:Session[];total:number}>(`/sessions?page=${sessionPage}&page_size=${sessionPageSize}&search=${encodeURIComponent(sessionSearch)}`).then(v=>{setSessions(v.items);setSessionTotal(v.total)}).catch(notify);const [authRecheck,setAuthRecheck]=useState(0);
useEffect(()=>{
 if(joinPath||publicPath)return;
 let active=true;const controller=new AbortController();
 const deadline=window.setTimeout(()=>controller.abort(),12000);
 let retry:number|undefined;
 void request('/auth/me','GET',undefined,{signal:controller.signal,cache:'no-store'}).then(v=>{
  if(active){setMe(v);setNickname(v?.nickname||'')}
 }).catch(e=>{
  if(!active)return;
  setMe(null);
  if(sessionFailureForStatus((e as Error&{status?:number})?.status)==='retry'){
   setNotice('Connessione al server temporaneamente non disponibile. Nuova verifica automatica dell’accesso.');
   retry=window.setTimeout(()=>{if(active)setAuthRecheck(v=>v+1)},12000);
  }
 }).finally(()=>window.clearTimeout(deadline));
 return()=>{active=false;controller.abort();window.clearTimeout(deadline);if(retry!==undefined)window.clearTimeout(retry)};
},[authRecheck]);useEffect(()=>{if(me)load()},[me,sessionPage,sessionPageSize,sessionSearch]);useEffect(()=>{setNickname(me?.nickname||'')},[me?.id,me?.nickname]);useEffect(()=>{if(!me||me.role!=='platform_admin')return;if(dashboardPage==='users')void request<{items:any[];total:number}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`).then(v=>{setAdminUsers(v.items);setUserTotal(v.total)}).catch(notify);if(dashboardPage==='settings')void request<any>('/admin/settings').then(cfg=>{setAdminUrl(cfg.public_base_url||'');setAdminRetention(Number(cfg.closed_session_retention_days||60));setAdminUploadMb(Number(cfg.max_upload_mb||100))}).catch(notify)},[dashboardPage,me?.role,userPage,userPageSize,userSearch]);useEffect(()=>{if(me?.role!=='platform_admin'||dashboardPage!=='settings')return;let active=true;void request<any>('/admin/converter').then(info=>{if(active)setConverterStatus(info)}).catch(e=>{if(active)notify(e)});return()=>{active=false}},[dashboardPage,me?.role]);useEffect(()=>{if(me?.role!=='platform_admin'||dashboardPage!=='settings')return;let active=true;
 const refresh=async()=>{try{const value=await request<DiskStatus>('/admin/disk-usage','GET',undefined,{cache:'no-store'});if(active){setDiskStatus(value);setDiskStatusError('')}}catch{if(active){setDiskStatus(null);setDiskStatusError('Monitoraggio disco temporaneamente non disponibile')}}};
 void refresh();const timer=window.setInterval(()=>void refresh(),60000);return()=>{active=false;window.clearInterval(timer)}
},[dashboardPage,me?.role]);
const [sessionLoadState,setSessionLoadState]=useState<'idle'|'loading'|'ready'|'retry'>('idle');
 const [sessionReload,setSessionReload]=useState(0);
 const [showSessionLoading,setShowSessionLoading]=useState(false);
 // In-memory authenticated prefetch: never cache to disk or share across accounts.
 // Coalesce the in-flight hover/focus request with the actual open request.
 const warmSessionSnapshot=React.useCallback((sessionId:string)=>{
  if(!sessionId||!me?.id)return;
  const key=me.id+':'+sessionId;
  if(Date.now()-(sessionPreviewCache.current.get(key)?.at??0)<8000||sessionPreviewPending.current.has(key))return;
  let promise:Promise<Snapshot|null>;
  promise=sessionSnapshotRequest(sessionId).then(raw=>{
   if(!isOwnerSessionSnapshot(raw,sessionId))return null;
   const snapshot=normalizeOwnerSessionSnapshot(raw);
   sessionPreviewCache.current.set(key,{snapshot,at:Date.now()});
   return snapshot;
  }).catch(()=>null).finally(()=>{if(sessionPreviewPending.current.get(key)===promise)sessionPreviewPending.current.delete(key)});
  sessionPreviewPending.current.set(key,promise);
 },[me?.id]);
 useEffect(()=>{sessionPreviewCache.current.clear();sessionPreviewPending.current.clear()},[me?.id]);
 useEffect(()=>{
  if(!selected||!me){setSessionLoadState('idle');return}
  let active=true;let retryTimer:number|undefined;let attempt=0;let running:AbortController|undefined;
  const key=me.id+':'+selected,cached=sessionPreviewCache.current.get(key);
  const preview=cached&&Date.now()-cached.at<5000?cached.snapshot:null;
  setSnap(current=>current?.session?.id===selected?current:preview);
  setSelectedSessionRole(preview?.session.access_role||null);
  setSessionLoadState(preview?'ready':'loading');
  const recover=async()=>{
   if(!active)return;
   const controller=new AbortController();running=controller;
   const deadline=window.setTimeout(()=>controller.abort(),12000);
   try{
    const inFlight=attempt===0?sessionPreviewPending.current.get(key):undefined;
    const value=await (inFlight?inFlight.then(value=>value??sessionSnapshotRequest(selected,controller.signal)):sessionSnapshotRequest(selected,controller.signal));
    if(!isOwnerSessionSnapshot(value,selected))throw new Error('invalid_session_snapshot');
    if(!active)return;
    const normalized=normalizeOwnerSessionSnapshot(value);
    sessionPreviewCache.current.set(key,{snapshot:normalized,at:Date.now()});
    setSnap(normalized);setSelectedSessionRole(normalized.session.access_role||null);setSessionLoadState('ready');
   }catch(e){
    if(!active)return;
    const outcome=sessionFailureForStatus((e as Error&{status?:number})?.status);
    if(outcome==='expired'){
     setMe(null);setSnap(null);setSelectedSessionRole(null);setSessionLoadState('idle');
     setNotice('Accesso scaduto. Effettua nuovamente il login; non occorre cancellare i cookie.');
    }else if(outcome==='unavailable'){
     sessionPreviewCache.current.delete(key);
     writeWorkspaceLocation({sessionId:'',section:'workspace',tab:'overview',pageId:''});
     setSnap(null);setSelectedSessionRole(null);setSelected('');setDashboardPage('open');setDesignActivity('');setSessionLoadState('idle');
     setNotice('Sessione non accessibile: torna all’elenco e apri una sessione disponibile.');
    }else{
     setSessionLoadState('retry');
     retryTimer=window.setTimeout(()=>{if(active){attempt++;setSessionLoadState('loading');void recover()}},Math.min(30000,5000*(attempt+1)));
    }
   }finally{window.clearTimeout(deadline);if(running===controller)running=undefined}
  };
  void recover();
  return()=>{active=false;running?.abort();if(retryTimer!==undefined)window.clearTimeout(retryTimer)};
 },[selected,me?.id,sessionReload]);
 useEffect(()=>{if(!selected||snap?.session.id===selected||!me){setShowSessionLoading(false);return}const timer=window.setTimeout(()=>setShowSessionLoading(true),550);return()=>window.clearTimeout(timer)},[selected,snap?.session.id,me?.id]);
 const workspaceRestore=useRef(readWorkspaceLocation());useEffect(()=>{if(me===undefined||!me)return;writeWorkspaceLocation({sessionId:selected,section:dashboardPage,tab:sessionTab,pageId:designActivity||(workspaceRestore.current.sessionId===selected?workspaceRestore.current.pageId:'')})},[me,selected,dashboardPage,sessionTab,designActivity]);
useEffect(()=>{if(!me||!selected||!snap||snap.session.id!==selected||designActivity||dashboardPage!=='session')return;const saved=workspaceRestore.current;workspaceRestore.current={...saved,pageId:''};if(saved.sessionId===selected&&saved.pageId&&snap.activities.some(a=>a.id===saved.pageId)){const page=snap.activities.find(a=>a.id===saved.pageId);if(page)beginPageDesign(page)}},[me?.id,selected,snap?.session.id,designActivity,dashboardPage]);
useEffect(()=>{if(selected){void request<string[]>(`/sessions/${selected}/schedule`).then(setScheduleDates).catch(()=>setScheduleDates([]));void request<any[]>(`/sessions/${selected}/appointments`).then(setAppointments).catch(()=>setAppointments([]))}},[selected]);useEffect(()=>{if(!me)return;const [year,month]=calendarMonth.split('-').map(Number);const end=new Date(Date.UTC(year,month,0)).toISOString().slice(0,10);void request<any[]>(`/calendar?from=${calendarMonth}-01&to=${end}`).then(setGlobalAppointments).catch(()=>setGlobalAppointments([]))},[calendarMonth,me?.id]);const [presenterLive,setPresenterLive]=useState<'connecting'|'connected'|'disconnected'|'blocked'>('connecting');useLive(me?selected||undefined:undefined,s=>{if(selected&&isOwnerSessionSnapshot(s,selected)){setSnap(normalizeOwnerSessionSnapshot(s));setSessionLoadState('ready');setLiveFallback(false)}},setPresenterLive);
 const [liveFallback,setLiveFallback]=useState(false);
 useEffect(()=>{
  if(!selected||!me||presenterLive==='connected'){setLiveFallback(false);return}
  let stopped=false;let pending=false;let activeRequest:AbortController|undefined;
  const poll=async()=>{
   if(stopped||pending)return;
   pending=true;const controller=new AbortController();activeRequest=controller;
   const deadline=window.setTimeout(()=>controller.abort(),10000);
   try{
    const fresh=await sessionSnapshotRequest(selected,controller.signal);
    if(!stopped&&isOwnerSessionSnapshot(fresh,selected)){setSnap(normalizeOwnerSessionSnapshot(fresh));setLiveFallback(true)}
   }catch(e){
    if(stopped)return;
    setLiveFallback(false);
    if(sessionFailureForStatus((e as Error&{status?:number})?.status)==='expired'){
     setMe(null);setNotice('La sessione di accesso è scaduta: effettua nuovamente il login.');
    }
   }finally{window.clearTimeout(deadline);if(activeRequest===controller)activeRequest=undefined;pending=false}
  };
  void poll();const timer=window.setInterval(()=>void poll(),12000);
  return()=>{stopped=true;activeRequest?.abort();window.clearInterval(timer)};
 },[selected,me?.id,presenterLive]);
const sessionQr=useSynchronizedParticipantQr(me?selected:undefined,snap?.session.id===selected?snap.session.join_code:undefined);
const [entry,setEntry]=useState<any>(null);const [liveResults,setLiveResults]=useState<any[]>([]);
 const [audienceClock,setAudienceClock]=useState(Date.now());
 useEffect(()=>{if(!joinPath||!entry?.activity?.id)return;setAudienceClock(Date.now());const id=window.setInterval(()=>setAudienceClock(Date.now()),1000);return()=>window.clearInterval(id)},[joinPath,entry?.activity?.id]);
 // The joined, active slide has one visual stage. Logos and the long session title
 // belong to the join/status page, not above the live slide. The heading
 // remains in the accessibility tree for screen-reader navigation.
 const participantSlideActive=!!(joinPath&&joined&&entry?.session?.status==='active'&&entry?.activity);
 const audiencePortrait=joinPath&&participantPhoneLayoutEnabled(participantPhoneMode,participantReadingMode,participantModeExplicit,entry?.activity);
 // Rehearsal and public phone must agree on the *visible* widget population:
 // presenter-only controls must not affect phone height or auto stacking.
 const audienceAuthoredWidgets=entry?.activity?(entry.activity.page_design?.suppressMaster?(entry.activity.page_design?.widgets||[]):resolveSlideMasterWidgets(entry.activity.page_design?.widgets||[],entry?.theme?.master?.widgets)):[];
 const audienceVisibleWidgets=participantVisibleWidgets(audienceAuthoredWidgets); const audienceReadingWidgets=participantReadingWidgets(audienceAuthoredWidgets);
 const audiencePhoneLayout=participantPhoneLayout(audienceAuthoredWidgets,entry?.activity?.page_design?.mobile);
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
/** Filename collision handling is server-authoritative, including concurrent uploads.
 * A second upload is never started until the presenter confirms the numbered name. */
async function uploadNamedFile(file:File,mime:string,library:'assets'|'backgrounds'){
 if(!selected)throw Error('Apri prima una sessione.');
 const endpoint=`/api/sessions/${encodeURIComponent(selected)}/${library}`;
 const send=(acceptRename:boolean)=>fetch(endpoint,{method:'POST',credentials:'include',headers:{'Content-Type':mime,'X-Quorivio-Filename':encodeURIComponent(file.name),...(acceptRename?{'X-Quorivio-Allow-Rename':'1'}:{})},body:file});
 let response=await send(false);
 if(response.status===409){
  const detail=await response.json().catch(()=>null);
  if(detail?.error==='duplicate_filename'){
   const proposed=String(detail.suggested_name||file.name);
   if(!window.confirm(`Esiste già un file chiamato «${file.name}». Caricarne un altro come «${proposed}» senza sovrascrivere quello esistente?`))return null;
   response=await send(true);
  }
 }
 if(!response.ok){const detail=await response.json().catch(()=>null);const code=typeof detail?.error==='string'?detail.error:'';throw Error(library==='backgrounds'?backgroundUploadError(response.status,code):code||`Upload HTTP ${response.status}`)}
 return response.json();
}
async function uploadAsset(file:File|undefined){if(!file||!selected)return;setAssetBusy(true);try{
 const mime=mediaUploadMime(file,'asset');
 if(!mime)throw Error('Formato non supportato: JPG, PNG, GIF, WebP, PDF, MP4 o WebM.');
 // Use the same extension fallback as Logo and page backgrounds; the server
 // independently validates actual file bytes and the administrator's limit.
 const saved=await uploadNamedFile(file,mime,'assets');
 if(!saved)return;
 await refreshAssets();setNotice(lang==='it'?'File caricato':'Asset uploaded');
 }catch(e){notify(e)}finally{setAssetBusy(false)}}
async function uploadWidgetFillImage(widgetId:string,file:File|undefined){
 if(!file||!selected)return;
 const mime=mediaUploadMime(file,'image');
 if(!mime){setNotice('Il riempimento richiede PNG, JPEG, GIF o WebP.');return}
 setAssetBusy(true);
 try{
  const saved=await uploadNamedFile(file,mime,'assets');
  if(!saved)return;
  setPageWidgets(old=>old.map(w=>w.id===widgetId?{...w,style:{...w.style,fillMode:'image',fillNone:false,fillImageAssetId:saved.id}}:w));
  await refreshAssets();setNotice('Immagine del widget caricata; salvataggio automatico in corso.');
 }catch(e){notify(e)}finally{setAssetBusy(false)}
}
async function uploadWidgetMedia(widgetId:string,file:File|undefined,kind:string){if(!file||!selected)return;
 const mime=mediaUploadMime(file,kind);if(!mime){setNotice('Formato file non supportato. Usa JPG, PNG, GIF, WebP, MP4, WebM o PDF secondo il widget.');return}
 setAssetBusy(true);try{const saved=await uploadNamedFile(file,mime,'assets');if(!saved)return;
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
  const applied=await uploadNamedFile(file,mime,'backgrounds');
  if(!applied)return false;
  if(typeof applied?.id!=='string'||!/^[-a-f0-9]{36}$/i.test(applied.id))throw Error('Il server non ha restituito un identificativo dello sfondo valido');
  if(forMobile){setMobileLayoutDraft(old=>({...old,backgroundAssetId:applied.id}));}
  else if(forResults){setResultBackgroundAsset(applied.id);setResultBackground('')}
  else{setQuestionBackgroundAsset(applied.id);setQuestionBackground('')}
  await refreshAssets();setNotice(forMobile?'Immagine caricata nella libreria e applicata soltanto allo sfondo smartphone. Salvataggio del layout in corso.':'Immagine caricata nella libreria e applicata alla pagina. Salvataggio del layout in corso.');return true;
 }catch(e){notify(e);throw e}finally{setAssetBusy(false)}
}
async function uploadSchemaBackground(file:File|undefined){
 if(!file||!selected)return;
 const mime=mediaUploadMime(file,'image');if(!mime){setNotice('Immagine non valida: usa PNG, JPG, GIF o WebP.');return}
 setAssetBusy(true);
 try{const applied=await uploadNamedFile(file,mime,'backgrounds');if(!applied)return;if(typeof applied?.id!=='string'||!/^[-a-f0-9]{36}$/i.test(applied.id))throw Error('Identificativo dello sfondo non valido');
  setSchemaBackgroundAsset(applied.id);await refreshAssets();setNotice('Sfondo dello schema caricato: premi Salva schema per applicarlo alle pagine.');
 }catch(e){notify(e)}finally{setAssetBusy(false)}
}
async function renameAsset(id:string){
 const file=assets.find(a=>a.id===id);if(!file||!selected)return;
 const proposed=window.prompt('Nuovo nome dell’allegato',file.display_name||`Allegato ${id.slice(0,8)}`);
 if(proposed===null)return;const name=proposed.trim();if(!name||name.length>120){setNotice('Inserisci un nome da 1 a 120 caratteri.');return}
 try{await request(`/sessions/${selected}/assets/${id}`,'PATCH',{name});await refreshAssets();setNotice('Allegato rinominato.')}
 catch(e){setNotice(e instanceof Error&&e.message==='duplicate_filename'?'Esiste già un allegato con questo nome: scegli un altro nome.':`Rinomina non riuscita: ${e instanceof Error?e.message:String(e)}`)}
}
async function deleteAsset(id:string){if(!window.confirm(lang==='it'?'Eliminare definitivamente il file?':'Delete this file permanently?'))return;try{
 await request(`/sessions/${selected}/assets/${id}`,'DELETE');setAssets(old=>old.filter(item=>item.id!==id));await refreshAssets();setNotice('Allegato eliminato.');
 }catch(e){await refreshAssets();notify(e)}}
async function renameLibraryImage(id:string){
 const image=backgrounds.find(a=>a.id===id&&a.mine);if(!image)return;
 const name=window.prompt('Nome dell’immagine nella libreria',image.display_name||`Immagine ${id.slice(0,8)}`);
 if(name===null)return;const clean=name.trim();if(!clean||clean.length>120){setNotice('Il nome deve contenere da 1 a 120 caratteri.');return}
 try{await request(`/sessions/${selected}/backgrounds/${id}`,'PATCH',{name:clean});await refreshAssets();setNotice('Immagine rinominata')}catch(e){setNotice(e instanceof Error&&e.message==='duplicate_filename'?'Nome già utilizzato nella libreria: scegline un altro.':`Rinomina non riuscita: ${e instanceof Error?e.message:String(e)}`)}
}
async function deleteLibraryImage(id:string){
 if(!backgrounds.some(a=>a.id===id&&a.mine))return;
 if(!window.confirm('Eliminare definitivamente questa immagine dalla libreria? La cancellazione è possibile solo se non è in uso.'))return;
 try{await request(`/sessions/${selected}/backgrounds/${id}`,'DELETE');await refreshAssets();setNotice('Immagine inutilizzata eliminata')}catch(e){setNotice(e instanceof Error&&e.message.includes('background_in_use')?'Impossibile eliminare: l’immagine è ancora in uso.':`Eliminazione non riuscita: ${e instanceof Error?e.message:String(e)}`)}
}
// List actions intentionally operate on the listed ID, not on the currently opened session.
// They must remain usable when restoring an old session fails (RC208).
async function resetListedSession(session:Session){
 if(!canResetListedSession({id:session.id,status:session.status,access_role:session.access_role||'collaborator'})||listSessionBusyRef.current)return;
 if(!window.confirm(`Riportare «${session.title}» a non avviata?\n\nSaranno cancellati DEFINITIVAMENTE partecipanti, risposte, voti, statistiche e file privati dei partecipanti. Pagine, widget e impostazioni resteranno. Il link pubblico sarà rigenerato.`))return;
 listSessionBusyRef.current=session.id;setListSessionBusy(session.id);
 try{
  await request(`/sessions/${encodeURIComponent(session.id)}/reset-to-ready`,'POST',{confirmation:'RESET_SESSION_RESULTS'});
  // A list reset must never reopen a broken dashboard or touch the auth cookies.
  if(selected===session.id){setSelected('');setSnap(null);setDesignActivity('');writeWorkspaceLocation({sessionId:'',section:'open',tab:'overview',pageId:''})}
  await load();setNotice(`Sessione «${session.title}» riportata a non avviata. Dati delle risposte eliminati e link pubblico rigenerato.`);
 }catch(e){notify(e)}finally{listSessionBusyRef.current=null;setListSessionBusy(null)}
}
async function deleteListedSession(session:Session){
 if(!canDeleteListedSession({id:session.id,status:session.status,access_role:session.access_role||'collaborator'})||listSessionBusyRef.current)return;
 if(!window.confirm(`Eliminare definitivamente la sessione «${session.title}»?\n\nSaranno cancellati anche le pagine, gli allegati, i partecipanti e tutti i risultati. Questa operazione non può essere annullata.`))return;
 listSessionBusyRef.current=session.id;setListSessionBusy(session.id);
 try{
  const response=await authenticatedFetch(`/api/sessions/${encodeURIComponent(session.id)}`,{method:'DELETE',credentials:'include'});
  if(!response.ok){const error=await response.json().catch(()=>({}));throw Error(error.error||`HTTP ${response.status}`)}
  if(selected===session.id){setSelected('');setSnap(null);setDesignActivity('');writeWorkspaceLocation({sessionId:'',section:'open',tab:'overview',pageId:''})}
  // Removing the final item in a paginated list must not strand an empty page.
  if(sessions.length===1&&sessionPage>1){setSessionPage(page=>Math.max(1,page-1))}
  else await load();
  setNotice(`Sessione «${session.title}» eliminata definitivamente.`);
 }catch(e){notify(e)}finally{listSessionBusyRef.current=null;setListSessionBusy(null)}
}
async function duplicateSessionFrom(sourceId:string){
 if(!sourceId||!window.confirm('Duplicare la sessione in una nuova bozza? Saranno copiati pagine, widget e allegati, ma NON partecipanti, risposte, voti, statistiche o cronologia.'))return;
 try{const result=await request<{id:string;status:'draft';data_copied:false}>(`/sessions/${sourceId}/duplicate`,'POST');await load();setSelected(result.id);setSnap(null);setDashboardPage('session');setSessionTab('overview');setNotice('Nuova bozza creata senza risposte, partecipanti o statistiche della sessione sorgente')}
 catch(e){notify(e)}
}
async function duplicateSelected(){if(selected)await duplicateSessionFrom(selected)}
async function importQuorivioBundle(file:File|undefined){
 if(!file||sidebarBusy)return;
 const preflight=localSessionImportError(file);
 if(preflight){setNotice(preflight);return}
 setSidebarBusy(true);
 try{
  const response=await authenticatedFetch('/api/sessions/import.quo',{method:'POST',credentials:'include',headers:{'Content-Type':LOCAL_SESSION_ARCHIVE_MIME},body:file});
  const result=await response.json().catch(()=>({}));
  if(!response.ok)throw Error(result.error||`Importazione non riuscita (HTTP ${response.status})`);
  if(typeof result.id!=='string'||!/^[0-9a-f-]{36}$/i.test(result.id))throw Error('Il server non ha restituito una sessione valida.');
  await load();setSelected(result.id);setSnap(null);setSelectedSessionRole('owner');setSessionTab('overview');setDashboardPage('session');
  setNotice('Sessione importata come nuova copia: pagine, schemi e allegati ripristinati. Risposte e partecipanti non inclusi.');
 }catch(e){notify(e)}finally{setSidebarBusy(false)}
}
async function exportSelectedSessionLocal(){
 if(!selected||!snap||sidebarBusy)return;
 setSidebarBusy(true);
 try{
  const response=await authenticatedFetch(`/api/sessions/${encodeURIComponent(selected)}/export.quo`,{credentials:'include',cache:'no-store'});
  if(!response.ok){const info=await response.json().catch(()=>({}));throw Error(info.error||`Esportazione non riuscita (HTTP ${response.status})`)}
  if(!isLocalSessionArchiveMime(response.headers.get('Content-Type')))throw Error('Il server non ha restituito un archivio Quorivio valido.');
  const reported=Number(response.headers.get('Content-Length'));
  if(reported>LOCAL_SESSION_ARCHIVE_MAX_BYTES)throw Error('Archivio oltre il limite di 100 MiB.');
  const blob=await response.blob();
  if(blob.size<22||blob.size>LOCAL_SESSION_ARCHIVE_MAX_BYTES)throw Error('Dimensione archivio non valida.');
  const url=URL.createObjectURL(blob);
  try{
   const link=document.createElement('a');link.href=url;link.download=localSessionArchiveFilename(snap.session.title);
   document.body.appendChild(link);link.click();link.remove();
  }finally{window.setTimeout(()=>URL.revokeObjectURL(url),60000)}
  setNotice('Archivio .quo pronto per il salvataggio locale. Include tutte le pagine e gli allegati privati della sessione, non i dati dei partecipanti.');
 }catch(e){notify(e)}finally{setSidebarBusy(false)}
}
async function importSessionFile(file:File|undefined){if(!file)return;try{if(file.size>2*1024*1024)throw Error('JSON oltre 2 MB');const body=JSON.parse(await file.text());const r=await request<{id:string}>('/sessions/import','POST',body);await load();setSelected(r.id);setDashboardPage('session');setNotice('Definizione sessione importata')}catch(e){notify(e)}}
async function transferPrimaryOwner(){
 if(!selected||!snap||snap.session.access_role!=='owner'||ownershipBusy||!ownershipTarget.trim())return;
 const target=ownershipTarget.trim().toLowerCase();
 if(!window.confirm(`Trasferire definitivamente la proprietà primaria di «${snap.session.title}» a ${target}? ${ownershipKeepPrevious?'Resterai collaboratore.':'Perderai l’accesso alla sessione.'}`))return;
 setOwnershipBusy(true);
 try{
  await request(`/sessions/${selected}/transfer-owner`,'POST',{email:target,keep_previous_as_collaborator:ownershipKeepPrevious});
  setOwnershipTarget('');await load();
  if(ownershipKeepPrevious){const updated=await request<Snapshot>(`/sessions/${selected}`);setSnap(normalizeOwnerSessionSnapshot(updated));setSelectedSessionRole('collaborator');}
  else{setSnap(null);setSelected('');setSelectedSessionRole(null);setDashboardPage('open');writeWorkspaceLocation({sessionId:'',section:'open',tab:'overview',pageId:''});}
  setNotice('Proprietà primaria trasferita. L’operazione è registrata nel log di audit.');
 }catch(e){notify(e)}finally{setOwnershipBusy(false)}
}
async function refreshCollaborators(){try{setCoPresenters(await request(`/sessions/${selected}/presenters`))}catch(e){notify(e)}}
async function addCollaborator(){try{await request(`/sessions/${selected}/presenters`,'POST',{email:coEmail.trim()});setCoEmail('');await refreshCollaborators()}catch(e){notify(e)}}
async function removeCollaborator(uid:string){if(!window.confirm('Rimuovere il co-presentatore?'))return;try{await request(`/sessions/${selected}/presenters/${uid}`,'DELETE');await refreshCollaborators()}catch(e){notify(e)}}
function beginActivityEdit(a:Activity){setEditingActivity(a.id);setEditTitle(a.title);setEditOpts(a.options.map(o=>`${o.id}|${o.label}`).join('\n'));setEditCorrect((a as any).correct_option_id||'')}
async function saveActivityEdit(){try{const original=snap?.activities.find(a=>a.id===editingActivity);if(!original)return;const next=editOpts.split('\n').filter(x=>x.trim()).map(x=>{const pos=x.indexOf('|');return {id:pos<0?'':x.slice(0,pos).trim(),label:pos<0?x.trim():x.slice(pos+1).trim()}});if(next.some(x=>!x.id||!x.label))throw Error('Ogni opzione deve conservare il suo ID: ID|testo');await request(`/sessions/${selected}/activities/${editingActivity}`,'PATCH',{title:editTitle,options:next,correct_option_id:['quiz','timed_quiz'].includes(original.type)?editCorrect:null});setEditingActivity('');setSnap(await request(`/sessions/${selected}`))}catch(e){notify(e)}}
async function invalidateActivity(a:Activity){if(!window.confirm('Invalidare tutte le risposte di questa attività? L’operazione è tracciata.'))return;try{await request(`/sessions/${selected}/activities/${a.id}/invalidate`,'POST');setSnap(await request(`/sessions/${selected}`))}catch(e){notify(e)}}
async function requestPasswordRecovery(){try{await request('/auth/password-reset/request','POST',{email});setNotice(lang==='it'?'Se l’account è registrato, riceverai un link di recupero.':'If the account exists, a recovery link will be emailed.')}catch(e){notify(e)}}
async function confirmPasswordRecovery(){if(resetSubmitLock.current||!resetToken||resetPassword.length<12||resetPassword!==resetPasswordConfirmation)return;resetSubmitLock.current=true;setResetSubmitPending(true);try{await request('/auth/password-reset/confirm','POST',{token:resetToken,new_password:resetPassword});setResetToken('');setResetPassword('');setResetPasswordConfirmation('');history.replaceState(null,'',location.pathname);setNotice(lang==='it'?'Password aggiornata. Accedi con la nuova password e il codice MFA, se richiesto.':'Password changed. Sign in with your new password and MFA code if enabled.')}catch(e){notify(e)}finally{resetSubmitLock.current=false;setResetSubmitPending(false)}}
async function handleLogin(e:React.FormEvent){e.preventDefault();try{const result=await request<any>(loginBackend==='ldap'?'/auth/ldap/login':'/auth/login','POST',{email,password});if(result.mfa_required){setEmailChallenge(result.challenge_id);setMfaMethods(result.methods);setMfaMethod(result.methods.includes('totp')?'totp':'email');setShowRecovery(false);setTotpCode('');setRecoveryCode('');return}setMe(await request('/auth/me'))}catch(e){notify(e)}}
async function chooseMfaMethod(method:string){setMfaMethod(method);setShowRecovery(false);if(method==='email'){try{await request('/auth/mfa/challenge/email','POST',{challenge_id:emailChallenge});setNotice('Codice email inviato / Email code sent')}catch(e){notify(e)}}}
async function verifyEmailLogin(){
  // Enter and the submit button share one path. A rapid repeated Enter cannot replay the code.
  if(mfaVerifyLock.current||!emailChallenge)return;
  if(mfaMethod==='email'?emailCode.length!==6:showRecovery?!recoveryCode.trim():totpCode.length!==6)return;
  mfaVerifyLock.current=true;
  setMfaVerifyPending(true);
  try{
    if(mfaMethod==='email')await request('/auth/email-mfa/verify','POST',{challenge_id:emailChallenge,code:emailCode});
    else await request('/auth/mfa/challenge/verify','POST',{challenge_id:emailChallenge,method:showRecovery?'recovery':'totp',code:showRecovery?recoveryCode:totpCode});
    setEmailChallenge('');setEmailCode('');setTotpCode('');setRecoveryCode('');
    setMe(await request('/auth/me'));
  }catch(e){notify(e)}finally{mfaVerifyLock.current=false;setMfaVerifyPending(false)}
}
async function register(){try{await request(loginBackend==='ldap'?'/auth/ldap/register':'/auth/register','POST',{email,password});setRegisterMode(false);setNotice(lang==='it'?'Registrazione ricevuta: attendi approvazione amministratore.':'Registration received: wait for administrator approval.');setPassword('')}catch(e){notify(e)}}
async function setResultsVisibility(visible:boolean){try{await request(`/sessions/${selected}/results-visibility`,'PATCH',{show_results:visible});setSnap(await request(`/sessions/${selected}`))}catch(e){notify(e)}}
async function setAnonymous(allowed:boolean){try{await request(`/sessions/${selected}/anonymous`,'PATCH',{allow_anonymous:allowed});setSnap(await request(`/sessions/${selected}`))}catch(e){notify(e)}}
async function createSession(){try{const s=await request<Session>('/sessions','POST',{title:newTitle,reference_date:newReferenceDate});setNewTitle('');await load();setSelected(s.id);setDashboardPage('session');setSessionTab('overview')}catch(e){notify(e)}}
// The single authenticated session fetch supplies both snapshot and role.
 // Session actions remain visible in the navigation sidebar while one session is open.
// Closing the viewer is deliberately distinct from terminating the live session.
function leaveCurrentSession(){if(!confirmSchemaNavigation())return;workspaceRestore.current={sessionId:'',section:'open',tab:'overview',pageId:''};writeWorkspaceLocation({sessionId:'',section:'open',tab:'overview',pageId:''});setSelectedSessionRole(null);setSidebarRename(null);setSelected('');setSnap(null);setDashboardPage('open');}
 function closeSidebarSession(){if(!sidebarBusy)leaveCurrentSession()}
 // Ending a live session remains exclusively in the explicit presenter 'Termina' control.
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
function insertSchemaWidget(kind:string,preset?:GraphicPreset,options?:{strokeWidth:number;strokeColor:string;fillColor:string;fillNone:boolean}){
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
  return [...old,{...template,id,kind,...(['image','video','logo','pdf'].includes(kind)?{assetId:schemaMediaAssets(kind)[0].id}:{}),label:['shape','line','footer'].includes(kind)?'':kind==='question'?'Nuova domanda':editorWidgetNames[kind]||'Widget',style:{...initialWidgetTextStyle(kind),...((template as any).style||{}),...(['shape','line'].includes(kind)?graphicStyle(kind as GraphicKind,preset,options):{fillNone:true,shapeType:'rectangle'})},position:{...placement,rotation:0}}];
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
 if(JSON.stringify(schemaWidgets)===schemaBaseline.current&&schemaBackgroundAsset===schemaBackgroundBaseline.current)return true;
 return window.confirm('Lo schema contiene modifiche non salvate. Uscire e scartarle?');
}
function navigateDashboard(page:typeof dashboardPage){if(confirmSchemaNavigation())setDashboardPage(page)}
function openSchemaEditor(){
 if(!selected||!snap)return;
 if(!confirmSchemaNavigation())return;
 const stored=snap.session.theme?.master?.widgets;
 const widgets=schemaStoredWidgets(stored);
 const initial=widgets.length?widgets:[newTitleWidget(snap.session.title),newFooterWidget('schema-footer')];
 schemaBaseline.current=JSON.stringify(widgets);schemaBackgroundBaseline.current=snap.session.theme?.master?.backgroundAssetId||'';setSchemaBackgroundAsset(schemaBackgroundBaseline.current);
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
  if(JSON.stringify(schemaStoredWidgets(fresh.session.theme?.master?.widgets))!==schemaBaseline.current||(fresh.session.theme?.master?.backgroundAssetId||'')!==schemaBackgroundBaseline.current){
   throw Error('Lo schema è stato aggiornato da un altro editor. Esci e riapri gli schemi per caricare la versione corrente.');
  }
  const theme={...(fresh.session.theme||{}),master:{...(fresh.session.theme?.master||{}),widgets:canonical,backgroundAssetId:schemaBackgroundAsset||undefined}};
  if(!validPageDesign(theme))throw Error('Il modello contiene widget o proprietà non valide');
  await request(`/sessions/${selected}/design`,'PATCH',{theme});
  setSnap(await request<Snapshot>(`/sessions/${selected}`));
  schemaBaseline.current=JSON.stringify(canonical);schemaBackgroundBaseline.current=schemaBackgroundAsset;
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
 const canonical=items.map(w=>{const original=desktop.get(w.id);return original?{...w,position:original.position,style:original.style}:{...w,position:{x:10,y:12,width:45,height:24,rotation:0}}});
 if(JSON.stringify(canonical)!==JSON.stringify(pageWidgets))setPageWidgets(canonical);
 setMobileLayoutDraft(old=>mergeMobilePositionEdits(pageWidgets,old,items));
}
function currentPageDraft():EditablePageDraft{const mobile=pruneMobilePageLayout(mobileLayoutDraft,pageWidgets);return {...(pageAudienceId?{audiencePageId:pageAudienceId}:{}),...(pagePresenterHidden?{presenterHidden:true}:{}),widgets:pageWidgets,questionHeader,resultHeader,questionBackground,resultBackground,questionBackgroundColor,resultBackgroundColor,questionBackgroundAsset,resultBackgroundAsset,...(Object.keys(mobile).length?{mobile}:{})}}
function pageDraftSignature(){return serializePageDraft(currentPageDraft())}
const mergePreview=mergeCandidate?mergePageDrafts(mergeCandidate.base??JSON.parse(savedPageDraft.current) as EditablePageDraft,mergeCandidate.local??currentPageDraft(),mergeCandidate.remote,mergeChoices):null;
const unresolvedMergeConflicts=mergePreview?.conflicts.filter(c=>!mergeChoices[c.path])||[];
function describeMergeValue(value:unknown):string{if(value===undefined)return '(elemento eliminato)';const raw=typeof value==='string'?value:JSON.stringify(value);return raw.length>240?raw.slice(0,240)+'…':raw}
async function inspectPageConflict(){if(!designActivity||pendingPageSave.current)return;try{const latest=await request<Snapshot>(`/sessions/${selected}`);const page=latest.activities.find(a=>a.id===designActivity) as any;if(!page){setNotice('La pagina non esiste più sul server: esporta la bozza locale prima di uscire.');return}const revision=validDesignRevision(page.design_revision)?page.design_revision:1;const remote=pageDraftFromActivity(page);mergePageDrafts(JSON.parse(savedPageDraft.current) as EditablePageDraft,currentPageDraft(),remote);setMergeChoices({});setMergeCandidate({remote,revision,snapshot:latest});setNotice('Confronto disponibile: scegli come risolvere ogni modifica incompatibile, poi applica la bozza riconciliata.')}catch(e){notify(e)}}
async function applyPageRebase(){if(!mergeCandidate||!mergePreview||unresolvedMergeConflicts.length||pendingPageSave.current)return;const draftAtClick=latestPageDraft.current;try{const fresh=await request<Snapshot>(`/sessions/${selected}`);const current=fresh.activities.find(a=>a.id===designActivity) as any;if(!current){setNotice('La pagina non esiste più: esporta la bozza locale.');return}const revision=validDesignRevision(current.design_revision)?current.design_revision:1;if(revision!==mergeCandidate.revision){setMergeCandidate({...mergeCandidate,remote:pageDraftFromActivity(current),revision,snapshot:fresh});setMergeChoices({});setNotice('Il server è cambiato durante il confronto. Rivedi i nuovi conflitti prima di applicare la bozza.');return}}catch(e){notify(e);return}if(latestPageDraft.current!==draftAtClick){setNotice('La bozza è cambiata durante il confronto. Verifica nuovamente le scelte prima di applicarle.');return}const d=mergePreview.draft;resetPageWidgets(d.widgets as any[]);setPageAudienceId(d.audiencePageId||'');setPagePresenterHidden(d.presenterHidden===true);setQuestionHeader(d.questionHeader);setResultHeader(d.resultHeader);setQuestionBackground(d.questionBackground);setResultBackground(d.resultBackground);setQuestionBackgroundColor(d.questionBackgroundColor);setResultBackgroundColor(d.resultBackgroundColor);setQuestionBackgroundAsset(d.questionBackgroundAsset);setResultBackgroundAsset(d.resultBackgroundAsset);setMobileLayoutDraft(d.mobile||{});loadedDesignRevision.current=mergeCandidate.revision;savedPageDraft.current=serializePageDraft(mergeCandidate.remote);setSnap(mergeCandidate.snapshot);setPageConflict(false);setMergeCandidate(null);setMergeChoices({});setNotice('Bozza riconciliata localmente. Controlla il layout e premi Salva layout per pubblicarla; nessuna modifica è stata ancora inviata.')}
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
  resetPageWidgets(backup.draft.widgets as any[]);setPageAudienceId(backup.draft.audiencePageId||'');setPagePresenterHidden(backup.draft.presenterHidden===true);
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
  const question={...(activity?.page_design||{}),audiencePageId:pageAudienceId||undefined,presenterHidden:pagePresenterHidden||undefined,header:questionHeader,widgets:pageWidgets.map(w=>w.kind==='rating'&&!w.label?.trim()?{...w,label:'Indice di gradimento'}:w),mobile:Object.keys(mobileLayoutDraft).length?pruneMobilePageLayout(mobileLayoutDraft,pageWidgets):undefined,backgroundUrl:questionBackground||undefined,backgroundColor:questionBackgroundColor||undefined,backgroundAssetId:questionBackgroundAsset||undefined};
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
  if(!persisted||persisted.design_revision!==saved.design_revision||stableJson(persisted.page_design?.widgets||[])!==stableJson(question.widgets)||stableJson(persisted.page_design?.mobile||{})!==stableJson(question.mobile||{})||persisted.page_design?.audiencePageId!==(question.audiencePageId||undefined)||Boolean(persisted.page_design?.presenterHidden)!==Boolean(question.presenterHidden)){
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
function beginPageDesign(a:Activity,skipNavigationConfirm=false){setSlideMasterDraft({...DEFAULT_TITLE_STYLE,...(snap?.session.theme?.master?.titleStyle||{})});if(designActivity&&designActivity!==a.id&&!skipNavigationConfirm&&!confirmPageNavigation())return;void request<any[]>(`/sessions/${selected}/presenter-profiles`).then(setAvailablePresenters).catch(()=>setAvailablePresenters([]));const x=a as any;setDesignActivity(a.id);setPageThumbMenu('');setPageContextOpen(false);setInspectedWidget('');resetPageWidgets((x.page_design?.widgets||[]).map((w:any)=>normalizeLegacyFooter(w)));setPageAudienceId(x.page_design?.audiencePageId||'');setPagePresenterHidden(x.page_design?.presenterHidden===true);setQuestionHeader(x.page_design?.header||'');setResultHeader(x.result_design?.header||'');setQuestionBackground(x.page_design?.backgroundUrl||'');setQuestionBackgroundColor(x.page_design?.backgroundColor||'');setResultBackground(x.result_design?.backgroundUrl||'');setResultBackgroundColor(x.result_design?.backgroundColor||'');setQuestionBackgroundAsset(x.page_design?.backgroundAssetId||'');setResultBackgroundAsset(x.result_design?.backgroundAssetId||'');setMobileLayoutDraft(x.page_design?.mobile||{});loadedDesignRevision.current=validDesignRevision(x.design_revision)?x.design_revision:1;setPageConflict(false);setMergeCandidate(null);setMergeChoices({});setAutoSaveBlockedSignature('');setPageSaveError('');savedPageDraft.current=serializePageDraft(pageDraftFromActivity(x))}
async function deleteCanvasPage(a:Activity){
 if(designActivity===a.id&&!confirmPageNavigation())return;
 if(!window.confirm(`Eliminare definitivamente la pagina "${a.title}" e le eventuali risposte associate? I collegamenti presenti in altre pagine verranno scollegati.`))return;
 try{
  const deletion=await request<{ok:boolean;detached_pages:number}>(`/sessions/${selected}/pages/${a.id}`,'DELETE');
  const updated=await request<Snapshot>(`/sessions/${selected}`);setSnap(updated);
  if(designActivity===a.id){const next=updated.activities[0];if(next)beginPageDesign(next);else setDesignActivity('')}
  setNotice(deletion.detached_pages?`Pagina eliminata. Scollegati i riferimenti presenti in ${deletion.detached_pages} altre pagine.`:'Pagina eliminata');
 }catch(e){notify(e)}
}
/** Operate on the *persisted* snapshot, not unsaved page drafts. Selection is
 * only a UI state; every mutation remains authenticated and server-authoritative. */
async function duplicateSelectedPages(fallbackId?:string){
 const snapshot=snap;if(!snapshot||pageBatchBusy||pageOrderPending||snapshot.session.status==='closed'||!confirmPageNavigation())return;
 const ids=orderedSelectedPageIds(snapshot.activities,selectedPageIds.length?selectedPageIds:fallbackId?[fallbackId]:designActivity?[designActivity]:[]);
 if(!ids.length)return;
 const original=snapshot.activities.map(p=>p.id);const copies=new Map<string,string>();
 setPageBatchBusy(true);setPageThumbMenu('');
 try{
  for(const id of ids){
   const before=new Set((await request<Snapshot>(`/sessions/${selected}`)).activities.map(p=>p.id));
   await request(`/sessions/${selected}/activities/${id}/duplicate`,'POST');
   const updated=await request<Snapshot>(`/sessions/${selected}`);
   const added=updated.activities.filter(p=>!before.has(p.id));
   if(added.length!==1)throw Error('La duplicazione non ha restituito una sola nuova pagina: controlla la sessione prima di riprovare.');
   copies.set(id,added[0].id);
  }
  const updated=await request<Snapshot>(`/sessions/${selected}`);
  const order=duplicatePageOrder(original,copies);
  if(order.length!==updated.activities.length)throw Error('Le pagine sono cambiate durante la duplicazione: riordino non applicato.');
  await request(`/sessions/${selected}/pages/order`,'PUT',{activity_ids:order});
  const verified=await request<Snapshot>(`/sessions/${selected}`);setSnap(verified);
  setSelectedPageIds([...copies.values()]);
  const first=verified.activities.find(a=>a.id===copies.get(ids[0]));if(first)beginPageDesign(first,true);
  setNotice(`${copies.size} pagine duplicate dopo le originali.`);
 }catch(e){notify(e);setSnap(await request<Snapshot>(`/sessions/${selected}`).catch(()=>snapshot))}finally{setPageBatchBusy(false)}
}
async function deleteSelectedPages(fallbackId?:string){
 const snapshot=snap;if(!snapshot||pageBatchBusy||pageOrderPending||snapshot.session.status==='closed'||!confirmPageNavigation())return;
 const ids=orderedSelectedPageIds(snapshot.activities,selectedPageIds.length?selectedPageIds:fallbackId?[fallbackId]:designActivity?[designActivity]:[]);
 if(!ids.length)return;
 if(!window.confirm(`Eliminare definitivamente ${ids.length} ${ids.length===1?'pagina':'pagine'} e le relative risposte? I riferimenti ad altre pagine saranno scollegati.`))return;
 setPageBatchBusy(true);setPageThumbMenu('');let deleted=0;
 try{
  for(const id of ids){await request(`/sessions/${selected}/pages/${id}`,'DELETE');deleted++}
  const updated=await request<Snapshot>(`/sessions/${selected}`);setSnap(updated);setSelectedPageIds([]);
  if(ids.includes(designActivity)){const next=updated.activities.find(a=>!ids.includes(a.id))||updated.activities[0];if(next)beginPageDesign(next,true);else setDesignActivity('')}
  setNotice(`${deleted} pagine eliminate.`);
 }catch(e){notify(e);setSnap(await request<Snapshot>(`/sessions/${selected}`).catch(()=>snapshot));setNotice(`${deleted} pagine eliminate prima dell'interruzione; verifica la selezione.`)}finally{setPageBatchBusy(false)}
}
async function renameSelectedPages(fallbackId?:string){
 const snapshot=snap;if(!snapshot||pageBatchBusy||snapshot.session.status==='closed')return;
 const ids=orderedSelectedPageIds(snapshot.activities,selectedPageIds.length?selectedPageIds:fallbackId?[fallbackId]:designActivity?[designActivity]:[]);
 for(const id of ids){const page=snapshot.activities.find(a=>a.id===id);if(page)await renameCanvasPage(page)}
}
function openSidebarEmptyMenu(event:{clientX:number;clientY:number}){
 const pages=snap?.activities||[];
 const chosen=selectedPageIds.find(id=>pages.some(a=>a.id===id))
  ||(pages.some(a=>a.id===designActivity)?designActivity:pages[0]?.id);
 if(chosen)openThumbnailMenu(chosen,event);
}
function openThumbnailMenu(id:string,event:{clientX:number;clientY:number;anchor?:{left:number;right:number;top:number;bottom:number}}){
 // Portal + viewport clamping: never clipped by the scrollable thumbnail rail.
 // DOMRect and PointerEvent coordinates are in *visual* CSS pixels. CSS zoom
 // scales the portal's fixed-position coordinates again, so convert the final
 // menu rectangle back into layout pixels (RC250, CI 42410387603).
 const rootZoom=Number.parseFloat(getComputedStyle(document.documentElement).zoom)||1;
 setPageMenuPosition(thumbnailMenuPosition(event.clientX,event.clientY,window.innerWidth,window.innerHeight,
  event.anchor,rootZoom));
 setPageExportError('');setSelectedPageIds(current=>current.includes(id)?current:[id]);setPageThumbMenu(id);
}
// A scrollable rail, keyboard focus, or zoom can move a thumbnail while its
// body-portal menu remains open. Re-anchor on capture-phase scroll and resize
// so its overlay cannot intercept the original trigger's next real click.
useEffect(()=>{
 if(!pageThumbMenu)return;
 const reposition=()=>{
  const button=document.querySelector<HTMLButtonElement>('.page-editor-thumb-menu-trigger[aria-expanded="true"]');
  if(!button)return;
  const rect=button.getBoundingClientRect();
  if(!rect.width||!rect.height)return;
  const rootZoom=Number.parseFloat(getComputedStyle(document.documentElement).zoom)||1;
  const next=thumbnailMenuPosition(rect.right+8,rect.top,window.innerWidth,window.innerHeight,
   {left:rect.left,right:rect.right,top:rect.top,bottom:rect.bottom},rootZoom);
  setPageMenuPosition(old=>old.left===next.left&&old.top===next.top&&old.maxHeight===next.maxHeight&&old.width===next.width?old:next);
 };
 reposition();
 window.addEventListener('scroll',reposition,true);
 window.addEventListener('resize',reposition);
 window.visualViewport?.addEventListener('resize',reposition);
 // A live app-wide zoom changes the root style, not necessarily window size.
 const zoomObserver=new MutationObserver(reposition);
 zoomObserver.observe(document.documentElement,{attributes:true,attributeFilter:['style']});
 return()=>{
  window.removeEventListener('scroll',reposition,true);
  window.removeEventListener('resize',reposition);
  window.visualViewport?.removeEventListener('resize',reposition);
  zoomObserver.disconnect();
 };
},[pageThumbMenu]);
useEffect(()=>{if(!designActivity||!snap)return;const onKey=(event:KeyboardEvent)=>{
 const target=event.target as HTMLElement|null;
 if(event.defaultPrevented||target?.closest('input,textarea,select,[contenteditable],[role="textbox"],[role="dialog"]'))return;
 const focusInThumbnails=!!target?.closest('.page-editor-thumbnails,.page-editor-thumb-menu-floating');
 const action=thumbnailShortcut(event,focusInThumbnails);
 // Destructive page shortcut requires focus in page strip; canvas widgets own Backspace.
 if(action==='delete'&&!focusInThumbnails)return;
 if(!action||pageBatchBusy||pageOrderPending||snap.session.status==='closed')return;
 event.preventDefault();event.stopImmediatePropagation();
 if(action==='duplicate')void duplicateSelectedPages();
 if(action==='rename')void renameSelectedPages();
 if(action==='delete')void deleteSelectedPages();
 };window.addEventListener('keydown',onKey,true);return()=>window.removeEventListener('keydown',onKey,true)
},[designActivity,snap,selectedPageIds,pageBatchBusy,pageOrderPending,pageHasUnsavedChanges]);
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
async function dropPageAtSlot(sourceId:string,slot:number){
 if(!snap||snap.session.status==='closed'||!confirmPageNavigation()||pageOrderRequestInFlight.current)return;
 try{
  const ids=snap.activities.map(a=>a.id);
  const reordered=movePageToSlot(ids,sourceId,slot);
  if(reordered.every((id,i)=>id===ids[i]))return;
  await persistPageOrder(reordered);
 }catch(e){notify(e)}
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
 if(!/\.(pdf|pptx)$/i.test(file.name)||file.size>50*1024*1024){setError('Seleziona un PDF o PPTX fino a 50 MiB');return}
 setAssetBusy(true);
 try{
  const response=await authenticatedFetch('/api/presentations/import-editable',{method:'POST',credentials:'include',headers:{'Content-Type':file.name.toLowerCase().endsWith('.pdf')?'application/pdf':'application/vnd.openxmlformats-officedocument.presentationml.presentation'},body:file});
  const result=await response.json();if(!response.ok)throw Error(result.error||`HTTP ${response.status}`);
  await load();setSelected(result.id);setSnap(null);setDashboardPage('session');
  setNotice(`${result.pages} pagine parzialmente modificabili importate. Verifica font, immagini, forme e impaginazione: la conversione non è fedele e non esegue OCR.`);
 }catch(e){notify(e)}finally{setAssetBusy(false)}
}
async function importPresentationFile(file:File|undefined,afterPageId?:string,imageFit:'contain'|'cover'|'fill'='cover',hideScheme=true){
 if(!file||!selected)return;
 if(designActivity&&!confirmPageNavigation())return;
 setPageExportError('');
 if(file.size>100*1024*1024){setError('File superiore a 100 MiB');return}
 const pdf=file.name.toLowerCase().endsWith('.pdf'),pptx=file.name.toLowerCase().endsWith('.pptx');
 if(!pdf&&!pptx){setError('Seleziona PDF o PPTX');return}
 setAssetBusy(true);
 try{
  const response=await authenticatedFetch(`/api/sessions/${selected}/presentation-import`,{method:'POST',credentials:'include',headers:{'Content-Type':pdf?'application/pdf':'application/vnd.openxmlformats-officedocument.presentationml.presentation','X-Quorivio-Image-Fit':imageFit,'X-Quorivio-Hide-Scheme':hideScheme?'1':'0'},body:file});
  const result=await response.json();if(!response.ok)throw Error(result.error||`HTTP ${response.status}`);
  let updated=await request<Snapshot>(`/sessions/${selected}`);
  const importedIds:Array<string>=Array.isArray(result.activity_ids)?result.activity_ids:[];
  if(!importedIds.length||!result.created)throw Error('Il convertitore non ha prodotto pagine. Verifica PDF/PPTX e configurazione del worker.');
  if(afterPageId){
   const original=updated.activities.map(activity=>activity.id).filter(id=>!importedIds.includes(id));
   const insertion=original.indexOf(afterPageId);
   if(insertion<0)throw Error('Importazione riuscita, ma la pagina di inserimento non è più presente. Ricarica le miniature.');
   await request(`/sessions/${selected}/pages/order`,'PUT',{activity_ids:[...original.slice(0,insertion+1),...importedIds,...original.slice(insertion+1)]});
   updated=await request<Snapshot>(`/sessions/${selected}`);
  }
  setSnap(updated);await refreshAssets();
  const imported=updated.activities.find(activity=>activity.id===importedIds[0]);
  if(imported&&designActivity)beginPageDesign(imported,true);
  setNotice(`${importedIds.length} pagine importate${afterPageId?' dopo la miniatura selezionata':''}${designActivity?'; prima pagina aperta nell’editor':''}.`);
 }catch(e){
  const message=e instanceof Error?e.message:String(e);
  const readable=message==='conversion_failed'?'Conversione non riuscita: il documento non è stato elaborato. Controlla i log del converter e verifica che sia installata la nuova immagine con correzione dei volumi temporanei.':message==='conversion_worker_not_configured'?'Convertitore PDF/PPTX non disponibile: apri Amministrazione → Configurazione server → Convertitore PDF/PowerPoint e verifica prerequisiti e stato del worker.':message==='conversion_worker_unavailable'?'Convertitore isolato PDF/PPTX non raggiungibile: l’amministratore deve verificare stato e log del worker da Configurazione server.':message;
  setPageExportError('Importazione PDF/PPTX non riuscita: '+readable);setNotice('Importazione PDF/PPTX non riuscita: '+readable);
 }finally{setAssetBusy(false)}
}
async function importSlideImages(files:FileList|null){if(!files?.length||!selected)return;if(files.length>100){setError('Massimo 100 immagini per importazione');return}setAssetBusy(true);try{let created=0;for(const [index,file] of Array.from(files).entries()){
const mime=mediaUploadMime(file,'image');
if(!mime||!['image/png','image/jpeg','image/webp'].includes(mime)||file.size>100*1024*1024)throw Error(`Formato o dimensione non validi: ${file.name}`);
const asset=await uploadNamedFile(file,mime,'assets');if(!asset)continue;const title=file.name.replace(/\.[^.]+$/,'').slice(0,240)||`Slide ${index+1}`;
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
async function deleteSession(){if(!window.confirm(lang==='it'?'Eliminare definitivamente la sessione e tutte le risposte?':'Permanently delete this session and all responses?'))return;try{await authenticatedFetch(`/api/sessions/${selected}`,{method:'DELETE',credentials:'include'}).then(r=>{if(!r.ok)throw Error(`HTTP ${r.status}`)});setSelected('');setDashboardPage('open');setSnap(null);await load()}catch(e){notify(e)}}
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
useEffect(()=>{setRatingSent([]);setRatingComments({});setSelectedReaction('');setMultipleAnswers([]);setAnswer('');setFreeText('');setSent(false);setVotePending(false)},[entry?.activity?.id,entry?.activity?.opened_at]);const current= snap?.activities.find(a=>a.id===snap.session.current_activity_id);const showResults=(s:Snapshot,a:Activity,mode="bars")=>{const results=Array.isArray(s?.results)?s.results:[];const options=Array.isArray(a?.options)?a.options:[];const rows=options.filter(o=>o&&typeof o.id==='string').map(o=>{const raw=results.find(r=>r&&r.activity_id===a.id&&r.option_id===o.id)?.count;const count=Number(raw);return {...o,count:Number.isFinite(count)&&count>0?count:0}});const total=rows.reduce((n,r)=>n+r.count,0);return <div className="results">{mode==="pie"&&total>0&&<div className="result-pie" role="img" aria-label="Distribuzione percentuale delle risposte" style={{background:`conic-gradient(${rows.map((r,i)=>`hsl(${(i*137.5)%360} 62% 53%) ${rows.slice(0,i).reduce((n,x)=>n+x.count,0)/total*100}% ${rows.slice(0,i+1).reduce((n,x)=>n+x.count,0)/total*100}%`).join(",")})`}}/>}{rows.map(r=><div className="result" key={r.id}><div className="result-heading"><span>{r.label}</span><strong>{r.count} · {total?Math.round(r.count/total*100):0}%</strong></div>{mode==="bars"&&<div className="bar-track"><div className="bar" style={{width:`${total?r.count/total*100:0}%`}}/></div>}</div>)}<p className="muted">{total} risposte</p></div>};
return <div className="app"><a className="skip-link" href="#main-content">{pc.skip}</a><header><a className="brand" href="/"><img src="/editor-quorivio-logo.svg" alt="Quorivio" style={{height:35,maxWidth:172}}/></a><nav><a href={`/docs/manuals/user-guide.${lang}.pdf`} target="_blank" rel="noreferrer">{lang==='it'?'Manuale utente':'User guide'}</a>{me&&<a href={`/docs/manuals/presenter-guide.${lang}.pdf`} target="_blank" rel="noreferrer">{lang==='it'?'Manuale presentatore':'Presenter guide'}</a>}{me&&<a href={`/docs/manuals/admin-guide.${lang}.pdf`} target="_blank" rel="noreferrer">{lang==='it'?'Manuale amministratore':'Administrator guide'}</a>}<span className="version">0.1.0-dev</span><button className="small ghost" onClick={()=>setLang(lang==='it'?'en':'it')} aria-label={lang==='it'?'Switch interface language to English':'Passa la lingua dell’interfaccia in italiano'} title={lang==='it'?'Switch all menus and interface text to English':'Cambia tutti i menu e i testi in italiano'}>{lang==='it'?'🇬🇧 English':'🇮🇹 Italiano'}</button>{me&&!joinPath&&<button className="small ghost" onClick={async()=>{await request('/auth/logout','POST');writeWorkspaceLocation({sessionId:'',section:'workspace',tab:'overview',pageId:''});setMe(null);setSelected('');setSnap(null);setDesignActivity('');setDashboardPage('workspace')}}><LogOut size={16}/> Logout</button>}</nav></header>{!me&&(new URLSearchParams(location.search).has('reauthentication_required')||new URLSearchParams(location.search).has('authentication_required'))&&<p className="alert" role="status">Sessione scaduta: accedi nuovamente per continuare.</p>}{notice&&<div role="status" className="alert" onClick={()=>setNotice('')}>{notice} <button className="small outline" type="button" onClick={e=>{e.stopPropagation();setNotice('')}} aria-label="Chiudi messaggio">×</button></div>}{error&&<div role="alert" className="alert" onClick={()=>setError('')}>{error} <button className="small outline" type="button" onClick={e=>{e.stopPropagation();setError('')}} aria-label="Chiudi errore">×</button></div>}{!cookieAcknowledged&&createPortal(<dialog ref={node=>{if(node&&!node.open)node.showModal()}} aria-label="Informativa cookie funzionali" className="panel functional-cookie-dialog" onCancel={event=>event.preventDefault()}><h3>Cookie funzionali</h3><p>Quorivio utilizza cookie tecnici necessari per autenticazione, sessioni e sicurezza. Non sono utilizzati cookie di profilazione da questa funzione.</p><button className="primary small" onClick={()=>{document.cookie='q_cookie_notice=ack; Max-Age=31536000; Path=/; SameSite=Lax'+(location.protocol==='https:'?'; Secure':'');setCookieAcknowledged(true)}}>Ho capito</button></dialog>,document.body)}
{joinPath?<main id="main-content" className={"narrow participant-live-view"+(participantSlideActive?" participant-slide-active":"")} style={{backgroundColor:"transparent",backgroundImage:"none"}}>{!participantSlideActive&&(entry?.theme?.logos||[]).map((url:string,i:number)=><img key={i} src={url} alt="Logo organizzazione" style={{maxHeight:72,maxWidth:210,marginRight:12}}/>)}<div className="eyebrow"><Radio size={17}/> LIVE SESSION</div><h1 className={participantSlideActive?"participant-session-heading-offscreen":undefined}>{entry?.session?.title||'Sessione non disponibile'}</h1>{joinStatus==='loading'?<section className="panel centered" role="status">{pc.loading}</section>:joinStatus==='unavailable'?<section className="panel centered" role="alert"><h2>{pc.unavailable}</h2><p>{pc.unavailableHelp}</p><button type="button" onClick={()=>void refreshPublicEntry()}>{pc.retry}</button><a href="/">{pc.another}</a></section>:!participantReady?<section className="panel centered" role="status">{pc.checking}</section>:entry?.session&&(!joined?<section className="panel centered"><Users size={42} className="accent"/><h2>Partecipa alla sessione</h2><p>Puoi accedere senza account scegliendo uno pseudonimo, se il presentatore abilita gli anonimi. I cookie funzionali sono necessari per ritrovare la partecipazione dopo la riapertura del browser.</p><label>Pseudonimo<input autoComplete="nickname" value={pseudonym} maxLength={40} onChange={e=>setPseudonym(e.target.value)}/></label><label><input type="checkbox" checked={consent} onChange={e=>setConsent(e.target.checked)}/> Accetto i cookie funzionali necessari al servizio</label>{entry.allow_anonymous===false?<p>Accesso anonimo disabilitato: effettua l’accesso con un account approvato.</p>:<button type="button" className="primary" disabled={joinPending||!consent||pseudonym.trim().length<2} onClick={()=>void join()}>{joinPending?pc.joining:t.enter} <ArrowRight size={18}/></button>}</section>:entry?.session?.status!=='active'?<section className="panel centered" role="status"><h2>{pc.paused}</h2><p>{pc.pausedHelp}</p></section>:entry?.activity?<section className="panel"><p className="participant-connection" role="status" aria-live="polite">{liveConnection==='connected'?pc.connected:liveConnection==='connecting'?pc.connecting:liveConnection==='blocked'?pc.blocked:pc.disconnected}</p><span className="pill">{entry.activity.type==='slide'?'Slide':entry.activity.type==='timed_quiz'?'Quiz a tempo':entry.activity.type==='quiz'?'Quiz':'Sondaggio'}</span>{!entry.activity.page_design?.importedImageFit&&!resolveSlideMasterWidgets(entry.activity.page_design?.widgets||[],entry?.theme?.master?.widgets).length&&<h2>{entry.activity.page_design?.header||entry.activity.title}</h2>}{entry.activity.type==='timed_quiz'&&<PageTimer openedAt={entry.activity.opened_at} duration={entry.activity.duration_seconds} label="Quiz a tempo"/>}{!audienceAuthoredWidgets.length&&(entry.activity.page_design?.media||[]).map((m:any,i:number)=>m.kind==='image'?<img key={i} src={m.url} alt={m.alt||'Media'} style={{maxWidth:'100%'}}/>:m.kind==='video'?<video key={i} controls src={m.url} style={{maxWidth:'100%'}}/>:<a key={i} href={m.url} target="_blank" rel="noreferrer">Apri documento PDF</a>)}<div className="audience-layout-controls" role="group" aria-label="Visualizzazione della pagina"><button type="button" aria-pressed={!participantReadingMode&&!audiencePortrait} onClick={()=>{setParticipantModeExplicit(true);setParticipantReadingMode(false);setParticipantPhoneMode(false)}}>Diapositiva 16:9</button><button type="button" aria-pressed={!!audiencePortrait} onClick={()=>{setParticipantModeExplicit(true);setParticipantReadingMode(false);setParticipantPhoneMode(true)}}>Layout smartphone</button><button type="button" aria-pressed={participantReadingMode} onClick={()=>{setParticipantModeExplicit(true);setParticipantReadingMode(true);setParticipantPhoneMode(false)}}>Lettura accessibile</button></div><div className="audience-stage-scroll" role="region" aria-label="Contenuto della diapositiva" tabIndex={0}><div ref={element=>{if(element)element.inert=audienceTimerExpired}} className={'audience-widget-layout'+(audiencePortrait?' stage-phone':participantReadingMode?' stage-reading':' stage-fidelity')} style={{position:'relative',...(audiencePortrait&&!entry.activity.page_design?.importedImageFit?{height:audiencePhoneLayout.height,backgroundImage:entry.activity.page_design?.mobile?.backgroundAssetId?`url(/api/join/${encodeURIComponent(joinCode)}/activities/${encodeURIComponent(entry.activity.id)}/media/${encodeURIComponent(entry.activity.page_design.mobile.backgroundAssetId)})`:'none',backgroundColor:entry.activity.page_design?.mobile?.backgroundColor||'#ffffff',backgroundSize:'cover',backgroundPosition:'center'}:participantReadingMode?{backgroundImage:"none",backgroundColor:"#ffffff",backgroundSize:"auto"}:{...(audiencePortrait?{height:audiencePhoneLayout.height}:{}),...slideBackgroundCss(entry.activity.page_design,entry.theme,id=>`/api/join/${encodeURIComponent(joinCode)}/activities/${encodeURIComponent(entry.activity.id)}/media/${encodeURIComponent(id)}`)})}}>{(audiencePortrait?audiencePhoneLayout.widgets:participantReadingMode?audienceReadingWidgets:audienceVisibleWidgets).map((w:any)=><div key={w.id} data-widget-kind={w.kind} className={`page-widget widget-${w.style?.animation||'none'}`} data-show-title={widgetTitleVisible(w)} data-vertical-align={w.style?.verticalAlign||'top'} data-footer-separator={w.kind==='footer'?String(w.footerSeparator!==false):undefined} {...widgetArtData(w.style)} style={{...(w.position?widgetGeometryStyle(w.position):{}),...(w.position?{'--stage-x':w.position.x+'%','--stage-y':w.position.y+'%','--stage-width':w.position.width+'%','--stage-height':(w.position.height??24)+'%','--stage-rotation':(w.position.rotation??0)+'deg'}:{}),...widgetAppearanceStyle(w.style,w.style?.fillImageAssetId?`/api/join/${encodeURIComponent(joinCode)}/activities/${entry.activity.id}/media/${w.style.fillImageAssetId}`:undefined),...stageWidgetTypography(w,{pageTitle:entry.activity.title,masterTitleStyle:entry.theme?.master?.titleStyle},audiencePortrait)} as React.CSSProperties}>{w.kind!=='shape'&&<WidgetShapeOutline style={w.style}/>}<WidgetGraphic kind={w.kind} style={w.style}/><WidgetContentFit allowScale={w.autoFit!==false&&!['qr','participant-count'].includes(w.kind)}>{['title','footer','text','postit','divider','shape','line'].includes(w.kind)?<ProjectionWidgetContent sessionId={entry.session.id} widget={w} activity={entry.activity} joinCode={joinCode} sessionTitle={entry.session.title} pageNumber={Math.max(1,Number(entry.session.presenter_page_number)||Number(entry.activity.position)+1)} masterTitleStyle={entry.theme?.master?.titleStyle}/>:w.kind==='rating'?<RatingStageContent widget={w} comment={ratingComments[w.id]||''} disabled={ratingPending.includes(w.id)} onCommentChange={value=>setRatingComments(old=>({...old,[w.id]:value}))} selected={ratingVotes[entry.activity.id+':'+w.id]} onSelect={n=>void ratePage(n,w.id)}/>:w.kind==='profile'?<PresenterProfileWidget code={joinCode} presenterId={w.presenterId} label={w.label} showEmail={w.showEmail===true}/>:['image','logo'].includes(w.kind)&&w.assetId?<CroppedImage className="projection-media" src={`/api/join/${encodeURIComponent(joinCode)}/activities/${encodeURIComponent(entry.activity.id)}/media/${encodeURIComponent(w.assetId)}`} crop={w.crop} alt={w.label||'Immagine'}/>:w.kind==='pdf'&&w.assetId?<a href={`/api/join/${encodeURIComponent(joinCode)}/activities/${entry.activity.id}/media/${w.assetId}`} target="_blank" rel="noopener noreferrer">Apri PDF</a>:w.kind==='video'&&w.assetId?<video className="projection-media" controls preload="metadata" style={{maxWidth:'100%'}} src={`/api/join/${encodeURIComponent(joinCode)}/activities/${entry.activity.id}/media/${w.assetId}`}/>:w.kind==='postit'?<div className="rehearsal-postit" style={{whiteSpace:'pre-wrap',backgroundColor:w.style?.fillNone?'transparent':w.style?.fillColor||undefined,textAlign:w.style?.textAlign||undefined}}>{w.description&&w.description.startsWith(w.label||'')?<WidgetStyledText text={w.description} widget={w} field="description"/>:<><WidgetStyledText text={w.label||'Nota'} widget={w} field="label"/>{w.description&&<> {'\n'}<WidgetStyledText text={w.description} widget={w} field="description"/></>}</>}</div>:w.kind==='text'?<p style={{whiteSpace:'pre-wrap',textAlign:w.style?.textAlign||undefined}}>{w.description&&w.description.startsWith(w.label||'')?<WidgetStyledText text={w.description} widget={w} field="description"/>:<><WidgetStyledText text={w.label||''} widget={w} field="label"/>{w.description&&<> {'\n'}<WidgetStyledText text={w.description} widget={w} field="description"/></>}</>}</p>:w.kind==='divider'?<hr/>:w.kind==='footer'?<div className="projection-slide-footer" style={widgetDisplay(w,{sessionTitle:entry.session?.title,pageNumber:Math.max(1,Number(entry.session.presenter_page_number)||Number(entry.activity.position)+1)}).style as React.CSSProperties}><span className="slide-footer-center">{w.showTitle===false?'':widgetDisplay(w,{sessionTitle:entry.session?.title,pageNumber:Math.max(1,Number(entry.session.presenter_page_number)||Number(entry.activity.position)+1)}).center}</span></div>:w.kind==='timer'?<PageTimer openedAt={entry.activity.opened_at} duration={entry.activity.duration_seconds} label={w.label} face={widgetTimerFace(w.style)}/>:w.kind==='qr'?<ParticipantAccessQr sessionId={entry.session.id} joinCode={joinCode} publicAccess widget={w}/>:w.kind==='question'?<QuestionWidget key={`${entry.activity.id}:${entry.activity.opened_at}:${w.id}`} code={joinCode} activityId={entry.activity.id} widget={w}/>:w.kind==='timed-quiz'?<><PageTimer openedAt={entry.activity.opened_at} duration={w.durationSeconds||30} label={w.label||'Quiz a tempo'} face={widgetTimerFace(w.style)}/><QuestionWidget key={`${entry.activity.id}:${entry.activity.opened_at}:${w.id}`} code={joinCode} activityId={entry.activity.id} widget={w}/></>:w.kind==='results-button'?null:w.kind==='topic-question'?<TopicQuestionWidget code={joinCode} activityId={entry.activity.id} widget={w}/>:w.kind==='reactions'?<div className="projection-sample-reactions">{w.showTitle!==false&&<strong><WidgetStyledText text={w.label||'Reazioni'} widget={w} field="label"/></strong>}<ReactionChoices size={w.reactionIconSize||32} selected={selectedReaction} onSelect={emoji=>void react(emoji)}/></div>:(w.kind==='shape'||w.kind==='line')?null:w.kind==='participant-count'?<div className="widget-live-count"><strong>{w.label||'Partecipanti connessi'}</strong><span>{entry.activity.connected_participants??0}</span></div>:null}</WidgetContentFit></div>)}<SlideCanvasNumber widgets={entry.activity.page_design?.suppressMaster?(entry.activity.page_design?.widgets||[]):resolveSlideMasterWidgets(entry.activity.page_design?.widgets||[],entry?.theme?.master?.widgets)} pageNumber={Math.max(1,Number(entry.session.presenter_page_number)||Number(entry.activity.position)+1)}/></div></div>{audienceTimerExpired&&<p role="status" className="notice">Tempo scaduto: le interazioni con i widget sono terminate.</p>}{(entry.activity.page_design?.widgets||[]).length||entry.activity.type==='slide'?null:sent?<div className="success" role="status" aria-live="polite"><ShieldCheck size={36}/><h3>{t.thankyou}</h3><p>Attendi la prossima attività.</p></div>:entry.activity.status!=='open'?<p>Questa attività è chiusa.</p>:<>{(entry.activity.answer_mode==='text')?<textarea aria-label="La tua risposta" rows={5} maxLength={5000} value={freeText} onChange={e=>setFreeText(e.target.value)} placeholder="Scrivi la tua risposta"/>:(entry.activity.answer_mode==='file')?<p>Carica un allegato usando l'upload della sessione e indica il suo identificativo.<input value={answer} onChange={e=>setAnswer(e.target.value)} placeholder="UUID allegato"/></p>:<div className="choices" role="group" aria-label="Opzioni di risposta">{entry.activity.options.map((o:any)=><button type="button" aria-pressed={entry.activity.answer_mode==='multiple'?multipleAnswers.includes(o.id):answer===o.id} disabled={votePending} className={(entry.activity.answer_mode==='multiple'?multipleAnswers.includes(o.id):answer===o.id)?'choice active':'choice'} key={o.id} onClick={()=>entry.activity.answer_mode==='multiple'?setMultipleAnswers(prev=>prev.includes(o.id)?prev.filter(x=>x!==o.id):[...prev,o.id]):setAnswer(o.id)}>{o.label}</button>)}</div>}<button type="button" disabled={votePending||!canSubmitParticipantAnswer(entry.activity.answer_mode||'single',entry.activity.answer_required!==false,{answer,multipleAnswers,freeText})} className="primary" onClick={()=>void vote()}>{votePending?pc.sending:t.vote} <ArrowRight size={18}/></button></>}</section>:<section className="panel centered"><Wifi size={36}/><h2>Sei connesso</h2><p>Il presentatore avvierà presto un’attività.</p></section>)}</main>:
publicPath?<PresenterLiveScreen sessionId={publicId} renderResults={showResults}/>:
me===undefined?<main id="main-content" className="narrow">Caricamento...</main>:me?.must_change_password?<main id="main-content" className="narrow"><section className="panel"><h1>Modifica obbligatoria della password</h1><p>Prima di utilizzare Quorivio, imposta una password personale di almeno 12 caratteri.</p><label>Nuova password<input type="password" autoComplete="new-password" value={newPassword} onChange={e=>setNewPassword(e.target.value)}/></label><label>Conferma nuova password<input type="password" autoComplete="new-password" value={confirmNewPassword} onChange={e=>setConfirmNewPassword(e.target.value)}/></label><button className="primary" disabled={newPassword.length<12||newPassword!==confirmNewPassword} onClick={async()=>{try{await request('/auth/change-password','POST',{current_password:password,new_password:newPassword});setMe(null);setSelected('');setNewPassword('');setConfirmNewPassword('');setPassword('');setError('');setNotice('Password aggiornata: accedi nuovamente con la nuova password.')}catch(e){notify(e)}}}>Aggiorna password</button></section></main>:!me&&resetToken?<main id="main-content" className="narrow"><form className="panel" aria-labelledby="reset-password-title" onSubmit={e=>{e.preventDefault();void confirmPasswordRecovery()}}><h1 id="reset-password-title">Recupero password / Password reset</h1><label>Nuova password / New password<input type="password" autoComplete="new-password" minLength={12} maxLength={256} value={resetPassword} onChange={e=>setResetPassword(e.target.value)}/></label><label>Conferma nuova password / Confirm new password<input type="password" autoComplete="new-password" minLength={12} maxLength={256} value={resetPasswordConfirmation} onChange={e=>setResetPasswordConfirmation(e.target.value)}/></label>{resetPasswordConfirmation&&resetPassword!==resetPasswordConfirmation&&<p role="status" className="muted tiny">Le password non coincidono. / Passwords do not match.</p>}<button className="primary" disabled={resetSubmitPending||!resetToken||resetPassword.length<12||resetPassword!==resetPasswordConfirmation} type="submit">{resetSubmitPending?"Verifica in corso… / Verifying…":"Conferma / Confirm"}</button><p className="muted tiny">L’autenticazione a due fattori resta attiva. / MFA remains enabled.</p></form></main>:!me?<main id="main-content" className="hero login-manual-cover"><div><div className="eyebrow"><span className="live-dot"/> INTERACTIVE PRESENTATIONS, REIMAGINED</div><h1>Ogni voce<br/>conta<span className="brand-dot">.</span></h1><p className="lead">{t.subtitle}. Crea esperienze live con sondaggi, quiz e risultati istantanei.</p><div className="join-by-code"><input aria-label="Codice sessione" placeholder="Codice sessione" value={code} onChange={e=>setCode(normalizeJoinCode(e.target.value))}/><button className="outline" disabled={!code.trim()} onClick={()=>location.assign(`/join/${encodeURIComponent(code.trim())}`)}>Partecipa <ArrowRight size={16}/></button></div><div className="features"><span><Radio size={17}/> Live polls</span><span><Users size={17}/> Audience first</span><span><BarChart3 size={17}/> Real-time insights</span></div></div>{emailChallenge&&<form className="panel login" aria-label="Secondo fattore" onSubmit={e=>{e.preventDefault();void verifyEmailLogin()}}><h3>Verifica secondo fattore / Second factor</h3><div className="downloads">{mfaMethods.map(method=><button type="button" key={method} className={mfaMethod===method?'primary small':'outline small'} onClick={()=>void chooseMfaMethod(method)}>{method==='email'?'Email':'Authenticator TOTP'}</button>)}</div>{mfaMethod==='email'?<label>Codice email<input inputMode="numeric" autoComplete="one-time-code" value={emailCode} maxLength={6} onChange={e=>setEmailCode(e.target.value.replace(/\D/g,''))}/></label>:<>{showRecovery?<label>Codice di recupero<input autoComplete="off" value={recoveryCode} onChange={e=>setRecoveryCode(e.target.value)}/></label>:<label>Codice autenticatore<input inputMode="numeric" autoComplete="one-time-code" value={totpCode} maxLength={6} onChange={e=>setTotpCode(e.target.value.replace(/\D/g,''))}/></label>}<button type="button" className="small outline" onClick={()=>setShowRecovery(v=>!v)}>{showRecovery?'Usa autenticatore':'Usa codice di recupero'}</button></>}<div className="downloads"><button type="submit" disabled={mfaVerifyPending||(mfaMethod==='email'?emailCode.length!==6:showRecovery?!recoveryCode.trim():totpCode.length!==6)}>Verifica / Verify</button><button type="button" className="outline small" onClick={()=>{setEmailChallenge('');setEmailCode('')}}>Annulla</button></div></form>}{!emailChallenge&&<form className="panel login" onSubmit={e=>{if(registerMode){e.preventDefault();register()}else handleLogin(e)}}><div className="eyebrow">PRESENTER STUDIO</div><h2>{registerMode?"Registrazione nuovo utente":t.login}</h2><label>{registerMode?t.email:"Email o nickname"}<input type={registerMode?"email":"text"} autoComplete="username" required value={email} onChange={e=>setEmail(e.target.value)}/></label><label>{t.password}<input type="password" required value={password} onChange={e=>setPassword(e.target.value)}/></label>{ldapStatus.enabled&&<fieldset className="login-backend-selector"><legend>{registerMode?'Backend di registrazione':'Backend di autenticazione'}</legend><label><input type="radio" name="authentication-backend" checked={loginBackend==='local'} onChange={()=>setLoginBackend('local')}/> Locale</label><label><input type="radio" name="authentication-backend" checked={loginBackend==='ldap'} onChange={()=>setLoginBackend('ldap')}/> {ldapStatus.label}</label></fieldset>}<button className="primary">{registerMode?"Invia richiesta di registrazione":"Accedi"} <ArrowRight size={18}/></button><button type="button" className="outline small" onClick={()=>setRegisterMode(!registerMode)}>{registerMode?"Torna al login":"Registrati"}</button><p className="muted tiny">Accesso locale · Configurazione amministratore</p><p className="muted tiny">Nuovi account soggetti all'approvazione dell'amministratore.</p><button type="button" className="outline small" onClick={requestPasswordRecovery} disabled={!email.includes('@')}>Password dimenticata? / Forgot password?</button>{oidcProviders.length>0&&<div className="oidc-options"><p>SSO / Federated sign-in</p>{oidcProviders.map(p=><a key={p.id} className="button outline small" href={'/api/auth/'+(['github','facebook'].includes(p.id)?'social':'oidc')+'/'+encodeURIComponent(p.id)+'/start'}>Accedi con {p.label||p.id.toUpperCase()}</a>)}</div>}</form>}</main>:
<main id="main-content" className="dashboard"><div className="aside"><section className="panel dashboard-nav" aria-label="Navigazione funzionalità"><h3>Sezioni</h3>{([['new','Nuova sessione'],['open','Apri sessione'],['calendar','Calendario'],['profile','Profilo presentatore'],['mfa','Sicurezza / MFA'],['sso','SSO / Identità'],...(me?.role==='platform_admin'?([['users','Gestione utenti'],['settings','Impostazioni server']] as const):[])] as const).map(([key,label])=>{const Icon=key==='new'?Plus:key==='open'?BookImage:key==='calendar'?Clock3:key==='profile'?UserCircle:key==='mfa'?ShieldCheck:key==='sso'?Users:key==='users'?Users:Settings2;return <button key={key} className={dashboardPage===key?'session selected':'session'} aria-current={dashboardPage===key?'page':undefined} style={{width:'100%',marginBottom:7}} onClick={()=>navigateDashboard(key)}><Icon size={18} aria-hidden="true"/>{translateUiText(label,lang)}</button>})}<button type="button" className="session local-session-import" disabled={sidebarBusy} onClick={()=>localSessionImportRef.current?.click()} aria-label="Importa sessione da archivio .quo locale" style={{width:'100%',marginTop:8}}><Upload size={17}/> Importa sessione da locale</button><input ref={localSessionImportRef} type="file" accept=".quo,application/vnd.quorivio.session+zip" hidden aria-label="Seleziona archivio sessione .quo" onChange={e=>{const file=e.currentTarget.files?.[0];e.currentTarget.value='';void importQuorivioBundle(file)}}/></section>{selected&&snap&&<section className="panel" aria-label="Modelli della sessione"><button type="button" className="small outline dashboard-schemes-shortcut" onClick={openSchemaEditor} disabled={sidebarBusy} aria-label="Apri editor degli schemi della sessione">▤ Editor degli schemi</button><p className="muted tiny">Titolo, footer e modelli globali</p></section>}{selected&&dashboardPage==='session'&&snap&&<section className="panel current-session-actions" aria-label="Azioni della sessione corrente">
  <h3>Sessione aperta</h3><strong className="current-session-name">{snap.session.title}</strong>
  <p className="muted tiny">Stato: {snap.session.status}</p>
  <button type="button" className="small outline" onClick={leaveCurrentSession} disabled={sidebarBusy}>Torna alle sessioni</button>
  <button type="button" className="small outline" disabled={sidebarBusy} onClick={closeSidebarSession} title="Chiude soltanto questa vista: presentazione e partecipanti restano attivi.">Chiudi sessione</button>
  <button type="button" className="small outline" disabled={sidebarBusy} onClick={()=>void duplicateSelected()}>Duplica sessione</button>
  <button type="button" className="small outline" disabled={sidebarBusy} onClick={()=>void exportSelectedSessionLocal()} aria-label="Esporta copia completa della sessione in locale (.quo)"><Download size={16}/> Esporta in locale (.quo)</button>
  <button type="button" className="small outline" disabled={sidebarBusy} onClick={()=>localSessionImportRef.current?.click()}><Upload size={16}/> Importa da locale (.quo)</button>
  <p className="muted tiny">Copia portabile di pagine, widget, schemi e allegati. Non comprende risposte, partecipanti, statistiche o credenziali.</p>
  {snap.session.status!=='closed'&&<button type="button" className="small outline" disabled={sidebarBusy} onClick={()=>setSidebarRename(snap.session.title)}>Rinomina sessione</button>}
  {sidebarRename!==null&&<form onSubmit={e=>{e.preventDefault();void renameSidebarSession()}} aria-label="Rinomina sessione corrente">
    <label>Nuovo nome<input autoFocus maxLength={255} required value={sidebarRename} onChange={e=>setSidebarRename(e.target.value)}/></label>
    <div className="downloads"><button type="submit" className="small primary" disabled={sidebarBusy||!sidebarRename.trim()}>Conferma nome</button><button type="button" className="small outline" disabled={sidebarBusy} onClick={()=>setSidebarRename(null)}>Annulla</button></div>
  </form>}
  {selectedSessionRole==='owner'&&<button type="button" className="small outline danger-action" disabled={sidebarBusy} onClick={()=>void deleteSession()}>Elimina sessione</button>}
  <button type="button" className="small outline" onClick={openSchemaEditor} disabled={sidebarBusy}>Modifica schemi</button>
 </section>}</div><div className="workspace">{selected&&!snap&&(dashboardPage==='session'||dashboardPage==='master')&&(sessionLoadState==='retry'||showSessionLoading)&&<section className="panel session-restore-status" role="status" aria-live="polite">
 <h2>{sessionLoadState==='retry'?'Ripristino della sessione non riuscito':'Caricamento sessione…'}</h2>
 <p>{sessionLoadState==='retry'?'Il server non ha risposto correttamente. Riproverò automaticamente, senza cancellare i cookie o perdere le modifiche salvate.':'Verifica dei dati e dei permessi della sessione in corso.'}</p>
 <div className="downloads"><button type="button" className="primary" onClick={()=>{setSessionLoadState('loading');setSessionReload(v=>v+1)}}>Riprova ora</button><button type="button" className="outline" onClick={()=>{writeWorkspaceLocation({sessionId:'',section:'workspace',tab:'overview',pageId:''});setSelected('');setSnap(null);setDesignActivity('');setDashboardPage('open')}}>Torna alle sessioni</button></div>
 </section>}{dashboardPage==='master'&&snap&&selected&&<section className="panel slide-scheme-workspace" aria-label="Editor degli schemi PowerPoint">
 <header className="slide-scheme-header"><div><h2>Editor degli schemi</h2><p className="muted tiny">Schema globale della sessione · elementi ereditati dalle pagine, personalizzabili localmente</p></div>
  <button type="button" className="slide-scheme-exit outline" onClick={()=>navigateDashboard('session')}>Esci dagli schemi</button>
 </header>
 <div className="slide-scheme-ribbon" role="toolbar" aria-label="Barra multifunzione schemi">
   <div className="slide-scheme-ribbon-group"><strong>Inserisci</strong><div className="slide-scheme-ribbon-actions"><SchemaRibbonButton label="Titolo" hint="Inserisci il titolo predefinito nello schema" icon={<Heading1 size={20}/>} disabled={schemaSaving||schemaWidgets.some(w=>w.kind==='title')} onClick={()=>insertSchemaWidget('title')}/><SchemaRibbonButton label="Footer" hint="Inserisci il piè di pagina predefinito" icon={<PanelBottom size={20}/>} disabled={schemaSaving||schemaWidgets.some(w=>w.kind==='footer')} onClick={()=>insertSchemaWidget('footer')}/></div></div>
   <div className="slide-scheme-ribbon-group"><strong>Allinea</strong><div className="slide-scheme-ribbon-actions">{([['left','Sinistra'],['center-x','Centro X'],['right','Destra'],['top','In alto'],['center-y','Centro Y'],['bottom','In basso']] as const).map(([mode,label])=><SchemaRibbonButton key={mode} label={label} hint={'Allinea le widget selezionate: '+label.toLowerCase()} icon={schemaAlignIcons[mode]} disabled={!schemaSelected.length} onClick={()=>arrangeSchema(mode as ArrangeMode)}/>)}</div></div>
   <div className="slide-scheme-ribbon-group"><strong>Distribuisci</strong><div className="slide-scheme-ribbon-actions">{([['distribute-x','Orizzontale'],['distribute-y','Verticale']] as const).map(([mode,label])=><SchemaRibbonButton key={mode} label={label} hint={'Distribuisci almeno tre widget: '+label.toLowerCase()} icon={schemaAlignIcons[mode]} disabled={schemaSelected.length<3} onClick={()=>arrangeSchema(mode as ArrangeMode)}/>)}</div></div>
   <div className="slide-scheme-ribbon-group slide-scheme-background-controls"><strong>Sfondo globale delle pagine</strong><div className="slide-scheme-ribbon-actions"><SchemaBackgroundTool items={assets.filter(a=>typeof a.mime_type==='string'&&a.mime_type.startsWith('image/'))} selectedId={schemaBackgroundAsset} disabled={schemaSaving||assetBusy} label="Immagine sfondo dello schema" onSelect={setSchemaBackgroundAsset}/><label className="slide-scheme-background-upload" title="Carica una nuova immagine di sfondo nella libreria dello schema"><ImageIcon size={20} aria-hidden="true"/><span>Carica immagine</span><input type="file" aria-label="Carica immagine di sfondo dello schema" accept="image/png,image/jpeg,image/gif,image/webp" disabled={assetBusy||schemaSaving} onChange={e=>{void uploadSchemaBackground(e.target.files?.[0]);e.target.value=''}}/></label><SchemaRibbonButton label="Rimuovi" hint="Rimuovi lo sfondo globale dello schema" icon={<X size={20}/>} disabled={!schemaBackgroundAsset||schemaSaving} onClick={()=>setSchemaBackgroundAsset('')}/></div></div>
    <div className="slide-scheme-ribbon-group slide-scheme-ribbon-save"><strong>Schema</strong><div className="slide-scheme-ribbon-actions"><SchemaRibbonButton label="Salva schema" hint="Salva lo schema globale e propaga le modifiche alle pagine" icon={<Save size={20}/>} primary disabled={schemaSaving||snap.session.status==='closed'} onClick={()=>void saveSchemaEditor()}/><span className="muted tiny" role="status">{JSON.stringify(schemaWidgets)!==schemaBaseline.current||schemaBackgroundAsset!==schemaBackgroundBaseline.current?'Modifiche non salvate':'Sincronizzato'}</span></div></div>
 </div>
 <div className="slide-scheme-widget-rail" aria-label="Aggiungi widget allo schema"><strong>Widget</strong><div className="slide-scheme-widget-options">{schemaWidgetKinds.map(kind=>kind==='shape'||kind==='line'?<GraphicInsertTool key={kind} kind={kind} schema disabled={schemaSaving||schemaWidgets.length>=16} onInsert={(preset,options)=>insertSchemaWidget(kind,preset,options)}/>:<button type="button" key={kind} data-widget-kind={kind} disabled={schemaSaving||schemaWidgets.length>=16||(['title','footer'].includes(kind)&&schemaWidgets.some(w=>w.kind===kind))||(['image','video','logo','pdf'].includes(kind)&&!schemaMediaAssets(kind).length)} title={['image','video','logo','pdf'].includes(kind)&&!schemaMediaAssets(kind).length?'Carica un allegato compatibile nella libreria della sessione':''} onClick={()=>insertSchemaWidget(kind)} aria-label={'Aggiungi widget allo schema: '+editorWidgetNames[kind]}><EditorWidgetIcon kind={kind}/><span>{editorWidgetNames[kind]}</span></button>)}</div></div>
 <div className="slide-scheme-layout"><div className="slide-scheme-canvas"><WidgetCanvas key={`${selected}:master`} widgets={schemaWidgets} onChange={next=>setSchemaWidgets(masterWidgetTemplate(next))} onSelectionChange={ids=>{setSchemaSelected(ids);setSchemaInspected(ids[0]||'')}} onInspectWidget={setSchemaInspected} assets={assets} sessionId={selected} joinCode={snap.session.join_code} backgrounds={backgrounds} onRenameLibraryImage={renameLibraryImage} onDeleteLibraryImage={deleteLibraryImage} onBackgroundSelect={id=>{if(!id){setSchemaBackgroundAsset('');return}void request<{id:string}>(`/sessions/${selected}/backgrounds/${encodeURIComponent(id)}/use`,'POST').then(result=>{setSchemaBackgroundAsset(result.id);void refreshAssets()}).catch(notify)}} onBackgroundUpload={async file=>{if(!file)return false;await uploadSchemaBackground(file);return true}} backgroundAssetId={schemaBackgroundAsset} pageTitle="Titolo della pagina" sessionTitle={snap.session.title} pageNumber={1} masterTitleStyle={snap.session.theme?.master?.titleStyle}/></div>
 <aside className="panel slide-scheme-inspector" aria-label="Proprietà schema selezionato"><h3>Proprietà dello schema</h3>
 {schemaWidgets.filter(w=>w.id===schemaInspected).map(w=><div key={w.id} className="slide-scheme-properties">
 <h4>{editorWidgetNames[w.kind]||w.kind}</h4>
 {['image','video','logo','pdf'].includes(w.kind)&&<label>Allegato dello schema<select value={w.assetId||''} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,assetId:e.target.value}:x))}>{schemaMediaAssets(w.kind).map(a=><option key={a.id} value={a.id}>{a.mime_type} · {a.id.slice(0,8)}</option>)}</select></label>}
 {!['shape','line'].includes(w.kind)&&<label><input type="checkbox" checked={w.showTitle!==false} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,showTitle:e.target.checked}:x))}/>Mostra nome/titolo</label>}
 {!['title','footer','shape','line'].includes(w.kind)&&<label>Testo widget<input maxLength={240} value={w.label||''} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,label:e.target.value}:x))}/></label>}
 {w.kind==='title'&&<><label><input type="checkbox" checked={w.titleFollowPage!==false} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,titleFollowPage:e.target.checked}:x))}/> Segui il titolo della pagina</label>{w.titleFollowPage===false&&<label>Testo personalizzato<input maxLength={240} value={w.label||''} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,label:e.target.value}:x))}/></label>}</>}
 {w.kind==='footer'&&<><label><input type="checkbox" checked={w.footerShowSessionTitle!==false} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,footerShowSessionTitle:e.target.checked}:x))}/> Mostra nome della sessione</label><label><input type="checkbox" checked={w.footerShowPageNumber!==false} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,footerShowPageNumber:e.target.checked}:x))}/> Numero pagina (10 px dal bordo del canvas)</label><label><input type="checkbox" checked={w.footerSeparator!==false} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,footerSeparator:e.target.checked}:x))}/> Separatore superiore</label>{w.footerSeparator!==false&&<label>Colore separatore<input type="color" value={w.footerSeparatorColor||'#9ca3af'} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,footerSeparatorColor:e.target.value}:x))}/></label>}
 {w.footerShowSessionTitle===false&&<label>Testo centrale<input maxLength={240} value={w.label||''} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,label:e.target.value}:x))}/></label>}
 <fieldset className="slide-scheme-number-controls" disabled={w.footerShowPageNumber===false}><legend>Posizione numero pagina</legend><p className="muted tiny">Percentuali all'interno del Footer. Senza personalizzazione: 10 px dal bordo inferiore e destro della pagina.</p>
 {([['footerNumberX','Orizzontale (%)'],['footerNumberY','Verticale (%)']] as const).map(([field,label])=><label key={field}>{label}<input type="number" min={0} max={100} step={1} value={w[field]??100} onChange={e=>{const value=Number(e.target.value);if(Number.isFinite(value)&&value>=0&&value<=100)setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,[field]:value}:x))}}/></label>)}
 <button type="button" className="outline small" onClick={()=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,footerNumberX:undefined,footerNumberY:undefined}:x))}>Ripristina numero in basso a destra</button></fieldset></>}
  {['shape','line'].includes(w.kind)&&<section className="widget-graphic-settings" aria-label="Formato grafico dello schema">
  {w.kind==='shape'&&<label>Forma<select value={w.style?.shapeType||'rectangle'} onChange={e=>setSchemaWidgets(old=>old.map(x=>x.id===w.id?{...x,style:{...x.style,shapeType:e.target.value}}:x))}>{GRAPHIC_PRESETS.shape.map(p=><option key={p.id} value={p.id}>{p.label}</option>)}</select></label>}
  {w.kind==='line'&&<><label>Direzione<select value={w.style?.lineDirection||'horizontal'} onChange={e=>setSchemaWidgets(old=>old.map(x=>x.id===w.id?{...x,style:{...x.style,lineDirection:e.target.value}}:x))}>{['horizontal','vertical','diagonal','reverse'].map(x=><option key={x} value={x}>{x}</option>)}</select></label><label>Frecce<select aria-label="Terminali freccia schema" value={w.style?.lineArrow||'none'} onChange={e=>setSchemaWidgets(old=>old.map(x=>x.id===w.id?{...x,style:{...x.style,lineArrow:e.target.value}}:x))}><option value="none">Nessuna</option><option value="start">Inizio / sinistra</option><option value="end">Fine / destra</option><option value="both">Entrambe</option></select></label></>}
  <label>Spessore bordo (pt)<input type="number" min="0" max="12" step="0.5" value={w.style?.strokeWidth??2} onChange={e=>{const n=Number(e.target.value);if(n>=0&&n<=12)setSchemaWidgets(old=>old.map(x=>x.id===w.id?{...x,style:{...x.style,strokeWidth:n}}:x))}}/></label>
  <label>Tratto<select value={w.style?.strokeDash||'solid'} onChange={e=>setSchemaWidgets(old=>old.map(x=>x.id===w.id?{...x,style:{...x.style,strokeDash:e.target.value}}:x))}><option value="solid">Continua</option><option value="dash">Tratteggiata</option><option value="dot">Punteggiata</option></select></label>
  <label>Colore bordo<input type="color" value={w.style?.strokeColor||'#334155'} onChange={e=>setSchemaWidgets(old=>old.map(x=>x.id===w.id?{...x,style:{...x.style,strokeColor:e.target.value}}:x))}/></label>
  {w.kind==='shape'&&<><label>Riempimento<input type="color" disabled={w.style?.fillNone} value={w.style?.fillColor||'#dbeafe'} onChange={e=>setSchemaWidgets(old=>old.map(x=>x.id===w.id?{...x,style:{...x.style,fillColor:e.target.value}}:x))}/></label><label><input type="checkbox" checked={!!w.style?.fillNone} onChange={e=>setSchemaWidgets(old=>old.map(x=>x.id===w.id?{...x,style:{...x.style,fillNone:e.target.checked}}:x))}/> Trasparente</label></>}
  </section>}
 <label>Colore del testo<input type="color" value={w.style?.color|| (w.kind==='title'?'#000000':'#26364a')} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,color:e.target.value}}:x))}/></label>
  <label>Carattere<select value={w.style?.fontFamily||'Arial'} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,fontFamily:e.target.value}}:x))}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(font=><option key={font}>{font}</option>)}</select></label>
 <div className="slide-scheme-typography"><label><input type="checkbox" checked={w.style?.bold===true} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,bold:e.target.checked}}:x))}/> Grassetto</label><label><input type="checkbox" checked={w.style?.italic===true} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,italic:e.target.checked}}:x))}/> Corsivo</label><label><input type="checkbox" checked={w.style?.underline===true} onChange={e=>setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,underline:e.target.checked}}:x))}/> Sottolineato</label></div>
<label>Dimensione testo (px)<input type="number" min={8} max={120} value={w.style?.fontSize||(w.kind==='title'?24:14)} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=8&&n<=120)setSchemaWidgets(items=>items.map(x=>x.id===w.id?{...x,style:{...x.style,fontSize:n}}:x))}}/></label>
 <button type="button" className="outline small danger-action" onClick={()=>{if(window.confirm('Eliminare il widget dallo schema globale?')){setSchemaWidgets(items=>items.filter(x=>x.id!==w.id));setSchemaInspected('')}}}>Rimuovi dallo schema</button>
 </div>)}
 {!schemaWidgets.some(w=>w.id===schemaInspected)&&<p className="muted tiny">Seleziona un widget e apri Proprietà widget dal menu contestuale, dalla palette o con doppio clic sul widget.</p>}
 </aside></div>
 <p className="muted tiny">Le pagine ereditano i widget globali; Titolo/Footer locali prevalgono sui relativi tipi. Il numero pagina è dinamico e può essere posizionato oppure nascosto.</p>
 </section>}{dashboardPage==='calendar'  &&<section className="panel"><CalendarAgenda date={calendarMonth} setDate={setCalendarMonth} view={calendarView} setView={setCalendarView} entries={globalAppointments} onSelect={(id:string)=>{setSelected(id);setSnap(null);setDashboardPage('session')}}/></section>}{dashboardPage==='open'&&<section className="panel"><h2>Apri sessione</h2><label>Ricerca sessioni<input value={sessionSearch} placeholder="Nome, codice, stato, ruolo" onChange={e=>{setSessionSearch(e.target.value);setSessionPage(1)}}/></label><label>Sessioni per pagina<select value={sessionPageSize} onChange={e=>{setSessionPageSize(Number(e.target.value));setSessionPage(1)}}>{[10,20,50,100].map(n=><option key={n} value={n}>{n}</option>)}</select></label><div className="activity-row"><button className="small outline" disabled={sessionPage===1} onClick={()=>setSessionPage(n=>n-1)}>Precedente</button><span>Pagina {sessionPage}</span><button className="small outline" disabled={sessionTotal<=sessionPage*sessionPageSize} onClick={()=>setSessionPage(n=>n+1)}>Successiva</button></div>{sessions.map(s=><details key={s.id} className="panel" style={{margin:'8px 0',padding:12}}><summary><strong style={{color:s.access_role==='collaborator'?'#37b5a5':'#8064d5'}}>{s.title}</strong> · {s.access_role==='collaborator'?'Collaboratore':'Owner'} · {s.status}</summary><p>Codice: {s.join_code}</p><div className="downloads" role="group" aria-label={`Azioni sessione ${s.title}`}><button type="button" className="small primary" disabled={listSessionBusy!==null} onMouseEnter={()=>warmSessionSnapshot(s.id)} onFocus={()=>warmSessionSnapshot(s.id)} onTouchStart={()=>warmSessionSnapshot(s.id)} onClick={()=>{const candidate=sessionPreviewCache.current.get((me?.id||'')+':'+s.id);setSnap(candidate&&Date.now()-candidate.at<5000?candidate.snapshot:null);setSelected(s.id);setDashboardPage('session')}}>Apri sessione</button><button type="button" className="small outline" disabled={listSessionBusy!==null} onClick={()=>void duplicateSessionFrom(s.id)} aria-label={`Duplica sessione ${s.title} senza risposte`}>Duplica senza dati {s.status==='closed'?'(terminata)':''}</button>{canResetListedSession({id:s.id,status:s.status,access_role:s.access_role||'collaborator'})&&<button type="button" className="small outline" disabled={listSessionBusy!==null} onClick={()=>void resetListedSession(s)} aria-label={`Resetta la sessione ${s.title} a non avviata`}>{listSessionBusy===s.id?'Operazione in corso…':'↺ Resetta a non avviata'}</button>}{canDeleteListedSession({id:s.id,status:s.status,access_role:s.access_role||'collaborator'})&&<button type="button" className="small outline danger-action" disabled={listSessionBusy!==null} onClick={()=>void deleteListedSession(s)} aria-label={`Elimina definitivamente la sessione ${s.title}`}>Elimina sessione</button>}</div></details>)}</section>}{dashboardPage==='new'&&<section className="panel"><h2>Nuova sessione</h2><p className="muted">Crea una sessione e aggiungi le date e gli orari nella sua dashboard.</p><label>Nome della sessione<input maxLength={255} value={newTitle} onChange={e=>setNewTitle(e.target.value)} placeholder="Workshop"/></label><button className="primary" disabled={!newTitle.trim()} onClick={createSession}><Plus size={18}/> Crea sessione</button></section>}{dashboardPage==='sso'&&<FederatedIdentities providers={oidcProviders} onMessage={setNotice}/>}{dashboardPage==='mfa'&&<section className="panel"><h3>Autenticazione a due fattori: email e TOTP</h3><div className="notice"><strong>Email MFA / Secondo fattore email:</strong> {me?.email_mfa_enabled?'Attivo / Enabled':'Disattivo / Disabled'}<p>Email e TOTP sono indipendenti. L'attivazione email richiede SMTP e conferma del codice ricevuto; la disattivazione richiede la password. / Email and TOTP are independent; email setup requires OTP confirmation.</p><label>Password corrente / Current password<input type="password" autoComplete="current-password" value={emailMfaPassword} onChange={e=>setEmailMfaPassword(e.target.value)}/></label><button className="small outline" disabled={!emailMfaPassword} onClick={async()=>{try{const result=await request<any>('/auth/email-mfa/settings','POST',{enabled:!me?.email_mfa_enabled,password:emailMfaPassword});if(result.pending_confirmation){setEmailEnrollmentId(result.challenge_id);setEmailEnrollmentCode('');setNotice('Controlla la tua email e inserisci il codice entro 10 minuti / Check your email for a code valid for 10 minutes')}else{setMe(null);setEmailEnrollmentId('');setEmailMfaPassword('');setNotice('Impostazione aggiornata; accedi di nuovo / Setting updated; sign in again')}}catch(e){notify(e)}}}>{me?.email_mfa_enabled?'Disattiva email MFA / Disable':'Invia codice di attivazione / Send enrollment code'}</button>{emailEnrollmentId&&!me?.email_mfa_enabled&&<div className="panel"><p>Inserisci il codice di verifica ricevuto via email. / Enter the code received by email.</p><label>Codice email / Email code<input inputMode="numeric" autoComplete="one-time-code" maxLength={6} value={emailEnrollmentCode} onChange={e=>setEmailEnrollmentCode(e.target.value.replace(/\D/g,'').slice(0,6))}/></label><button className="small primary" disabled={!/^\d{6}$/.test(emailEnrollmentCode)} onClick={async()=>{try{await request('/auth/email-mfa/enrollment/confirm','POST',{challenge_id:emailEnrollmentId,code:emailEnrollmentCode});setEmailEnrollmentId('');setEmailEnrollmentCode('');setEmailMfaPassword('');setMe(null);setNotice('MFA email attivata: esegui nuovamente l’accesso / Email MFA enabled: sign in again')}catch(e){notify(e)}}}>Conferma e attiva MFA email / Confirm and enable</button></div>}</div><p>Stato: {me?.totp_enabled?'Attivata':'Disattivata'}</p>{!me?.totp_enabled?<><button className="small outline" onClick={async()=>{try{setEnrollment(await request('/auth/mfa/setup','POST'))}catch(e){notify(e)}}}>Configura MFA</button>{enrollment&&<><p>Inserisci questo segreto nella tua app di autenticazione:</p><code style={{overflowWrap:'anywhere'}}>{enrollment.secret}</code><p>URI completo per l'app autenticatore:</p><code style={{overflowWrap:'anywhere'}}>{enrollment.otpauth_url}</code><p>QR da scansionare con l'autenticatore:</p><img alt="QR configurazione TOTP" width={180} height={180} src={'/api/auth/mfa/qr'} /><p>Oppure usa il collegamento otpauth: <a href={enrollment.otpauth_url}>Apri app autenticatore</a></p><label>Codice di conferma<input inputMode="numeric" value={mfaAdminCode} onChange={e=>setMfaAdminCode(e.target.value.slice(0,6))}/></label><button className="small" onClick={async()=>{try{const confirmed=await request('/auth/mfa/confirm','POST',{code:mfaAdminCode});setRecoveryCodes(confirmed.recovery_codes||[]);setMe(await request('/auth/me'));setEnrollment(null);setMfaAdminCode('')}catch(e){notify(e)}}}>Attiva MFA</button></>}</>:<><label>Codice MFA per disattivare<input inputMode="numeric" value={mfaAdminCode} onChange={e=>setMfaAdminCode(e.target.value.slice(0,6))}/></label><label>Password corrente<input type="password" value={password} onChange={e=>setPassword(e.target.value)}/></label><button className="small outline" onClick={async()=>{try{await request('/auth/mfa/disable','POST',{code:mfaAdminCode,password});setMe(await request('/auth/me'));setMfaAdminCode('');setPassword('');setRecoveryCodes([])}catch(e){notify(e)}}}>Disattiva MFA</button></>}{recoveryCodes.length>0&&<div className="notice"><strong>Salva i codici di recupero: vengono mostrati solo ora.</strong><pre style={{whiteSpace:'pre-wrap',overflowWrap:'anywhere'}}>{recoveryCodes.join('\n')}</pre><button className="small outline" onClick={()=>{void navigator.clipboard.writeText(recoveryCodes.join('\n'))}}>Copia codici</button><button className="small outline" onClick={()=>setRecoveryCodes([])}>Li ho salvati</button></div>}{me?.totp_enabled&&<button className="small outline" onClick={async()=>{try{const answer=await request('/auth/mfa/recovery-codes/rotate','POST',{password,code:mfaAdminCode});setRecoveryCodes(answer.recovery_codes||[]);setMfaAdminCode('')}catch(e){notify(e)}}}>Rigenera codici di recupero (password e TOTP richiesti)</button>}</section>}{me?.role==='platform_admin'&&dashboardPage==='settings'&&<div className="server-settings-tabs" role="tablist" aria-label={lang==='it'?'Schede delle impostazioni del server':'Server settings tabs'} onKeyDown={event=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(event.key))return;const tabs=Array.from(event.currentTarget.querySelectorAll<HTMLButtonElement>('[role=tab]'));const selectedIndex=tabs.findIndex(button=>button===event.target);if(selectedIndex<0)return;event.preventDefault();const index=event.key==='Home'?0:event.key==='End'?tabs.length-1:(selectedIndex+(event.key==='ArrowRight'?1:-1)+tabs.length)%tabs.length;setServerSettingsTab(SERVER_SETTINGS_TABS[index].id);tabs[index]?.focus()}}>{SERVER_SETTINGS_TABS.map(item=><button key={item.id} type="button" role="tab" id={'server-settings-tab-'+item.id} aria-controls={'server-settings-panel-'+item.id} aria-selected={serverSettingsTab===item.id} tabIndex={serverSettingsTab===item.id?0:-1} className={serverSettingsTab===item.id?'server-settings-tab active':'server-settings-tab'} onClick={()=>setServerSettingsTab(item.id)}>{translateUiText(item.label,lang)}</button>)}</div>}{me?.role==='platform_admin'&&dashboardPage==='settings'&&<section role="tabpanel" id="server-settings-panel-storage" aria-labelledby="server-settings-tab-storage" hidden={serverSettingsTab!=='storage'} className="panel disk-monitor-settings" aria-label="Occupazione disco e allarmi"><h3>Spazio disco e allarmi</h3><p className="muted tiny">Occupazione reale dei volumi: allegati Quorivio e dati PostgreSQL. Allarme email agli amministratori di piattaforma al raggiungimento del 90%; il controllo viene riarmato dopo il ritorno all’85% o meno. SMTP configurato obbligatorio per ricevere email. Misure automatiche ogni 5 minuti.</p>{diskStatusError&&<p role="alert">{diskStatusError}</p>}{!diskStatus&&!diskStatusError&&<p role="status">Caricamento metriche disco…</p>}{diskStatus&&<>{!diskStatus.emailNotificationsConfigured&&<p role="alert">SMTP non configurato: gli allarmi restano visibili, ma le email non possono essere inviate. Configura SMTP/SMTPS qui sotto.</p>}{(['application','conversion','database'] as const).map(volume=>{const reading=diskStatus[volume];const label=volume==='application'?'Spazio applicazione (volume allegati)':volume==='conversion'?'Filesystem temporaneo conversioni (pod attuale)':'Spazio PostgreSQL (volume dati)';return <div className="disk-volume-row" key={volume} style={{padding:'10px 0'}}><strong>{label}</strong> <span role="status" style={{fontWeight:600,color:reading.status==='warning'?'#bd3d22':undefined}}>{reading.status==='unavailable'?'Misura non disponibile':reading.status==='warning'?'ALLARME ≥90%':`${reading.usedPercent?.toLocaleString('it-IT')}% occupato`}</span>{reading.status!=='unavailable'&&<><progress aria-label={`Occupazione ${label}`} value={reading.usedPercent??0} max={100} style={{width:'100%',display:'block'}}/ ><span>{diskGigabytes(reading.usedBytes)} utilizzati / {diskGigabytes(reading.totalBytes)} totali · {diskGigabytes(reading.availableBytes)} disponibili</span><p className="muted tiny">Misurato: {reading.observedAt?new Date(reading.observedAt).toLocaleString('it-IT'):'—'}</p></>}{reading.status==='unavailable'&&<p className="muted tiny" role="status">{volume==='database'?'Sonda del filesystem PostgreSQL non attiva o dato scaduto (oltre 15 minuti). La dimensione del solo database non viene usata per calcolare la percentuale né per inviare allarmi.':volume==='conversion'?'Volume temporaneo delle conversioni non montato o non accessibile (la quota Kubernetes emptyDir richiede un controllo separato).':'Impossibile leggere lo spazio sul volume allegati. Verificare il mount e i permessi del pod.'}</p>}</div>})}<p className="muted tiny">Dimensione logica del database corrente: {diskGigabytes(diskStatus.logicalDatabaseBytes)} (solo informativa, non indica lo spazio libero del PVC).</p><p className="muted tiny">Ultimo aggiornamento dashboard: {new Date(diskStatus.checkedAt).toLocaleString('it-IT')}</p></>}<button className="small outline" onClick={async()=>{try{setDiskStatus(await request<DiskStatus>('/admin/disk-usage','GET',undefined,{cache:'no-store'}));setDiskStatusError('')}catch{setDiskStatusError('Monitoraggio disco temporaneamente non disponibile')}}}>Aggiorna ora</button></section>}{me?.role==='platform_admin'&&dashboardPage==='settings'&&<section role="tabpanel" id="server-settings-panel-smtp" aria-labelledby="server-settings-tab-smtp" hidden={serverSettingsTab!=='smtp'} className="panel"><h3>SMTP/SMTPS</h3><p>Configurazione SMTP cifrata. Scegli TLS implicito (di norma porta 465) oppure STARTTLS obbligatorio (di norma porta 587): la password è cifrata nel database e non viene mai restituita dal server.</p><label>Server SMTP<input value={smtpForm.host} onChange={e=>setSmtpForm(v=>({...v,host:e.target.value}))}/></label><label>Porta SMTP<input type="number" value={smtpForm.port} onChange={e=>setSmtpForm(v=>({...v,port:Number(e.target.value)}))}/></label><label>Utente SMTP<input value={smtpForm.user} onChange={e=>setSmtpForm(v=>({...v,user:e.target.value}))}/></label><label>Password SMTP (lasciare vuota per conservare quella precedente)<input type="password" autoComplete="new-password" value={smtpForm.password} onChange={e=>setSmtpForm(v=>({...v,password:e.target.value}))}/></label><label>Email mittente (indirizzo email valido)<input type="email" value={smtpForm.from} onChange={e=>setSmtpForm(v=>({...v,from:e.target.value}))}/></label><label>Trasporto<select value={smtpForm.secure?'tls':'starttls'} onChange={e=>setSmtpForm(v=>({...v,secure:e.target.value==='tls',port:e.target.value==='tls'?465:587}))}><option value="tls">SMTPS - TLS implicito</option><option value="starttls">SMTP - STARTTLS obbligatorio</option></select></label><label>Nome del mittente<input maxLength={120} value={smtpForm.senderName} onChange={e=>setSmtpForm(v=>({...v,senderName:e.target.value}))}/></label><button className="small primary" onClick={async()=>{try{const r=await request('/admin/smtp','PUT',{...smtpForm});setSmtpStatus(r);setSmtpForm(v=>({...v,password:''}));setNotice('Configurazione SMTPS salvata')}catch(e){notify(e)}}}>Salva configurazione SMTP</button><button className="small outline" onClick={async()=>{try{const c=await request('/admin/smtp');setSmtpStatus(c);setNotice(c.configured?'Configurazione SMTP verificata: '+c.transport:'SMTP non configurato');setSmtpForm(v=>({...v,host:c.host||'',port:Number(c.port||465),user:c.user||'',from:c.from||'',senderName:c.senderName||'',secure:c.transport!=='starttls',password:''}))}catch(e){notify(e)}}}>Verifica configurazione</button>{smtpStatus&&<p>{smtpStatus.configured?`SMTPS: ${smtpStatus.host}:${smtpStatus.port} — ${smtpStatus.from}`:smtpStatus.error||'Non configurato'}</p>}<label>Destinatario email di prova<input type="email" value={smtpRecipient} onChange={e=>setSmtpRecipient(e.target.value)}/></label><button className="small" onClick={async()=>{try{await request('/admin/smtp/test','POST',{recipient:smtpRecipient});setNotice('Email di test inviata')}catch(e){notify(e)}}}>Invia email di prova</button></section>}{me?.role==='platform_admin'&&dashboardPage==='users'&&ldapStatus.enabled&&<AdminLdapPanel/>}{me?.role==='platform_admin'&&dashboardPage==='users'&&<section className="panel"><h3>Gestione utenti</h3><label>Nuovo utente (email)<input type="email" value={newUserEmail} onChange={e=>setNewUserEmail(e.target.value)}/></label><label>Nickname facoltativo<input maxLength={32} value={newUserNickname} onChange={e=>setNewUserNickname(e.target.value)}/></label><label>Password temporanea (almeno 12 caratteri)<input type="password" value={newUserTemporaryPassword} onChange={e=>setNewUserTemporaryPassword(e.target.value)}/></label><button className="small" disabled={!newUserEmail||newUserTemporaryPassword.length<12} onClick={async()=>{try{await request('/admin/users','POST',{email:newUserEmail,temporary_password:newUserTemporaryPassword,nickname:newUserNickname||null,role:'user'});setNewUserEmail('');setNewUserNickname('');setNewUserTemporaryPassword('');setAdminUsers((await request<{items:any[]}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`)).items)}catch(e){notify(e)}}}>Crea utente</button><button className="outline small" onClick={async()=>{try{setAdminUsers((await request<{items:any[]}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`)).items);const cfg=await request('/admin/settings');setAdminUrl(cfg.public_base_url||'');setAdminRetention(Number(cfg.closed_session_retention_days||60))}catch(e){notify(e)}}}>Carica utenti e impostazioni</button><div className="activity-row"><label>Ricerca email, nickname o stato<input placeholder="Email, nickname, approvato, non approvato" value={userSearch} onChange={e=>{setUserSearch(e.target.value);setUserPage(1)}}/></label><label>Utenti per pagina<select value={userPageSize} onChange={e=>{setUserPageSize(Number(e.target.value));setUserPage(1)}}>{[10,20,50,100].map(n=><option key={n} value={n}>{n}</option>)}</select></label></div><div className="activity-row"><button className="small outline" disabled={userPage<=1} onClick={()=>setUserPage(x=>x-1)}>← Precedente</button><span>Pagina {userPage}</span><button className="small outline" disabled={userTotal<=userPage*userPageSize} onClick={()=>setUserPage(x=>x+1)}>Successiva →</button></div>{adminUsers.map((u:any)=><details key={u.id} className="panel" style={{margin:'8px 0',padding:12}}><summary style={{cursor:'pointer'}}><strong>{u.nickname||u.email}</strong> · {u.email} · <span style={{color:u.approved?'#29b96f':'#e35353'}}>{u.approved?'Approvato':'Non approvato'}</span></summary><div className="activity-row"><span>MFA TOTP: <strong>{u.totp_enabled?'Attiva':'Disattiva'}</strong></span><button type="button" className="outline small" disabled={!u.totp_enabled||!!u.is_primary_admin||u.id===me?.id} onClick={async()=>{if(!window.confirm('Ripristinare la MFA di questo utente? I codici di recupero esistenti saranno revocati.'))return;const admin_password=window.prompt('Conferma la tua password amministratore');if(!admin_password)return;const admin_totp_code=window.prompt('Codice TOTP amministratore (se attivato)')||'';try{await request(`/admin/users/${u.id}/mfa/reset`,'POST',{admin_password,admin_totp_code,confirm:true});setAdminUsers(old=>old.map(x=>x.id===u.id?{...x,totp_enabled:false}:x));setNotice('MFA azzerata. L’utente dovrà configurarla nuovamente.')}catch(e){notify(e)}}}>Azzera MFA utente</button></div><label>Nickname<input value={u.nickname||''} disabled={!!u.is_primary_admin} onChange={e=>setAdminUsers(old=>old.map(x=>x.id===u.id?{...x,nickname:e.target.value}:x))}/></label>{u.is_primary_admin&&<button className="outline small" onClick={async()=>{const next=window.prompt('Nuova email admin principale',u.email);if(!next||next===u.email)return;try{await request(`/admin/users/${u.id}/identity`,'PATCH',{email:next});setAdminUsers((await request<{items:any[]}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`)).items)}catch(e){notify(e)}}}>Cambia email principale</button>}<select disabled={!!u.is_primary_admin} value={u.role} onChange={e=>setAdminUsers(old=>old.map(x=>x.id===u.id?{...x,role:e.target.value}:x))}><option value="user">user</option><option value="presenter">presenter</option><option value="moderator">moderator</option><option value="org_admin">org_admin</option><option value="platform_admin">platform_admin</option></select><button type="button" className="small" disabled={!!u.is_primary_admin} aria-label={`Stato approvazione di ${u.email}: ${u.approved?'approvato':'non approvato'}`} style={{background:u.approved?'#166534':'#991b1b',color:'#fff',borderRadius:9,padding:'8px 14px'}} onClick={()=>setAdminUsers(old=>old.map(x=>x.id===u.id?{...x,approved:!x.approved}:x))}>{u.approved?'Approvato · clicca per revocare':'Non approvato · clicca per approvare'}</button><button className="small" disabled={!!u.is_primary_admin||!!adminSavingId} onClick={async()=>{if(adminSavingId)return;setAdminSavingId(u.id);try{await request(`/admin/users/${u.id}`,'PATCH',{nickname:u.nickname||null,role:u.role,approved:u.approved});setAdminUsers((await request<{items:any[]}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`)).items);setNotice('Utente salvato')}catch(e){notify(e)}finally{setAdminSavingId('')}}}>{adminSavingId===u.id?'Salvataggio…':'Salva utente'}</button><button className="small outline" disabled={!!u.is_primary_admin} onClick={async()=>{if(!window.confirm('Eliminare l’account?'))return;try{const r=await fetch(`/api/admin/users/${u.id}`,{method:'DELETE',credentials:'include'});if(!r.ok)throw Error(`HTTP ${r.status}`);setAdminUsers((await request<{items:any[]}>(`/admin/users?page=${userPage}&page_size=${userPageSize}&search=${encodeURIComponent(userSearch)}`)).items)}catch(e){notify(e)}}}>Elimina</button></details>)}</section>}{me?.role==='platform_admin'&&dashboardPage==='settings'&&<section role="tabpanel" id="server-settings-panel-converter" aria-labelledby="server-settings-tab-converter" hidden={serverSettingsTab!=='converter'} className="panel" aria-label="Convertitore PDF e PowerPoint"><h3>Convertitore PDF / PowerPoint (worker isolato)</h3><p>Gestisci qui l’importazione PDF/PPTX. Il servizio richiede un container converter isolato, token interno e volume condiviso. Il pulsante non installa il worker e non bypassa i controlli di sicurezza.</p>{converterStatus?<><p role="status">Stato: <strong>{converterStatus.enabled&&converterStatus.worker_ready?'Attivo e pronto':converterStatus.enabled?'Abilitato, worker non raggiungibile':'Non disponibile'}</strong></p><p className="muted tiny">Abilitazione deployment: {converterStatus.deployment_enabled?'Sì':'No'} · Configurazione worker: {converterStatus.worker_configured?'Completa':'Incompleta'} · Risposta worker: {converterStatus.worker_ready?'Pronto':'Non pronto'} · Preferenza amministratore: {converterStatus.admin_enabled?'Abilitato':'Disabilitato'}</p>{!converterStatus.deployment_enabled&&<p role="alert">Il deployment deve avere QUORIVIO_ENABLE_CONVERTER=true. Configura il worker isolato e riavvia l’API prima di abilitare il servizio.</p>}{!converterStatus.worker_configured&&<p role="alert">Configurare QUORIVIO_CONVERTER_WORKER_URL e QUORIVIO_WORKER_TOKEN (almeno 32 caratteri) nel deployment. Non inserire token in questa pagina.</p>}{converterStatus.deployment_enabled&&converterStatus.worker_configured&&!converterStatus.worker_ready&&<p role="alert">Il worker non risponde correttamente a /health. Verifica container, volume condiviso e log del servizio.</p>}<div className="activity-row"><button type="button" className="small primary" disabled={converterBusy||converterStatus.enabled&&converterStatus.worker_ready||!converterStatus.deployment_enabled||!converterStatus.worker_configured||!converterStatus.worker_ready} onClick={async()=>{setConverterBusy(true);try{setConverterStatus(await request('/admin/converter','PUT',{enabled:true}));setNotice('Convertitore PDF/PPTX abilitato')}catch(e){notify(e)}finally{setConverterBusy(false)}}}>Abilita importazione PDF/PPTX</button><button type="button" className="small outline" disabled={converterBusy||!converterStatus.admin_enabled} onClick={async()=>{if(!window.confirm('Disabilitare tutte le conversioni PDF/PPTX per gli utenti?'))return;setConverterBusy(true);try{setConverterStatus(await request('/admin/converter','PUT',{enabled:false}));setNotice('Convertitore PDF/PPTX disabilitato')}catch(e){notify(e)}finally{setConverterBusy(false)}}}>Disabilita importazione PDF/PPTX</button><button type="button" className="small outline" disabled={converterBusy} onClick={async()=>{try{setConverterStatus(await request('/admin/converter'))}catch(e){notify(e)}}}>Verifica stato worker</button></div></>:<p role="status">Caricamento stato convertitore…</p>}<p className="muted tiny">Guida installazione: docs/ISOLATED_CONVERTER.it.md · Non esporre la porta interna 8099.</p></section>}
{me?.role==='platform_admin'&&dashboardPage==='settings'&&<><div role="tabpanel" id="server-settings-panel-auth" aria-labelledby="server-settings-tab-auth" hidden={serverSettingsTab!=='auth'}><AuthBackendSettingsPanel request={request}/></div><div role="tabpanel" id="server-settings-panel-backup" aria-labelledby="server-settings-tab-backup" hidden={serverSettingsTab!=='backup'}><AdminBackupPanel/></div><div role="tabpanel" id="server-settings-panel-audit" aria-labelledby="server-settings-tab-audit" hidden={serverSettingsTab!=='audit'}><AdminAuditPanel/></div></>}{me?.role==='platform_admin'&&dashboardPage==='settings'&&<section role="tabpanel" id="server-settings-panel-general" aria-labelledby="server-settings-tab-general" hidden={serverSettingsTab!=='general'} className="panel"><h3>Configurazione server</h3><label>URL esterna HTTPS<input value={adminUrl} onChange={e=>setAdminUrl(e.target.value)}/></label><label>Giorni conservazione sessioni chiuse<input type="number" min="1" max="3650" value={adminRetention} onChange={e=>setAdminRetention(Number(e.target.value))}/></label><label>Limite upload (MB, 1–1024)<input type="number" min="1" max="1024" value={adminUploadMb} onChange={e=>setAdminUploadMb(Number(e.target.value))}/></label><p className="muted tiny">Dopo una modifica del limite rigenera e applica i manifest Ingress Kubernetes.</p><button className="small" onClick={async()=>{try{await request('/admin/settings','PATCH',{public_base_url:adminUrl,closed_session_retention_days:adminRetention,max_upload_mb:adminUploadMb})}catch(e){notify(e)}}}>Salva impostazioni</button></section>}{dashboardPage==='profile'&&<section className="panel"><h3>Profilo utente e presentatore</h3><p>Account: {me?.email} · nickname: {me?.nickname||'non impostato'}</p><label>Nickname (univoco)<input maxLength={32} placeholder="nickname" value={nickname} onChange={e=>setNickname(e.target.value)}/></label><p className="muted tiny">Nome e foto visibili nei widget profilo delle sessioni.</p><label>Nome visualizzato<input maxLength={100} value={profileName} onChange={e=>setProfileName(e.target.value)}/></label><section className="gravatar-profile-settings" aria-label="Gravatar del tuo account"><label><input type="checkbox" aria-label="Usa Gravatar per la foto profilo" checked={!!myProfile?.gravatar_enabled} disabled={photoBusy||profileSaving} onChange={async e=>{const enabled=e.target.checked;setPhotoBusy(true);try{const data=await request<any>('/auth/profile/gravatar','PUT',{enabled});setMyProfile((old:any)=>({...old,...data}));setProfilePhoto(data.profile_photo_url||'');setPhotoVersion(v=>v+1);setNotice(enabled?(data.sync==='unavailable'?'Gravatar attivato; riprova la sincronizzazione più tardi':data.sync==='missing'?'Gravatar attivato: nessuna foto trovata per la tua email':'Foto Gravatar sincronizzata'):'Sincronizzazione Gravatar disattivata')}catch(error){notify(error)}finally{setPhotoBusy(false)}}}/>Usa Gravatar per la foto del mio account</label><p className="muted tiny">È una scelta facoltativa. La foto viene importata nel server Quorivio usando la tua email registrata e verificata a ogni accesso; non viene caricata direttamente da Gravatar nei browser dei partecipanti.</p><div className="downloads"><a className="outline asbutton small" target="_blank" rel="noopener noreferrer" href="https://gravatar.com/">Aggiungi o modifica una foto su Gravatar</a>{myProfile?.gravatar_enabled&&<button type="button" className="outline small" disabled={photoBusy||profileSaving} onClick={async()=>{setPhotoBusy(true);try{const data=await request<any>('/auth/profile/gravatar','PUT',{enabled:true});setMyProfile((old:any)=>({...old,...data}));setProfilePhoto(data.profile_photo_url||'');setPhotoVersion(v=>v+1);setNotice(data.sync==='imported'?'Foto Gravatar importata':data.sync==='unchanged'?'Gravatar già aggiornato':data.sync==='missing'?'Nessun Gravatar associato alla email':'Servizio Gravatar momentaneamente non disponibile')}catch(error){notify(error)}finally{setPhotoBusy(false)}}}>Importa / aggiorna Gravatar</button>}</div></section><label>Foto del profilo (PNG, JPEG o WebP, massimo 5 MB, lato massimo 4096 px)<input type="file" accept="image/png,image/jpeg,image/webp" disabled={photoBusy||profileSaving} aria-label="Carica foto del profilo" onChange={async e=>{const file=e.target.files?.[0];e.target.value='';if(!file||photoBusy||profileSaving)return;setPhotoBusy(true);try{if(!['image/png','image/jpeg','image/webp'].includes(file.type)||file.size===0||file.size>5*1024*1024)throw Error('Immagine non valida o troppo grande');const response=await authenticatedFetch('/api/auth/profile/photo',{method:'POST',credentials:'include',headers:{'Content-Type':file.type},body:file});const result=await response.json();if(!response.ok)throw Error(result.error||'Caricamento fallito');setProfilePhoto(result.profile_photo_url);setMyProfile((old:any)=>({...old,profile_photo_url:result.profile_photo_url}));setPhotoVersion(v=>v+1);setNotice('Foto aggiornata')}catch(err){notify(err)}finally{setPhotoBusy(false)}}}/></label><button type="button" className="outline small" disabled={photoBusy||profileSaving||!myProfile?.profile_photo_url} onClick={async()=>{if(photoBusy||profileSaving)return;setPhotoBusy(true);try{await request('/auth/profile/photo','DELETE');setProfilePhoto('');setMyProfile((old:any)=>({...old,profile_photo_url:null}));setPhotoVersion(v=>v+1);setNotice('Foto rimossa')}catch(err){notify(err)}finally{setPhotoBusy(false)}}}>Elimina foto</button><div className="downloads"><button className="outline small" disabled={!myProfile||photoBusy||profileSaving||profileName.trim().length<2||profileName.trim().length>100} onClick={async()=>{if(profileSaving||photoBusy)return;setProfileSaving(true);try{const p=await request<any>('/auth/profile','PATCH',{nickname:nickname||null,display_name:profileName});setMyProfile((old:any)=>({...old,...p}));setMe(await request('/auth/me'));setNotice('Profilo salvato')}catch(e){notify(e)}finally{setProfileSaving(false)}}}>{profileSaving?'Salvataggio in corso…':'Salva profilo'}</button></div>{photoBusy&&<p role="status" aria-live="polite">Aggiornamento foto in corso…</p>}{myProfile?.profile_photo_url&&<img src={`${myProfile.profile_photo_url}?v=${photoVersion}`} alt="Foto profilo" style={{maxHeight:72,maxWidth:72,objectFit:'cover',borderRadius:'50%'}}/>}{ldapStatus.enabled&&<details className="panel" aria-label="Collegamento LDAP"><summary>Collega account a {ldapStatus.label}</summary><p className="muted tiny">Per sicurezza il collegamento richiede la tua sessione locale attiva e la password valida della directory; la sola email non è sufficiente.</p><label>Utente LDAP<input autoComplete="username" maxLength={254} value={ldapLinkLogin} onChange={e=>setLdapLinkLogin(e.target.value)}/></label><label>Password LDAP<input type="password" autoComplete="current-password" value={ldapLinkPassword} onChange={e=>setLdapLinkPassword(e.target.value)}/></label><button type="button" className="outline small" disabled={ldapLinkBusy||!ldapLinkLogin.trim()||!ldapLinkPassword} onClick={async()=>{setLdapLinkBusy(true);try{await request('/auth/ldap/link','POST',{email:ldapLinkLogin,password:ldapLinkPassword});setNotice('Account LDAP collegato; potrai usarlo al prossimo accesso.');setLdapLinkLogin('')}catch(e){notify(e)}finally{setLdapLinkPassword('');setLdapLinkBusy(false)}}}>Collega identità LDAP</button></details>}</section>}{dashboardPage!=='session'?(['new','open','calendar'].includes(dashboardPage)?null:<div className="welcome"><h1>{dashboardPage==='users'?'Gestione utenti':dashboardPage==='settings'?'Impostazioni server':dashboardPage==='mfa'?'Autenticazione a due fattori':dashboardPage==='sso'?'Identità federate':'Profilo presentatore'}</h1><p>Gestisci questa funzionalità dal pannello dedicato a sinistra.</p></div>):!snap?<div className="welcome"><div className="orb"><BarChart3 size={55}/></div><h1>Le idee prendono vita.</h1><p>Seleziona una sessione o creane una nuova.</p></div>:<><div className="workspace-head"><div><div className="eyebrow">PRESENTER CONTROL ROOM</div><h1>{snap.session.title}</h1><div className="subline"><span className="pill">{snap.session.status}</span><span>Codice: <strong>{snap.session.join_code}</strong></span></div></div><div className="actions">{snap.session.status==='active'&&!snap.session.current_activity_id&&<span role="status" className="muted tiny">Sessione avviata: pubblica una pagina da «Pagine e contenuti» per mostrarla sullo schermo.</span>}{snap.session.status==='paused'&&<span role="status" className="muted tiny">Sessione in pausa: i partecipanti non possono inviare nuove risposte.</span>}{snap.session.status!=='closed'&&snap.session.status!=='active'&&<button className="primary" onClick={()=>changeStatus('active')}><Play size={16}/> Avvia</button>}{snap.session.status==='active'&&<button className="outline session-action-pause" onClick={()=>changeStatus('paused')}>Pausa</button>}{snap.session.status==='paused'&&<button className="primary" onClick={()=>changeStatus('active')}>Riprendi</button>}{snap.session.status==='active'&&snap.activities.find(a=>a.id===snap.session.current_activity_id)?.page_design?.widgets?.some((w:any)=>w.kind==='timer')&&<button type="button" className="primary" title="Riavvia manualmente il timer della pagina e cancella i risultati precedenti" onClick={()=>{const a=snap.activities.find(a=>a.id===snap.session.current_activity_id);if(a)void restartPageTimer(a)}}><Timer size={19}/> Riavvia countdown</button>}{(snap.session.status==='active'||snap.session.status==='paused')&&<button type="button" className="outline session-action-reset" title="Ritorna a non avviata: elimina partecipanti, voti e risultati, conserva pagine e configurazioni" onClick={()=>void resetSessionToReady()}>↺ Riporta a non avviata</button>}{(snap.session.status==='active'||snap.session.status==='paused')&&<button className="outline session-action-terminate" onClick={()=>changeStatus('closed')}><Square size={16}/> Termina</button>}</div></div>{presenterLive==='disconnected'&&<div className="live-stale-warning" role="status">{liveFallback?'WebSocket in riconnessione; dati della dashboard aggiornati tramite HTTP.':'Connessione live interrotta: riconnessione in corso.'}</div>}<div className="rehearsal-launch">{(snap.session.status==='active'||snap.session.status==='paused')?<div className="session-live-access" aria-label="Accesso alla sessione live"><div className="session-live-qr"><img key={sessionQr.revision} src={sessionQr.url?`/api/sessions/${selected}/qr?format=svg&revision=${sessionQr.revision}`:undefined} alt="QR per il pubblico"/><div><strong>Partecipanti</strong>{sessionQr.url?<a href={sessionQr.url} target="_blank" rel="noreferrer">Apri URL partecipanti</a>:<small role="status">Link partecipanti non disponibile</small>}<small>Codice: {snap.session.join_code}</small></div></div><div className="session-live-presenter"><img key={sessionQr.revision} className="session-presenter-qr" src={sessionQr.url?`/api/sessions/${selected}/presenter-qr?revision=${sessionQr.revision}`:undefined} alt="QR presentatore (richiede autenticazione)"/><strong>Presentatore</strong><a href={`/screen/${selected}`} target="_blank" rel="noopener noreferrer" title="Apri lo schermo presentatore live"><Presentation size={22}/> Apri schermo presentatore</a><a href={`${location.origin}/screen/${selected}`} target="_blank" rel="noopener noreferrer" title="Collegamento diretto autenticato del presentatore">URL presentatore</a></div></div>:null}<div className="rehearsal-launch-actions" role="group" aria-label={snap.session.status==='active'||snap.session.status==='paused'?'Accessi reali alla sessione':'Anteprime della sessione'}>{!(snap.session.status==='active'||snap.session.status==='paused')&&(['presenter','participant','mobile','both'] as RehearsalMode[]).map(m=><button type="button" key={m} className="primary" title={m==='presenter'?'Apri anteprima presentatore':m==='participant'?'Apri anteprima partecipante':m==='mobile'?'Apri anteprima smartphone':'Apri anteprime affiancate'} onClick={()=>{setRehearsalMode(m);setRehearsalOpen(true)}}>{m==='presenter'?<><Presentation size={22}/> Anteprima presentatore</>:m==='participant'?<><Users size={22}/> Anteprima partecipante</>:m==='mobile'?<><Users size={22}/> Anteprima smartphone</>:<><Square size={22}/> Anteprime affiancate</>}</button>)}</div>{!(snap.session.status==='active'||snap.session.status==='paused')&&<small>Le risposte della prova non incidono sulle statistiche.</small>}</div>{rehearsalOpen&&!designActivity&&<RehearsalErrorBoundary onClose={()=>setRehearsalOpen(false)}><SessionRehearsal initialMode={rehearsalMode} snapshot={snap} onClose={()=>setRehearsalOpen(false)}/></RehearsalErrorBoundary>}<button className="primary" onClick={()=>{setSessionTab('pages');if(snap.activities.length)beginPageDesign(snap.activities.find(a=>a.id===designActivity)||snap.activities[0]);else void createCanvasPage()}}>✎ Modifica le pagine</button><nav className="session-tabs" aria-label="Sezioni della sessione">{([['overview','Impostazioni e monitoraggio'],['pages','Pagine e contenuti']] as const).map(([id,label])=><button key={id} className={sessionTab===id?'primary':'outline'} aria-pressed={sessionTab===id} onClick={()=>setSessionTab(id)}>{label}</button>)}</nav><div className={`session-detail-layout session-tab-${sessionTab}`}><div><section className="panel"><h3>Metadati della sessione</h3><label>Nome<input placeholder={snap.session.title} value={sessionTitleEdit} onChange={e=>setSessionTitleEdit(e.target.value)}/></label><button className="outline small" disabled={snap.session.status==='closed'} onClick={updateSessionMetadata}>Salva nome</button><h4>Date della sessione</h4><p className="muted tiny">Ogni data comprende ora di inizio, durata e fuso orario IANA. Le modifiche vengono applicate dopo «Salva date della sessione».</p><div className="activity-row"><label>Data<input type="date" value={appointmentDate} onChange={e=>setAppointmentDate(e.target.value)}/></label><label>Ora di inizio<input type="time" value={appointmentTime} onChange={e=>setAppointmentTime(e.target.value)}/></label><label>Durata (min)<input type="number" min={5} max={1440} value={appointmentMinutes} onChange={e=>setAppointmentMinutes(Number(e.target.value))}/></label><label>Fuso orario IANA<input aria-label="Fuso orario della data" list="session-time-zones" value={appointmentZone} onChange={e=>setAppointmentZone(e.target.value)} placeholder="Europe/Rome"/><datalist id="session-time-zones"><option value="Europe/Rome"/><option value="Europe/Paris"/><option value="Europe/London"/><option value="UTC"/><option value="America/New_York"/><option value="Asia/Tokyo"/></datalist></label><button className="outline small" disabled={!appointmentDate||!/^([01]\d|2[0-3]):[0-5]\d$/.test(appointmentTime)||!Number.isInteger(appointmentMinutes)||appointmentMinutes<5||appointmentMinutes>1440||!appointmentZone||(()=>{try{new Intl.DateTimeFormat('en',{timeZone:appointmentZone});return false}catch{return true}})()} onClick={()=>setAppointments(a=>a.some(x=>x.date===appointmentDate&&x.start_time===appointmentTime&&x.time_zone===appointmentZone)?a:[...a,{date:appointmentDate,start_time:appointmentTime,duration_minutes:appointmentMinutes,time_zone:appointmentZone}].sort((x,y)=>`${x.date}T${x.start_time}`.localeCompare(`${y.date}T${y.start_time}`)))}>Aggiungi data</button></div>{appointments.length===0&&<p className="muted tiny">Non sono ancora state inserite date con orario.</p>}{appointments.map((a,i)=><div className="activity-row" key={`${a.date}-${a.start_time}-${a.time_zone}-${i}`}><span>{a.date} · {a.start_time} · {a.duration_minutes} min · {a.time_zone}</span><button className="outline small" aria-label={`Rimuovi data ${a.date} ${a.start_time}`} onClick={()=>setAppointments(v=>v.filter((_,n)=>n!==i))}>Rimuovi</button></div>)}<button className="primary small" onClick={async()=>{try{await request(`/sessions/${selected}/appointments`,'PUT',{appointments});setAppointments(await request(`/sessions/${selected}/appointments`));setNotice('Date della sessione salvate')}catch(e){notify(e)}}}>Salva date della sessione</button>{scheduleDates.length>0&&<details><summary>Importa date dal calendario precedente ({scheduleDates.length})</summary><p className="muted tiny">Le date precedenti non contengono l'ora. Imposta l'ora, la durata e il fuso qui sopra, poi importa e salva. Il vecchio calendario non viene eliminato automaticamente.</p><button className="outline small" onClick={()=>{setAppointments(v=>[...v,...scheduleDates.filter(d=>!v.some(x=>x.date===d&&x.start_time===appointmentTime&&x.time_zone===appointmentZone)).map(d=>({date:d,start_time:appointmentTime,duration_minutes:appointmentMinutes,time_zone:appointmentZone}))].sort((a,b)=>`${a.date}T${a.start_time}`.localeCompare(`${b.date}T${b.start_time}`)));setNotice('Date precedenti importate nella bozza: salva per confermare')}} disabled={!appointmentZone||!Number.isInteger(appointmentMinutes)||appointmentMinutes<5||appointmentMinutes>1440}>Importa date precedenti</button></details>}</section><section className="panel invitation-panel"><h3><Radio size={19}/> Invito alla sessione</h3><p>Inserisci questo QR code in qualsiasi PowerPoint o PDF.</p><div className="qr-layout"><img key={sessionQr.revision} className="qr" src={sessionQr.url?`/api/sessions/${selected}/qr?format=svg&revision=${sessionQr.revision}`:undefined} alt="QR code della sessione"/><div><p className="muted">Codice sessione</p><div className="join-code">{snap.session.join_code}</div>{sessionQr.url?<a href={sessionQr.url} target="_blank" rel="noreferrer">Link partecipanti <ExternalLink size={14}/></a>:<small role="status">{sessionQr.failed?"Link partecipanti non disponibile":"Aggiornamento link partecipanti…"}</small>}<div className="downloads">{sessionQr.url&&<><a href={`/api/sessions/${selected}/qr?format=png&revision=${sessionQr.revision}`}><Download size={15}/> PNG</a><a href={`/api/sessions/${selected}/qr?format=svg&revision=${sessionQr.revision}`}><Download size={15}/> SVG</a></>}</div></div></div></section><section className="panel"><h3><Plus size={19}/> Crea contenuti con i widget</h3><p className="muted">Apri l’editor grafico per creare o duplicare pagine, scegliere lo sfondo, aggiungere widget e configurare domande, sondaggi e quiz. La pagina si apre direttamente nell’editor, dove puoi modificarla subito.</p><p className="muted tiny">Seleziona una miniatura nell’editor. Usa il clic destro (pressione prolungata su mobile) per le azioni contestuali.</p><button type="button" className="primary" onClick={()=>{setSessionTab('pages');if(!designActivity&&snap.activities.length)beginPageDesign(snap.activities[0]);else if(!snap.activities.length)void createCanvasPage()}}>✎ Modifica le pagine</button></section></div><div><details className="panel live-stats-tools" aria-label="Statistiche delle interazioni live">
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
 </details>{designActivity&&<section className="panel powerpoint-editor editor-ux-v2" id="quorivio-slide-editor" aria-label="Editor grafico delle pagine" onPointerDown={e=>{if(e.pointerType==='mouse')return;const button=(e.target as HTMLElement).closest('button');if(button&&!button.classList.contains('editor-icon-tool')&&!button.hasAttribute('data-graphic-palette'))setEditorTouchHint(button.title||button.getAttribute('aria-label')||button.textContent?.trim()||'')}}>
<header className="editor-mock-header"><div className="editor-mock-brand"><img src="/editor-quorivio-logo.svg" alt="Quorivio"/></div> <div className="editor-device-switch" role="group" aria-label="Layout da modificare (selettore superiore)">
   <span className={canvasDevice==='desktop'?'device-label is-active':'device-label'}>Desktop 16:9</span>
   <label className="editor-device-slider" title="Passa tra editor desktop e smartphone">
     <input type="checkbox" role="switch" aria-label="Modifica layout Smartphone" checked={canvasDevice==='phone'} onChange={e=>setCanvasDevice(e.target.checked?'phone':'desktop')}/>
     <span className="editor-device-slider-track" aria-hidden="true"><span className="editor-device-slider-thumb"/></span>
   </label>
   <span className={canvasDevice==='phone'?'device-label is-active':'device-label'}>Smartphone 390px</span>
   {canvasDevice==='phone'&&<button className="outline small editor-mobile-reset" type="button" title="Ripristina layout smartphone automatico · elimina eventuali vecchie posizioni memorizzate e ricompatta la pagina" onClick={()=>setMobileLayoutDraft(old=>({...old,positions:undefined}))}>Ricompatta automaticamente</button>}
   <small>{canvasDevice==='phone'?(Object.keys(mobileLayoutDraft.positions||{}).length?`${Object.keys(mobileLayoutDraft.positions||{}).length} widget con posizione personalizzata · altri automatici`:'Disposizione automatica derivata dai widget desktop · puoi spostare e ridimensionare i widget'):'Layout proiettore e desktop. Gli stili e i contenuti sono condivisi.'}</small>
 </div><div className="editor-mock-actions"><div className="editor-mock-action-buttons"><div className="editor-quick-actions" role="toolbar" aria-label="Comandi editor pagine">
<button type="button" title="Taglia i widget selezionati (Ctrl/Cmd+X)" aria-label="Taglia widget selezionati" disabled={!editorSelectedWidgets.length||pageConflict} onClick={()=>issueEditorClipboard('cut')}><Scissors size={17}/></button>
<button type="button" title="Copia i widget selezionati (Ctrl/Cmd+C)" aria-label="Copia widget selezionati" disabled={!editorSelectedWidgets.length} onClick={()=>issueEditorClipboard('copy')}><Copy size={17}/></button>
<button type="button" title="Incolla i widget copiati (Ctrl/Cmd+V)" aria-label="Incolla widget" disabled={!editorClipboardReady||pageConflict||pageWidgets.length>=16} onClick={()=>issueEditorClipboard('paste')}><ClipboardPaste size={17}/></button>
<button type="button" title="Informazioni sul widget selezionato o sull'editor" aria-label="Informazioni editor" onClick={()=>{if(editorSelectedWidgets.length){setPageContextOpen(false);setInspectedWidget(editorSelectedWidgets[0]);}else setEditorInfoOpen(true)}}><Info size={17}/></button>
<button type="button" title="Annulla l'ultima modifica (Ctrl/Cmd+Z)" aria-label="Annulla modifica" disabled={!widgetHistory.past.length||widgetHistory.gestureBase!==null||pageConflict} onClick={undoPageWidgets}><Undo2 size={17}/></button>
<button type="button" title="Ripristina la modifica annullata (Ctrl/Cmd+Y o Ctrl/Cmd+Maiusc+Z)" aria-label="Ripeti modifica" disabled={!widgetHistory.future.length||widgetHistory.gestureBase!==null||pageConflict} onClick={redoPageWidgets}><Redo2 size={17}/></button>
</div><span role="status" aria-live="polite" className={'editor-autosave-indicator'+((pageSaveError||pageConflict)?' has-error':'')}>{pageConflict?'Conflitto di revisione':pageSaveError?'Errore salvataggio: '+pageSaveError:pageSavePending?'Salvataggio automatico…':pageHasUnsavedChanges?'Modifiche in attesa…':'Salvato automaticamente'}</span><button type="button" className="editor-preview-open editor-schemes-open" title="Apri l'editor degli schemi (titoli e footer)" onClick={()=>{if(confirmPageNavigation()){setRehearsalOpen(false);setInspectedWidget('');openSchemaEditor()}}}>▤ Schemi</button>{(['presenter','participant','mobile','both'] as RehearsalMode[]).map(m=><button key={m} type="button" className={'editor-preview-open preview-'+m} aria-haspopup="dialog" aria-expanded={rehearsalOpen&&rehearsalMode===m} onClick={()=>{setRehearsalMode(m);setRehearsalOpen(true)}}>{m==='presenter'?'▶ Presentatore':m==='participant'?'▶ Partecipante':m==='mobile'?'▯ Smartphone':'▣ Affiancate'}</button>)}<button type="button" className="editor-exit" onClick={()=>void exitPageEditor()}>Esci</button></div><div className="editor-mock-meta" aria-label="Presentazione e proprietari"><span className="editor-session-title" title={snap.session.title}>{snap.session.title}</span><div className="editor-presenter-identities" aria-label="Proprietario e collaboratori della sessione"><span className="editor-owner-chip" title="Proprietario primario">Proprietario primario: {availablePresenters.find(p=>p.is_owner)?.name||'Proprietario'}</span>{availablePresenters.filter(p=>!p.is_owner).map(p=><span key={p.id} className="editor-collaborator-chip" title="Collaboratore della sessione">{p.name}</span>)}</div></div></div></header>
{editorInfoOpen&&<div className="presentation-import-backdrop" role="presentation"><section className="presentation-import-dialog" role="dialog" aria-modal="true" aria-label="Informazioni editor"><h3>Comandi dell'editor</h3><p>Seleziona uno o più widget per tagliare, copiare e visualizzarne le proprietà. Incolla nella pagina corrente o in un'altra pagina della stessa sessione. Annulla e Ripeti agiscono sulla cronologia della pagina in modifica.</p><p className="muted tiny">Scorciatoie: Ctrl/Cmd+C, X, V, Z; Ctrl/Cmd+Y o Ctrl/Cmd+Maiusc+Z per ripetere. Le operazioni non sostituiscono la modifica del testo nei campi attivi.</p><button type="button" className="primary" onClick={()=>setEditorInfoOpen(false)}>Chiudi informazioni</button></section></div>}
{rehearsalOpen&&<RehearsalErrorBoundary onClose={()=>setRehearsalOpen(false)}><SessionRehearsal initialMode={rehearsalMode} initialPageId={designActivity} snapshot={{...snap,activities:snap.activities.map(a=>a.id===designActivity?{...a,page_design:{...((a as any).page_design||{}),widgets:pageWidgets,mobile:mobileLayoutDraft,backgroundColor:questionBackgroundColor,backgroundUrl:questionBackground,backgroundAssetId:questionBackgroundAsset,header:questionHeader}}:a)}} onClose={()=>setRehearsalOpen(false)}/></RehearsalErrorBoundary>}
<aside className="page-editor-sidebar" aria-label="Miniature delle pagine" onContextMenu={e=>{clearSidebarLongPress();if((e.target as HTMLElement).closest('.page-editor-thumb-row,.page-editor-thumb-menu-floating'))return;e.preventDefault();openSidebarEmptyMenu({clientX:e.clientX,clientY:e.clientY})}} onTouchStart={e=>{if((e.target as HTMLElement).closest('button,input,select,textarea,.page-editor-thumb-row'))return;clearSidebarLongPress();const touch=e.touches[0];if(!touch)return;const x=touch.clientX,y=touch.clientY;sidebarLongPress.current=window.setTimeout(()=>{sidebarLongPress.current=undefined;openSidebarEmptyMenu({clientX:x,clientY:y})},650)}} onTouchMove={clearSidebarLongPress} onTouchEnd={clearSidebarLongPress} onTouchCancel={clearSidebarLongPress}>
  <header><strong>Pagine</strong><span aria-label={`Totale ${snap.activities.length} pagine`}>{snap.activities.length}</span></header>
  <p className="page-editor-order-status" role="status" aria-live="polite">{pageOrderAnnouncement}</p><small className="thumbnail-selection-help" aria-live="polite">{selectedPageIds.length>1?`${selectedPageIds.length} pagine selezionate · D duplica · R rinomina · Backspace elimina`:'Ctrl/Cmd+clic: selezione multipla · D/R/Backspace'}</small>
  {pageExportError&&<p className="page-editor-export-error" role="alert">{pageExportError}</p>}
  <div className="page-editor-thumbnails" aria-busy={pageOrderPending}>
   {snap.activities.map((a,i)=><React.Fragment key={a.id}><div className="page-editor-drop-slot" data-insert-index={i} data-active={pageDropSlot===i} role="separator" aria-label={`Inserisci pagina prima della pagina ${i+1}`} onDragOver={e=>{if(!e.dataTransfer.types.includes('application/x-quorivio-page'))return;e.preventDefault();e.dataTransfer.dropEffect='move';setPageDropSlot(i)}} onDragLeave={e=>{if(!(e.currentTarget.contains(e.relatedTarget as Node)))setPageDropSlot(v=>v===i?null:v)}} onDrop={e=>{e.preventDefault();e.stopPropagation();setPageDropSlot(null);const id=e.dataTransfer.getData('application/x-quorivio-page');if(id)void dropPageAtSlot(id,i)}}/>
   <div className={'page-editor-thumb-row'+(designActivity===a.id?' is-active':'')+(selectedPageIds.includes(a.id)?' is-selected':'')} key={a.id}
      draggable={snap.session.status!=='closed'&&!pageOrderPending}
      onDragStart={e=>{e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('application/x-quorivio-page',a.id)}} onDragEnd={()=>setPageDropSlot(null)}
      onDragOver={e=>{if(e.dataTransfer.types.includes('application/x-quorivio-page'))e.preventDefault()}}
      onDrop={e=>{e.preventDefault();const dragged=e.dataTransfer.getData('application/x-quorivio-page');if(dragged)void dropPage(dragged,a.id)}}
      onContextMenu={e=>{e.preventDefault();openThumbnailMenu(a.id,{clientX:e.clientX,clientY:e.clientY})}}>
     <button type="button" className="page-editor-thumb" aria-current={designActivity===a.id?'page':undefined} aria-pressed={selectedPageIds.includes(a.id)}
       aria-label={`Mostra pagina ${i+1}: ${a.title}; Ctrl/Cmd+clic seleziona più pagine; D duplica, R rinomina, Backspace elimina`} 
       aria-keyshortcuts="Alt+ArrowUp Alt+ArrowDown D R Backspace"
       onClick={e=>{if(e.ctrlKey||e.metaKey){setSelectedPageIds(v=>choosePageIds(v,a.id,true));return}setSelectedPageIds([a.id]);beginPageDesign(a)}} onKeyDown={e=>{if(!['ArrowUp','ArrowDown','Home','End'].includes(e.key))return;e.preventDefault();const pages=snap.activities;const to=e.key==='Home'?0:e.key==='End'?pages.length-1:Math.max(0,Math.min(pages.length-1,i+(e.key==='ArrowDown'?1:-1)));if(e.altKey){if((e.key==='ArrowUp'||e.key==='ArrowDown')&&to!==i)void dropPage(a.id,pages[to].id);return}if(pages[to]){beginPageDesign(pages[to]);requestAnimationFrame(()=>document.querySelectorAll<HTMLButtonElement>('.page-editor-thumb')[to]?.focus())}}}>
       {!(a as any).page_design?.importedImageFit&&<span className="page-editor-thumb-number" aria-hidden="true">{String(i+1).padStart(2,'0')}</span>}
       <span data-imported-image={(a as any).page_design?.importedImageFit?'true':undefined} className="page-editor-preview" aria-hidden="true" style={slideBackgroundCss((a as any).page_design,snap.session.theme,id=>assets.find(x=>x.id===id)?.url||`/api/sessions/${selected}/assets/${id}`)}>{!(a as any).page_design?.importedImageFit&&<span className="page-editor-preview-title">{(a as any).page_design?.header||a.title}</span>}{(designActivity===a.id?pageWidgets:((a as any).page_design?.widgets||[])).slice(0,40).map((w:any,i:number)=>{const p=w.position||{x:(i%2)*50,y:Math.floor(i/2)*14,width:48,height:24};return <span key={w.id||i} className="page-editor-preview-widget" style={{left:`${Math.max(0,Math.min(100,Number(p.x)||0))}%`,top:`${Math.max(0,Math.min(100,Number(p.y)||0))}%`,width:`${Math.max(1,Math.min(100,Number(p.width)||20))}%`,height:`${Math.max(1,Math.min(100,Number(p.height)||15))}%`,transform:`rotate(${Number(p.rotation)||0}deg)`,backgroundColor:w.style?.fillNone?'transparent':w.style?.fillColor||'#e7e8f4',...widgetAppearanceStyle(w.style)}} title={w.label||w.kind}><ThumbnailWidgetContent widget={w} assetUrl={w.assetId?(assets.find(asset=>asset.id===w.assetId)?.url||`/api/sessions/${selected}/assets/${w.assetId}`):undefined}/></span>})}</span>
     </button>
     <span className="page-editor-thumbnail-caption" aria-label={`Numero pagina ${i+1}`}>{i+1}</span>
     <button type="button" className="page-editor-thumb-menu-trigger"  aria-label={`Menu pagina ${i+1}: crea, duplica, elimina, sposta`}
       aria-expanded={pageThumbMenu===a.id} onClick={e=>{if(pageThumbMenu===a.id){setPageThumbMenu('');return}const box=e.currentTarget.getBoundingClientRect();openThumbnailMenu(a.id,{clientX:box.right+8,clientY:box.top,anchor:{left:box.left,right:box.right,top:box.top,bottom:box.bottom}})}}><MoreVertical size={19}/></button>
     {pageThumbMenu===a.id&&createPortal(<div className="page-editor-thumb-menu page-editor-thumb-menu-floating" style={{position:'fixed',left:pageMenuPosition.left,top:pageMenuPosition.top,maxHeight:pageMenuPosition.maxHeight,'--thumbnail-menu-max-height':`${pageMenuPosition.maxHeight}px`,'--thumbnail-menu-width':`${pageMenuPosition.width}px`} as React.CSSProperties} role="group" aria-label={`Azioni pagina ${i+1}`} onKeyDown={e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();const trigger=document.querySelector<HTMLButtonElement>('.page-editor-thumb-menu-trigger[aria-expanded="true"]');setPageThumbMenu('');requestAnimationFrame(()=>trigger?.focus())}}}>
       <button type="button" title="Mostra questa pagina nell'editor" onClick={()=>{beginPageDesign(a);setPageThumbMenu('')}}>Apri pagina</button>
       {snap.session.status!=='closed'&&<>
       <button type="button" title="Rinomina questa pagina senza modificare i widget o le risposte" onClick={()=>{setPageThumbMenu('');void renameSelectedPages(a.id)}}>Rinomina {selectedPageIds.length>1?'pagine selezionate':'pagina'} (R)</button>
       <button type="button" title="Duplica questa pagina subito dopo" onClick={()=>{setPageThumbMenu('');void duplicateSelectedPages(a.id)}}>Duplica {selectedPageIds.length>1?'pagine selezionate':'pagina'} (D)</button>
       <details className="page-editor-thumb-submenu">
        <summary>Crea e importa pagine</summary>
        <div className="page-editor-thumb-submenu-items">
         <button type="button" title="Inserisce una pagina prima di questa" onClick={()=>{setPageThumbMenu('');void createCanvasPageAt(a.id,'before')}}>Nuova pagina prima</button>
         <button type="button" title="Inserisce una pagina dopo questa" onClick={()=>{setPageThumbMenu('');void createCanvasPageAt(a.id,'after')}}>Nuova pagina dopo</button>
         <label className="editor-thumb-import" title="Importa tutte le slide di un PDF o PowerPoint dopo questa pagina">Importa PDF/PPTX…<input type="file" aria-label={`Importa PDF o PPTX dopo pagina ${i+1}`} accept=".pdf,.pptx,application/pdf,application/vnd.openxmlformats-officedocument.presentationml.presentation" disabled={assetBusy||pageOrderPending} onChange={e=>{const f=e.target.files?.[0];e.target.value='';setPageThumbMenu('');if(f)setPendingPresentation({file:f,afterPageId:a.id})}}/></label>
         <label className="editor-thumb-import">Importa layout JSON<input type="file" aria-label={`Importa layout JSON nella pagina ${i+1}`} accept=".json,application/json" onChange={e=>{const f=e.target.files?.[0];e.target.value='';setPageThumbMenu('');openImportDraftFor(a,f)}}/></label>
        </div>
       </details>
       <details className="page-editor-thumb-submenu">
        <summary>Ordina pagine</summary>
        <div className="page-editor-thumb-submenu-items">
         <button type="button" title="Sposta la pagina prima della precedente" disabled={pageOrderPending||i===0} onClick={()=>{setPageThumbMenu('');void movePage(i,i-1)}}>Sposta su</button>
         <button type="button" title="Sposta la pagina dopo la successiva" disabled={pageOrderPending||i===snap.activities.length-1} onClick={()=>{setPageThumbMenu('');void movePage(i,i+1)}}>Sposta giù</button>
        </div>
       </details>
       <details className="page-editor-thumb-submenu">
        <summary>Esporta e dati</summary>
        <div className="page-editor-thumb-submenu-items">
         <button type="button" title="Esporta layout di questa pagina in JSON" onClick={()=>{try{downloadPageDraftFor(a);setPageExportError('');setPageThumbMenu('')}catch(e){setPageExportError('Esportazione non riuscita: '+(e instanceof Error?e.message:String(e)))}}}>Esporta layout JSON</button>
        </div>
       </details>
       <button type="button" className="editor-delete-action" title="Elimina definitivamente questa pagina" onClick={()=>{setPageThumbMenu('');void deleteSelectedPages(a.id)}}>Elimina {selectedPageIds.length>1?'pagine selezionate':'pagina'} (Backspace)</button>
       </>}
     </div>,document.body)}
    </div></React.Fragment>)}
   <div className="page-editor-drop-slot page-editor-drop-slot-final" data-insert-index={snap.activities.length} data-active={pageDropSlot===snap.activities.length} role="separator" aria-label="Inserisci pagina dopo l'ultima pagina" onDragOver={e=>{if(!e.dataTransfer.types.includes('application/x-quorivio-page'))return;e.preventDefault();e.dataTransfer.dropEffect='move';setPageDropSlot(snap.activities.length)}} onDragLeave={()=>setPageDropSlot(null)} onDrop={e=>{e.preventDefault();setPageDropSlot(null);const id=e.dataTransfer.getData('application/x-quorivio-page');if(id)void dropPageAtSlot(id,snap.activities.length)}}/>
  </div>
  {!snap.activities.length&&<EditorIconTool label="Crea la prima pagina" onClick={()=>void createCanvasPage()}><Plus size={22}/></EditorIconTool>}
</aside>
<div className="editor-stage" data-editor-device={canvasDevice}>

 <div className="editor-canvas-slot">
  <WidgetCanvas key={`${selected}:${designActivity}:${canvasDevice}`} widgets={canvasDevice==='phone'?mobilePageWidgets(pageWidgets,mobileLayoutDraft):pageWidgets} numberingWidgets={(snap.activities.find(a=>a.id===designActivity) as any)?.page_design?.suppressMaster?pageWidgets:resolveSlideMasterWidgets(pageWidgets,snap.session.theme?.master?.widgets)} mobileMode={canvasDevice==='phone'} mobileHeight={mobileStageHeight(pageWidgets,mobileLayoutDraft)} mobileBackgroundColor={mobileLayoutDraft.backgroundColor} pageTitle={snap.activities.find(a=>a.id===designActivity)?.title||""} sessionTitle={snap.session.title} pageNumber={slidePageNumber(snap.activities,designActivity)} masterTitleStyle={snap.session.theme?.master?.titleStyle} sourceActivities={snap.activities} currentActivityId={designActivity} onChange={changeCanvasWidgets} onAutoFit={canvasDevice==='phone'?undefined:reconcilePageAutoFit}
    toolbarCommand={editorToolbarCommand} onToolbarClipboardChange={setEditorClipboardReady} onSelectionChange={ids=>setEditorSelectedWidgets(before=>before.length===ids.length&&before.every((id,index)=>id===ids[index])?before:ids)}
    onBeginGesture={beginPageWidgetGesture} onEndGesture={endPageWidgetGesture}
    assets={assets} backgrounds={backgrounds} onRenameLibraryImage={renameLibraryImage} onDeleteLibraryImage={deleteLibraryImage} sessionId={selected} joinCode={snap.session.join_code} onUpload={uploadWidgetMedia} assetBusy={assetBusy}
    importedImageFit={(snap.activities.find(a=>a.id===designActivity) as any)?.page_design?.importedImageFit} backgroundAssetId={canvasDevice==='phone'?mobileLayoutDraft.backgroundAssetId||'':slideBackground({backgroundAssetId:questionBackgroundAsset||undefined,backgroundUrl:questionBackground||undefined},snap.session.theme).assetId||''} onBackgroundSelect={id=>{if(canvasDevice==='phone'){if(id)void selectLibraryBackground(id,false,true);else setMobileLayoutDraft(old=>({...old,backgroundAssetId:undefined}));}else if(id)void selectLibraryBackground(id,false);else setQuestionBackgroundAsset('')}}
    onBackgroundUpload={file=>uploadBackground(file,false,canvasDevice==='phone')} onBackgroundColorChange={color=>setMobileLayoutDraft(old=>({...old,backgroundColor:color,backgroundAssetId:undefined}))}
    pageAudienceId={pageAudienceId} onPageAudienceChange={setPageAudienceId} pagePresenterHidden={pagePresenterHidden} onPagePresenterHiddenChange={setPagePresenterHidden} pageOptions={snap.activities}
    onRenamePage={renameCurrentCanvasPage}
    onContextOpen={()=>{setPageContextOpen(false);setInspectedWidget('');setPageThumbMenu('')}} dismissContextMenus={!!pageThumbMenu} suspendFormattingRibbon={pageConflict} onSaveRequested={()=>void updatePageDesign()} onOpenPageSettings={()=>{setInspectedWidget('');setPageContextOpen(true)}} onInspectWidget={id=>{setPageContextOpen(false);setInspectedWidget(id)}}/>
  {pageContextOpen&&<EditorFloatingWindow portal placement="page" className="editor-context-drawer" ariaLabel="Impostazioni contestuali pagina">
    <div className="editor-drawer-heading"><strong>Impostazioni pagina e risultati</strong><button type="button" className="editor-drawer-close" aria-label="Chiudi impostazioni pagina" onClick={()=>setPageContextOpen(false)}>×</button></div>
     <section className="slide-master-editor" aria-label="Instradamento proiezione live"><h4>Proiezione presentatore e partecipanti</h4>
       <label>Pagina visibile ai partecipanti quando il presentatore mostra questa pagina
        <select aria-label="Pagina destinata ai partecipanti" value={pageAudienceId} onChange={e=>setPageAudienceId(e.target.value)}>
         <option value="">Questa stessa pagina (predefinita)</option>
         {snap.activities.map((page,i)=><option key={page.id} value={page.id}>{i+1}. {page.title}{page.page_design?.presenterHidden?' · solo partecipanti':''}</option>)}
        </select>
       </label>
       <label><input type="checkbox" aria-label="Salta questa pagina sullo schermo del presentatore" checked={pagePresenterHidden} onChange={e=>setPagePresenterHidden(e.target.checked)}/> Salta questa pagina nella navigazione dello schermo presentatore</label>
       <small>Le pagine saltate rimangono disponibili ai partecipanti e come sorgenti di statistiche. Il presentatore può mostrare una pagina di risultati mentre il pubblico risponde su una pagina diversa.</small>
     </section>
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
     <div><strong>Seleziona sfondo pagina dalla libreria</strong><BackgroundGallery items={backgrounds} disabled={assetBusy} label="Seleziona sfondo pagina dalla libreria" onSelect={id=>void selectLibraryBackground(id,false)}/></div>
     <label>Carica un nuovo sfondo<input type="file" accept="image/png,image/jpeg,image/gif,image/webp" disabled={assetBusy} onChange={e=>{void uploadBackground(e.target.files?.[0],false).catch(()=>{});e.target.value=''}}/></label>
     <button type="button" className="outline small" onClick={()=>{setQuestionBackgroundAsset('');setQuestionBackground('')}}>Rimuovi sfondo pagina</button>
     <label>Testo sopra i risultati<input value={resultHeader} onChange={e=>setResultHeader(e.target.value)}/></label>
     <label>Colore sfondo risultati<input type="color" value={resultBackgroundColor||'#ffffff'} onChange={e=>setResultBackgroundColor(e.target.value)}/></label>
     <p>{resultBackgroundAsset?'Sfondo dei risultati applicato':'Nessuna immagine di sfondo risultati applicata'}</p>
     <div><strong>Seleziona sfondo risultati dalla libreria</strong><BackgroundGallery items={backgrounds} disabled={assetBusy} label="Seleziona sfondo risultati dalla libreria" onSelect={id=>void selectLibraryBackground(id,true)}/></div>
     <label>Carica sfondo risultati<input type="file" accept="image/png,image/jpeg,image/gif,image/webp" disabled={assetBusy} onChange={e=>{void uploadBackground(e.target.files?.[0],true).catch(()=>{});e.target.value=''}}/></label>
     <button type="button" className="outline small" onClick={()=>{setResultBackgroundAsset('');setResultBackground('')}}>Rimuovi sfondo risultati</button>
   </EditorFloatingWindow>}
  {inspectedWidget&&<EditorFloatingWindow portal placement="properties" className="editor-context-drawer editor-widget-drawer" ariaLabel="Proprietà widget selezionato">
   <div className="editor-drawer-heading"><strong>Proprietà widget</strong><button type="button" className="editor-drawer-close" aria-label="Chiudi proprietà widget" onClick={()=>setInspectedWidget('')}>×</button></div>
   {pageWidgets.filter(w=>w.id===inspectedWidget).map(w=><div key={w.id} className="slide-master-widget-settings" onPointerDown={e=>{if((e.target as HTMLElement).closest('input,textarea,[contenteditable=true]'))e.stopPropagation()}}>
    {canvasDevice==='phone'&&mobileLayoutDraft.positions?.[w.id]&&<button type="button" className="outline small" onClick={()=>setMobileLayoutDraft(old=>{const positions={...old.positions};delete positions[w.id];return {...old,positions:Object.keys(positions).length?positions:undefined}})}>Ripristina posizione automatica smartphone per questo widget</button>}
   {canvasDevice==='phone'&&<section className="editor-phone-appearance" aria-label="Stile smartphone del widget">
      <h4>Stile smartphone (indipendente dal desktop)</h4>
      <label>Font smartphone<select aria-label="Font smartphone" value={mobileLayoutDraft.styles?.[w.id]?.fontFamily||w.style?.fontFamily||'Arial'} onChange={e=>setMobileLayoutDraft(old=>({...old,styles:{...old.styles,[w.id]:{...old.styles?.[w.id],fontFamily:e.target.value}}}))}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(name=><option key={name} value={name}>{name}</option>)}</select></label>
      <label>Dimensione font smartphone (px)<input type="number" min={10} max={96} value={mobileLayoutDraft.styles?.[w.id]?.fontSize||w.style?.fontSize||16} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=10&&n<=96)setMobileLayoutDraft(old=>({...old,styles:{...old.styles,[w.id]:{...old.styles?.[w.id],fontSize:n}}}))}}/></label>
      <label>Colore testo smartphone<input type="color" value={mobileLayoutDraft.styles?.[w.id]?.color||w.style?.color||'#000000'} onChange={e=>setMobileLayoutDraft(old=>({...old,styles:{...old.styles,[w.id]:{...old.styles?.[w.id],color:e.target.value}}}))}/></label>
      {mobileLayoutDraft.styles?.[w.id]&&<button type="button" className="outline small" onClick={()=>setMobileLayoutDraft(old=>{const styles={...old.styles};delete styles[w.id];return {...old,styles:Object.keys(styles).length?styles:undefined}})}>Ripristina stile smartphone automatico per questo widget</button>}
      <small className="muted">Font, dimensioni e colori personalizzati su smartphone non modificano il desktop. Il resto delle proprietà del widget è condiviso.</small>
   </section>}
   {w.kind==='title'&&<><h4>Titolo della pagina</h4><label><input type="checkbox" checked={w.titleFollowPage!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,titleFollowPage:e.target.checked}:z))}/> Usa il nome corrente della pagina</label><label><input type="checkbox" checked={w.titleUseMaster!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,titleUseMaster:e.target.checked}:z))}/> Usa lo schema del titolo della sessione</label>{w.titleFollowPage===false&&<label>Testo personalizzato<input maxLength={240} value={w.label||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,label:e.target.value}:z))}/></label>}<small>Disattivando lo schema, il widget usa la propria formattazione.</small></>}
    <label><input type="checkbox" checked={w.kind==='qr'?w.showTitle===true:w.showTitle!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,showTitle:e.target.checked}:z))}/>Mostra nome/titolo del widget</label>
    {w.kind==='qr'&&<section className="widget-qr-properties" aria-label="Proprietà Codice QR">
      <label><input type="checkbox" checked={w.showQrUrl!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,showQrUrl:e.target.checked}:z))}/>Mostra URL sotto al codice QR</label>
      {w.showTitle===true&&<label>Testo del titolo QR<input maxLength={240} value={w.label||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,label:e.target.value}:z))}/></label>}
      <small className="muted">Il titolo è nascosto per impostazione predefinita. Quando l'URL è visibile, resta sotto al codice anche dopo il ridimensionamento.</small>
    </section>}
    
   {requiresAnswerSubmit(w.kind)&&<section className="widget-answer-typography" aria-label="Formattazione delle risposte e invio"><h4>Risposte e pulsante invio</h4>
    <label>Font risposta<select aria-label="Font campo risposta" value={w.style?.answerFontFamily||w.style?.fontFamily||'Arial'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerFontFamily:e.target.value}}:z))}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(f=><option key={f}>{f}</option>)}</select></label>
    <label>Dimensione carattere risposta (px)<input type="number" min={10} max={96} value={w.style?.answerFontSize||w.style?.fontSize||16} onChange={e=>{const v=Number(e.target.value);if(Number.isInteger(v)&&v>=10&&v<=96)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerFontSize:v}}:z))}}/></label>
    <label>Colore testo risposta<input type="color" value={w.style?.answerColor||'#152236'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerColor:e.target.value}}:z))}/></label>
    <label><input type="checkbox" checked={!!w.style?.answerBold} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerBold:e.target.checked}}:z))}/> Risposta in grassetto</label>
    <label><input type="checkbox" checked={!!w.style?.answerItalic} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerItalic:e.target.checked}}:z))}/> Risposta in corsivo</label>
    <label><input type="checkbox" checked={!!w.style?.answerUnderline} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerUnderline:e.target.checked}}:z))}/> Risposta sottolineata</label>
    <label><input type="checkbox" checked={!!w.style?.answerStrikethrough} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerStrikethrough:e.target.checked}}:z))}/> Risposta barrata</label>
     <label>Larghezza casella risposta libera (%)<input type="number" aria-label="Larghezza casella risposta libera" min={25} max={100} step={5} value={w.style?.answerFieldWidth||100} onChange={e=>{const v=Number(e.target.value);if(Number.isInteger(v)&&v>=25&&v<=100)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerFieldWidth:v}}:z))}}/></label>
     <label>Altezza casella risposta libera (px)<input type="number" aria-label="Altezza casella risposta libera" min={48} max={400} step={8} value={w.style?.answerFieldHeight||96} onChange={e=>{const v=Number(e.target.value);if(Number.isInteger(v)&&v>=48&&v<=400)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,answerFieldHeight:v}}:z))}}/></label>
    <label>Dimensione pulsante invio (px)<input type="number" aria-label="Dimensione pulsante invio" min={12} max={40} value={w.style?.submitButtonSize||16} onChange={e=>{const v=Number(e.target.value);if(Number.isInteger(v)&&v>=12&&v<=40)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,submitButtonSize:v}}:z))}}/></label>
    <p className="muted tiny">Le opzioni di scelta supportano anche la formattazione dei singoli caratteri tramite la palette.</p>
   </section>}
 {w.kind==='footer'&&<><h4>Footer della pagina</h4><label><input type="checkbox" checked={w.footerShowSessionTitle!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,footerShowSessionTitle:e.target.checked}:z))}/> Mostra il nome della sessione nel footer</label><label><input type="checkbox" checked={w.footerShowPageNumber!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,footerShowPageNumber:e.target.checked}:z))}/> Mostra il numero della pagina a destra</label>{w.footerShowSessionTitle===false&&<label>Testo centrale personalizzato<input maxLength={240} value={w.label||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,label:e.target.value}:z))}/></label>}<small>La numerazione si aggiorna automaticamente al riordino delle diapositive.</small></>}
   </div>)}
   <ol className="widget-list">{pageWidgets.map((w,i)=>({w,i})).filter(x=>x.w.id===inspectedWidget).map(({w,i})=><li key={w.id} draggable onDragStart={e=>e.dataTransfer.setData('text/plain',String(i))} onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();const from=Number(e.dataTransfer.getData('text/plain'));if(Number.isInteger(from)&&from>=0&&from<pageWidgets.length)setPageWidgets(old=>{const next=[...old];const [m]=next.splice(from,1);next.splice(i,0,m);return next})}}><span aria-label="Trascina">⠿ {w.kind}</span>{eligibleStatisticSources(pageWidgets).some(source=>source.id===w.id)&&<label>Grafico risultati del widget<select aria-label={'Grafico risultati '+w.id} value={(w as any).resultsView||'bars'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,resultsView:e.target.value}:z))}><option value="bars">Barre</option><option value="pie">Torta</option><option value="table">Tabella</option><option value="cloud">Nuvola</option><option value="gauge">Gauge</option>{w.kind==='reactions'&&<option value="bubbles">Bolle emoji (reazioni)</option>}</select></label>}{w.kind==='results-button'&&<label className="widget-results-top-setting">Risultati principali da mostrare<input type="number" aria-label="Numero risultati principali" min={1} max={20} step={1} value={w.resultTopCount??5} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=1&&n<=20)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,resultTopCount:n}:z))}}/><small>Default 5 · tutte le voci selezionate saranno mostrate per intero, riscalandole se necessario.</small></label>}
     {w.kind==='results-button'&&<label className="widget-results-only-setting"><input type="checkbox" aria-label="Mostra soltanto i risultati" checked={w.resultsOnly===true} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,resultsOnly:e.target.checked,showSourceQuestion:e.target.checked?false:z.showSourceQuestion,showSourceTitle:e.target.checked?false:z.showSourceTitle,showSourceAnswers:e.target.checked?false:z.showSourceAnswers}:z))}/> Solo risultati (nascondi titolo e testo della domanda)<small>Disattivata per impostazione predefinita. I conteggi restano visibili soltanto al presentatore.</small></label>}{w.kind==='results-button'&&<label className="widget-source-title-setting"><input type="checkbox" aria-label="Mostra titolo della widget collegata" checked={w.showSourceTitle??w.showSourceQuestion===true} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,showSourceTitle:e.target.checked,showSourceAnswers:z.showSourceAnswers??z.showSourceQuestion===true,showSourceQuestion:e.target.checked,resultsOnly:e.target.checked?false:z.resultsOnly}:z))}/> Mostra titolo della widget collegata<small>Il titolo appare in alto, su una riga nuova, più grande e in grassetto.</small></label>}{w.kind==='results-button'&&<label className="widget-source-answers-setting"><input type="checkbox" aria-label="Mostra risposte della widget collegata" checked={w.showSourceAnswers??w.showSourceQuestion===true} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,showSourceAnswers:e.target.checked,showSourceTitle:z.showSourceTitle??z.showSourceQuestion===true,resultsOnly:e.target.checked?false:z.resultsOnly}:z))}/> Mostra risposte della widget collegata<small>Ogni risposta è in grassetto e preceduta da un pallino. La domanda ha un colore distinto, configurabile da Formato widget. Le soluzioni sono nascoste finché non abiliti lo switch dedicato.</small></label>}{w.kind==='results-button'&&resultHasAnswerKey(linkedStatisticSource(w,w.targetActivityId?(snap.activities.find(a=>a.id===w.targetActivityId)?.page_design?.widgets||[]):pageWidgets)||{},w.targetQuestionId||'')&&<label className="widget-show-correct-setting"><input type="checkbox" role="switch" aria-label="Evidenzia risposte vere nei risultati" checked={w.showCorrectAnswers===true} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,showCorrectAnswers:e.target.checked}:z))}/> Evidenzia le risposte vere nei risultati<small>Solo per il presentatore; disattivato per impostazione predefinita. Non pubblica le chiavi ai partecipanti.</small></label>}
     {w.kind==='results-button'&&<label className="widget-auto-fit-setting"><input type="checkbox" aria-label="Ridimensionamento automatico contenuto risultati" checked={w.autoFit!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,autoFit:e.target.checked}:z))}/> Adatta automaticamente il contenuto alla dimensione del widget<small>Attivo per default: ridimensiona proporzionalmente insieme grafici, legende, percentuali, risposte e testi, senza scorrimento. Rimane attivo quando modifichi geometria, font e opzioni.</small></label>}{w.kind==='results-button'&&<label>Pagina sorgente delle statistiche<select aria-label="Pagina sorgente statistiche" value={w.targetActivityId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,targetActivityId:e.target.value||undefined,targetWidgetId:undefined,targetQuestionId:undefined}:z))}><option value="">Questa stessa pagina</option>{snap.activities.filter(page=>page.id!==designActivity).map((page,i)=><option key={page.id} value={page.id}>{page.title}</option>)}</select></label>}
     {w.kind==='results-button'&&<label>Widget sorgente delle statistiche<select aria-label="Widget sorgente statistiche" value={w.targetWidgetId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,targetWidgetId:e.target.value||undefined,targetQuestionId:undefined}:z))}><option value="">Seleziona un widget</option>{eligibleStatisticSources(w.targetActivityId?(snap.activities.find(page=>page.id===w.targetActivityId)?.page_design?.widgets||[]):pageWidgets,w.id).map(source=><option key={source.id} value={source.id}>{source.label||editorWidgetNames[source.kind]||source.kind}</option>)}</select><small>Il presentatore vede i risultati live della pagina sorgente, anche se il pubblico è su una pagina diversa.</small></label>}{w.kind==='results-button'&&(w.targetActivityId?snap.activities.find(a=>a.id===w.targetActivityId)?.page_design?.widgets:pageWidgets)?.find((z:any)=>z.id===w.targetWidgetId)?.questions?.length&&<label>Domanda da visualizzare<select aria-label="Domanda sorgente delle statistiche" value={(w as any).targetQuestionId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,targetQuestionId:e.target.value||undefined}:z))}><option value="">Domanda principale</option>{((w.targetActivityId?snap.activities.find(a=>a.id===w.targetActivityId)?.page_design?.widgets:pageWidgets)?.find((z:any)=>z.id===w.targetWidgetId)?.questions||[]).map((q:any)=><option key={q.id} value={q.id}>{q.label}</option>)}</select></label>}{w.kind==='profile'&&<label>Testo aggiuntivo del presentatore<textarea aria-label="Testo opzionale profilo presentatore" maxLength={500} rows={3} value={w.description||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,description:e.target.value}:z))}/></label>}{w.kind==='reactions'&&<label>Dimensione icone delle reazioni (px)<input type="range" aria-label="Dimensione icone reazioni" min={16} max={96} step={2} value={w.reactionIconSize||32} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,reactionIconSize:Number(e.target.value)}:z))}/><output>{w.reactionIconSize||32}px</output></label>}{w.kind==='timer'&&<label>Durata massima countdown (secondi)<input type="number" aria-label="Durata massima countdown del widget" min={1} max={3600} step={1} value={w.durationSeconds??60} onChange={e=>{const value=Number(e.target.value);if(Number.isInteger(value)&&value>=1&&value<=3600)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,durationSeconds:value}:z))}}/><small>Da 1 secondo a 60 minuti. Allo scadere, tutte le interazioni della pagina vengono bloccate.</small></label>}{w.kind==='profile'&&<select aria-label="Presentatore da mostrare" value={(w as any).presenterId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,presenterId:e.target.value||undefined}:z))}><option value="">Autore della sessione</option>{availablePresenters.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select>}{['question','timed-quiz'].includes(w.kind)&&<label><input type="checkbox" checked={w.allowAnswerChange===true} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,allowAnswerChange:e.target.checked}:z))}/>Consenti al partecipante di modificare la risposta inviata (durante la finestra di voto)</label>}{w.kind==='profile'&&<label><input type="checkbox" checked={w.showEmail===true} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,showEmail:e.target.checked}:z))}/>Pubblica l'e-mail del presentatore nella pagina (visibile a tutti i partecipanti)</label>}{w.kind==='rating'&&<p className="muted tiny">0 = gradimento minimo · 9 = gradimento massimo</p>}{w.kind==='rating'&&<select aria-label="Oggetto del gradimento" value={(w as any).targetKind||'question'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,targetKind:e.target.value}:z))}><option value="question">Domanda</option><option value="quiz">Quiz</option><option value="session">Sessione</option><option value="presenter">Presentatore</option></select>}{w.kind==='rating'&&(w as any).targetKind==='presenter'&&<select aria-label="Presentatore valutato" value={(w as any).targetId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,targetId:e.target.value||undefined}:z))}><option value="">Seleziona presentatore</option>{availablePresenters.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select>}{!['line','shape'].includes(w.kind)&&<input aria-label="Titolo widget" title="Clicca per posizionare il cursore; trascina per selezionare il testo" onPointerDown={e=>e.stopPropagation()} value={w.label||''} maxLength={240} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,label:e.target.value}:z))}/>} {['rating','question','text','postit'].includes(w.kind)&&<textarea aria-label="Descrizione o commento opzionale" rows={2} maxLength={500} value={w.description||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,description:e.target.value}:z))}/>} {w.kind==='topic-question'&&<label><input type="checkbox" checked={!!(w as any).showNames} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,showNames:e.target.checked}:z))}/>Mostra nickname al presentatore</label>}{w.kind==='question'&&<label><input type="checkbox" checked={w.required!==false} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,required:e.target.checked}:z))}/>Obbligatoria</label>}{['question','timed-quiz'].includes(w.kind)&&<WidgetSubquestionEditor widget={w} onPatch={changes=>setPageWidgets(old=>old.map(z=>{if(z.id!==w.id)return z;let marks:TextMark[]=z.textMarks||[];if(Array.isArray(changes.questions)){const next=changes.questions as any[];for(const q of z.questions||[]){const changed=next.find(n=>n.id===q.id);if(!changed){marks=marks.filter(m=>!m.field.startsWith('question:'+q.id+':'));continue}if(changed.label!==q.label)marks=remapMarks(marks,'question:'+q.id+':label',q.label||'',changed.label||'');if(changed.description!==q.description)marks=remapMarks(marks,'question:'+q.id+':description',q.description||'',changed.description||'');for(const option of q.options||[]){const target=(changed.options||[]).find((o:any)=>o.id===option.id);const f='question:'+q.id+':option:'+option.id;if(!target)marks=marks.filter(m=>m.field!==f);else if(target.label!==option.label)marks=remapMarks(marks,f,option.label||'',target.label||'')}}}return {...z,...changes,textMarks:marks}}))}/>}{['question','timed-quiz'].includes(w.kind)&&<WidgetChoiceEditor widget={w} onPatch={changes=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,...changes}:z))}/>}{['image','video','logo','pdf'].includes(w.kind)&&<label>File multimediale caricato<select aria-label={'Allegato '+w.kind} value={w.assetId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,assetId:e.target.value}:z))}><option value="">Seleziona file</option>{assets.filter(a=>w.kind==='pdf'?a.mime_type==='application/pdf':w.kind==='logo'?a.mime_type.startsWith('image/'):a.mime_type.startsWith(w.kind+'/')).map(a=><option key={a.id} value={a.id}>{a.mime_type} · {a.id.slice(0,8)}</option>)}</select><input type="file" aria-label={"Carica media "+w.kind} accept={w.kind==='pdf'?'application/pdf':w.kind==='video'?'video/mp4,video/webm':'image/png,image/jpeg,image/gif,image/webp'} disabled={assetBusy} onChange={e=>{void uploadWidgetMedia(w.id,e.target.files?.[0],w.kind);e.target.value=''}}/><small>Seleziona oppure carica un file e salva il layout prima di pubblicare.</small></label>}{['shape','line'].includes(w.kind)&&<section className="widget-graphic-settings" aria-label="Formato elementi grafici"><h4>Forma e linea</h4>{w.kind==='shape'&&<label>Tipo di forma<select aria-label="Tipo forma grafica" value={w.style?.shapeType||'rectangle'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,shapeType:e.target.value as WidgetTextStyle['shapeType']}}:z))}>{['rectangle','rounded-rectangle','circle','ellipse','triangle','diamond','hexagon','pentagon','star','arrow','heart','cloud','speech'].map(t=><option key={t} value={t}>{t}</option>)}</select></label>}{w.kind==='line'&&<label>Direzione linea<select aria-label="Direzione linea" value={w.style?.lineDirection||'horizontal'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,lineDirection:e.target.value as WidgetTextStyle['lineDirection']}}:z))}>{['horizontal','vertical','diagonal','reverse'].map(t=><option key={t} value={t}>{t}</option>)}</select></label>}{w.kind==='line'&&<label>Terminali della linea<select aria-label="Terminali freccia" value={w.style?.lineArrow||'none'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,lineArrow:e.target.value as WidgetTextStyle['lineArrow']}}:z))}><option value="none">Nessuno</option><option value="start">Freccia all'inizio</option><option value="end">Freccia alla fine</option><option value="both">Due frecce</option></select></label>}<label>Spessore (pt)<input type="number" min={0} max={12} step={0.5} value={w.style?.strokeWidth??2} onChange={e=>{const n=Number(e.target.value);if(n>=0&&n<=12)setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,strokeWidth:n}}:z))}}/></label><label>Colore<input type="color" value={w.style?.strokeColor||'#334155'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,strokeColor:e.target.value}}:z))}/></label><label>Tratto<select value={w.style?.strokeDash||'solid'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,strokeDash:e.target.value as WidgetTextStyle['strokeDash']}}:z))}>{['solid','dash','dot'].map(t=><option key={t} value={t}>{t}</option>)}</select></label></section>}<WidgetAppearanceEditor widget={w} onPatch={style=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,...style}}:z))}/>{w.style?.fillMode==='image'&&<label>Immagine di riempimento del widget<select aria-label="Immagine di riempimento del widget" value={w.style?.fillImageAssetId||''} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,fillImageAssetId:e.target.value||undefined}}:z))}><option value="">Seleziona immagine</option>{assets.filter(a=>a.mime_type?.startsWith('image/')).map(a=><option key={a.id} value={a.id}>{a.id.slice(0,8)} · {a.mime_type}</option>)}</select></label>}{w.style?.fillMode==='image'&&<label>Carica immagine di riempimento<input type="file" accept="image/png,image/jpeg,image/gif,image/webp" disabled={assetBusy} onChange={e=>{void uploadWidgetFillImage(w.id,e.target.files?.[0]);e.target.value=''}}/></label>}<details className="widget-options"><summary>Stile e animazioni</summary><div className="widget-style"><label>Font<select value={w.style?.fontFamily||'Arial'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,fontFamily:e.target.value}}:z))}>{['Arial','Georgia','Verdana','Tahoma','Trebuchet MS','monospace'].map(x=><option key={x}>{x}</option>)}</select></label><label>Dimensione<input type="number" min="10" max="96" value={w.style?.fontSize||18} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,fontSize:Number(e.target.value)}}:z))}/></label><label>Allineamento testo<select aria-label="Allineamento testo widget" value={w.style?.textAlign||"left"} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,textAlign:e.target.value as WidgetTextStyle['textAlign']}}:z))}><option value="left">Sinistra</option><option value="center">Centro</option><option value="right">Destra</option></select></label><label>Allineamento verticale<select aria-label="Allineamento verticale widget" value={w.style?.verticalAlign||"top"} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,verticalAlign:e.target.value as WidgetTextStyle['verticalAlign']}}:z))}><option value="top">Alto</option><option value="middle">Centro</option><option value="bottom">Basso</option></select></label><label>Colore<input type="color" value={w.style?.color||'#1f2937'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,color:e.target.value}}:z))}/></label>{(['bold','italic','underline','strikethrough'] as const).map(k=><label key={k}><input type="checkbox" checked={!!w.style?.[k]} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,[k]:e.target.checked}}:z))}/>{k}</label>)}<label>Animazione<select value={w.style?.animation||'none'} onChange={e=>setPageWidgets(old=>old.map(z=>z.id===w.id?{...z,style:{...z.style,animation:e.target.value as WidgetTextStyle['animation']}}:z))}><option>none</option><option>fade</option><option>slide</option></select></label></div></details><button className="outline small" onClick={()=>{if(!window.confirm('Eliminare questo widget dal canvas?'))return;setPageWidgets(old=>old.filter(z=>z.id!==w.id))}}>Rimuovi</button><button className="outline small" disabled={i===0} onClick={()=>setPageWidgets(old=>{const n=[...old];[n[i-1],n[i]]=[n[i],n[i-1]];return n})}>↑</button><button className="outline small" disabled={i===pageWidgets.length-1} onClick={()=>setPageWidgets(old=>{const n=[...old];[n[i+1],n[i]]=[n[i],n[i+1]];return n})}>↓</button></li>)}</ol>
  </EditorFloatingWindow>}
 </div>
  {pageConflict&&<div className="editor-secondary-workflow" aria-label="Esportazione, salvataggio e risoluzione conflitti"><div className="editor-save-feedback" role="status" aria-live="polite">{notice|| (pageHasUnsavedChanges?"Modifiche da salvare":"Nessuna modifica in sospeso")}</div><div className="downloads">{pageHasUnsavedChanges&&<span role="status" className="muted tiny">● Modifiche non salvate</span>}{pageConflict&&<div role="alert" className="notice">Un altro presentatore ha salvato questa pagina. La tua bozza è ancora disponibile, ma non può sovrascrivere la versione più recente.</div>}{pageConflict&&<><button className="outline small" disabled={pageSavePending || !!mergeCandidate?.local} onClick={()=>void inspectPageConflict()}>Confronta e riconcilia le modifiche</button><button className="outline small" disabled={pageSavePending} onClick={async()=>{if(!window.confirm('Scartare le modifiche locali e ricaricare il layout aggiornato dal server?'))return;try{const latest=await request<Snapshot>(`/sessions/${selected}`);const page=latest.activities.find(a=>a.id===designActivity);if(!page){setNotice('La pagina non esiste più');return}setSnap(latest);beginPageDesign(page);setNotice('Layout aggiornato dal server')}catch(e){notify(e)}}}>Ricarica layout dal server</button></>}{pageConflict&&mergeCandidate&&mergePreview&&<section className="page-merge-panel" aria-label="Riconciliazione delle modifiche"><h4>Riconciliazione con la versione server {mergeCandidate.revision}</h4><p className="muted tiny">Le modifiche indipendenti sono combinate senza sovrascrivere il server. Per ogni conflitto scegli esplicitamente quale valore conservare. La sincronizzazione automatica riprende dopo la risoluzione esplicita dei conflitti.</p>{mergePreview.conflicts.length===0&&<p role="status">Nessun conflitto sui singoli campi: le modifiche sono combinabili.</p>}{mergePreview.conflicts.map(c=><label key={c.path} className="page-merge-choice">{c.label}<select aria-label={'Risolvi '+c.label} value={mergeChoices[c.path]||''} onChange={e=>setMergeChoices(old=>({...old,[c.path]:e.target.value as MergeChoice}))}><option value="">Scegli una versione</option><option value="local">Conserva la mia modifica</option><option value="remote">Conserva la modifica del server</option></select><div className="page-merge-diff"><span><strong>La mia versione:</strong> <code>{describeMergeValue(c.local)}</code></span><span><strong>Versione server:</strong> <code>{describeMergeValue(c.remote)}</code></span></div></label>)}<div className="downloads"><button type="button" className="outline small" disabled={!mergePreview.conflicts.length} onClick={()=>setMergeChoices(Object.fromEntries(mergePreview.conflicts.map(c=>[c.path,'local' as MergeChoice])))}>Scegli la mia versione per tutti</button><button type="button" className="outline small" disabled={!mergePreview.conflicts.length} onClick={()=>setMergeChoices(Object.fromEntries(mergePreview.conflicts.map(c=>[c.path,'remote' as MergeChoice])))}>Scegli la versione server per tutti</button></div><p className="muted tiny" role="status">{unresolvedMergeConflicts.length} conflitti ancora da risolvere. Le modifiche non vengono pubblicate finché non premi Salva layout.</p><div className="downloads"><button className="primary small" disabled={unresolvedMergeConflicts.length>0||pageSavePending} onClick={()=>void applyPageRebase()}>Applica riconciliazione alla bozza</button><button className="outline small" onClick={()=>{if(mergeCandidate?.local)setPageConflict(false);setMergeCandidate(null);setMergeChoices({})}}>Annulla confronto</button></div></section>}<button className="primary small" onClick={updatePageDesign} disabled={!pageHasUnsavedChanges||pageSavePending||pageConflict}>Salva layout</button><button className="outline small" onClick={()=>{if(confirmPageNavigation())setDesignActivity('')}}>Chiudi</button></div></div>}
</div>
<aside className="editor-widget-rail" aria-label="Aggiungi widget">
 <header><strong>Widget</strong><span className="muted tiny">Trascina o tocca</span></header>
 <div className="editor-widget-grid">{editorWidgetKinds.map(k=>k==='shape'||k==='line'?<GraphicInsertTool key={k} kind={k} disabled={pageWidgets.length>=16} onInsert={(preset,options)=>{setInspectedWidget('');setPageContextOpen(false);setPageWidgets(old=>{if(old.length>=16){setNotice('Massimo 16 widget per pagina.');return old}const i=old.length;const position=freeWidgetPosition(old,{x:4+(i%4)*24,y:4+Math.floor(i/4)*24},22,20);if(!position){setNotice('Non c’è spazio per un altro widget su questa pagina.');return old}return [...old,{id:crypto.randomUUID(),kind:k,showTitle:false,label:'',style:graphicStyle(k,preset,options),position:{...position,rotation:0}}]})}}/>:<EditorIconTool key={k} kind={k} label={`Aggiungi widget: ${editorWidgetNames[k]}`} draggable onDragStart={e=>{e.dataTransfer.setData('application/x-quorivio-widget',k);e.dataTransfer.effectAllowed='copy'}} onClick={()=>{setInspectedWidget('');setPageContextOpen(false);setPageWidgets(old=>{if(old.length>=16){setNotice('Massimo 16 widget per pagina.');return old}const i=old.length;const position=k==='footer'?newFooterWidget('new').position:freeWidgetPosition(old,{x:4+(i%4)*24,y:4+Math.floor(i/4)*24},22,20);if(!position){setNotice('Non c’è spazio per un altro widget su questa pagina.');return old}return [...old,{...(k==='footer'?newFooterWidget(crypto.randomUUID()):{}),id:crypto.randomUUID(),kind:k,...(k==='qr'?{showTitle:false,showQrUrl:true}:{}),...(k==='results-button'&&eligibleStatisticSources(old).length?{targetWidgetId:eligibleStatisticSources(old)[0].id}:{}),style:{...initialWidgetTextStyle(k),...(k==='footer'?newFooterWidget('new').style:{}),fillNone:true,shapeType:'rectangle'},label:k==='footer'?'':k==='rating'?'Quanto hai gradito?':k==='question'?'Nuova domanda':k==='timed-quiz'?'Quiz a tempo':k==='results-button'?'Risultati':k==='participant-count'?'Partecipanti connessi':editorWidgetNames[k],position:{...position,rotation:0}}]})}}><EditorWidgetIcon kind={k}/><span className="editor-icon-caption" aria-hidden="true">{editorWidgetNames[k]}</span></EditorIconTool>)}</div>
 </aside>
{editorTouchHint&&<div className="editor-touch-assist" role="status" aria-live="polite">{editorTouchHint}</div>}
</section>}{selected&&<section className="panel"><h3>Schermo presentatore</h3><p>Apri la vista di presentazione e le statistiche live in una finestra separata.</p><a className="outline asbutton" target="_blank" rel="noopener noreferrer" href={'/screen/'+encodeURIComponent(selected)}>Apri schermo presentatore ↗</a><details className="presenter-preview"><summary>Mostra anteprima della schermata di proiezione</summary><iframe title="Anteprima presentatore e risultati live" loading="lazy" src={'/screen/'+encodeURIComponent(selected)}/></details></section>}{selected&&(presenterLive==='disconnected'||presenterLive==='blocked')&&<div className="live-stale-warning" role="status" aria-live="polite">{presenterLive==='blocked'?'Accesso live revocato: i dati potrebbero non essere aggiornati.':'Connessione live interrotta: le statistiche potrebbero essere obsolete. Riconnessione in corso…'}</div>}{current&&<section className="panel live-panel"><div className="eyebrow"><span className="live-dot"/> {t.results}</div><h2>{current.title}</h2><ResultsWidgetErrorBoundary key={'dashboard-live-'+current.id} widgetId={'dashboard-live-'+current.id}><DashboardLiveResults snapshot={snap} activity={current} renderResults={showResults}/></ResultsWidgetErrorBoundary></section>}{current&&<ResultsWidgetErrorBoundary key={'audience-extension-'+current.id} widgetId={'audience-extension-'+current.id}><>{(Array.isArray((current as any).page_design?.widgets)?(current as any).page_design.widgets:[]).filter((w:any)=>w&&w.kind==='topic-question').map((w:any)=><TopicPresenterList key={w.id} sessionId={selected} activityId={current.id} widget={w}/>)}<PresenterAudienceExtensions key={current.id} sessionId={selected} activityId={current.id}/></></ResultsWidgetErrorBoundary>}<section className="panel"><h3><ShieldCheck size={19}/> {lang==='it'?'Privacy e ciclo di vita':'Privacy and lifecycle'}</h3><button type="button" className="binary-toggle" aria-pressed={snap.session.allow_anonymous!==false} onClick={()=>setAnonymous(!(snap.session.allow_anonymous!==false))}>Consenti partecipazione anonima: {snap.session.allow_anonymous!==false?'SÌ':'NO'}</button><button type="button" className="binary-toggle" aria-pressed={!!snap.session.show_results} onClick={()=>setResultsVisibility(!(!!snap.session.show_results))}>Pubblica risultati live ai partecipanti: {!!snap.session.show_results?'SÌ':'NO'}</button><label htmlFor="retention-days">{lang==='it'?'Conservazione risposte (giorni)':'Response retention (days)'}</label><div className="downloads"><input id="retention-days" type="number" min="1" max="3650" defaultValue={snap.session.retention_days??60} key={selected+String(snap.session.retention_days)} onBlur={e=>{const days=Number(e.target.value);if(Number.isInteger(days)&&days>=1&&days<=3650&&days!==snap.session.retention_days)updateRetention(days)}} aria-label="Retention days"/></div><p className="muted tiny">{lang==='it'?'Per salvare, modifica il valore e sposta il focus. La cancellazione programmata riguarda sessioni chiuse o scadute.':'Change the value and leave the field to save. Scheduled purging applies to closed or expired sessions.'}</p><div className="downloads"><button className="outline small" onClick={revokeSession} disabled={snap.session.status==='closed'}>{lang==='it'?'Revoca accessi':'Revoke access'}</button></div></section><details className="panel dashboard-attachments-collapsible" aria-label="Allegati della sessione"><summary>Allegati della sessione <span className="dashboard-attachments-count">{assets.length}</span></summary><div className="dashboard-attachments-body"><p className="muted tiny">Per importare PDF o PowerPoint scegli prima la modalità: immagini fedeli oppure elementi modificabili in una nuova sessione. La conversione editabile è parziale.</p><p className="muted tiny">Testi, immagini PNG/JPEG e alcune forme semplici diventano widget modificabili. Grafici, SmartArt, animazioni e temi complessi possono perdere fedeltà: per preservare l’aspetto originale usa anche l’importazione grafica.</p><label>Importa direttamente PDF/PPTX (richiede worker di conversione configurato)<input type="file" accept=".pdf,.pptx,application/pdf,application/vnd.openxmlformats-officedocument.presentationml.presentation" disabled={assetBusy||snap.session.status==='closed'} onChange={e=>{const file=e.target.files?.[0];if(file)setPendingPresentation({file});e.target.value=''}}/></label><label>Importa pagine convertite (PNG/JPEG/WebP, in ordine alfabetico)<input type="file" accept="image/png,image/jpeg,image/webp" multiple disabled={assetBusy||snap.session.status==='closed'} onChange={e=>{void importSlideImages(e.target.files);e.target.value=''}}/></label><p className="muted tiny">Puoi importare direttamente PDF/PPTX quando il convertitore è configurato. In alternativa usa tools/import_presentation.py e seleziona le immagini convertite.</p><p className="muted tiny">PNG, JPEG, GIF, WebP, PDF, MP4, WebM. Limite predefinito 100 MB, modificabile dall’amministratore. I file sono privati e scaricabili solo dai presentatori autorizzati.</p><label>Carica un file<input type="file" accept="image/png,image/jpeg,image/gif,image/webp,application/pdf,video/mp4,video/webm" disabled={assetBusy||snap.session.status==='closed'} onChange={e=>{void uploadAsset(e.target.files?.[0]);e.target.value=''}}/></label><div className="downloads"><button className="outline small" onClick={refreshAssets}>Aggiorna allegati</button></div>{assets.map(a=><div className="activity-row" key={a.id}><div><strong>{a.display_name||`Allegato ${a.id.slice(0,8)}`}</strong><div className="muted tiny">{a.mime_type} · {Math.ceil(Number(a.byte_size)/1024)} KiB</div></div><div className="activity-actions"><a className="outline asbutton" href={a.url} target="_blank" rel="noreferrer">Apri</a>{a.mime_type.startsWith('image/')&&snap.session.status!=='closed'&&<button className="outline small" onClick={()=>addSlide(a)}>Crea pagina slide</button>}{snap.session.status!=='closed'&&<button className="outline small" onClick={()=>void renameAsset(a.id)}>Rinomina</button>}{snap.session.status!=='closed'&&<button className="outline small" onClick={()=>deleteAsset(a.id)}>Elimina</button>}</div></div>)}</div></details><section className="panel"><h3>Portabilità e collaborazione</h3><p className="muted tiny">Il formato .quo include pagine, schemi, widget, configurazioni e allegati utilizzati, ma non risposte, credenziali, collaboratori o dati dei partecipanti. È reimportabile come nuovo proprietario in un altro account. I formati legacy restano importabili tramite gli strumenti amministrativi di migrazione. La duplicazione genera un nuovo codice QR.</p><div className="downloads"><button className="outline small" onClick={duplicateSelected}>Duplica sessione</button><a className="outline asbutton" href={`/api/sessions/${selected}/export.quo`} download>Esporta archivio Quorivio completo</a><a className="outline asbutton" href={`/api/sessions/${selected}/export.pptx`} download>Esporta PowerPoint (contenuti supportati)</a><a className="outline asbutton" href={`/api/sessions/${selected}/export.pdf`} download>Esporta PDF (pagine statiche)</a></div><label>Importa archivio Quorivio con allegati (.quo)<input type="file" accept=".quo,application/vnd.quorivio.session+zip" onChange={e=>{void importQuorivioBundle(e.target.files?.[0]);e.target.value=''}}/></label><hr/><label>Email co-presentatore approvato<input type="email" value={coEmail} onChange={e=>setCoEmail(e.target.value)}/></label><div className="downloads"><button className="outline small" onClick={addCollaborator} disabled={!coEmail.includes('@')}>Aggiungi presentatore</button><button className="outline small" onClick={refreshCollaborators}>Mostra collaboratori</button></div>{coPresenters.map(x=><div className="activity-row" key={x.id}><span>{x.email}</span><button className="small outline" onClick={()=>removeCollaborator(x.id)}>Rimuovi</button></div>)}{snap.session.access_role==='owner'&&<div className="session-owner-transfer"><h4>Trasferisci proprietà primaria</h4><p className="muted tiny">Il destinatario deve essere un presentatore approvato della stessa organizzazione. Le pagine, le risposte e i collaboratori rimangono invariati. Il trasferimento è registrato per audit.</p><label>Email del nuovo proprietario<input type="email" autoComplete="off" value={ownershipTarget} onChange={e=>setOwnershipTarget(e.target.value)} placeholder="presentatore@organizzazione.it"/></label><label><input type="checkbox" checked={ownershipKeepPrevious} onChange={e=>setOwnershipKeepPrevious(e.target.checked)}/> Mantieni il precedente proprietario come collaboratore</label><button className="outline small" disabled={ownershipBusy||!ownershipTarget.includes('@')} onClick={()=>void transferPrimaryOwner()}>{ownershipBusy?'Trasferimento in corso…':'Trasferisci proprietà primaria'}</button></div>}</section><section className="panel"><h3><Download size={19}/> Dati della sessione</h3><p className="muted">Esporta risposte, quiz, widget, gradimento e reazioni. L'export anonimo raggruppa le risposte e mostra un conteggio soltanto se la stessa risposta proviene da almeno 5 partecipanti distinti. Le voci con meno partecipanti sono omesse. Identificativi, orari precisi e contenuti liberi non vengono esportati. L'export nominativo è riservato al proprietario primario.</p><label className="statistics-anonymize"><input type="checkbox" checked={statisticsAnonymize} onChange={e=>setStatisticsAnonymize(e.target.checked)}/> Anonimizza i dati (consigliato)</label><a className="outline asbutton" href={`/api/sessions/${selected}/report.json`} download>Report JSON aggregato e audit</a><div className="downloads"><a className="outline asbutton" href={`/api/sessions/${selected}/export.csv?anonymize=${statisticsAnonymize?'1':'0'}`} download><Download size={16}/> Esporta CSV {statisticsAnonymize?'anonimo':'nominativo'}</a><a className="outline asbutton" href={`/api/sessions/${selected}/export.xlsx?anonymize=${statisticsAnonymize?'1':'0'}`} download><Download size={16}/> Esporta Excel {statisticsAnonymize?'anonimo':'nominativo'}</a></div>{!statisticsAnonymize&&<p role="alert" className="muted tiny">Esportazione con dati personali: gestire il file secondo le norme GDPR. I testi liberi possono contenere informazioni sensibili.</p>}</section></div></div></>}</div></main>}
{pendingPresentation&&<div className="presentation-import-backdrop" role="presentation"><section className="presentation-import-dialog" role="dialog" aria-modal="true" aria-label="Modalità importazione PDF o PowerPoint"><h3>Come vuoi importare {pendingPresentation.file.name}?</h3><p>Scegli prima di iniziare la conversione.</p><fieldset className="pdf-import-image-options"><legend>Immagine sul canvas</legend><label>Adattamento della pagina<select aria-label="Adattamento immagini PDF/PPTX sul canvas" value={importImageFit} onChange={e=>setImportImageFit(e.target.value as 'contain'|'cover'|'fill')}><option value="cover">Riempi canvas — proporzioni preservate, ritaglio ai bordi (predefinito)</option><option value="contain">Adatta interamente — nessun ritaglio, eventuali bande bianche</option><option value="fill">Espansione forzata — nessun bordo, possibili deformazioni</option></select></label><label className="pdf-import-hide-master"><input type="checkbox" checked={importHideScheme} onChange={e=>setImportHideScheme(e.target.checked)}/> Nascondi schema, titoli, footer e numero pagina nelle nuove slide (consigliato)</label></fieldset><button type="button" className="primary" disabled={assetBusy} onClick={()=>{const item=pendingPresentation;setPendingPresentation(null);void importPresentationFile(item.file,item.afterPageId,importImageFit,importHideScheme)}}>Come immagini — fedeltà visiva</button><p className="muted tiny">Crea una slide immagine per ogni pagina nella sessione corrente. Contenuti non modificabili singolarmente.</p><button type="button" className="outline" disabled={assetBusy} onClick={()=>{const item=pendingPresentation;if(designActivity&&!confirmPageNavigation())return;setPendingPresentation(null);void importEditablePowerPoint(item.file)}}>Elementi modificabili — conversione parziale</button><p className="muted tiny">Crea una nuova sessione con testo nativo e immagini estraibili come widget indipendenti. Geometrie, font, grafici e vettori complessi possono andare persi; nessun OCR su PDF scansiti.</p><button type="button" className="outline" onClick={()=>setPendingPresentation(null)}>Annulla importazione</button></section></div>}
<footer>QUORIVIO · Open infrastructure for interactive experiences</footer></div>}
/** An error in an audience-only page must never erase the authenticated
 * presenter's selected session. An isolated child error stays inside its local
 * boundary; for unexpected root errors retry the SAME saved session once.
 * Never silently navigate to the welcome/dashboard screen. */
class WorkspaceErrorBoundary extends React.Component<Record<string,never>,{failed:boolean;recovered:boolean;generation:number}>{
 state={failed:false,recovered:false,generation:0};
 static getDerivedStateFromError(){return {failed:true}}
 componentDidCatch(error:Error){
  console.error('[quorivio-workspace-boundary]',error);
  if(!this.state.recovered){
   // Preserve readWorkspaceLocation().sessionId and the current session route.
   this.setState(s=>({failed:false,recovered:true,generation:s.generation+1}));
  }
 }
 render(){
  if(this.state.failed)return <main className="session-restore-error" role="alert"><h1>Interfaccia temporaneamente non disponibile</h1><p>La sessione selezionata è stata conservata. È possibile riprovare senza perdere i dati salvati.</p><button type="button" className="primary" onClick={()=>this.setState(s=>({failed:false,generation:s.generation+1}))}>Riprova la sessione corrente</button><button type="button" className="outline" onClick={()=>{writeWorkspaceLocation({sessionId:'',section:'workspace',tab:'overview',pageId:''});window.location.assign('/')}}>Torna all'elenco delle sessioni</button></main>;
  return <App key={this.state.generation}/>;
 }
}
/** Studio-wide zoom shrinks dashboard/editor chrome while the live audience and
 * public screen retain native pixel geometry and 44px minimum touch targets.
 * Portaled studio dialogs still share the root CSS zoom. */
function GlobalPageZoomShell(){
 const isLiveSurface=isUnscaledPublicSurface(window.location.pathname);
 const [zoom,setZoom]=useState<number>(()=>{
  try{return normalizeGlobalZoom(window.localStorage.getItem(GLOBAL_ZOOM_STORAGE_KEY))}
  catch{return 100}
 });
 useEffect(()=>{
  const root=document.documentElement;
  const value=zoomStyleValue(zoom,window.location.pathname);
  root.style.setProperty('zoom',value);
  // Fixed-position overlays are compensated separately so that the whole
  // physical viewport remains covered instead of revealing the dashboard.
  root.style.setProperty(GLOBAL_ZOOM_CSS_VARIABLE,String(Number.parseFloat(value)/100));
  try{window.localStorage.setItem(GLOBAL_ZOOM_STORAGE_KEY,String(zoom))}catch{/* Private mode: zoom remains usable this session. */}
  return()=>{root.style.removeProperty('zoom');root.style.removeProperty(GLOBAL_ZOOM_CSS_VARIABLE);};
 },[zoom]);
 return <>
  <WorkspaceErrorBoundary/>
  {!isLiveSurface&&<aside className="global-page-zoom" role="group" aria-label="Zoom globale dell'interfaccia">
   <button type="button" aria-label="Riduci zoom dell'interfaccia" title="Riduci zoom in tutte le pagine" disabled={zoom<=GLOBAL_ZOOM_MIN} onClick={()=>setZoom(n=>nextGlobalZoom(n,-1))}>−</button>
   <output aria-live="polite" aria-label="Livello di zoom corrente">{zoom}%</output>
   <button type="button" aria-label="Aumenta zoom dell'interfaccia" title="Aumenta zoom in tutte le pagine" disabled={zoom>=GLOBAL_ZOOM_MAX} onClick={()=>setZoom(n=>nextGlobalZoom(n,1))}>+</button>
   <button type="button" className="global-page-zoom-reset" aria-label="Ripristina zoom al 100%" title="Zoom predefinito 100%" disabled={zoom===100} onClick={()=>setZoom(100)}>100%</button>
  </aside>}
 </>;
}
createRoot(document.getElementById('root')!).render(<GlobalPageZoomShell/>);
