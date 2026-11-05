/** One presenter slide can expose another slide to the audience. The audience
 * activity remains the ONLY open activity allowed to collect responses. */
export type RoutedPage = {id:string;page_design?:{audiencePageId?:string;presenterHidden?:boolean}|null};
export function presenterPages<T extends RoutedPage>(pages:readonly T[]):T[]{return pages.filter(p=>p.page_design?.presenterHidden!==true)}
export function audienceForPresenter<T extends RoutedPage>(pages:readonly T[],presenter:T):T|null {
 const id=presenter.page_design?.audiencePageId||presenter.id;
 return pages.find(p=>p.id===id)||null;
}
/** A fixed mapping is not a client-supplied activity permission. */
export function validAudienceMapping<T extends RoutedPage>(pages:readonly T[],page:T):boolean {
 return !page.page_design?.audiencePageId||pages.some(p=>p.id===page.page_design?.audiencePageId);
}
export function firstPresenterPage<T extends RoutedPage>(pages:readonly T[]):T|null {return presenterPages(pages)[0]||null}

export const PAGE_UUID=/^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
/** Portable archives retain page identity only inside the archive; import
 * remaps all references to newly generated page IDs, without the old join code. */
export function validPortablePageRouting(activities:readonly {portable_id?:unknown;page_design?:any;result_design?:any}[]):boolean {
 if(!Array.isArray(activities)||activities.some(a=>!a||typeof a!=='object'))return false;
 const ids=activities.map(a=>a.portable_id);
 if(ids.some(id=>id!==undefined&&(typeof id!=='string'||!PAGE_UUID.test(id))))return false;
 const defined=ids.filter((id):id is string=>typeof id==='string');
 if(new Set(defined).size!==defined.length)return false;
 const pages=new Map(activities.map(a=>[a.portable_id,a]));
 for(const activity of activities){
  if(activity.page_design?.audiencePageId&&!pages.has(activity.page_design.audiencePageId))return false;
  for(const design of [activity.page_design,activity.result_design]){
   if(design?.widgets!==undefined&&!Array.isArray(design.widgets))return false;
   for(const w of design?.widgets||[]){
   if(!w||typeof w!=='object')return false;
   if(!w.targetActivityId)continue;
   const target=pages.get(w.targetActivityId);
   if(!target)return false;
   if(!w.targetWidgetId)continue;
   const sourceWidgets=target.page_design?.widgets;
   if(!Array.isArray(sourceWidgets))return false;
   const source=sourceWidgets.find((item:any)=>item&&typeof item==='object'&&item.id===w.targetWidgetId);
   if(!source||!['question','timed-quiz','rating','reactions','topic-question'].includes(source.kind))return false;
   if(w.targetQuestionId&&(!['question','timed-quiz'].includes(source.kind)||!Array.isArray(source.questions)||!source.questions.some((q:any)=>q&&q.id===w.targetQuestionId)))return false;
   }
  }
 }
 return true;
}
export function remapPortablePageRouting(design:any,pageIds:ReadonlyMap<string,string>):any {
 const copy=structuredClone(design||{});
 if(copy.audiencePageId){const mapped=pageIds.get(copy.audiencePageId);if(!mapped)throw Error('missing_portable_audience_page');copy.audiencePageId=mapped}
 for(const w of copy.widgets||[])if(w.targetActivityId){const mapped=pageIds.get(w.targetActivityId);if(!mapped)throw Error('missing_portable_result_source');w.targetActivityId=mapped}
 return copy;
}
