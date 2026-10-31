import type {WidgetTextStyle} from '../../api/src/domain';
/** Presentation master and contextual widgets: numbering is derived from current order, never stored. */
export type SlideWidget = {id:string;kind:string;label?:string;style?:WidgetTextStyle;position?:{x:number;y:number;width:number;height:number;rotation:number};titleFollowPage?:boolean;titleUseMaster?:boolean;footerShowSessionTitle?:boolean;footerShowPageNumber?:boolean};
export const DEFAULT_TITLE_STYLE={fontFamily:'Arial',fontSize:38,color:'#f5f6ff',bold:true,textAlign:'center' as const};
export const DEFAULT_FOOTER_STYLE={fontFamily:'Arial',fontSize:14,color:'#e0e5f2',textAlign:'center' as const};
export function newTitleWidget(pageTitle:string):SlideWidget{return {id:'page-title',kind:'title',label:pageTitle,titleFollowPage:true,titleUseMaster:true,style:{fillNone:true,strokeNone:true,shapeType:'rectangle'},position:{x:8,y:3,width:84,height:12,rotation:0}}}
export function newFooterWidget(id:string):SlideWidget{return {id,kind:'footer',label:'',footerShowSessionTitle:true,footerShowPageNumber:true,style:{...DEFAULT_FOOTER_STYLE,fillNone:true,strokeNone:true,shapeType:'rectangle'},position:{x:0,y:94,width:100,height:6,rotation:0}}}
export function slidePageNumber(activities:ReadonlyArray<{id:string}>,id:string):number{return Math.max(0,activities.findIndex(a=>a.id===id))+1}
export function widgetDisplay(w:SlideWidget,context:{pageTitle?:string;sessionTitle?:string;pageNumber?:number;masterTitleStyle?:WidgetTextStyle}){
 const title=w.kind==='title'?(w.titleFollowPage===false?w.label||'':context.pageTitle||w.label||''):w.label||'';
 const style=w.kind==='title'&&w.titleUseMaster!==false?{...w.style,...DEFAULT_TITLE_STYLE,...context.masterTitleStyle}:w.style||{};
 const center=w.kind==='footer'?(w.footerShowSessionTitle!==false?context.sessionTitle||'':w.label||''):'';
 const page=w.kind==='footer'&&w.footerShowPageNumber!==false&&typeof context.pageNumber==='number'&&Number.isInteger(context.pageNumber)&&context.pageNumber>0?String(context.pageNumber):'';
 return {title,style,center,page};
}
