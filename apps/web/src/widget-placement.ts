/** Magnetic alignment for the 0..100 percentage slide geometry.
 * A collision is rejected rather than persisted; rotations use their saved
 * unrotated bounding rectangles, a conservative placement rule. */
type Box={x:number;y:number;width:number;height:number};
type Widget={id:string;position?:Partial<Box>};
const number=(n:unknown,fallback:number)=>typeof n==='number'&&Number.isFinite(n)?n:fallback;
const rect=(w:Widget):Box=>({x:number(w.position?.x,0),y:number(w.position?.y,0),width:number(w.position?.width,22),height:number(w.position?.height,20)});
const hit=(a:Box,b:Box)=>a.x<b.x+b.width-0.0001&&a.x+a.width>b.x+0.0001&&a.y<b.y+b.height-0.0001&&a.y+a.height>b.y+0.0001;
export function overlapsOtherWidgets<T extends Widget>(widgets:readonly T[],movingIds:readonly string[]):boolean{
 const ids=new Set(movingIds);const moved=widgets.filter(w=>ids.has(w.id)),fixed=widgets.filter(w=>!ids.has(w.id));
 return moved.some(a=>fixed.some(b=>hit(rect(a),rect(b))));
}
/** Return the original positions when the proposed movement overlaps another widget. */
export function rejectWidgetCollisions<T extends Widget>(original:readonly T[],proposed:T[],movingIds:readonly string[]):T[]{
 return overlapsOtherWidgets(proposed,movingIds)?[...original]:proposed;
}
export function magneticSnapWidget<T extends Widget>(candidate:T,others:readonly T[],threshold=1.5):T{
 const box=rect(candidate);let bestX=box.x,bestY=box.y,dx=threshold+1,dy=threshold+1;
 for(const w of others){if(w.id===candidate.id)continue;const b=rect(w);
  for(const x of [b.x,b.x+b.width,b.x-box.width,b.x+b.width-box.width]){
   const d=Math.abs(x-box.x);if(d<=threshold&&d<dx){bestX=x;dx=d}
  }
  for(const y of [b.y,b.y+b.height,b.y-box.height,b.y+b.height-box.height]){
   const d=Math.abs(y-box.y);if(d<=threshold&&d<dy){bestY=y;dy=d}
  }
 }
 return {...candidate,position:{...candidate.position,x:Math.max(0,Math.min(100-box.width,bestX)),y:Math.max(0,Math.min(100-box.height,bestY))}} as T;
}
/** Choose a free area, preferring the requested drop point, then nearby cells.
 * Return null if the slide has no free rectangle of the requested size. */
export function freeWidgetPosition<T extends Widget>(items:readonly T[],preferred:{x:number;y:number},width=22,height=20):Box|null{
 const first={x:Math.max(0,Math.min(100-width,preferred.x)),y:Math.max(0,Math.min(100-height,preferred.y)),width,height};
 const available=(b:Box)=>items.every(w=>!hit(b,rect(w)));
 if(available(first))return first;
 const cells:Box[]=[];
 for(let y=0;y<=100-height;y+=2)for(let x=0;x<=100-width;x+=2)cells.push({x,y,width,height});
 cells.sort((a,b)=>Math.abs(a.x-first.x)+Math.abs(a.y-first.y)-Math.abs(b.x-first.x)-Math.abs(b.y-first.y));
 return cells.find(available)||null;
}
