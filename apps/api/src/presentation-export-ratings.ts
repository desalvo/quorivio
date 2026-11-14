/** Ratings are stored per activity/participant, not per widget. Export
 * only aggregate counts, attached to authored rating widgets of that page. */
export const PRESENTATION_EXPORT_RATINGS_SQL = [
 'SELECT activity_id, score::text AS option_id, count(*)::int AS count',
 'FROM page_ratings WHERE session_id=$1',
 'GROUP BY activity_id,score LIMIT 10000'
].join(' ');

export type ExportRatingCount={activity_id:string;widget_id:string;option_id:string;count:number};
type CaptureActivity={portable_id?:unknown;page_design?:{widgets?:unknown}|null};
export function capturePageRatingWidgetCounts(activities:readonly CaptureActivity[],totals:unknown):ExportRatingCount[]{
 if(!Array.isArray(totals))return [];
 const widgetIds=new Map<string,string[]>();
 for(const activity of activities){
  if(typeof activity?.portable_id!=='string'||!Array.isArray(activity.page_design?.widgets))continue;
  const ids=new Set<string>();
  for(const widget of activity.page_design.widgets){
   if(widget&&typeof widget==='object'&&!Array.isArray(widget)){
    const w=widget as Record<string,unknown>;
    if(w.kind==='rating'&&typeof w.id==='string'&&w.id.length>0&&w.id.length<=128)ids.add(w.id);
   }
  }
  widgetIds.set(activity.portable_id,[...ids]);
 }
 const result:ExportRatingCount[]=[];
 for(const item of totals){
  if(!item||typeof item!=='object'||Array.isArray(item))continue;
  const r=item as Record<string,unknown>;
  if(typeof r.activity_id!=='string'||typeof r.option_id!=='string'
    || !/^(?:[0-9]|10)$/.test(r.option_id)
    || !Number.isSafeInteger(r.count)||Number(r.count)<0)continue;
  for(const widget_id of widgetIds.get(r.activity_id)||[]){
   if(result.length>=10000)throw Error('visual_export_rating_limit');
   result.push({activity_id:r.activity_id,widget_id,option_id:r.option_id,count:Number(r.count)});
  }
 }
 return result;
}
