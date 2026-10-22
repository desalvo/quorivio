/** Pure drag-and-drop ordering; preserves stable activity IDs and therefore all existing answers. */
export function movePageId(ids:readonly string[], sourceId:string, targetId:string):string[]{
 if(!Array.isArray(ids)||new Set(ids).size!==ids.length||ids.some(x=>typeof x!=='string'||!x))throw Error('Invalid page sequence');
 const source=ids.indexOf(sourceId),target=ids.indexOf(targetId);
 if(source<0||target<0)throw Error('Page is not in this session');
 const next=[...ids];if(source===target)return next;
 next.splice(source,1);next.splice(target,0,sourceId);return next;
}
