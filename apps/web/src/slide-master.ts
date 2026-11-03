import type {WidgetTextStyle} from '../../api/src/domain';
/** Presentation master and contextual widgets: numbering is derived from current order, never stored. */
export type SlideWidget = {id:string;kind:string;label?:string;style?:WidgetTextStyle;position?:{x:number;y:number;width:number;height:number;rotation:number};titleFollowPage?:boolean;titleUseMaster?:boolean;footerShowSessionTitle?:boolean;footerShowPageNumber?:boolean;footerSeparator?:boolean;footerSeparatorColor?:string;footerNumberX?:number;footerNumberY?:number};
export const DEFAULT_TITLE_STYLE={fontFamily:'Arial',fontSize:24,color:'#000000',bold:true,textAlign:'center' as const};
export const DEFAULT_FOOTER_STYLE={fontFamily:'Arial',fontSize:14,color:'#26364a',textAlign:'center' as const};
export function newTitleWidget(pageTitle:string):SlideWidget{return {id:'page-title',kind:'title',label:pageTitle,titleFollowPage:true,titleUseMaster:true,style:{fillNone:true,strokeNone:true,shapeType:'rectangle'},position:{x:8,y:3,width:84,height:12,rotation:0}}}
export function newFooterWidget(id:string):SlideWidget{return {id,kind:'footer',label:'',footerShowSessionTitle:true,footerShowPageNumber:true,style:{...DEFAULT_FOOTER_STYLE,fillNone:true,strokeNone:true,shapeType:'rectangle'},position:{x:0,y:93,width:100,height:7,rotation:0}}}
export function slidePageNumber(activities:ReadonlyArray<{id:string}>,id:string):number{return activities.findIndex(a=>a.id===id)+1}
export function widgetDisplay(w:SlideWidget,context:{pageTitle?:string;sessionTitle?:string;pageNumber?:number;masterTitleStyle?:WidgetTextStyle}){
 const title=w.kind==='title'?(w.titleFollowPage===false?w.label||'':context.pageTitle||w.label||''):w.label||'';
 const style=w.kind==='title'?{...DEFAULT_TITLE_STYLE,...(w.titleUseMaster!==false?context.masterTitleStyle:{}),...w.style}:w.style||{};
 const center=w.kind==='footer'?(w.footerShowSessionTitle!==false?context.sessionTitle||'':w.label||''):'';
 const page=w.kind==='footer'&&w.footerShowPageNumber!==false&&typeof context.pageNumber==='number'&&Number.isInteger(context.pageNumber)&&context.pageNumber>0?String(context.pageNumber):'';
 return {title,style,center,page};
}

/** The number belongs to the slide, not to the position or rotation of a Footer widget. */
export function footerPageNumber(widgets:ReadonlyArray<SlideWidget>,pageNumber:number){
 const footer=widgets.find(w=>w.kind==='footer');
 if(!footer||footer.footerShowPageNumber===false||!Number.isSafeInteger(pageNumber)||pageNumber<=0)return null;
 return {text:String(pageNumber),fontFamily:footer.style?.footerNumberFontFamily||footer.style?.fontFamily||DEFAULT_FOOTER_STYLE.fontFamily,
  fontSize:footer.style?.footerNumberFontSize||footer.style?.fontSize||DEFAULT_FOOTER_STYLE.fontSize,
  color:footer.style?.footerNumberColor||footer.style?.color||DEFAULT_FOOTER_STYLE.color,
  paddingRight:footer.style?.footerNumberPaddingRight??5,paddingBottom:footer.style?.footerNumberPaddingBottom??5,
  ...(footer.footerNumberX!==undefined||footer.footerNumberY!==undefined?{x:(footer.position?.x??0)+((footer.position?.width??100)*(footer.footerNumberX??100))/100,y:(footer.position?.y??93)+((footer.position?.height??7)*(footer.footerNumberY??100))/100}:{} )};
}
