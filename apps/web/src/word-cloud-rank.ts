/** Shared accessible ranking for live statistics: distinct top five, uniform remainder. */
export const CLOUD_TOP_COLORS=['#2563eb','#c2410c','#0f766e','#7c3aed','#be185d'] as const;
export const CLOUD_REMAINDER_COLOR='#475569';
export function cloudRankColor(rank:number):string{return Number.isInteger(rank)&&rank>=0&&rank<5?CLOUD_TOP_COLORS[rank]:CLOUD_REMAINDER_COLOR}
export function rankCloudItems<T>(items:readonly T[],count:(item:T)=>number,label:(item:T)=>string):T[]{return [...items].sort((a,b)=>{
 const ac=Number(count(a)),bc=Number(count(b));const diff=(Number.isFinite(bc)?bc:0)-(Number.isFinite(ac)?ac:0);
 return diff||label(a).localeCompare(label(b));
})}
