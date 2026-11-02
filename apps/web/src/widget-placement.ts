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
/** Resize an interactive widget towards a proposed rectangle until its first
 * collision. Resizing is monotone from its saved starting rectangle: it cannot
 * jump across a narrow neighbour or undo an entire gesture when one edge hits.
 * Graphics keep the intentional overlay policy; invalid geometries fail shut.
 * Use the pointer-down base for every move, not the preceding intermediate box.
 */
export function resizeWidgetToCollisionLimit<T extends Widget>(
 original:readonly T[],id:string,proposed:Box
):T[]{
 const source=original.find(item=>item.id===id);
 if(!source||!source.position)return [...original];
 const base=rect(source);
 const values=[...Object.values(base),...Object.values(proposed)];
 if(!values.every(Number.isFinite)||proposed.width<.01||proposed.height<.01||
    proposed.x<0||proposed.y<0||proposed.x+proposed.width>100.0001||
    proposed.y+proposed.height>100.0001)return [...original];
 const withBox=(box:Box):T[]=>original.map(w=>w.id===id?{
  ...w,position:{...w.position,...box},autoFit:false
 } as T:w);
 if(isFreeGraphic(source.kind))return withBox(proposed);
 const fixed=original.filter(w=>w.id!==id&&!isFreeGraphic(w.kind));
 if(fixed.some(w=>hit(base,rect(w))))return [...original];
 if(!fixed.some(w=>hit(proposed,rect(w))))return withBox(proposed);
 const interpolated=(t:number):Box=>({
  x:base.x+(proposed.x-base.x)*t,y:base.y+(proposed.y-base.y)*t,
  width:base.width+(proposed.width-base.width)*t,
  height:base.height+(proposed.height-base.height)*t
 });
 // Along an edge/corner resize the occupied rectangle can only grow or shrink
 // on each affected side. Collision occupancy is monotonic for these gestures.
 let low=0,high=1;
 for(let n=0;n<36;n++){
  const mid=(low+high)/2;
  if(fixed.some(w=>hit(interpolated(mid),rect(w))))high=mid;
  else low=mid;
 }
 const maxDelta=Math.max(...Object.keys(base).map(k=>Math.abs(proposed[k as keyof Box]-base[k as keyof Box])));
 const inset=maxDelta?Math.min(low,.0003/maxDelta):0;
 const safe=Math.max(0,low-inset);
 // Match the page's serialized four-decimal geometry. Round-trip quantization
 // must never introduce a tiny overlap that the analytical sweep had avoided.
 let candidate:Box=interpolated(safe);
 candidate={x:+candidate.x.toFixed(4),y:+candidate.y.toFixed(4),width:+candidate.width.toFixed(4),height:+candidate.height.toFixed(4)};
 return fixed.some(w=>hit(candidate,rect(w)))?[...original]:withBox(candidate);
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

/** Continuous swept AABB collision test for a rigid translated widget group.
 * Sampling the pointer path can tunnel through thin obstacles when the browser
 * coalesces pointer events; calculate the FIRST contact time analytically.
 * Both axes use the same fraction, so diagonal drags do not skew the group.
 * Graphics (shapes and lines) remain freely overlayable by design. */
function sweptContact(a:Box,b:Box,dx:number,dy:number):number|null{
 const axis=(a0:number,a1:number,b0:number,b1:number,d:number):[number,number]|null=>{
  if(d===0)return a0<b1-.0001&&a1>b0+.0001?[-Infinity,Infinity]:null;
  const t0=(b0-a1)/d,t1=(b1-a0)/d;
  return [Math.min(t0,t1),Math.max(t0,t1)];
 };
 const x=axis(a.x,a.x+a.width,b.x,b.x+b.width,dx);
 const y=axis(a.y,a.y+a.height,b.y,b.y+b.height,dy);
 if(!x||!y)return null;
 const enter=Math.max(x[0],y[0]),leave=Math.min(x[1],y[1]);
 if(enter>=leave||leave<=0||enter>1)return null;
 return Math.max(0,enter);
}
/** Stop at the first physical boundary, independently of pointer speed or
 * obstacle thickness. The canvas clamp from moveWidgetGroup is honored before
 * the sweep, and all selected widgets retain their original relative offsets. */
export function moveWidgetsToCollisionLimit<T extends Widget>(original:T[],ids:readonly string[],dx:number,dy:number):T[]{
 if(!Number.isFinite(dx)||!Number.isFinite(dy)||!ids.length)return original;
 const chosen=new Set(ids);
 const moving=original.filter(w=>chosen.has(w.id)&&!isFreeGraphic(w.kind));
 if(!original.some(w=>chosen.has(w.id)))return original;
 const target=moveWidgetGroup(original,ids,dx,dy);
 const first=original.find(w=>chosen.has(w.id))!;
 const final=target.find(w=>w.id===first.id)!;
 // Account for the common group clamp and 4-decimal stage rounding.
 const actualX=number(final.position?.x,0)-number(first.position?.x,0);
 const actualY=number(final.position?.y,0)-number(first.position?.y,0);
 if(!actualX&&!actualY)return original;
 const fixed=original.filter(w=>!chosen.has(w.id)&&!isFreeGraphic(w.kind));
 // Starting in an invalid overlapping state must never generate an additional
 // overlap; independent repair belongs to the explicit layout recovery path.
 if(moving.some(a=>fixed.some(b=>hit(rect(a),rect(b)))))return original;
 let firstContact=1;
 for(const a of moving)for(const b of fixed){
  const contact=sweptContact(rect(a),rect(b),actualX,actualY);
  if(contact!==null)firstContact=Math.min(firstContact,contact);
 }
 if(firstContact>=1)return target;
 // Keep the saved four-decimal rectangles strictly outside their neighbors.
 const inset=Math.min(firstContact,.0002/Math.max(Math.abs(actualX),Math.abs(actualY)));
 const safe=Math.max(0,firstContact-inset);
 const stopped=moveWidgetGroup(original,ids,actualX*safe,actualY*safe);
 return overlapsOtherWidgets(stopped,ids)?original:stopped;
}
