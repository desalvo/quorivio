/** Place a portaled widget menu within the visual viewport (CSS fixed coords). */
export function contextMenuCoordinates(x:number,y:number,viewportWidth:number,viewportHeight:number){
 const width=Math.min(240,Math.max(80,viewportWidth-16));
 const height=Math.min(430,Math.max(90,viewportHeight-16));
 const safeX=Number.isFinite(x)?x:8,safeY=Number.isFinite(y)?y:8;
 return {x:Math.round(Math.max(8,Math.min(safeX,viewportWidth-width-8))),y:Math.round(Math.max(8,Math.min(safeY,viewportHeight-height-8)))};
}


/** Place the portaled menu alongside the widget instead of under the pointer.
 * Candidate sides are evaluated against the visual viewport; in a cramped
 * viewport the lowest-overlap visible position wins. */
export function floatingWidgetMenuPosition(
 rect:{left:number;top:number;right:number;bottom:number},
 viewportWidth:number,viewportHeight:number,
 preferredY?:number, menuWidth=240, menuHeight=430
){
 const gap=12,pad=8;
 const width=Math.min(menuWidth,Math.max(80,viewportWidth-2*pad));
 const height=Math.min(menuHeight,Math.max(90,viewportHeight-2*pad));
 const clamp=(v:number,lo:number,hi:number)=>Math.max(lo,Math.min(v,hi));
 const anchor=Number.isFinite(preferredY)?Number(preferredY):rect.top;
 const candidates=[
  {x:rect.right+gap,y:anchor}, {x:rect.left-width-gap,y:anchor},
  {x:rect.left,y:rect.bottom+gap}, {x:rect.left,y:rect.top-height-gap}
 ];
 const overlap=(x:number,y:number)=>Math.max(0,Math.min(x+width,rect.right)-Math.max(x,rect.left))*
  Math.max(0,Math.min(y+height,rect.bottom)-Math.max(y,rect.top));
 let best={x:pad,y:pad,score:Infinity};
 for(const c of candidates){
  const x=clamp(c.x,pad,Math.max(pad,viewportWidth-width-pad));
  const y=clamp(c.y,pad,Math.max(pad,viewportHeight-height-pad));
  const score=overlap(x,y)*1000+Math.hypot(x-c.x,y-c.y);
  if(score<best.score)best={x,y,score};
 }
 return {x:Math.round(best.x),y:Math.round(best.y)};
}
