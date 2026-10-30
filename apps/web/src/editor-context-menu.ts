/** Place a portaled widget menu within the visual viewport (CSS fixed coords). */
export function contextMenuCoordinates(x:number,y:number,viewportWidth:number,viewportHeight:number){
 const width=Math.min(240,Math.max(80,viewportWidth-16));
 const height=Math.min(430,Math.max(90,viewportHeight-16));
 const safeX=Number.isFinite(x)?x:8,safeY=Number.isFinite(y)?y:8;
 return {x:Math.round(Math.max(8,Math.min(safeX,viewportWidth-width-8))),y:Math.round(Math.max(8,Math.min(safeY,viewportHeight-height-8)))};
}
