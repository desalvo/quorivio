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
/** Overlapping widgets are intentional (slide layering). Keep this compatibility
 * entry point for old callers; only canvas bounds constrain interaction. */
export function rejectWidgetCollisions<T extends Widget>(_original:readonly T[],proposed:T[],_movingIds:readonly string[]):T[]{
 return proposed;
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
/** Resize is bounded by the slide only; peers may be freely overlapped.
 * Preserve the original gesture transaction and explicitly disable autoFit
 * after a manual resize, so the author controls the rectangle exactly. */
export function resizeWidgetToCollisionLimit<T extends Widget>(original:readonly T[],id:string,proposed:Box):T[]{
 const source=original.find(w=>w.id===id);
 if(!source||!source.position)return [...original];
 if(!Object.values(proposed).every(Number.isFinite)||proposed.width<.01||proposed.height<.01||
    proposed.x<0||proposed.y<0||proposed.x+proposed.width>100.0001||
    proposed.y+proposed.height>100.0001)return [...original];
 return original.map(w=>w.id===id?{...w,position:{...w.position,...proposed},autoFit:false} as T:w);
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
/** Preserve the chosen drop point without reserving space around other widgets.
 * Layers can intentionally cover each other; the canvas is the only boundary. */
export function freeWidgetPosition<T extends Widget>(_items:readonly T[],preferred:{x:number;y:number},width=22,height=20):Box|null{
 if(![preferred.x,preferred.y,width,height].every(Number.isFinite)||width<=0||height<=0||width>100||height>100)return null;
 return {x:Math.max(0,Math.min(100-width,preferred.x)),y:Math.max(0,Math.min(100-height,preferred.y)),width,height};
}

/** Pointer and keyboard movement share slide-boundary clamping; overlapping is
 * permitted for every widget kind, not just decoration/graphics. */
export function moveWidgetsToCollisionLimit<T extends Widget>(original:T[],ids:readonly string[],dx:number,dy:number):T[]{
 return moveWidgetGroup(original,ids,dx,dy);
}
