/** RC327 — a single, overflow-safe proportional transform for the whole widget.
 * The renderer measures the unscaled content including all chart/legend/rows.
 * No font, SVG, bar, label or answer option gets an independent scale.
 */
export type FitDimensions={frameWidth:number;frameHeight:number;contentWidth:number;contentHeight:number;predictedWidth?:number;predictedHeight?:number;minScale?:number;maxScale?:number};
export function proportionalWidgetScale(d:FitDimensions):number {
 const numbers=[d.frameWidth,d.frameHeight,d.contentWidth,d.contentHeight,d.predictedWidth??0,d.predictedHeight??0];
 if(numbers.some(n=>!Number.isFinite(n)||n<0)||d.frameWidth<=0||d.frameHeight<=0)return 1;
 const width=Math.max(1,d.contentWidth,d.predictedWidth??0),height=Math.max(1,d.contentHeight,d.predictedHeight??0);
 // A user-preferred minimum must never override the actual fit: otherwise
 // unusually long answers overflow even when automatic scaling is enabled.
 // Grow to the largest possible proportional fit, unless an explicit positive
 // upper bound was requested by a specialized renderer.
 const maximum=Number.isFinite(d.maxScale)&&d.maxScale!>0?d.maxScale!:Infinity;
 const fit=Math.min(d.frameWidth/width,d.frameHeight/height,maximum);
 return fit>0?fit:Number.MIN_VALUE;
}
export function predictedResultsHeight(input:{rows:number;maxRowHeight:number;otherHeight:number;truthBadge?:boolean}):number{
 if(!Number.isFinite(input.rows)||!Number.isFinite(input.maxRowHeight)||!Number.isFinite(input.otherHeight))return 0;
 const rows=Math.max(0,Math.min(1024,Math.ceil(input.rows)));
 // A checked answer/circle never causes a fresh scroll when its visibility changes.
 const rowHeight=Math.max(16,input.maxRowHeight)+(input.truthBadge?4:0);
 return Math.max(0,input.otherHeight)+rows*rowHeight;
}
