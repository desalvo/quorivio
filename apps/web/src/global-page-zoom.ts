/** Accessible, app-wide visual zoom; no project/session or credential data is stored. */
export const GLOBAL_ZOOM_STORAGE_KEY='quorivio.ui.zoom.v1';
export const GLOBAL_ZOOM_MIN=70;
export const GLOBAL_ZOOM_MAX=150;
export const GLOBAL_ZOOM_STEP=10;
export function normalizeGlobalZoom(value:unknown):number{
 const numeric=typeof value==='number'?value:typeof value==='string'&&value.trim()?Number(value):NaN;
 if(!Number.isFinite(numeric))return 100;
 return Math.max(GLOBAL_ZOOM_MIN,Math.min(GLOBAL_ZOOM_MAX,Math.round(numeric/GLOBAL_ZOOM_STEP)*GLOBAL_ZOOM_STEP));
}
export function nextGlobalZoom(value:number,direction:-1|1):number{
 return normalizeGlobalZoom(normalizeGlobalZoom(value)+direction*GLOBAL_ZOOM_STEP);
}
export function zoomStyleValue(value:number):string{
 return normalizeGlobalZoom(value)===100?'':`${normalizeGlobalZoom(value)}%`;
}
