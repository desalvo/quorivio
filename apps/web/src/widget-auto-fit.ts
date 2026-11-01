/** Grow an editor widget just enough to show its content without moving its top edge.
 * Geometric bounds and collision safety are enforced by the caller.
 * Manual resizing disables autoFit until explicitly reenabled in Properties. */
export function autoFitExpandedPosition<P extends {x:number;y:number;width:number;height:number}>(p:P, overflowPx:number, canvasHeightPx:number):P|null{
 if(!Number.isFinite(overflowPx)||!Number.isFinite(canvasHeightPx)||overflowPx<=2||canvasHeightPx<=0)return null;
 const height=Math.min(100-p.y,Math.ceil((p.height+(overflowPx+8)/canvasHeightPx*100)*100)/100);
 if(height<=p.height+.2)return null;
 return {...p,height};
}
export function widgetMayAutoFit(kind:string,autoFit?:boolean){
 return autoFit!==false&&['question','timed-quiz','topic-question','text','postit','profile','rating'].includes(kind);
}

/** Measure ONLY the inner content. The outer widget's scrollHeight also includes
 * absolutely positioned resize handles protruding past its lower edge; using
 * that figure caused a self-sustaining +pixels auto-grow loop on every render.
 * Report zero for unmounted or invalid geometry rather than enlarging a slide.
 */
export function measuredContentOverflowPx(frameHeight:number, contentScrollHeight:number):number {
 if(!Number.isFinite(frameHeight)||!Number.isFinite(contentScrollHeight)||frameHeight<=0||contentScrollHeight<0)return 0;
 return Math.max(0,Math.ceil(contentScrollHeight-frameHeight));
}
