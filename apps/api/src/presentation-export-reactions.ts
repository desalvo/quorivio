/** Capture only aggregated, activity-scoped reactions. The database table
 * page_reactions has activity_id/participant_id/emoji, not widget_id.
 * Duplicate each page total across the authored reaction widgets on that page,
 * consistent with the page-scoped live reaction storage; never leak user IDs.
 */
export type ExportReactionCount={
 activity_id:string;widget_id:string;option_id:string;count:number
};
type CaptureActivity={
 portable_id?:unknown;
 page_design?:{widgets?:unknown}|null
};
export function capturePageReactionWidgetCounts(activities:readonly CaptureActivity[],totals:unknown):ExportReactionCount[]{
 if(!Array.isArray(totals))return [];
 const widgetIds=new Map<string,string[]>();
 for(const activity of activities){
  if(typeof activity?.portable_id!=='string'||!Array.isArray(activity.page_design?.widgets))continue;
  const ids=new Set<string>();
  for(const widget of activity.page_design.widgets){
   if(widget&&typeof widget==='object'&&!Array.isArray(widget)){
    const w=widget as Record<string,unknown>;
    if(w.kind==='reactions'&&typeof w.id==='string'&&w.id.length>0&&w.id.length<=128)ids.add(w.id);
   }
  }
  widgetIds.set(activity.portable_id,[...ids]);
 }
 const result:ExportReactionCount[]=[];
 for(const item of totals){
  if(!item||typeof item!=='object'||Array.isArray(item))continue;
  const r=item as Record<string,unknown>;
  if(typeof r.activity_id!=='string'||typeof r.emoji!=='string'||r.emoji.length>64
   ||!Number.isSafeInteger(r.count)||Number(r.count)<0)continue;
  for(const widget_id of widgetIds.get(r.activity_id)||[]){
   if(result.length>=10000)throw Error('visual_export_reaction_limit');
   result.push({activity_id:r.activity_id,widget_id,option_id:r.emoji,count:Number(r.count)});
  }
 }
 return result;
}
