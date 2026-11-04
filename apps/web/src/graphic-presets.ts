import type {WidgetTextStyle} from '../../api/src/domain';
export type GraphicKind='line'|'shape';
export type GraphicPreset={id:string;label:string;style:WidgetTextStyle};
const line=(id:string,label:string,extra:WidgetTextStyle):GraphicPreset=>({id,label,style:{fontFamily:'Arial',strokeColor:'#334155',strokeWidth:2,strokeDash:'solid',lineDirection:'horizontal',lineArrow:'none',fillNone:true,...extra}});
const shape=(id:NonNullable<WidgetTextStyle['shapeType']>,label:string):GraphicPreset=>({id,label,style:{fontFamily:'Arial',strokeColor:'#334155',strokeWidth:2,strokeDash:'solid',fillColor:'#dbeafe',fillMode:'solid',shapeType:id,fillNone:false}});
export const GRAPHIC_PRESETS:Record<GraphicKind,readonly GraphicPreset[]>={
 line:[line('solid','Linea continua',{}),line('dash','Tratteggiata',{strokeDash:'dash'}),line('dot','Punteggiata',{strokeDash:'dot'}),line('arrow-end','Freccia a destra',{lineArrow:'end'}),line('arrow-start','Freccia a sinistra',{lineArrow:'start'}),line('arrow-both','Doppia freccia',{lineArrow:'both'}),line('vertical','Verticale',{lineDirection:'vertical'}),line('diagonal','Diagonale ↘',{lineDirection:'diagonal'}),line('reverse','Diagonale ↙',{lineDirection:'reverse'}),line('dash-arrow','Tratteggio con freccia',{strokeDash:'dash',lineArrow:'end'})],
 shape:[shape('rectangle','Rettangolo'),shape('rounded-rectangle','Rettangolo arrotondato'),shape('circle','Cerchio'),shape('ellipse','Ovale'),shape('triangle','Triangolo'),shape('diamond','Rombo'),shape('pentagon','Pentagono'),shape('hexagon','Esagono'),shape('star','Stella'),shape('arrow','Freccia'),shape('heart','Cuore'),shape('cloud','Nuvola'),shape('speech','Fumetto')]
};
export function graphicStyle(kind:GraphicKind,preset?:GraphicPreset,options?:{strokeWidth?:number;strokeColor?:string;fillColor?:string;fillNone?:boolean}):WidgetTextStyle{
 const base=preset?.style||GRAPHIC_PRESETS[kind][0].style;
 return {...base,strokeWidth:options?.strokeWidth??base.strokeWidth,strokeColor:options?.strokeColor??base.strokeColor,...(kind==='shape'?{fillColor:options?.fillColor??base.fillColor,fillNone:options?.fillNone??false}:{})};
}
