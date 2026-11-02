import {moveWidgetGroup} from './widget-group.ts';
/** Magnetic alignment for the 0..100 percentage slide geometry.
 * A collision is rejected rather than persisted; rotations use their saved
 * unrotated bounding rectangles, a conservative placement rule. */
type Box={x:number;y:number;width:number;height:number};
type Widget={id:string;kind?:string;position?:Partial<Box>};
export const isFreeGraphic=(kind?:string)=>kind==='shape'||kind==='line'||kind==='divider';
const number=(n:unknown,fallback:number)=>typeof n==='number'&&Number.isFinite(n)?n:fallback;
const rect=(w:Widget):Box=>({x:number(w.position?.x,0),y:number(w.position?.y,0),width:number(w.position?.width,22),height:number(w.position?.height,20)});
const hit=(a:Box,b:Box)=>a.x<b.x+b.width-0.0001&&a.x+a.width>b.x+0.0001&&a.y<b.y+b.height-0.0001&&a.y+a.height>b.y+0.0001;
export function overlapsOtherWidgets<T extends Widget>(widgets:readonly T[],movingIds:readonly string[]):boolean{
 const ids=new Set(movingIds);const moved=widgets.filter(w=>ids.has(w.id)),fixed=widgets.filter(w=>!ids.has(w.id));
 return moved.some(a=>!isFreeGraphic(a.kind)&&fixed.some(b=>!isFreeGraphic(b.kind)&&hit(rect(a),rect(b))));
}
/** Return the original positions when the proposed movement overlaps another widget. */
export function rejectWidgetCollisions<T extends Widget>(original:readonly T[],proposed:T[],movingIds:readonly string[]):T[]{
 return overlapsOtherWidgets(proposed,movingIds)?[...original]:proposed;
}
/** Snap the actual selected bounding-box origin to slide grid coordinates.
 * Rounding only the pointer delta left widgets permanently off-grid when they
 * started at a non-grid position (e.g. 13% + 5% = 18%). */
export function snapWidgetGroupDelta<T extends Widget>(widgets:readonly T[],ids:readonly string[],dx:number,dy:number,step=5):{dx:number;dy:number}{
 if(!Number.isFinite(dx)||!Number.isFinite(dy)||!Number.isFinite(step)||step<=0)return {dx:0,dy:0};
 const chosen=new Set(ids);const positions=widgets.filter(w=>chosen.has(w.id)).map(rect);
 if(!positions.length)return {dx:0,dy:0};
 const left=Math.min(...positions.map(p=>p.x)),top=Math.min(...positions.map(p=>p.y));
 const right=Math.max(...positions.map(p=>p.x+p.width)),bottom=Math.max(...positions.map(p=>p.y+p.height));
 if(![left,top,right,bottom].every(Number.isFinite))return {dx:0,dy:0};
 return {dx:+(Math.max(-left,Math.min(100-right,Math.round((left+dx)/step)*step-left))).toFixed(4),
         dy:+(Math.max(-top,Math.min(100-bottom,Math.round((top+dy)/step)*step-top))).toFixed(4)};
}
export type AlignmentGuide={axis:'x'|'y';at:number;source:'canvas'|'widget'};
/** PowerPoint-like non-persistent alignment guides, computed with the snap itself.
 * Each axis is chosen independently using a stable smallest-distance rule.
 * Guides must never be stored in session JSON or affect undo history.
 */
