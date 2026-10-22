/** A page sequence must be a complete permutation, not a partial update. */
export function validPageOrder(requested:unknown,existing:readonly string[]):requested is string[]{
 return Array.isArray(requested)&&requested.length===existing.length&&requested.length<=500&&
 requested.every(x=>typeof x==='string'&&/^[0-9a-f-]{36}$/i.test(x))&&
 new Set(requested).size===requested.length&&existing.every(id=>requested.includes(id));
}
