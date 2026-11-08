import type {MobilePageLayout,WidgetTextStyle} from '../../api/src/domain';

/** Independent smartphone stage: logical 390px viewport, scrollable 720px+
 * document. No desktop background or desktop positions are imported. */
export const MOBILE_PAGE_WIDTH = 390;
export const MOBILE_PAGE_MIN_HEIGHT = 720;
export type MobileWidget={id:string;kind:string;position?:{x:number;y:number;width:number;height?:number;rotation?:number};options?:unknown[];questions?:unknown[];description?:string;resultTopCount?:number;showTitle?:boolean;showQrUrl?:boolean;style?:WidgetTextStyle};

/** Automatically compact phone slides while leaving every answer usable.
 * Heights are measured in 390px *logical* pixels, not scaled desktop pixels.
 * A page only grows beyond 720px if its actual interactive content needs it.
 * User-authored mobile positions are never rewritten by the automatic plan. */
/** Approximate wrapped 18px phone choices at 390px, reserving a 44px tap row.
 * Long (up to 255-character) answers must gain height instead of shrinking. */
function mobileChoiceHeight(choice:unknown):number {
 const label=choice&&typeof choice==='object'&&'label' in choice&&typeof choice.label==='string'?choice.label:'';
 return Math.max(44,Math.ceil(Math.max(1,label.length)/32)*26+12);
}
export function mobileWidgetHeight(widget:MobileWidget):number {
 const options=Array.isArray(widget.options)?widget.options:[];
 const subquestions=Array.isArray(widget.questions)?widget.questions:[];
 const optionSpace=options.reduce<number>((sum,choice)=>sum+mobileChoiceHeight(choice),0);
 const subquestionSpace=subquestions.reduce<number>((sum,question)=>{
  const options=question&&typeof question==='object'&&'options' in question&&Array.isArray(question.options)?question.options:[];
  return sum+190+options.reduce<number>((size,choice)=>size+mobileChoiceHeight(choice),0);
 },0);
 const textLength=(widget.description||'').length;
 switch(widget.kind){
  case 'question':case 'timed-quiz':return Math.min(3000,
    // The historical 190px header was charged again even when the widget has
    // options, leaving large unused blank zones above/below short answers.
    // 150px reserves title/description/submit plus the 44px choice rows.
    (options.length?150:190)+optionSpace+subquestionSpace+Math.min(190,Math.ceil(textLength/40)*26));
  case 'topic-question':return 228; // 96px textarea, 44px submit and title without scaling.
  case 'rating':return 230; // Comment and all ten 0–9 choices remain usable.
  case 'reactions':return 125;
  case 'results-button':return Math.min(360,Math.max(176,110+Math.min(5,Math.max(1,Number(widget.resultTopCount)||5))*36)); // Reserve visible result rows, not empty card space.
  case 'title':return 68;
  case 'footer':return 54;
  case 'shape':case 'line':return 64;
  case 'text':case 'postit':return textLength>120?Math.min(220,130+Math.ceil((textLength-120)/90)*25):110;
  case 'qr':return 198+(widget.showQrUrl===false?0:28)+(widget.showTitle===true?22:0); // Bounded QR with optional URL/title, never desktop-sized.
  default:return 145;
 }
}

const MOBILE_TOP_MARGIN=16;
const MOBILE_GAP=8;
const MOBILE_BOTTOM_MARGIN=16;
function mobileOrderedWidgets<T extends MobileWidget>(widgets:readonly T[]):T[]{
 return widgets.map((w,index)=>({w,index})).sort((a,b)=>{
  if(a.w.kind==='footer')return b.w.kind==='footer'?a.index-b.index:1;
  if(b.w.kind==='footer')return -1;
  return (a.w.position?.y??a.index*10)-(b.w.position?.y??b.index*10)
   ||(a.w.position?.x??0)-(b.w.position?.x??0)||a.index-b.index;
 }).map(item=>item.w);
}
/** Shared phone planner. Manual widget placements are reserved vertical slots;
 * later automatic widgets must not overlap the authored phone coordinates.
 * The conservative full-width reservation keeps interactive controls usable.
 */