export function magneticSnapWithGuides<T extends Widget>(candidate:T,others:readonly T[],threshold=1.5):{widget:T;guides:AlignmentGuide[]}{
 if(candidate.position&&Object.values(candidate.position).some(v=>typeof v==='number'&&!Number.isFinite(v)))
  return {widget:candidate,guides:[]};
 const box=rect(candidate);
 if(![box.x,box.y,box.width,box.height,threshold].every(Number.isFinite)||box.width<=0||box.height<=0||threshold<0)
  return {widget:candidate,guides:[]};
 type Match={delta:number;distance:number;guide:AlignmentGuide;priority:number};
 const targetsX:[number,'canvas'|'widget'][]=[[0,'canvas'],[50,'canvas'],[100,'canvas']];
 const targetsY:[number,'canvas'|'widget'][]=[[0,'canvas'],[50,'canvas'],[100,'canvas']];
 // Compare only rectangles with meaningful dimensions, and never candidate itself.
 for(const other of others){if(other.id===candidate.id)continue;const b=rect(other);
  if(![b.x,b.y,b.width,b.height].every(Number.isFinite)||b.width<=0||b.height<=0)continue;
  targetsX.push([b.x,'widget'],[b.x+b.width/2,'widget'],[b.x+b.width,'widget']);
  targetsY.push([b.y,'widget'],[b.y+b.height/2,'widget'],[b.y+b.height,'widget']);
 }
 const match=(axis:'x'|'y',targets:[number,'canvas'|'widget'][],start:number,extent:number):Match|undefined=>{
  const origin:[number,number][]=[[start,0],[start+extent/2,1],[start+extent,2]];
  let best:Match|undefined;
  for(const [target,source] of targets)for(const [edge,priority] of origin){const delta=target-edge,distance=Math.abs(delta);
   if(distance>threshold||start+delta<-.0001||start+extent+delta>100.0001)continue;
   const candidateMatch={delta,distance,guide:{axis,at:target,source} as AlignmentGuide,priority};
   // Prefer exact boundaries, then centers, then existing widgets. Stable on ties.
   if(!best||distance<best.distance-1e-8||(Math.abs(distance-best.distance)<1e-8&&
       (priority<best.priority||(priority===best.priority&&source==='widget'&&best.guide.source==='canvas'))))best=candidateMatch;
  }
  return best;
 };
 const x=match('x',targetsX,box.x,box.width),y=match('y',targetsY,box.y,box.height);
 if(!x&&!y&&box.x>=0&&box.x+box.width<=100&&box.y>=0&&box.y+box.height<=100)return {widget:candidate,guides:[]};
 return {widget:{...candidate,position:{...candidate.position,
  x:+Math.max(0,Math.min(100-box.width,box.x+(x?.delta||0))).toFixed(4),
  y:+Math.max(0,Math.min(100-box.height,box.y+(y?.delta||0))).toFixed(4)}} as T,
  guides:[...(x?[x.guide]:[]),...(y?[y.guide]:[])]};
}
export function magneticSnapWidget<T extends Widget>(candidate:T,others:readonly T[],threshold=1.5):T{
 return magneticSnapWithGuides(candidate,others,threshold).widget;
}
/** Choose a free area, preferring the requested drop point, then nearby cells.
 * Return null if the slide has no free rectangle of the requested size. */
export function freeWidgetPosition<T extends Widget>(items:readonly T[],preferred:{x:number;y:number},width=22,height=20):Box|null{
 const first={x:Math.max(0,Math.min(100-width,preferred.x)),y:Math.max(0,Math.min(100-height,preferred.y)),width,height};
 const available=(b:Box)=>items.every(w=>isFreeGraphic(w.kind)||!hit(b,rect(w)));
 if(available(first))return first;
 const cells:Box[]=[];
 for(let y=0;y<=100-height;y+=2)for(let x=0;x<=100-width;x+=2)cells.push({x,y,width,height});
 cells.sort((a,b)=>Math.abs(a.x-first.x)+Math.abs(a.y-first.y)-Math.abs(b.x-first.x)-Math.abs(b.y-first.y));
 return cells.find(available)||null;
}

/** Sweep the whole dragged group from its initial position to the pointer target.
 * Stop at the first blocking boundary instead of teleporting back to origin.
 * Bisection never permits the group to pass through another widget at high pointer speed. */
export function moveWidgetsToCollisionLimit<T extends Widget>(original:T[],ids:readonly string[],dx:number,dy:number):T[]{
 if(!Number.isFinite(dx)||!Number.isFinite(dy)||!ids.length)return original;
 const target=moveWidgetGroup(original,ids,dx,dy);
 if(!overlapsOtherWidgets(target,ids)){
  // A straight move can cross a thin widget even if the final position is clear.
  // Check successive substeps using the smallest relevant slide dimension.
  const extents=original.filter(w=>ids.includes(w.id)).map(rect);
  const fixed=original.filter(w=>!ids.includes(w.id)&&!isFreeGraphic(w.kind)).map(rect);
  const smallest=Math.min(5,...extents.map(b=>Math.min(b.width,b.height)),...fixed.map(b=>Math.min(b.width,b.height)));
  const segments=Math.min(400,Math.max(1,Math.ceil(Math.hypot(dx,dy)/Math.max(.2,smallest/3))));
  let safe=0;
  for(let i=1;i<=segments;i++){const t=i/segments;if(overlapsOtherWidgets(moveWidgetGroup(original,ids,dx*t,dy*t),ids)){
    let high=t,low=safe;
    for(let k=0;k<24;k++){const mid=(high+low)/2;if(overlapsOtherWidgets(moveWidgetGroup(original,ids,dx*mid,dy*mid),ids))high=mid;else low=mid}
    return moveWidgetGroup(original,ids,dx*low,dy*low);
   }safe=t}
  return target;
 }
 // Blocking geometry may occur before the target. Probe along the path,
 // then refine the first collision to sub-pixel slide precision.
 let safe=0;
 const segments=Math.min(400,Math.max(8,Math.ceil(Math.hypot(dx,dy)/.5)));
 for(let i=1;i<=segments;i++){
  const t=i/segments;
  if(overlapsOtherWidgets(moveWidgetGroup(original,ids,dx*t,dy*t),ids)){
   let lo=safe,hi=t;
   for(let k=0;k<24;k++){const mid=(lo+hi)/2;if(overlapsOtherWidgets(moveWidgetGroup(original,ids,dx*mid,dy*mid),ids))hi=mid;else lo=mid}
   return moveWidgetGroup(original,ids,dx*lo,dy*lo);
  }
  safe=t;
 }
 return original;
}
