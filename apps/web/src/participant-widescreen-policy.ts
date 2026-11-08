/** A static slide is shown 16:9 on a participant's phone by default.
 * Imported PDF/PPTX pages are page backgrounds, not resizeable widgets.
 * A page whose own authored widget array is empty has no resizeable objects;
 * inherited master decorations are deliberately ignored for this decision.
 * Interactive activities and pages containing even one authored widget keep
 * the regular accessible phone layout.
 *
 * This decision is view-only. It never rewrites saved mobile positions or
 * changes the participant's explicit layout preference.
 */
export type ParticipantDisplayPage={
 type?:string;
 page_design?:{
  importedImageFit?:unknown;
  backgroundAssetId?:unknown;
  widgets?:readonly {kind?:string}[]|null;
 }|null;
};
export function participantStaticWidescreenPage(page:ParticipantDisplayPage|null|undefined):boolean{
 if(!page||page.type!=='slide')return false;
 const design=page.page_design;
 if(design?.importedImageFit!==undefined&&typeof design.backgroundAssetId==='string'&&design.backgroundAssetId.length>0)return true;
 return !design?.widgets||design.widgets.length===0;
}
/** Manual participant selection always wins; automatic 16:9 applies to the
 * currently presented static page only and is reevaluated on page changes. */
export function participantPhoneLayoutEnabled(
 phonePreferred:boolean,readingMode:boolean,explicitPreference:boolean,page:ParticipantDisplayPage|null|undefined
):boolean{
 return phonePreferred&&!readingMode&&(explicitPreference||!participantStaticWidescreenPage(page));
}