function mobileLayoutPlan(widgets:readonly MobileWidget[],mobile?:MobilePageLayout):{
 height:number;defaults:Map<string,NonNullable<MobileWidget['position']>>
}{
 const ordered=mobileOrderedWidgets(widgets);
 const total=ordered.reduce((height,w)=>height+mobileWidgetHeight(w),0);
 const baseline=Math.max(MOBILE_PAGE_MIN_HEIGHT,MOBILE_TOP_MARGIN+total+Math.max(0,ordered.length-1)*MOBILE_GAP+MOBILE_BOTTOM_MARGIN);
 const fixed=ordered.filter(w=>mobile?.positions?.[w.id]);
 const place=(height:number)=>{
  const reservations=fixed.map(w=>{
   const p=mobile!.positions![w.id];
   const start=Math.max(0,p.y*height/100);
   const end=start+(p.height===undefined?mobileWidgetHeight(w):Math.max(0,p.height)*height/100);
   return {start,end};
  }).sort((a,b)=>a.start-b.start);
  const defaults=new Map<string,NonNullable<MobileWidget['position']>>();
  let top=MOBILE_TOP_MARGIN;
  const findFree=(candidate:number,size:number)=>{
   for(let tries=0;tries<=reservations.length;tries++){
    const clash=reservations.find(r=>candidate<r.end+MOBILE_GAP&&candidate+size+MOBILE_GAP>r.start);
    if(!clash)break;
    candidate=clash.end+MOBILE_GAP;
   }
   return candidate;
  };
  for(const w of ordered){
   if(mobile?.positions?.[w.id])continue;
   const size=mobileWidgetHeight(w);
   let y=w.kind==='footer'?findFree(Math.max(top,height-MOBILE_BOTTOM_MARGIN-size),size):findFree(top,size);
   if(w.kind==='footer'&&y+size>height-MOBILE_BOTTOM_MARGIN){
    const earlier=findFree(top,size);
    if(earlier+size<=height-MOBILE_BOTTOM_MARGIN)y=earlier;
   }
   defaults.set(w.id,{x:4,y:Number((y/height*100).toFixed(4)),width:92,
    height:Number((size/height*100).toFixed(4)),rotation:0});
   top=y+size+MOBILE_GAP;
  }
  return {defaults,required:top-MOBILE_GAP+MOBILE_BOTTOM_MARGIN};
 };
 if(!fixed.length)return {height:baseline,defaults:place(baseline).defaults};
 let height=baseline;
 for(let iteration=0;iteration<16;iteration++){
  const candidate=place(height);
  if(candidate.required<=height+0.01)return {height,defaults:candidate.defaults};
  // Authored positions use percentages. Allow them to move as the stage grows.
  height=Math.min(30000,Math.max(height+64,Math.ceil(height*1.25),Math.ceil(candidate.required)));
  if(height===30000)break;
 }
 // A manually placed widget covering the entire page has no collision-free
 // solution; avoid an unbounded layout loop and retain its exact coordinates.
 return {height,defaults:place(height).defaults};
}
export function mobileStageHeight(widgets:readonly MobileWidget[],mobile?:MobilePageLayout):number {
 return mobileLayoutPlan(widgets,mobile).height;
}
export function mobilePageWidgets<T extends MobileWidget>(widgets:readonly T[],mobile?:MobilePageLayout):T[]{
 const layout=mobileLayoutPlan(widgets,mobile);
 return widgets.map(w=>({...w,position:mobile?.positions?.[w.id]??layout.defaults.get(w.id),...(mobile?.styles?.[w.id]?{style:{...w.style,...mobile.styles[w.id]}}:{})}));
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
