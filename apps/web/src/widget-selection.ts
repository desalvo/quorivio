/** Pure multi-selection commands used by pointer, keyboard and accessible toolbar. */
import {moveWidgetGroup,pasteWidgetGroup} from './widget-group.ts';
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
