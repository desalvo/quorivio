/** Thumbnail actions use a separate selection from canvas widget selection. */
export function choosePageIds(current:readonly string[],id:string,modifier:boolean):string[]{
 if(!modifier)return [id];
 return current.includes(id)?current.filter(value=>value!==id):[...current,id];
}
export function orderedSelectedPageIds(pages:readonly {id:string}[],selected:readonly string[]):string[]{
 const wanted=new Set(selected);return pages.filter(page=>wanted.has(page.id)).map(page=>page.id);
}
export function duplicatePageOrder(original:readonly string[],copies:ReadonlyMap<string,string>):string[]{
 const order:string[]=[];
 for(const id of original){order.push(id);const copy=copies.get(id);if(copy)order.push(copy)}
 return order;
}
/** Ignore canvas/widget typing and native browser shortcuts. */
export function thumbnailShortcut(event:{key:string;ctrlKey?:boolean;metaKey?:boolean;altKey?:boolean;shiftKey?:boolean;repeat?:boolean},focusInThumbnails:boolean):'duplicate'|'rename'|'delete'|null{
 if(!focusInThumbnails||event.ctrlKey||event.metaKey||event.altKey||event.shiftKey||event.repeat)return null;
 if(event.key.toLowerCase()==='d')return 'duplicate';
 if(event.key.toLowerCase()==='r')return 'rename';
 if(event.key==='Backspace')return 'delete';
 return null;
}
