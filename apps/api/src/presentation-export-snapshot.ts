import {presenterPages,audienceForPresenter} from './presentation-routing.js';
import type {PresentationExportView} from './presentation-export-names.js';

/** Enumerate the same presenter-driven steps as real projection. The participant
 * deck can therefore use a different authored page for each visible presenter
 * step, including a hidden question page. Duplicates are intentional: two
 * presenter steps can legitimately map the same audience slide. */
export function presentationExportPages<T extends {id:string;page_design?:{audiencePageId?:string;presenterHidden?:boolean}|null}>(
  pages:readonly T[],view:PresentationExportView):T[]{
 const visible=presenterPages(pages);
 if(view==='presenter')return visible;
 return visible.map(page=>{
  const audience=audienceForPresenter(pages,page);
  if(!audience)throw new Error('missing_participant_page');
  return audience;
 });
}

/** Only authored page metadata and optional *aggregated* result totals, never
 * participant votes, names, tokens or private quiz answer submissions. */
export function visualExportSnapshot(definition:any,sessionId:string,aggregates?:{results?:unknown;totals?:unknown;connected_participants?:unknown;responded_connected_participants?:unknown}){
 if(definition?.format!=='quorivio-session'||definition.version!==1||!Array.isArray(definition.activities))throw new Error('invalid_visual_export');
 const activities=definition.activities.map((a:any,i:number)=>({...a,id:a.portable_id,status:'open',position:i+1,duration_seconds:a.duration_seconds??null}));
 const session={...definition.session,id:sessionId,status:'draft',join_code:'',join_url:definition.session?.participant_join_url||'',current_activity_id:null,presenter_activity_id:null};
 const connected=Number.isSafeInteger(aggregates?.connected_participants)&&Number(aggregates?.connected_participants)>=0?Math.min(1000000,Number(aggregates!.connected_participants)):0;
 const responded=Number.isSafeInteger(aggregates?.responded_connected_participants)&&Number(aggregates?.responded_connected_participants)>=0?Math.min(connected,Number(aggregates!.responded_connected_participants)):0;
 delete session.join_secret;
 return {session,activities,results:Array.isArray(aggregates?.results)?aggregates.results:[],totals:Array.isArray(aggregates?.totals)?aggregates.totals:[],connected_participants:connected,responded_connected_participants:responded,capture_profiles:Array.isArray(definition.capture_profiles)?definition.capture_profiles:[],capture_widget_results:definition.capture_widget_results||{widgets:[],ratings:[],reactions:[]}};
}
