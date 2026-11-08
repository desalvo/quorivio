/** Pure drag-and-drop ordering; preserves stable activity IDs and therefore all existing answers. */
export function movePageId(ids:readonly string[], sourceId:string, targetId:string):string[]{
 if(!Array.isArray(ids)||new Set(ids).size!==ids.length||ids.some(x=>typeof x!=='string'||!x))throw Error('Invalid page sequence');
 const source=ids.indexOf(sourceId),target=ids.indexOf(targetId);
 if(source<0||target<0)throw Error('Page is not in this session');
 const next=[...ids];if(source===target)return next;
 next.splice(source,1);next.splice(target,0,sourceId);return next;
}

/** Drop onto a gap, rather than onto another thumbnail. The slot is in the
 * ORIGINAL sequence: zero before the first page, ids.length after the last.
 * Removing a page ahead of its destination shifts that slot left by one. */
export function movePageToSlot(ids:readonly string[],sourceId:string,slot:number):string[]{
 if(!Array.isArray(ids)||new Set(ids).size!==ids.length||ids.some(x=>typeof x!=='string'||!x))throw Error('Invalid page sequence');
 if(!Number.isInteger(slot)||slot<0||slot>ids.length)throw Error('Invalid page slot');
 const source=ids.indexOf(sourceId);
 if(source<0)throw Error('Page is not in this session');
 const next=[...ids];
 next.splice(source,1);
 next.splice(source<slot?slot-1:slot,0,sourceId);
 return next;
}
