/**
 * Portal thumbnail menus must never cover their own trigger.  A scrollable
 * side-rail and global zoom can move the trigger after opening, so this
 * calculation uses the live trigger rectangle, not stale click coordinates.
 *
 * The optional anchor preserves the historical coordinate-only positioning
 * contract for unrelated callers/tests.  With an anchor, first use the free
 * space beside it (shrinking menu width on narrow phones), otherwise choose
 * the larger vertical gap. The menu remains scrollable inside the viewport.
 */
export type ThumbnailMenuAnchor={left:number;right:number;top:number;bottom:number};

export function thumbnailMenuPosition(
 x:number,y:number,viewportWidth:number,viewportHeight:number,
 anchor?:ThumbnailMenuAnchor,
){
 const pad=8,gap=8;
 const safeViewportWidth=Math.max(1,viewportWidth);
 const safeViewportHeight=Math.max(1,viewportHeight);
 const menuWidth=Math.min(270,Math.max(1,safeViewportWidth-pad*2));
 const availableHeight=Math.max(1,safeViewportHeight-pad*2);
 const preferredHeight=Math.min(340,availableHeight);
 const safeX=Number.isFinite(x)?x:pad,safeY=Number.isFinite(y)?y:pad;
 const clamp=(n:number,low:number,high:number)=>Math.max(low,Math.min(n,Math.max(low,high)));
 let width=menuWidth;
 let left=clamp(safeX,pad,safeViewportWidth-width-pad);
 let top=clamp(safeY,pad,safeViewportHeight-preferredHeight-pad);
 let maxHeight=Math.max(1,Math.floor(viewportHeight-top-pad));
 if(anchor && [anchor.left,anchor.right,anchor.top,anchor.bottom].every(Number.isFinite)
    && anchor.right>=anchor.left && anchor.bottom>=anchor.top){
   const freeRight=Math.max(0,safeViewportWidth-pad-anchor.right-gap);
   const freeLeft=Math.max(0,anchor.left-gap-pad);
   const reasonableMin=Math.min(160,menuWidth);
   if(freeRight>=reasonableMin || (freeRight>=freeLeft && freeRight>0)){
     width=Math.min(menuWidth,freeRight);
     left=clamp(anchor.right+gap,pad,safeViewportWidth-width-pad);
   }else if(freeLeft>=reasonableMin || freeLeft>0){
     width=Math.min(menuWidth,freeLeft);
     left=clamp(anchor.left-gap-width,pad,safeViewportWidth-width-pad);
   }else{
     // No usable side space: open wholly above/below the button, never on it.
     const below=Math.max(0,safeViewportHeight-pad-anchor.bottom-gap);
     const above=Math.max(0,anchor.top-gap-pad);
     left=clamp(anchor.left,pad,safeViewportWidth-width-pad);
     if(below>=above){
       top=clamp(anchor.bottom+gap,pad,safeViewportHeight-pad);
       maxHeight=Math.max(1,Math.floor(below));
     }else{
       maxHeight=Math.max(1,Math.floor(above));
       top=clamp(anchor.top-gap-maxHeight,pad,safeViewportHeight-pad);
     }
   }
 }
 return {left,top,maxHeight,width};
}
