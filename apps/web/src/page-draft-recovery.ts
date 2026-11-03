/** Explicit, non-persistent page draft transfer. Nothing is written to storage or server. */
import {validDesignRevision,type EditablePageDraft} from './page-draft.ts';
import {validMobilePageLayout} from '../../api/src/domain.ts';

export type PageDraftBackup={format:'quorivio-local-draft-v1'|'quorivio-local-draft-v2';session_id:string;activity_id:string;base_revision:number;draft:EditablePageDraft;base_draft?:EditablePageDraft};
const forbidden=new Set(['__proto__','prototype','constructor']);
const fields=['questionHeader','resultHeader','questionBackground','resultBackground','questionBackgroundColor','resultBackgroundColor','questionBackgroundAsset','resultBackgroundAsset'] as const;
const isRecord=(v:unknown):v is Record<string,unknown>=>v!==null&&typeof v==='object'&&!Array.isArray(v);
function validateTree(value:unknown,depth:number,remaining:{count:number}):void{
 if(--remaining.count<0||depth>24)throw Error('draft_complexity_limit');
 if(value===null||typeof value==='boolean')return;
 if(typeof value==='number'){if(!Number.isFinite(value))throw Error('invalid_draft_number');return}
 if(typeof value==='string'){if(value.length>100_000)throw Error('draft_text_too_long');return}
 if(Array.isArray(value)){if(value.length>1000)throw Error('draft_array_too_large');for(const item of value)validateTree(item,depth+1,remaining);return}
 if(!isRecord(value))throw Error('invalid_draft_value');
 const keys=Object.keys(value);
 if(keys.length>1000)throw Error('draft_object_too_large');
 for(const key of keys){if(forbidden.has(key)||key.length>128)throw Error('unsafe_draft_key');validateTree(value[key],depth+1,remaining)}
}
export function validateEditablePageDraft(value:unknown):EditablePageDraft{
 if(!isRecord(value))throw Error('invalid_page_draft');
 if(!Array.isArray(value.widgets)||value.widgets.length>500)throw Error('invalid_page_widgets');
 for(const field of fields){if(typeof value[field]!=='string'||(value[field] as string).length>100_000)throw Error('invalid_page_field_'+field)}
 const ids=new Set<string>();
 for(const widget of value.widgets){
  if(!isRecord(widget)||typeof widget.id!=='string'||!widget.id||widget.id.length>128||ids.has(widget.id)||forbidden.has(widget.id))throw Error('invalid_page_widget_id');
  if(typeof widget.kind!=='string'||!widget.kind||widget.kind.length>80)throw Error('invalid_page_widget_kind');
  ids.add(widget.id);
 }
 if(value.mobile!==undefined&&!validMobilePageLayout(value.mobile,value.widgets))throw Error('invalid_mobile_page_layout');
 validateTree(value,0,{count:50_000});
 return value as EditablePageDraft;
}
export function parsePageDraftBackup(content:string,sessionId:string,activityId:string):PageDraftBackup{
 if(content.length>2_000_000)throw Error('draft_file_too_large');
 let raw:unknown;
 try{raw=JSON.parse(content)}catch{throw Error('invalid_draft_json')}
 if(!isRecord(raw)||typeof raw.format!=='string'||!['quorivio-local-draft-v1','quorivio-local-draft-v2'].includes(raw.format))throw Error('unsupported_draft_format');
 if(raw.session_id!==sessionId||raw.activity_id!==activityId)throw Error('draft_page_mismatch');
 if(!validDesignRevision(raw.base_revision))throw Error('invalid_draft_revision');
 const draft=validateEditablePageDraft(raw.draft);
 const base=raw.format==='quorivio-local-draft-v2'?validateEditablePageDraft(raw.base_draft):undefined;
 return {format:raw.format as PageDraftBackup['format'],session_id:sessionId,activity_id:activityId,base_revision:raw.base_revision,draft,base_draft:base};
}
/** Turn in-memory widget props into lossless JSON before validating an export.
 * React widget state may contain OPTIONAL object properties set to undefined;
 * JSON.omit semantics are correct for those props, but undefined array items,
 * non-finite numbers, functions and cyclic objects are never valid draft data.
 * The original draft is not mutated. Import validation stays strict.
 */
function jsonDraftValue(value:unknown, seen:WeakSet<object>=new WeakSet(), inArray=false):unknown{
 if(value===undefined){if(inArray)throw Error('invalid_draft_value');return undefined}
 if(value===null||typeof value==='string'||typeof value==='boolean')return value;
 if(typeof value==='number'){if(!Number.isFinite(value))throw Error('invalid_draft_number');return value}
 if(typeof value!=='object'||seen.has(value))throw Error('invalid_draft_value');
 seen.add(value);
 let result:unknown;
 if(Array.isArray(value))result=value.map(item=>jsonDraftValue(item,seen,true));
 else if(isRecord(value)){
  const out:Record<string,unknown>=Object.create(null);
  for(const [key,item] of Object.entries(value)){
   if(item!==undefined)out[key]=jsonDraftValue(item,seen);
  }
  result=out;
 }else throw Error('invalid_draft_value');
 seen.delete(value);
 return result;
}
function exportReadyPageDraft(draft:EditablePageDraft):EditablePageDraft{
 // Required page-level fields must never be removed by optional-prop cleanup.
 if(!isRecord(draft)||!Array.isArray(draft.widgets))throw Error('invalid_page_draft');
 return validateEditablePageDraft({...draft,widgets:draft.widgets.map(widget=>jsonDraftValue(widget))});
}
export function createPageDraftBackup(sessionId:string,activityId:string,revision:number,draft:EditablePageDraft,base:EditablePageDraft):PageDraftBackup{
 if(!sessionId||!activityId||!validDesignRevision(revision))throw Error('invalid_draft_identity');
 return {format:'quorivio-local-draft-v2',session_id:sessionId,activity_id:activityId,base_revision:revision,draft:exportReadyPageDraft(draft),base_draft:exportReadyPageDraft(base)};
}
export type RecoveryPlan={mode:'restore'|'reconcile'|'blocked';reason?:string};
export function planPageDraftRecovery(backup:PageDraftBackup,serverRevision:number):RecoveryPlan{
 if(!validDesignRevision(serverRevision))return {mode:'blocked',reason:'invalid_server_revision'};
 if(backup.base_revision===serverRevision)return {mode:'restore'};
 if(backup.base_draft)return {mode:'reconcile'};
 return {mode:'blocked',reason:'legacy_backup_stale'};
}
