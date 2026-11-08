/** Floating editor panels are intentionally dockable at screen edges.
 * Keep a graspable strip of the window visible rather than constraining its
 * entire (sometimes very large) body inside the viewport. */
/** CSS zoom on the HTML root changes the fixed-element coordinate system,
 * but window.innerWidth/Height continue to report physical CSS pixels. Root
 * clientWidth/Height can be physical *or* logical depending on overflow rules. */
export function floatingLogicalViewport(physicalWidth:number,physicalHeight:number,cssZoom:number){
 const zoom=Number.isFinite(cssZoom)&&cssZoom>0?cssZoom:1;
 return {width:Math.max(1,physicalWidth/zoom),height:Math.max(1,physicalHeight/zoom)};
}

export const FLOATING_GRAB_WIDTH=112;
export const FLOATING_GRAB_HEIGHT=44;

export function boundFloatingPosition(left:number,top:number,width:number,height:number,viewportWidth:number,viewportHeight:number){
 const vw=Math.max(1,viewportWidth),vh=Math.max(1,viewportHeight);
 const reachableWidth=Math.min(FLOATING_GRAB_WIDTH,vw);
 const minLeft=Math.min(8,reachableWidth-Math.max(1,width));
 const maxLeft=Math.max(minLeft,vw-reachableWidth);
 const maxTop=Math.max(8,vh-Math.min(FLOATING_GRAB_HEIGHT,vh));
 return {left:Math.max(minLeft,Math.min(left,maxLeft)),top:Math.max(8,Math.min(top,maxTop))};
}

/** Pointer or keyboard resize; the entire panel must fit on a compact screen
 * when resized, while docking may leave the body outside the viewport. */
export function boundFloatingSize(width:number,height:number,viewportWidth:number,viewportHeight:number,placement:'palette'|'properties'|'page'='properties'){
 const maxWidth=Math.max(1,viewportWidth-16),maxHeight=Math.max(1,viewportHeight-16);
 const minWidth=Math.min(placement==='palette'?320:280,maxWidth);
 const minHeight=Math.min(placement==='palette'?115:160,maxHeight);
 return {width:Math.max(minWidth,Math.min(width,maxWidth)),height:Math.max(minHeight,Math.min(height,maxHeight))};
}
