import type {MobilePageLayout} from '../../api/src/domain';

/** Independent smartphone stage: logical 390px viewport, scrollable 720px+
 * document. No desktop background or desktop positions are imported. */
export const MOBILE_PAGE_WIDTH = 390;
export const MOBILE_PAGE_MIN_HEIGHT = 720;
export type MobileWidget={id:string;kind:string;position?:{x:number;y:number;width:number;height?:number;rotation?:number};options?:unknown[];questions?:unknown[];description?:string};

export function mobileWidgetHeight(widget:MobileWidget):number {
 const optionCount=Array.isArray(widget.options)?widget.options.length:0;
 const subquestionCount=Array.isArray(widget.questions)?widget.questions.length:0;
 switch(widget.kind){
  case 'question':case 'timed-quiz':return Math.min(470,200+optionCount*30+subquestionCount*85);
  case 'topic-question':return 210;
  case 'rating':return 165;
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
 let top=24;
 return widgets.map(w=>{
  const size=mobileWidgetHeight(w);
  const position=mobile?.positions?.[w.id]??{
   x:4,y:Number((top/stageHeight*100).toFixed(4)),width:92,
   height:Number((size/stageHeight*100).toFixed(4)),rotation:0
  };
  top+=size+16;
  return {...w,position};
 });
}
export function captureMobilePositions(widgets:readonly MobileWidget[]):NonNullable<MobilePageLayout['positions']>{
 return Object.fromEntries(widgets.filter(w=>!!w.position).map(w=>[w.id,w.position!]));
}

/** Remove stale per-widget positions after an author deletes a widget. A deleted
 * widget must never leave a mobile override that invalidates page saving. */
export function pruneMobilePageLayout(mobile:MobilePageLayout,widgets:readonly MobileWidget[]):MobilePageLayout{
 if(!mobile.positions)return mobile;
 const ids=new Set(widgets.map(w=>w.id));
 const positions=Object.fromEntries(Object.entries(mobile.positions).filter(([id])=>ids.has(id)));
 return Object.keys(positions).length===Object.keys(mobile.positions).length?mobile:{...mobile,positions};
}
