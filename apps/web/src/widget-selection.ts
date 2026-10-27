/** Pure multi-selection commands used by pointer, keyboard and accessible toolbar. */
import {moveWidgetGroup,pasteWidgetGroup,widgetRect} from './widget-group.ts';
import {overlapsOtherWidgets} from './widget-placement.ts';
type Widget={id:string;kind:string;position?:{x?:number;y?:number;width?:number;height?:number;rotation?:number}};
export function existingWidgetIds<T extends {id:string}>(widgets:readonly T[],ids:readonly string[]):string[]{
 const available=new Set(widgets.map(w=>w.id));return [...new Set(ids)].filter(id=>available.has(id));
}
export function deleteWidgetSelection<T extends {id:string}>(widgets:readonly T[],ids:readonly string[]):T[]{
 const chosen=new Set(existingWidgetIds(widgets,ids));return chosen.size?widgets.filter(w=>!chosen.has(w.id)):widgets as T[];
}
export function duplicateWidgetSelection<T extends Widget>(widgets:readonly T[],ids:readonly string[],newIds:readonly string[],offset=5):{widgets:T[];selected:string[]}{
 const chosen=new Set(existingWidgetIds(widgets,ids));const source=widgets.filter(w=>chosen.has(w.id));
 if(!source.length)return {widgets:widgets as T[],selected:[]};
 const occupied=new Set(widgets.map(w=>w.id));
 if(newIds.some(id=>occupied.has(id)))throw new Error('Duplicate ID conflicts with existing canvas widget');
 const copies=pasteWidgetGroup(source,newIds,offset);
 return {widgets:[...widgets,...copies],selected:copies.map(w=>w.id)};
}
export function nudgeWidgetSelection<T extends Widget>(widgets:T[],ids:readonly string[],dx:number,dy:number):T[]{
 return moveWidgetGroup(widgets,existingWidgetIds(widgets,ids),dx,dy);
}

/** Find a collision-free translation for copies of a selected group.
 *
 * A fixed 5% paste offset usually intersects the originals. Search complete
 * group translations, preserving each widget's relative x/y and dimensions.
 * Do not mutate the original canvas and do not silently drop any selected item.
 * Return null only if the entire group genuinely cannot fit without collision.
 */
export function insertWidgetGroupInFreeSpace<T extends Widget>(
 widgets:readonly T[],source:readonly T[],newIds:readonly string[],preferredOffset=5
):{widgets:T[];selected:string[]}|null{
 if(!source.length)return null;
 if(!Number.isFinite(preferredOffset))throw new Error('Invalid group paste offset');
 const existing=new Set(widgets.map(w=>w.id));
 if(newIds.some(id=>existing.has(id)))throw new Error('Group paste ID conflicts with canvas');
 const copies=pasteWidgetGroup(source,newIds,0);
 const positions=source.map(widgetRect);
 // Group may not fit if its members already overlap; copied widgets must not
 // introduce any new intersection, including intersections with one another.
 for(let i=0;i<positions.length;i++)for(let j=i+1;j<positions.length;j++){
  const a=positions[i],b=positions[j];
  if(a.x<b.x+b.width-0.0001&&a.x+a.width>b.x+0.0001&&a.y<b.y+b.height-0.0001&&a.y+a.height>b.y+0.0001)return null;
 }
 const minX=-Math.min(...positions.map(p=>p.x)),maxX=Math.min(...positions.map(p=>100-p.x-p.width));
 const minY=-Math.min(...positions.map(p=>p.y)),maxY=Math.min(...positions.map(p=>100-p.y-p.height));
 if(minX>maxX||minY>maxY)return null;
 const deltas=(min:number,max:number)=>{
  const values=new Set<number>([min,max]);
  for(let v=Math.ceil(min);v<=Math.floor(max);v++)values.add(v);
  if(preferredOffset>=min&&preferredOffset<=max)values.add(preferredOffset);
  return [...values].sort((a,b)=>Math.abs(a-preferredOffset)-Math.abs(b-preferredOffset)||b-a);
 };
 const xs=deltas(minX,maxX),ys=deltas(minY,maxY);
 const candidates=xs.flatMap(dx=>ys.map(dy=>({dx,dy})));
 candidates.sort((a,b)=>
  (a.dx-preferredOffset)**2+(a.dy-preferredOffset)**2-
  ((b.dx-preferredOffset)**2+(b.dy-preferredOffset)**2)||
  (b.dy-a.dy)||(b.dx-a.dx)
 );
 for(const {dx,dy} of candidates){
  const translated=copies.map((w,i)=>({...w,position:{...w.position,
    x:+(positions[i].x+dx).toFixed(4),y:+(positions[i].y+dy).toFixed(4)
  }} as T));
  if(!overlapsOtherWidgets([...widgets,...translated],newIds))return {widgets:[...widgets,...translated],selected:[...newIds]};
 }
 return null;
}
