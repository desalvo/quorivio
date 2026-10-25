/** Deterministic dirty-state signature for the complete editable page draft. */
export type EditablePageDraft={widgets:unknown[];questionHeader:string;resultHeader:string;questionBackground:string;resultBackground:string;questionBackgroundColor:string;resultBackgroundColor:string;questionBackgroundAsset:string;resultBackgroundAsset:string};
export function pageDraftSignature(d:EditablePageDraft):string{return JSON.stringify(d)}
export function pageDraftFromActivity(a:{page_design?:any;result_design?:any}):EditablePageDraft{
 const q=a.page_design||{},r=a.result_design||{};
 return {widgets:q.widgets||[],questionHeader:q.header||'',resultHeader:r.header||'',questionBackground:q.backgroundUrl||'',resultBackground:r.backgroundUrl||'',questionBackgroundColor:q.backgroundColor||'',resultBackgroundColor:r.backgroundColor||'',questionBackgroundAsset:q.backgroundAssetId||'',resultBackgroundAsset:r.backgroundAssetId||''};
}
export function validDesignRevision(value:unknown):value is number{return typeof value==='number'&&Number.isSafeInteger(value)&&value>=1}
