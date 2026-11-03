/** Smartphone uses a separate 390px logical stage. */
export const PHONE_STAGE_WIDTH = 390;
export const PHONE_STAGE_HEIGHT = 720;
export function phoneStageScale(viewportWidth:number):number {
 if (!Number.isFinite(viewportWidth) || viewportWidth<=0) return 1;
 return Math.min(1,viewportWidth/PHONE_STAGE_WIDTH);
}
