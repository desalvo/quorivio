/** Page-local group movement and clipboard operations. No input objects are mutated. */
type Position={x:number;y:number;width:number;height:number;rotation?:number};
type Widget={id:string;position?:Partial<Position>};
const finite=(v:unknown,fallback:number)=>typeof v==='number'&&Number.isFinite(v)?v:fallback;
const clamp=(v:number,min:number,max:number)=>Math.min(max,Math.max(min,v));
const round=(v:number)=>+v.toFixed(4);
export const widgetRect=(widget:Widget):Position=>{
 const p=widget.position||{};
 const width=clamp(finite(p.width,48),.01,100),height=clamp(finite(p.height,24),.01,100);
 return {x:clamp(finite(p.x,0),0,100-width),y:clamp(finite(p.y,0),0,100-height),width,height,rotation:finite(p.rotation,0)};
};
/** Clamp one common delta against all selected edges, preserving relative spacing. */
export function moveWidgetGroup<T extends Widget>(widgets:T[],ids:readonly string[],dx:number,dy:number):T[]{
 const chosen=new Set(ids),items=widgets.filter(w=>chosen.has(w.id));
 if(!items.length||!Number.isFinite(dx)||!Number.isFinite(dy))return widgets;
 const bounds=items.map(widgetRect);
 const actualX=clamp(dx,-Math.min(...bounds.map(p=>p.x)),Math.min(...bounds.map(p=>100-p.x-p.width)));
 const actualY=clamp(dy,-Math.min(...bounds.map(p=>p.y)),Math.min(...bounds.map(p=>100-p.y-p.height)));
 if(!actualX&&!actualY)return widgets;
 return widgets.map(w=>chosen.has(w.id)?{...w,position:{...w.position,x:round(widgetRect(w).x+actualX),y:round(widgetRect(w).y+actualY)}}:w);
}
/** Duplicate selected widgets as a unit with independent IDs and preserved spacing. */
export function pasteWidgetGroup<T extends Widget>(source:readonly T[],newIds:readonly string[],offset=5):T[]{
 if(!source.length)return [];
 const originalIds=new Set(source.map(w=>w.id));
 if(newIds.length!==source.length||new Set(newIds).size!==newIds.length||newIds.some(id=>!id||originalIds.has(id)))throw new Error('Group paste requires unique new IDs');
 if(!Number.isFinite(offset))throw new Error('Invalid paste offset');
 const originals=source.map(widgetRect);
 const deltaX=clamp(offset,-Math.min(...originals.map(p=>p.x)),Math.min(...originals.map(p=>100-p.x-p.width)));
 const deltaY=clamp(offset,-Math.min(...originals.map(p=>p.y)),Math.min(...originals.map(p=>100-p.y-p.height)));
 const clonedId=new Map(source.map((w,i)=>[w.id,newIds[i]]));
 return source.map((w,i)=>({
  ...structuredClone(w),
  ...(typeof (w as T&{targetWidgetId?:string}).targetWidgetId==='string'&&clonedId.has((w as T&{targetWidgetId:string}).targetWidgetId)?{targetWidgetId:clonedId.get((w as T&{targetWidgetId:string}).targetWidgetId)}:{}),
  id:newIds[i],position:{...w.position,x:round(originals[i].x+deltaX),y:round(originals[i].y+deltaY),width:originals[i].width,height:originals[i].height}
 } as T));
}
