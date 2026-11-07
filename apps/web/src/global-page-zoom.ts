/** Accessible, app-wide visual zoom; no project/session or credential data is stored. */
export const GLOBAL_ZOOM_STORAGE_KEY='quorivio.ui.zoom.v2';
/** 100% means the previous 80% interface chrome; viewport/canvas size is compensated in CSS. */
export const GLOBAL_ZOOM_BASE=0.8;
export const GLOBAL_ZOOM_CSS_VARIABLE='--quorivio-ui-scale';
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
 return `${Math.round(normalizeGlobalZoom(value)*GLOBAL_ZOOM_BASE)}%`;
}
