import type {MobilePageLayout,WidgetTextStyle} from '../../api/src/domain';

/** Independent smartphone stage: logical 390px viewport, scrollable 720px+
 * document. No desktop background or desktop positions are imported. */
export const MOBILE_PAGE_WIDTH = 390;
export const MOBILE_PAGE_MIN_HEIGHT = 720;
export type MobileWidget={id:string;kind:string;position?:{x:number;y:number;width:number;height?:number;rotation?:number};options?:unknown[];questions?:unknown[];description?:string;style?:WidgetTextStyle};

export function mobileWidgetHeight(widget:MobileWidget):number {
 const optionCount=Array.isArray(widget.options)?widget.options.length:0;
 const subquestionCount=Array.isArray(widget.questions)?widget.questions.length:0;
 switch(widget.kind){
  case 'question':case 'timed-quiz':return Math.min(470,200+optionCount*30+subquestionCount*85);
  case 'topic-question':return 210;
  case 'rating':return 230; // Includes optional comment and the full 0–9 rating row.
  case 'reactions':return 145;
  case 'results-button':return 205;
  case 'title':return 90;
  case 'footer':return 64;
  case 'shape':case 'line':return 80;
  case 'text':case 'postit':return widget.description&&widget.description.length>120?180:130;
  default:return 165;
 }
}
export function mobileStageHeight(widgets:readonly MobileWidget[]):number {
 return Math.max(MOBILE_PAGE_MIN_HEIGHT,24+widgets.reduce((height,w)=>height+mobileWidgetHeight(w)+16,0)+24);
}
export function mobilePageWidgets<T extends MobileWidget>(widgets:readonly T[],mobile?:MobilePageLayout):T[]{
 const stageHeight=mobileStageHeight(widgets);
 // The footer is the end of the mobile document, irrespective of the
 // order the presenter used when inserting widgets on the desktop canvas.
 // Explicit smartphone placements remain under the presenter's control.
 let top=24;
 const defaults=new Map<string,MobileWidget['position']>();
 // Reading order follows the desktop canvas top-to-bottom and left-to-right,
 // rather than the time a widget was inserted. Footer is always last.
 const ordered=widgets.map((w,index)=>({w,index})).sort((a,b)=>{
  if(a.w.kind==='footer')return b.w.kind==='footer'?a.index-b.index:1;
  if(b.w.kind==='footer')return -1;
  const ay=a.w.position?.y??a.index*10,by=b.w.position?.y??b.index*10;
  return ay-by||(a.w.position?.x??0)-(b.w.position?.x??0)||a.index-b.index;
 });
 for(const {w} of ordered){
  const size=mobileWidgetHeight(w);
  // Reserve the final bottom margin even on short pages (720px minimum).
  // Without this, a footer can appear halfway down an otherwise empty phone slide.
  if(w.kind==='footer')top=Math.max(top,stageHeight-24-size);
  defaults.set(w.id,{
   x:4,y:Number((top/stageHeight*100).toFixed(4)),width:92,
   height:Number((size/stageHeight*100).toFixed(4)),rotation:0
  });
  top+=size+16;
 }
 return widgets.map(w=>({...w,position:mobile?.positions?.[w.id]??defaults.get(w.id),...(mobile?.styles?.[w.id]?{style:{...w.style,...mobile.styles[w.id]}}:{})}));
}
export function captureMobilePositions(widgets:readonly MobileWidget[]):NonNullable<MobilePageLayout['positions']>{
 return Object.fromEntries(widgets.filter(w=>!!w.position).map(w=>[w.id,w.position!]));
}

/** Remove stale per-widget positions after an author deletes a widget. A deleted
 * widget must never leave a mobile override that invalidates page saving. */
export function pruneMobilePageLayout(mobile:MobilePageLayout,widgets:readonly MobileWidget[]):MobilePageLayout{
 if(!mobile.positions&&!mobile.styles)return mobile;
 const ids=new Set(widgets.map(w=>w.id));
 const positions=Object.fromEntries(Object.entries(mobile.positions||{}).filter(([id])=>ids.has(id)));
 const styles=Object.fromEntries(Object.entries(mobile.styles||{}).filter(([id])=>ids.has(id)));
 const cleaned={...mobile};
 if(Object.keys(positions).length)cleaned.positions=positions;
 else delete cleaned.positions;
 if(Object.keys(styles).length)cleaned.styles=styles;
 else delete cleaned.styles;
 return cleaned;
}

/** Keep phone layouts automatic unless the presenter actually moves/resizes one
 * widget. Never persist generated positions for untouched widgets: these must
 * keep adapting to later desktop edits, additions and deletions. */
export function mergeMobilePositionEdits<T extends MobileWidget>(desktop:readonly T[],mobile:MobilePageLayout,edited:readonly T[]):MobilePageLayout {
 const prior=new Map(mobilePageWidgets(desktop,mobile).map(w=>[w.id,w.position]));
 const positions:{[id:string]:NonNullable<MobileWidget['position']>}={...mobile.positions};
 const styles:NonNullable<MobilePageLayout['styles']>={...mobile.styles};
 const originals=new Map(desktop.map(w=>[w.id,w]));
 const ids=new Set(edited.map(w=>w.id));
 for(const id of Object.keys(positions))if(!ids.has(id))delete positions[id];
 for(const id of Object.keys(styles))if(!ids.has(id))delete styles[id];
 for(const widget of edited){
  const previous=prior.get(widget.id);
  if(widget.position&&(!previous||JSON.stringify(previous)!==JSON.stringify(widget.position)))positions[widget.id]=widget.position;
  // Only the typography/appearance keys that were edited on the phone are
  // overridden. Everything else continues to inherit later desktop changes.
  const original=originals.get(widget.id);
  if(!original)continue;
  const phoneBefore={...original.style,...mobile.styles?.[widget.id]};
  const delta:Record<string,unknown>={...styles[widget.id]};
  for(const key of new Set([...Object.keys(phoneBefore),...Object.keys(widget.style||{})])){
   const before=(phoneBefore as Record<string,unknown>)[key];
   const after=(widget.style as Record<string,unknown>|undefined)?.[key];
   if(before!==after){
    if(after===(original.style as Record<string,unknown>|undefined)?.[key]||after===undefined)delete delta[key];
    else delta[key]=after;
   }
  }
  if(Object.keys(delta).length)styles[widget.id]=delta as WidgetTextStyle;
  else delete styles[widget.id];
 }
 return {...mobile,positions:Object.keys(positions).length?positions:undefined,styles:Object.keys(styles).length?styles:undefined};
}
